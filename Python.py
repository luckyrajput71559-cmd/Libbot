#!/usr/bin/env python3
# Simple Stable Bot — Test Version
# Developer: @VICKYGAMING0

import telebot
import time

TOKEN = "8734071850:AAE7VVnXQiLDJSOwmEvLdL_W0XwSyZ6nvkc"  # CHANGE KAR
ADMIN_USERNAME = "VICKYGAMING0"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"🤖 Bot is live!\n👑 Developer: @{ADMIN_USERNAME}")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"📩 {message.text}")

if __name__ == "__main__":
    print("🤖 Bot Started Successfully!")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting...")
            time.sleep(5)
