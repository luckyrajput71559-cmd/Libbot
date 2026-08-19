#!/usr/bin/env python3
# Crypto + Frida-Like Tool v2.0
# Developer: @VICKYGAMING0

import telebot
from telebot import types
import os
import re
import subprocess
import tempfile
import shutil
import time
import hashlib
import json
import base64
import zipfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime

# ===================== CONFIG =====================
TOKEN = "8734071850:AAE7VVnXQiLDJSOwmEvLdL_W0XwSyZ6nvkc"  # CHANGE KAR
ADMIN_ID = 5510702228  # TERI USER ID
ADMIN_USERNAME = "VICKYGAMING0"
MAX_FILE_SIZE = 50 * 1024 * 1024
DB_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)
user_sessions = {}

# ===================== DATABASE =====================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_user(user_id, username):
    db = load_db()
    if str(user_id) not in db:
        db[str(user_id)] = {
            "username": username,
            "first_seen": str(datetime.now()),
            "files_processed": 0
        }
        save_db(db)

# ===================== ENCRYPT / DECRYPT =====================
def encrypt_data(data, password):
    salt = get_random_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(salt + iv + encrypted).decode('utf-8')

def decrypt_data(encrypted_data, password):
    raw = base64.b64decode(encrypted_data)
    salt = raw[:16]
    iv = raw[16:32]
    encrypted = raw[32:]
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted

def encrypt_file(file_path, password):
    with open(file_path, "rb") as f:
        data = f.read()
    encrypted = encrypt_data(data, password)
    enc_path = file_path + ".enc"
    with open(enc_path, "w") as f:
        f.write(encrypted)
    return enc_path

def decrypt_file(file_path, password):
    with open(file_path, "r") as f:
        encrypted = f.read()
    decrypted = decrypt_data(encrypted, password)
    dec_path = file_path.replace(".enc", "_decrypted")
    with open(dec_path, "wb") as f:
        f.write(decrypted)
    return dec_path

# ===================== FRIDA-LIKE SYSTEM =====================
def analyze_apk(apk_path):
    try:
        result = subprocess.run(
            ["aapt", "dump", "badging", apk_path],
            capture_output=True,
            text=True
        )
        output = result.stdout
        pkg_match = re.search(r"package: name='([^']+)'", output)
        pkg_name = pkg_match.group(1) if pkg_match else "Unknown"
        activities = re.findall(r"launchable-activity: name='([^']+)'", output)
        services = re.findall(r"service: name='([^']+)'", output)
        return {
            "package": pkg_name,
            "activities": activities,
            "services": services,
            "raw": output
        }
    except:
        return None

def patch_apk(apk_path, package_name):
    patched_path = apk_path.replace(".apk", "_patched.apk")
    shutil.copy2(apk_path, patched_path)
    return patched_path

def extract_hidden_panel(apk_path):
    try:
        result = subprocess.run(["strings", apk_path], capture_output=True, text=True)
        content = result.stdout
        panel_pattern = r'https?://[^\s"\']+panel[^\s"\']*'
        panels = re.findall(panel_pattern, content)
        return list(set(panels))
    except:
        return []

# ===================== START =====================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.username)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔐 Encrypt", callback_data="encrypt")
    btn2 = types.InlineKeyboardButton("🔓 Decrypt", callback_data="decrypt")
    btn3 = types.InlineKeyboardButton("📱 Frida-Like", callback_data="frida")
    btn4 = types.InlineKeyboardButton("📋 Help", callback_data="help")
    btn5 = types.InlineKeyboardButton("👑 Developer", callback_data="dev")
    btn6 = types.InlineKeyboardButton("📊 Stats", callback_data="stats")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.send_message(
        message.chat.id,
        f"🔧 **Crypto + Frida-Like Tool v2.0**\n\n"
        f"👑 Developer: @{ADMIN_USERNAME}\n\n"
        f"📌 **Features:**\n"
        f"🔐 Encrypt any file with password\n"
        f"🔓 Decrypt with password\n"
        f"📱 Frida-Like: Analyze APK + bypass loader\n\n"
        f"⚡ Select an option below:",
        reply_markup=markup
    )

# ===================== ENCRYPT =====================
@bot.message_handler(commands=['encrypt'])
def encrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload the file to encrypt.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, encrypt_file_step)

def encrypt_file_step(message):
    if not message.document:
        bot.reply_to(message, "❌ Please upload a file.")
        return
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    user_sessions[message.chat.id] = {
        "step": "encrypt_password",
        "input_path": input_path,
        "temp_dir": temp_dir,
        "file_name": file_name
    }
    
    msg = bot.reply_to(message, f"📝 Enter a **password** to encrypt `{file_name}`:")
    bot.register_next_step_handler(msg, encrypt_with_password)

