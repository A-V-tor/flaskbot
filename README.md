<h1>Телеграм бот с Flask-admin <img src='https://img.shields.io/badge/flaskbot-A--V--tor-blue?logo=telegram&logoColor=white&style=flat'/> <img src='https://img.shields.io/badge/-Flask%202.2.2-green'/> <img src='https://img.shields.io/badge/-Flask--Admin%201.6.2-green'/> <img src='https://img.shields.io/badge/-pyTelegramBotAPI%204.7.1-informational'/> <img src='https://img.shields.io/badge/-dash%202.7.0-9cf'/></h1>
<br>
Перед первым пуском разкомментировать строки<br><br>

<code># admin_user = AdminProfile(name='admin', psw='admin', owner=True)</code><br>
<code># db.session.add(admin_user)</code><br>
<code># db.session.commit()</code><br><br>
в <code>other.py</code> после вновь закомментить.<br><br>

Вход в админку <code>http://127.0.0.1:5000/login</code><br><br>

<h3>файл .env</h3>
<code>token=токен от BotFather</code>
</br>
<code>secret_key=ключ для шифрования</code>
</br>
<h3>Установить вебхук</h3>

<code>curl --location --request POST 'https://api.telegram.org/bot<b>TOKEN</b>/setWebhook' --header 'Content-Type: application/json' --data-raw '{"url": "https://<b>URL</b>"}'</code>

<br>
<img src="https://github.com/A-V-tor/flaskbot/blob/main/flaskbot/admin.png">
</br>
<img src="https://github.com/A-V-tor/flaskbot/blob/main/flaskbot/visits.png">
</br>


