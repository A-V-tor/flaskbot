<h1>Телеграм бот с Flask-admin</h1><img src='https://img.shields.io/badge/flaskbot-A--V--tor-blue?logo=telegram&logoColor=white&style=flat'/><img src='https://img.shields.io/badge/-Flask%202.2.2-green'/><img src='https://img.shields.io/badge/-Flask--Admin%201.6.2-green'/><img src='https://img.shields.io/badge/-pyTelegramBotAPI%204.7.1-informational'/>
<br>
<img src="https://github.com/A-V-tor/flaskbot/blob/main/flaskbot/admin.png">
</br>
<img src="https://github.com/A-V-tor/flaskbot/blob/main/flaskbot/visits.png">
</br>
<h3>файл .env</h3>
<code>token=токен от BotFather
</br>
secret_key=ключ для шифрования
</code>
</br>
<h3>Установить вебхук</h3>

<code>curl --location --request POST 'https://api.telegram.org/bot<TOKEN>/setWebhook' --header 'Content-Type: application/json' --data-raw '{"url": "https://<URL>"}'</code>

