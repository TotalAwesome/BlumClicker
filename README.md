# BlumClicker

Пример того, как можно автоматизировать рутину в телеграм боте с MiniApp

В публичный доступ код выкладываю без автоматизации получения access-токена,
но прикладываю краткую инструкцию как можно это сделать вручную.

Бот умеет:
- Запускать фарм
- Запускать игру и забирать с нее максимальный профит
- Собирать ежедневный бонус.

Что планирую сделать:
- ~~Рандомизировать результат игры~~ ✅
- ~~Починить сбор ежедневных наград~~ ✅

В Telegram Desktop необходимо включить режи отладки WebView:

_Settings -> Advanced -> Experimental settings -> Enable WebView inspecting_

1. Переходим в бота https://t.me/BlumCryptoBot
2. Нажимаем "`Launch Blum`"
3. На поверхности открывшегося приложения вызвать меню и выбрать `Inspect element`
4. Далее как на скрине ниже переходим в network и ждем пока в списке запросов не появится `refresh` (может понадобиться время, пока текущий токен не просрочится)
5. В ответе запроса будет то, что нам нужно. Содержимое скопировать в `token.json`
6. `pip install -r requirements.txt`
7. Запустить скрипт `python3 main.py`

![image](https://github.com/TotalAwesome/BlumClicker/assets/39047158/1acc5fbc-5e0b-430a-9f16-6e7e01d4f87b)

Для macos и windows нужно скачать бета-версию настольного клиента.

Для пользователей macOS включение отладки выглядит так:

https://telegram.org/dl/macos/beta

![image](https://github.com/TotalAwesome/BlumClicker/assets/39047158/9faf1a5d-430c-4acf-bbd6-389b31aa4b7a)

Обсудить можно тут: https://t.me/CryptoAutoFarm

Для донатов:
USDT TRC20: TTTMM1PXxNS7d3tAcruamT6GE8ye5BrZ4w
