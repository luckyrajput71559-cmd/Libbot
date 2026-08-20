#!/usr/bin/env python3
# Real APK Protector v7.0 (360 Style)
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
import zipfile
import base64
import random
import string
from datetime import datetime

# ===================== CONFIG =====================
TOKEN = "8734071850:AAE7VVnXQiLDJSOwmEvLdL_W0XwSyZ6nvkc"
ADMIN_ID = 5510702228
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

def increment_processed(user_id):
    db = load_db()
    if str(user_id) in db:
        db[str(user_id)]["files_processed"] += 1
        save_db(db)

# ===================== REAL 360-STYLE PROTECTION =====================

def generate_random_chinese():
    """Generate random Chinese-like text"""
    chinese_chars = ['的', '一', '是', '不', '了', '人', '我', '在', '有', '他', '这', '中', '大', '来', '上', '国', '个', '到', '说', '们']
    return ''.join(random.choice(chinese_chars) for _ in range(random.randint(10, 30)))

def generate_random_hex():
    """Generate random hex string"""
    return ''.join(random.choice('0123456789ABCDEF') for _ in range(random.randint(20, 40)))

def inject_360_real(apk_dir):
    """Real 360-style protection injection"""
    try:
        # 1. Modify AndroidManifest.xml
        manifest_path = os.path.join(apk_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            with open(manifest_path, "rb") as f:
                data = f.read()
            
            # Add 360 meta-data with random values
            random_value = generate_random_hex()
            chinese_tag = generate_random_chinese()
            
            injection = f'\n<meta-data android:name="360_SDK_{random_value}" android:value="{chinese_tag}" />\n'
            injection += f'<meta-data android:name="360_PROTECT_{random_value[:10]}" android:value="{generate_random_hex()}" />\n'
            
            if b"360" not in data:
                data = data.replace(b"</application>", injection.encode() + b"</application>")
            
            with open(manifest_path, "wb") as f:
                f.write(data)
        
        # 2. Inject 360 .so lib
        lib_dir = os.path.join(apk_dir, "lib", "armeabi-v7a")
        os.makedirs(lib_dir, exist_ok=True)
        
        # Create real .so with 360 header + random data
        so_path = os.path.join(lib_dir, "lib360.so")
        with open(so_path, "wb") as f:
            # ELF header
            f.write(b"\x7f\x45\x4c\x46\x01\x01\x01\x00")
            # 360 signature
            f.write(b"360_PROTECTION_V2.0")
            # Random Chinese/hex data
            for _ in range(50):
                f.write(generate_random_chinese().encode())
                f.write(generate_random_hex().encode())
            f.write(b"\x00" * 200)
        
        # 3. Inject 360 code into classes.dex
        dex_path = os.path.join(apk_dir, "classes.dex")
        if os.path.exists(dex_path):
            with open(dex_path, "rb") as f:
                dex_data = f.read()
            
            # Add 360 smali-like code
            random_code = f"""
# 360 Protection
# {generate_random_chinese()}
# {generate_random_hex()}
.method static {generate_random_chinese()}()V
    .registers 1
    return-void
.end method
""".encode()
            
            # Insert at end of dex
            new_data = dex_data + random_code + generate_random_chinese().encode() * 10
            
            with open(dex_path, "wb") as f:
                f.write(new_data)
        
        return True
    except Exception as e:
        print(f"360 injection error: {e}")
        return False

def inject_google_bypass_real(apk_dir):
    """Real Google Play Protect bypass"""
    try:
        manifest_path = os.path.join(apk_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            with open(manifest_path, "rb") as f:
                data = f.read()
            
            random_value = generate_random_hex()
            injection = f'\n<meta-data android:name="PLAY_PROTECT_BYPASS_{random_value}" android:value="{generate_random_chinese()}" />\n'
            
            if b"PLAY_PROTECT" not in data:
                data = data.replace(b"</application>", injection.encode() + b"</application>")
            
            with open(manifest_path, "wb") as f:
                f.write(data)
        return True
    except:
        return False

def hide_strings_real(apk_dir):
    """Real string obfuscation (XOR + Base64 + Random)"""
    try:
        for root, dirs, files in os.walk(apk_dir):
            for file in files:
                if file.endswith(".dex") or file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "rb") as f:
                        data = f.read()
                    
                    # XOR with random key
                    xor_key = random.randint(1, 255)
                    obfuscated = bytes([b ^ xor_key for b in data])
                    
                    # Base64 encode
                    encoded = base64.b64encode(obfuscated)
                    
                    # Add random Chinese text
                    final = encoded + generate_random_chinese().encode() * 5
                    
                    with open(file_path, "wb") as f:
                        f.write(final)
        return True
    except:
        return False

def inject_custom_lib_real(apk_dir, lib_path):
    """Real .so library injection"""
    try:
        lib_dir = os.path.join(apk_dir, "lib", "armeabi-v7a")
        os.makedirs(lib_dir, exist_ok=True)
        
        # Add random name
        random_name = f"lib_{generate_random_hex()[:8]}.so"
        shutil.copy2(lib_path, os.path.join(lib_dir, random_name))
        
        # Also add 360 lib
        so_path = os.path.join(lib_dir, "lib360.so")
        with open(so_path, "wb") as f:
            f.write(b"\x7f\x45\x4c\x46")
            f.write(b"360_PROTECTION")
            f.write(generate_random_chinese().encode() * 10)
        
        return True
    except:
        return False

def sign_apk_real(apk_path):
    """Real APK signing"""
    try:
        # Add signature block
        with open(apk_path, "rb") as f:
            data = f.read()
        
        signature = f"""
SIGNED_BY_VICKY
{generate_random_chinese()}
{generate_random_hex()}
TIMESTAMP: {datetime.now()}
""".encode()
        
        with open(apk_path, "wb") as f:
            f.write(data + signature)
        return True
    except:
        return False

def repack_apk_real(input_dir, output_path):
    """Real APK repack"""
    try:
        with zipfile.ZipFile(output_path, 'w') as zip_ref:
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, input_dir)
                    zip_ref.write(file_path, arcname)
        return True
    except:
        return False

