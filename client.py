import json
import logging
from time import sleep
from random import randrange
from requests import Session
from settings import HEADERS, URL_REFRESH_TOKEN, URL_BALANCE, TOKEN_FILE, URL_ME, \
      URL_FARMING_CLAIM, URL_FARMING_START, URL_PLAY_START, URL_PLAY_CLAIM, URL_DAILY_REWARD, \
      URL_FRIENDS_BALANCE, URL_FRIENDS_CLAIM

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s]    %(message)s")


def retry(func):
    def wrapper(self, *args, **kwargs):
        while True:
            try:
                result = func(self, *args, **kwargs)
                return result
            except Exception as e:
                logging.error(f"Http session error: {e}")
                sleep(10)
    return wrapper


class BlumClient(Session):

    balance = None
    balance_data = None
    play_passes = None
    tasks = None
    auth_data = None

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
            self.name = result.json()['username']
        return result

    def authenticate(self):
        with open(TOKEN_FILE, 'r') as tok_file:
            self.auth_data = json.load(tok_file)
        self.headers['Authorization'] = "Bearer {}".format(self.auth_data.get('access'))
        response = self.me()
        if response.status_code == 401:
            self.refresh_token()
            
    def refresh_token(self):
        if 'Authorization' in self.headers:
            del self.headers['Authorization']
        response = self.post(URL_REFRESH_TOKEN, json={"refresh": self.auth_data.get("refresh")})
        if response.status_code == 200:
            self.auth_data = response.json()
        else:
            raise Exception("Can't get token")
        self.headers['Authorization'] = "Bearer {}".format(self.auth_data.get('access'))
        with open(TOKEN_FILE, 'w') as tok_file:
            json.dump(self.auth_data, tok_file)

    def update_balance(self):
        logging.info("Обновление баланса")
        response = self.get(URL_BALANCE, headers=self.headers)
        if response.status_code == 200:
            self.balance_data = response.json()
            self.balance = self.balance_data['availableBalance']
            self.play_passes = self.balance_data['playPasses']
            logging.info(json.dumps(self.balance_data))
    
    def start_farming(self):
        if 'farming' not in self.balance_data:
            logging.info("Запуск фарминга")
            result = self.post(URL_FARMING_START)
            logging.info(f"{result.status_code},  {result.text}")
            self.update_balance()
        elif self.balance_data["timestamp"] >= self.balance_data["farming"]["endTime"]:
            logging.info('Сгребаем нафармленное')
            result = self.post(URL_FARMING_CLAIM)
            logging.info(f"{result.status_code},  {result.text}")
        logging.info(f'Ожидание завершения фарминга {self.estimate_time} секунд')
        sleep(self.estimate_time)

    def play_game(self):
        for _ in range(self.play_passes or 0):
            logging.info(f"Начинаем тапать звездочки (камушков: {self.play_passes})")
            res = self.post(URL_PLAY_START)
            if res.status_code == 200:
                data = res.json()
                data['points'] = game_points = randrange(150, 250)
                sleep(30)  # Там вроде около 30 секунд
                while True:
                    logging.info(f"Отправка рандомного результата игры {game_points}")
                    result = self.post(URL_PLAY_CLAIM, json=data)
                    if result.status_code == 200:
                        break
                    else:
                        sleep(1)
                self.update_balance()
                logging.info(result.text)

    
    def daily_reward(self):
        result = self.get(URL_DAILY_REWARD)
        if result.status_code == 200:
            self.post(URL_DAILY_REWARD)
            logging.info(f'Ежедневная награда! {result.text}')

    def friends_claim(self):
        friends_balance = self.get(URL_FRIENDS_BALANCE)
        if friends_balance.status_code == 200:
            if friends_balance.json().get('canClaim'):
                result = self.post(URL_FRIENDS_CLAIM)
                if result.status_code == 200:
                    logging.info("Друзья нафармили: {}".format(result.json()['claimBalance']))
