import logging
import json
from time import sleep
from random import randrange
import requests
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

from settings import HEADERS, URL_REFRESH_TOKEN, URL_BALANCE, TOKEN_FILE, URL_ME, \
    URL_FARMING_CLAIM, URL_FARMING_START, URL_PLAY_START, URL_PLAY_CLAIM, URL_DAILY_REWARD, \
    URL_FRIENDS_BALANCE, URL_FRIENDS_CLAIM

class CustomFormatter(logging.Formatter):
    GREEN = Fore.GREEN
    RED = Fore.RED
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL

    def format(self, record):
        if hasattr(record, 'username') and record.username:
            username_colored = f"{self.GREEN}@{record.username}{self.RESET}"
            if hasattr(record, 'error_code') and hasattr(record, 'error_message'):
                error_msg_colored = f"{self.RED}{record.msg}. Код ошибки: {record.error_code}, Причина: {record.error_message}{self.RESET}"
                record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {error_msg_colored}"
            else:
                if 'Обновление баланса' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.BLUE}{record.msg}{self.RESET}"
                elif 'Ежедневная награда получена!' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.GREEN}{record.msg}{self.RESET}"
                elif 'Не удалось получить ежедневную награду' in record.msg and 'Уже получено!' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.RED}{record.msg}{self.RESET}"
                elif 'Не удалось получить токен' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.RED}{record.msg}{self.RESET}"
                elif 'Ошибка при обновлении баланса:' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.RED}{record.msg}{self.RESET}"
                elif 'Ошибка при получении награды от друзей:' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.RED}{record.msg}{self.RESET}"
                elif 'Ошибка при запросе баланса друзей:' in record.msg:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {self.RED}{record.msg}{self.RESET}"
                else:
                    record.msg = f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} - {record.levelname} [{username_colored}] — {record.msg}"
        return super().format(record)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
formatter = CustomFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger().handlers = [handler]

def retry(func):
    def wrapper(self, *args, **kwargs):
        while True:
            try:
                result = func(self, *args, **kwargs)
                return result
            except Exception as e:
                logging.error(f"Ошибка HTTP сессии: {e}", extra={'username': self.username})
                sleep(10)
    return wrapper

class BlumClient(requests.Session):

    balance = None
    balance_data = None
    play_passes = None
    tasks = None
    auth_data = None
    username = None  # Добавляем атрибут username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = HEADERS.copy()
        self.authenticate()
        self.me()

    @retry
    def request(self, *args, **kwargs):
        while True:
            result = super().request(*args, **kwargs)
            if result.status_code == 401:
                self.refresh_token()
            else:
                return result
    
    @property
    def estimate_time(self):
        default_est_time = 60
        if 'farming' in self.balance_data:
            est_time = (self.balance_data['farming']['endTime'] - self.balance_data['timestamp']) / 1000 + 1
            return est_time if est_time > 0 else default_est_time
        else:
            return default_est_time

    def me(self):
        result = self.get(URL_ME)
        if result.status_code == 200:
            self.username = result.json().get('username')  # Устанавливаем значение username
        return result

    def authenticate(self):
        with open(TOKEN_FILE, 'r') as tok_file:
            self.auth_data = json.load(tok_file)
        self.headers['Authorization'] = "Bearer {}".format(self.auth_data.get('access'))
        response = self.me()
        if response.status_code == 401:
            self.refresh_token()
        elif response.status_code == 200:
            self.make_refresh()
    
    def dump_token(self, response):
        if response.status_code == 200:
            self.auth_data = response.json()
        else:
            raise Exception("Не удалось получить токен")
        self.headers['Authorization'] = "Bearer {}".format(self.auth_data.get('access'))
        with open(TOKEN_FILE, 'w') as tok_file:
            json.dump(self.auth_data, tok_file)

    def make_refresh(self):
        response = self.post(URL_REFRESH_TOKEN, json={"refresh": self.auth_data.get("access")})
        self.dump_token(response=response)
    
    def refresh_token(self):
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
        response = self.post(URL_REFRESH_TOKEN, json={"refresh": self.auth_data.get("refresh")})
        self.dump_token(response=response)

    def update_balance(self):
        logging.info("Обновление баланса", extra={'username': self.username})
        response = self.get(URL_BALANCE, headers=self.headers)
        if response.status_code == 200:
            self.balance_data = response.json()
            self.balance = self.balance_data['availableBalance']
            self.play_passes = self.balance_data['playPasses']
            logging.info(json.dumps(self.balance_data, ensure_ascii=False), extra={'username': self.username})
        else:
            logging.error(f"Ошибка при обновлении баланса: {response.status_code}, {response.text}", extra={'username': self.username})
            
    def start_farming(self):
        if 'farming' not in self.balance_data:
            logging.info("Запуск фарминга", extra={'username': self.username})
            result = self.post(URL_FARMING_START)
            logging.info(f"{result.status_code},  {result.text}", extra={'username': self.username})
            self.update_balance()
        elif self.balance_data["timestamp"] >= self.balance_data["farming"]["endTime"]:
            logging.info('Сгребаем нафармленное', extra={'username': self.username})
            result = self.post(URL_FARMING_CLAIM)
            logging.info(f"{result.status_code},  {result.text}", extra={'username': self.username})
            self.update_balance()
        logging.info(f'Ожидание завершения фарминга {self.estimate_time} секунд', extra={'username': self.username})
        sleep(self.estimate_time)

    def play_game(self):
        for _ in range(self.play_passes or 0):
            logging.info(f"Начинаем тапать звездочки (камушков: {self.play_passes})", extra={'username': self.username})
            res = self.post(URL_PLAY_START)
            if res.status_code == 200:
                data = res.json()
                data['points'] = game_points = randrange(150, 250)
                sleep(30)  # Там вроде около 30 секунд
                while True:
                    logging.info(f"Отправка рандомного результата игры {game_points}", extra={'username': self.username})
                    result = self.post(URL_PLAY_CLAIM, json=data)
                    if result.status_code == 200:
                        break
                    else:
                        sleep(1)
                self.update_balance()
                logging.info(result.text, extra={'username': self.username})

    def daily_reward(self):
        result = self.post(URL_DAILY_REWARD)
        if result.status_code == 200:
            reward_data = result.json()
            logging.info(f'Ежедневная награда получена! Токены: {reward_data.get("tokens", 0)}, Билеты: {reward_data.get("tickets", 0)}', extra={'username': self.username})
        else:
            error_message = result.json().get('message', result.text)
            if error_message == "same day":
                error_message = "Уже получено!"
            logging.error(f'Не удалось получить ежедневную награду. Код ошибки: {result.status_code}, Причина: {error_message}', extra={'username': self.username})
            
    def friends_claim(self):
        friends_balance = self.get(URL_FRIENDS_BALANCE)
        if friends_balance.status_code == 200:
            if friends_balance.json().get('canClaim'):
                result = self.post(URL_FRIENDS_CLAIM)
                if result.status_code == 200:
                    logging.info("Друзья нафармили: {}".format(result.json()['claimBalance']), extra={'username': self.username})
                else:
                    logging.error(f"Ошибка при получении награды от друзей: {result.status_code}, {result.text}", extra={'username': self.username})
        else:
            logging.error(f"Ошибка при запросе баланса друзей: {friends_balance.status_code}, {friends_balance.text}", extra={'username': self.username})