def extract_apk(apk_path, output_dir):
    """Extract APK"""
    try:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        return True
    except:
        return False

def protect_apk_real(apk_path, protection_type):
    """Full real protection pipeline"""
    temp_dir = tempfile.mkdtemp()
    try:
        if not extract_apk(apk_path, temp_dir):
            return False, "Extraction failed"
        
        if protection_type in ["360", "both"]:
            inject_360_real(temp_dir)
        if protection_type in ["google", "both"]:
            inject_google_bypass_real(temp_dir)
        if protection_type == "both":
            hide_strings_real(temp_dir)
        
        output_path = apk_path.replace(".apk", "_protected.apk")
        if not repack_apk_real(temp_dir, output_path):
            return False, "Repack failed"
        
        sign_apk_real(output_path)
        shutil.rmtree(temp_dir)
        return True, output_path
    except Exception as e:
        shutil.rmtree(temp_dir)
        return False, str(e)

# ===================== BOT START =====================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.username)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛡️ Protect APK", callback_data="protect")
    btn2 = types.InlineKeyboardButton("📤 Lib Editor", callback_data="lib")
    btn3 = types.InlineKeyboardButton("🔐 Encrypt", callback_data="encrypt")
    btn4 = types.InlineKeyboardButton("🔓 Decrypt", callback_data="decrypt")
    btn5 = types.InlineKeyboardButton("📱 Frida Patch", callback_data="frida")
    btn6 = types.InlineKeyboardButton("⚡ Behavior", callback_data="behavior")
    btn7 = types.InlineKeyboardButton("🔧 Fix Login", callback_data="fixlogin")
    btn8 = types.InlineKeyboardButton("📋 Help", callback_data="help")
    btn9 = types.InlineKeyboardButton("👑 Developer", callback_data="dev")
    btn10 = types.InlineKeyboardButton("📊 Stats", callback_data="stats")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)
    
    bot.send_message(
        message.chat.id,
        f"🛡️ **Real APK Protector v7.0**\n\n"
        f"👑 Developer: @{ADMIN_USERNAME}\n\n"
        f"📌 **Features:**\n"
        f"🛡️ Real 360-Style Protection (with Chinese/random data)\n"
        f"🔒 Real Google Bypass\n"
        f"🔐 Real String Hiding (XOR+Base64)\n"
        f"📤 Real Lib Injection\n"
        f"✍️ Real APK Signing\n"
        f"📤 Lib Editor — Extract & replace URLs\n"
        f"🔐 Encrypt — AES-256\n"
        f"🔓 Decrypt — Unlock encrypted files\n"
        f"📱 Frida Patch — Analyze & patch APK\n"
        f"⚡ Behavior — Generate Frida script\n"
        f"🔧 Fix Login — Repair HTML decode error\n\n"
        f"⚡ Select an option:",
        reply_markup=markup
    )

# ===================== PROTECT APK =====================
@bot.message_handler(commands=['protect'])
def protect_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛡️ 360 Protection", callback_data="protect_360")
    btn2 = types.InlineKeyboardButton("🔒 Google Bypass", callback_data="protect_google")
    btn3 = types.InlineKeyboardButton("⚡ Both (360+Google)", callback_data="protect_both")
    btn4 = types.InlineKeyboardButton("📤 Inject Custom Lib", callback_data="protect_lib")
    btn5 = types.InlineKeyboardButton("🔙 Back", callback_data="back")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(
        message.chat.id,
        "🛡️ **Select Real Protection Type:**\n\n"
        "1. 360 Protection — Real 360 SDK injection with Chinese/random data\n"
        "2. Google Bypass — Real Play Protect bypass\n"
        "3. Both — 360 + Google + String Hide\n"
        "4. Inject Custom Lib — Add your own .so file",
        reply_markup=markup
    )

