from flask import Flask, request
from Core.Bot.Bot_Config import bot
import telebot

app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def Telegram_bot():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'OK', 200


@app.route('/')
def index():
    return 'Hello_Bot!!!'


if __name__ == '__main__':
    app.run()
