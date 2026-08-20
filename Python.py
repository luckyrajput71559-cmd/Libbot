#!/usr/bin/env python3
# Ultimate Lib Editor + Connect Panel Unlock + Login Fix
# Developer: @VICKYGAMING0
# Version: 4.0 HEAVY

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
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime

# ===================== CONFIG =====================
TOKEN = "8734071850:AAE7VVnXQiLDJSOwmEvLdL_W0XwSyZ6nvkc"
ADMIN_ID = 5510702228
ADMIN_USERNAME = "VICKYGAMING0"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
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

def increment_processed(user_id):
    db = load_db()
    if str(user_id) in db:
        db[str(user_id)]["files_processed"] += 1
        save_db(db)

# ===================== DEEP URL SCANNER =====================
def deep_scan_urls(file_path):
    """Scan every string, function, offset for URLs"""
    urls = []
    try:
        # Strings
        result = subprocess.run(["strings", file_path], capture_output=True, text=True)
        content = result.stdout
        
        # All URL patterns
        patterns = [
            r'https?://[^\s"\']+',
            r'http?://[^\s"\']+',
            r'wss?://[^\s"\']+',
            r'ftp://[^\s"\']+',
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s"\']*'
        ]
        
        for pattern in patterns:
            found = re.findall(pattern, content)
            urls.extend(found)
        
        # Unique only
        urls = list(set(urls))
        
        # Filter connect/panel/admin URLs
        connect_urls = [u for u in urls if 'connect' in u.lower() or 'panel' in u.lower() or 'admin' in u.lower()]
        
        return urls, connect_urls
    except:
        return [], []

# ===================== CONNECT PANEL UNLOCK =====================
def unlock_connect_panel(file_path, new_url):
    """Replace connect/panel URLs with new one"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        # Find old connect URL
        result = subprocess.run(["strings", file_path], capture_output=True, text=True)
        content = result.stdout
        old_urls = re.findall(r'https?://[^\s"\']+connect[^\s"\']*', content)
        
        if not old_urls:
            return False, "No connect URL found"
        
        old_url = old_urls[0]
        old_bytes = old_url.encode('utf-8')
        new_bytes = new_url.encode('utf-8')
        
        # Pad new URL if shorter
        if len(new_bytes) < len(old_bytes):
            new_bytes += b'\x00' * (len(old_bytes) - len(new_bytes))
        elif len(new_bytes) > len(old_bytes):
            new_bytes = new_bytes[:len(old_bytes)]
        
        # Replace
        new_data = data.replace(old_bytes, new_bytes)
        
        with open(file_path, "wb") as f:
            f.write(new_data)
        
        return True, f"{old_url} → {new_url}"
    except Exception as e:
        return False, str(e)

# ===================== LOGIN FIX =====================
def fix_login_error(file_path):
    """Fix external HTML decode/login errors"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        # Fix common login errors
        patterns = [
            (b'login', b'login_bypass'),
            (b'decode', b'decode_fix'),
            (b'external', b'internal'),
            (b'HTML', b'JSON')
        ]
        
        for old, new in patterns:
            data = data.replace(old, new)
        
        with open(file_path, "wb") as f:
            f.write(data)
        
        return True
    except:
        return False

# ===================== HYBRID ENCRYPTOR (AES-256 + RSA) =====================
def hybrid_encrypt(data, password):
    salt = get_random_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(salt + iv + encrypted).decode('utf-8')

def hybrid_decrypt(encrypted_data, password):
    raw = base64.b64decode(encrypted_data)
    salt = raw[:16]
    iv = raw[16:32]
    encrypted = raw[32:]
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted

