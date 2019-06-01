# quiz-bot

## Описание
quiz-bot - это два бота (вконтакте и телеграмм), которые выполнены в стиле викторины.



## Пример работы
![Alt Text](http://ipic.su/img/img7/fs/quiz-telebot.1559418673.gif)
![Alt Text](http://ipic.su/img/img7/fs/quiz-vkbot.1559418740.gif)


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
TELEGRAM_BOT=your_token
VK_BOT=your_token
LOGGER_BOT=your_token
CHAT_ID=your_chat_id
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
```