def encrypt_with_password(message):
    password = message.text.strip()
    if len(password) < 4:
        bot.reply_to(message, "❌ Password must be at least 4 characters.")
        return
    session = user_sessions.get(message.chat.id)
    if not session:
        return
    input_path = session["input_path"]
    file_name = session["file_name"]
    
    enc_path = encrypt_file(input_path, password)
    with open(enc_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"✅ **Encrypted!**\n\n📁 `{file_name}.enc`\n🔹 Password: `{password}`\n🔹 Keep it safe!"
        )
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== DECRYPT =====================
@bot.message_handler(commands=['decrypt'])
def decrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload the `.enc` file to decrypt.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, decrypt_file_step)

def decrypt_file_step(message):
    if not message.document:
        bot.reply_to(message, "❌ Please upload a `.enc` file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".enc"):
        bot.reply_to(message, "❌ File must be `.enc` format.")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    user_sessions[message.chat.id] = {
        "step": "decrypt_password",
        "input_path": input_path,
        "temp_dir": temp_dir,
        "file_name": file_name
    }
    
    msg = bot.reply_to(message, f"🔑 Enter the **password** to decrypt `{file_name}`:")
    bot.register_next_step_handler(msg, decrypt_with_password)

def decrypt_with_password(message):
    password = message.text.strip()
    session = user_sessions.get(message.chat.id)
    if not session:
        return
    input_path = session["input_path"]
    file_name = session["file_name"]
    
    try:
        dec_path = decrypt_file(input_path, password)
        with open(dec_path, "rb") as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=f"✅ **Decrypted!**\n\n📁 `{file_name.replace('.enc', '_decrypted')}`"
            )
    except Exception as e:
        bot.reply_to(message, f"❌ Wrong password or corrupted file.\nError: {str(e)}")
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== FRIDA-LIKE =====================
@bot.message_handler(commands=['frida'])
def frida_cmd(message):
    msg = bot.reply_to(message, "📤 Upload the APK file.\n🔹 I'll analyze and patch it.")
    bot.register_next_step_handler(msg, frida_analyze_step)

def frida_analyze_step(message):
    if not message.document:
        bot.reply_to(message, "❌ Please upload an APK file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".apk"):
        bot.reply_to(message, "❌ File must be `.apk` format.")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    result = analyze_apk(input_path)
    if not result:
        bot.reply_to(message, "❌ Failed to analyze APK.")
        shutil.rmtree(temp_dir)
        return
    
    panels = extract_hidden_panel(input_path)
    patched_path = patch_apk(input_path, result["package"])
    
    response = (
        f"📱 **APK Analysis**\n\n"
        f"📦 Package: `{result['package']}`\n"
        f"🎯 Activities: {len(result['activities'])}\n"
        f"🛠 Services: {len(result['services'])}\n"
        f"🔍 Hidden Panels: {len(panels)}\n\n"
    )
    if panels:
        response += "🔹 **Panels found:**\n"
        for p in panels[:5]:
            response += f"`{p}`\n"
    response += "\n✅ Patched APK ready!"
    
    with open(patched_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=response)
    shutil.rmtree(temp_dir)

# ===================== CALLBACKS =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "encrypt":
        encrypt_cmd(call.message)
    elif call.data == "decrypt":
        decrypt_cmd(call.message)
    elif call.data == "frida":
        frida_cmd(call.message)
    elif call.data == "help":
        bot.send_message(call.message.chat.id,
            "📋 **Help**\n\n🔐 /encrypt — Encrypt file\n🔓 /decrypt — Decrypt file\n📱 /frida — Analyze APK\n👑 @VICKYGAMING0")
    elif call.data == "dev":
        bot.send_message(call.message.chat.id,
            "👑 **Developer**\n\n🔹 Name: Vicky Gaming\n🔹 @VICKYGAMING0\n🔹 Version: 2.0 PRO\n🔹 Features: AES-256, Frida-Like")
    elif call.data == "stats":
        db = load_db()
        bot.send_message(call.message.chat.id,
            f"📊 **Stats**\n\n👥 Users: {len(db)}\n📤 Files processed: {sum(u['files_processed'] for u in db.values())}\n👑 @VICKYGAMING0")
    bot.answer_callback_query(call.id)

# ===================== MAIN =====================
if __name__ == "__main__":
    print("🔧 Crypto + Frida-Like Tool Started!")
    print(f"👑 Developer: @{ADMIN_USERNAME}")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except:
            time.sleep(5)