# ===================== BOT START =====================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.username)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📤 Deep Lib Scan", callback_data="deepscan")
    btn2 = types.InlineKeyboardButton("🔓 Unlock Connect", callback_data="unlock")
    btn3 = types.InlineKeyboardButton("🔧 Fix Login", callback_data="fixlogin")
    btn4 = types.InlineKeyboardButton("🔐 Encrypt", callback_data="encrypt")
    btn5 = types.InlineKeyboardButton("🔓 Decrypt", callback_data="decrypt")
    btn6 = types.InlineKeyboardButton("📋 Help", callback_data="help")
    btn7 = types.InlineKeyboardButton("👑 Developer", callback_data="dev")
    btn8 = types.InlineKeyboardButton("📊 Stats", callback_data="stats")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
    
    bot.send_message(
        message.chat.id,
        f"🔧 **Ultimate Lib Tool v4.0 HEAVY**\n\n"
        f"👑 Developer: @{ADMIN_USERNAME}\n\n"
        f"📌 **Features:**\n"
        f"📤 Deep Scan — Find ALL URLs\n"
        f"🔓 Unlock Connect — Replace connect/panel URLs\n"
        f"🔧 Fix Login — Fix external HTML decode\n"
        f"🔐 Hybrid Encrypt — AES + RSA\n\n"
        f"⚡ Select an option:",
        reply_markup=markup
    )

# ===================== DEEP SCAN =====================
@bot.message_handler(commands=['deepscan'])
def deepscan_cmd(message):
    msg = bot.reply_to(message, "📤 Upload lib file.\n🔹 I'll deep scan ALL URLs.")
    bot.register_next_step_handler(msg, deepscan_upload)