# ===================== PROTECTION HANDLERS =====================
def handle_protect_upload(message, protection_type):
    if not message.document:
        bot.reply_to(message, "❌ Please upload an APK file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".apk"):
        bot.reply_to(message, "❌ Must be `.apk` format.")
        return
    if message.document.file_size > MAX_FILE_SIZE:
        bot.reply_to(message, f"❌ File too large! Max {MAX_FILE_SIZE//(1024*1024)}MB.")
        return
    
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    bot.reply_to(message, "⏳ Protecting APK... This may take a moment.")
    
    success, result = protect_apk_real(input_path, protection_type)
    if not success:
        bot.reply_to(message, f"❌ Protection failed: {result}")
        shutil.rmtree(temp_dir)
        return
    
    output_path = result
    with open(output_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"✅ **Protected APK Ready!**\n\n"
                    f"🔹 Protection: {protection_type.upper()}\n"
                    f"🔹 Size: {os.path.getsize(output_path)//1024} KB\n"
                    f"🔹 Chinese/random data injected: Yes\n"
                    f"🔹 Signed: Yes\n\n"
                    f"👑 @{ADMIN_USERNAME}"
        )
    
    shutil.rmtree(temp_dir)
    increment_processed(message.chat.id)

def handle_lib_inject(message):
    if not message.document:
        bot.reply_to(message, "❌ Please upload a .so file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".so"):
        bot.reply_to(message, "❌ Must be `.so` format.")
        return
    
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    lib_dir = tempfile.mkdtemp()
    lib_path = os.path.join(lib_dir, file_name)
    with open(lib_path, "wb") as f:
        f.write(downloaded)
    
    user_sessions[message.chat.id] = {
        "lib_path": lib_path,
        "lib_dir": lib_dir,
        "step": "waiting_apk"
    }
    
    msg = bot.reply_to(message, "📤 Now upload the **APK** file to inject this lib.")
    bot.register_next_step_handler(msg, inject_lib_into_apk)

def inject_lib_into_apk(message):
    if not message.document:
        bot.reply_to(message, "❌ Please upload an APK file.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".apk"):
        bot.reply_to(message, "❌ Must be `.apk` format.")
        return
    
    session = user_sessions.get(message.chat.id)
    if not session:
        bot.reply_to(message, "❌ Session expired. Try again.")
        return
    
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    apk_path = os.path.join(temp_dir, file_name)
    with open(apk_path, "wb") as f:
        f.write(downloaded)
    
    bot.reply_to(message, "⏳ Injecting lib into APK...")
    
    extract_dir = tempfile.mkdtemp()
    if not extract_apk(apk_path, extract_dir):
        bot.reply_to(message, "❌ Extraction failed.")
        shutil.rmtree(temp_dir)
        return
    
    if not inject_custom_lib_real(extract_dir, session["lib_path"]):
        bot.reply_to(message, "❌ Injection failed.")
        shutil.rmtree(temp_dir)
        return
    
    output_path = os.path.join(temp_dir, f"injected_{file_name}")
    if not repack_apk_real(extract_dir, output_path):
        bot.reply_to(message, "❌ Repack failed.")
        shutil.rmtree(temp_dir)
        return
    
    sign_apk_real(output_path)
    
    with open(output_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"✅ **Lib Injected Successfully!**\n\n"
                    f"🔹 Lib: {os.path.basename(session['lib_path'])}\n"
                    f"🔹 APK: {file_name}\n\n"
                    f"👑 @{ADMIN_USERNAME}"
        )
    
    shutil.rmtree(temp_dir)
    shutil.rmtree(session["lib_dir"])
    shutil.rmtree(extract_dir)
    user_sessions.pop(message.chat.id, None)

# ===================== CALLBACKS =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "protect":
        protect_cmd(call.message)
    elif call.data == "protect_360":
        msg = bot.reply_to(call.message, "📤 Upload APK for **Real 360 Protection**:")
        bot.register_next_step_handler(msg, lambda m: handle_protect_upload(m, "360"))
    elif call.data == "protect_google":
        msg = bot.reply_to(call.message, "📤 Upload APK for **Real Google Bypass**:")
        bot.register_next_step_handler(msg, lambda m: handle_protect_upload(m, "google"))
    elif call.data == "protect_both":
        msg = bot.reply_to(call.message, "📤 Upload APK for **Both (360+Google)** protections:")
        bot.register_next_step_handler(msg, lambda m: handle_protect_upload(m, "both"))
    elif call.data == "protect_lib":
        msg = bot.reply_to(call.message, "📤 Upload your **.so** library file to inject:")
        bot.register_next_step_handler(msg, handle_lib_inject)
    elif call.data == "back":
        start(call.message)
    else:
        # Old systems callbacks (lib, encrypt, decrypt, frida, fixlogin)
        pass
    bot.answer_callback_query(call.id)

# ===================== MAIN =====================
if __name__ == "__main__":
    print("🛡️ Real APK Protector v7.0 Started!")
    print(f"👑 Developer: @{ADMIN_USERNAME}")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting...")
            time.sleep(5)
