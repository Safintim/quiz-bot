# quiz-bot

## Описание
quiz-bot - это два бота (вконтакте и телеграмм), которые выполнены в стиле викторины.

## Пример работы
![Alt Text](http://ipic.su/img/img7/fs/quiz-telebot.1560949231.gif)
![Alt Text](http://ipic.su/img/img7/fs/quiz-vkbot.1560949396.gif)

## Требования

Для запуска скрипта требуется:

*Python 3.6*

## Как установить:

1. Установить Python3:

(Windows):[python.org/downloads](https://www.python.org/downloads/windows/)

(Debian):

```sh
sudo apt-get install python3
sudo apt-get install python3-pip
```

2. Установить зависимости и скачать сам проект:

```sh
git clone https://github.com/Safintim/quiz-bot.git
cd quiz-bot
pip3 install -r requirements.txt
```

3. Зарегистрироваться на [Redislabs](https://redislabs.com/) и получить адрес базы данных.
4. Персональные настройки:

Скрипт берет настройки из .env файла, где указаны токен телеграм-бота, токен вк-бота, 
токен чат-логгер-бота, номер чата, хост, порт, пароль базы данных. Создайте файл .env вида:

```.env
TELEGRAM_BOT_TOKEN=your_token
VK_BOT_TOKEN=your_token
LOGGER_BOT_TOKEN=your_token
LOGS_RECEIVER_ID=your_chat_id
VK_GROUP_ID=your_vk_group_id
REDIS_HOST=your_redis_host
REDIS_PASSWORD=your_redis_password
REDIS_PORT=your_redis_port
```

6. Требуется создать внутри проекта quiz-bot директорию "quiz-questions", в которой должны быть файлы с вопросами
и ответами.

```sh
mkdir quiz-questions
```

7. Создать текстовые файлы с вопросами внутри директории quiz-questions вида:

```markdown
Вопрос 1:
...текст_вопроса...


Ответ:
...текст_ответа...


Вопрос 2:
...текст_вопроса...


Ответ:
...текст_ответа...
```

## Как использовать:

Загрузить вопросы в бд:

```sh
python3 db_tools.py
```

Запустить вк бота:

```sh
python3 vk_bot.py
```

Запустить телеграмм бота:
```sh
python3 telegram_bot.py
```

## Демо-боты
Данные боты готовы к использованию. Пример их работы указан на гифках выше.
 Можно поиграться с ботами, найдя их в вк и в телеграме.
 
* [Викторина](https://vk.com/public182993963) - вк-бот
* **_@test_quizz_bot_** - телеграм-бот
* **_@devmanlogging_bot_** - телеграм-логгер-бот, данный бот выполняет мониторинг телеграм- и вк-ботов.
В случае ошибки придет уведомление о том какой "бот упал" и почему "бот упал",
 а также при запуске бот сообщит о том какой бот запущен.

![Alt Text](http://ipic.su/img/img7/fs/quiz-log.1559419941.png)

## Комментарии

Есть возможность не использовать логгер-бота или использовать своего, для этого нужно написать свой обработчик логов. И если понадобится написать своего бота.

Пример:
```python
class LogsHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.bot = telegram.Bot(os.getenv('LOGGER_BOT_TOKEN'))

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=os.getenv('LOGS_RECEIVER_ID'), text=log_entry)
```
