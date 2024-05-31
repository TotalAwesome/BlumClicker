URL_ME = "https://gateway.blum.codes/v1/user/me"
URL_REFRESH_TOKEN = "https://gateway.blum.codes/v1/auth/refresh"
URL_BALANCE = "https://game-domain.blum.codes/api/v1/user/balance"
URL_FARMING_CLAIM = "https://game-domain.blum.codes/api/v1/farming/claim"
URL_FARMING_START = "https://game-domain.blum.codes/api/v1/farming/start"
URL_PLAY_START = "https://game-domain.blum.codes/api/v1/game/play"
URL_PLAY_CLAIM = "https://game-domain.blum.codes/api/v1/game/claim"
URL_DAILY_REWARD = "https://game-domain.blum.codes/api/v1/daily-reward?offset=-180"

HEADERS = {
    "Accept": 'application/json',
    "Accept-Encoding": 'gzip, deflate, br, zstd',
    "Accept-Language": 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36"
}

TOKEN_FILE = "token.json"