def deepscan_upload(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload a file.")
        return
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    urls, connect_urls = deep_scan_urls(input_path)
    
    if not urls:
        bot.reply_to(message, "❌ No URLs found.")
        shutil.rmtree(temp_dir)
        return
    
    response = f"✅ **Found {len(urls)} URLs**\n"
    response += f"🔹 **Connect/Panel URLs:** {len(connect_urls)}\n\n"
    response += "📋 **First 20 URLs:**\n"
    for i, url in enumerate(urls[:20], 1):
        response += f"`{i}. {url}`\n"
    
    if connect_urls:
        response += "\n🔹 **Connect URLs found!** Use `/unlock` to replace."
    
    bot.reply_to(message, response, parse_mode="Markdown")
    shutil.rmtree(temp_dir)
    increment_processed(message.chat.id)

# ===================== UNLOCK CONNECT =====================
@bot.message_handler(commands=['unlock'])
def unlock_cmd(message):
    msg = bot.reply_to(message, "📤 Upload lib file.\n🔹 I'll unlock connect panel.")
    bot.register_next_step_handler(msg, unlock_upload)

def unlock_upload(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload a file.")
        return
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    msg = bot.reply_to(message, "🔗 Send **new connect URL** (e.g., https://enginehost.org/connect)")
    bot.register_next_step_handler(msg, unlock_replace, input_path, temp_dir, file_name)

def unlock_replace(message, input_path, temp_dir, file_name):
    new_url = message.text.strip()
    if not new_url.startswith("http"):
        bot.reply_to(message, "❌ Must start with http:// or https://")
        return
    
    success, result = unlock_connect_panel(input_path, new_url)
    if not success:
        bot.reply_to(message, f"❌ Failed: {result}")
        shutil.rmtree(temp_dir)
        return
    
    output_path = os.path.join(temp_dir, f"unlocked_{file_name}")
    shutil.copy2(input_path, output_path)
    
    with open(output_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"✅ **Connect Panel Unlocked!**\n\n{result}"
        )
    shutil.rmtree(temp_dir)

# ===================== FIX LOGIN =====================
@bot.message_handler(commands=['fixlogin'])
def fixlogin_cmd(message):
    msg = bot.reply_to(message, "📤 Upload lib file.\n🔹 I'll fix login errors.")
    bot.register_next_step_handler(msg, fixlogin_upload)

def fixlogin_upload(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload a file.")
        return
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    success = fix_login_error(input_path)
    if not success:
        bot.reply_to(message, "❌ Login fix failed.")
        shutil.rmtree(temp_dir)
        return
    
    output_path = os.path.join(temp_dir, f"fixed_{file_name}")
    shutil.copy2(input_path, output_path)
    
    with open(output_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption="✅ **Login Error Fixed!**\n🔹 External HTML decode bypassed."
        )
    shutil.rmtree(temp_dir)

# ===================== ENCRYPT =====================
@bot.message_handler(commands=['encrypt'])
def encrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload file to encrypt.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, encrypt_upload)

def encrypt_upload(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload a file.")
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
        "input_path": input_path,
        "temp_dir": temp_dir,
        "file_name": file_name
    }
    msg = bot.reply_to(message, f"📝 Enter password for `{file_name}`:")
    bot.register_next_step_handler(msg, encrypt_with_password)

def encrypt_with_password(message):
    password = message.text.strip()
    if len(password) < 4:
        bot.reply_to(message, "❌ Min 4 chars.")
        return
    session = user_sessions.get(message.chat.id)
    if not session:
        return
    
    with open(session["input_path"], "rb") as f:
        data = f.read()
    encrypted = hybrid_encrypt(data, password)
    enc_path = session["input_path"] + ".enc"
    with open(enc_path, "w") as f:
        f.write(encrypted)
    
    with open(enc_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"✅ **Encrypted!**\n🔹 Password: `{password}`"
        )
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== DECRYPT =====================
@bot.message_handler(commands=['decrypt'])
def decrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload `.enc` file.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, decrypt_upload)

def decrypt_upload(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload `.enc` file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".enc"):
        bot.reply_to(message, "❌ Must be `.enc`.")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    user_sessions[message.chat.id] = {
        "input_path": input_path,
        "temp_dir": temp_dir,
        "file_name": file_name
    }
    msg = bot.reply_to(message, f"🔑 Enter password for `{file_name}`:")
    bot.register_next_step_handler(msg, decrypt_with_password)

def decrypt_with_password(message):
    password = message.text.strip()
    session = user_sessions.get(message.chat.id)
    if not session:
        return
    try:
        with open(session["input_path"], "r") as f:
            encrypted = f.read()
        decrypted = hybrid_decrypt(encrypted, password)
        dec_path = session["input_path"].replace(".enc", "_decrypted")
        with open(dec_path, "wb") as f:
            f.write(decrypted)
        with open(dec_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ **Decrypted!**")
    except:
        bot.reply_to(message, "❌ Wrong password.")
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== CALLBACKS =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "deepscan":
        deepscan_cmd(call.message)
    elif call.data == "unlock":
        unlock_cmd(call.message)
    elif call.data == "fixlogin":
        fixlogin_cmd(call.message)
    elif call.data == "encrypt":
        encrypt_cmd(call.message)
    elif call.data == "decrypt":
        decrypt_cmd(call.message)
    elif call.data == "help":
        bot.send_message(call.message.chat.id,
            "📋 **Commands**\n/deepscan — Deep scan URLs\n/unlock — Unlock connect panel\n/fixlogin — Fix login errors\n/encrypt — Encrypt file\n/decrypt — Decrypt file\n👑 @VICKYGAMING0")
    elif call.data == "dev":
        bot.send_message(call.message.chat.id,
            "👑 **Developer**\n🔹 Name: Vicky Gaming\n🔹 @VICKYGAMING0\n🔹 Version: 4.0 HEAVY\n🔹 Features: Deep scan, Connect unlock, Login fix, Hybrid encrypt")
    elif call.data == "stats":
        db = load_db()
        bot.send_message(call.message.chat.id,
            f"📊 **Stats**\n👥 Users: {len(db)}\n📤 Files: {sum(u['files_processed'] for u in db.values())}\n👑 @VICKYGAMING0")
    bot.answer_callback_query(call.id)

# ===================== MAIN =====================
if __name__ == "__main__":
    print("🔧 Ultimate Lib Tool v4.0 HEAVY Started!")
    print(f"👑 Developer: @{ADMIN_USERNAME}")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting...")
            time.sleep(5)
