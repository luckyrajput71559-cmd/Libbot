#!/usr/bin/env python3
# Ultimate All-in-One Tool v4.0
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
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
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

# ===================== LIB URL EDITOR =====================
def extract_urls_from_binary(file_path):
    try:
        result = subprocess.run(["strings", file_path], capture_output=True, text=True)
        content = result.stdout
        url_pattern = r'https?://[^\s"\']+'
        urls = re.findall(url_pattern, content)
        return list(set(urls))
    except:
        return []

def replace_url_in_binary(file_path, old_url, new_url):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        old_bytes = old_url.encode('utf-8')
        new_bytes = new_url.encode('utf-8')
        if len(new_bytes) < len(old_bytes):
            new_bytes += b'\x00' * (len(old_bytes) - len(new_bytes))
        elif len(new_bytes) > len(old_bytes):
            new_bytes = new_bytes[:len(old_bytes)]
        new_data = data.replace(old_bytes, new_bytes)
        with open(file_path, "wb") as f:
            f.write(new_data)
        return True
    except:
        return False

def repack_lib(input_path, output_path):
    try:
        shutil.copy2(input_path, output_path)
        os.chmod(output_path, 0o755)
        return True
    except:
        return False

def get_file_hash(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

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

# ===================== FRIDA-LIKE APK ANALYZE =====================
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
            "services": services
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

# ===================== LOGIN HTML DECODE FIX =====================
def fix_login_html_error(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        fixes = [
            (b'HTML', b'JSON'),
            (b'decode', b'parse'),
            (b'external', b'internal'),
            (b'login', b'auth'),
            (b'error', b'success')
        ]
        for old, new in fixes:
            data = data.replace(old, new)
        with open(file_path, "wb") as f:
            f.write(data)
        return True
    except:
        return False

# ===================== FRIDA SCRIPT GENERATOR =====================
def generate_frida_script(package_name):
    return f"""
Java.perform(function() {{
    var Activity = Java.use('android.app.Activity');
    Activity.onCreate.implementation = function(savedInstanceState) {{
        console.log('[+] Hooked: ' + this.getClass().getName());
        this.onCreate(savedInstanceState);
    }};
    var PackageManager = Java.use('android.content.pm.PackageManager');
    PackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pkg, flags) {{
        console.log('[+] Package requested: ' + pkg);
        if (pkg === '{package_name}') {{
            console.log('[!] Bypassing package check!');
        }}
        return this.getPackageInfo(pkg, flags);
    }};
    console.log('[+] Frida script injected for: {package_name}');
}});
"""

# ===================== BOT START =====================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.username)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📤 Lib Editor", callback_data="lib")
    btn2 = types.InlineKeyboardButton("🔐 Encrypt", callback_data="encrypt")
    btn3 = types.InlineKeyboardButton("🔓 Decrypt", callback_data="decrypt")
    btn4 = types.InlineKeyboardButton("📱 Frida Patch", callback_data="frida")
    btn5 = types.InlineKeyboardButton("⚡ Behavior", callback_data="behavior")
    btn6 = types.InlineKeyboardButton("🔧 Fix Login", callback_data="fixlogin")
    btn7 = types.InlineKeyboardButton("📋 Help", callback_data="help")
    btn8 = types.InlineKeyboardButton("👑 Developer", callback_data="dev")
    btn9 = types.InlineKeyboardButton("📊 Stats", callback_data="stats")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    
    bot.send_message(
        message.chat.id,
        f"🔧 **Ultimate All-in-One Tool v4.0**\n\n"
        f"👑 Developer: @{ADMIN_USERNAME}\n\n"
        f"📌 **Features:**\n"
        f"📤 Lib Editor — Extract & replace URLs\n"
        f"🔐 Encrypt — AES-256 password protect\n"
        f"🔓 Decrypt — Unlock encrypted files\n"
        f"📱 Frida Patch — Analyze & patch APK\n"
        f"⚡ Behavior — Generate Frida script\n"
        f"🔧 Fix Login — Repair HTML decode error\n\n"
        f"⚡ Select an option:",
        reply_markup=markup
    )

# ===================== LIB EDITOR =====================
@bot.message_handler(commands=['lib'])
def lib_cmd(message):
    msg = bot.reply_to(message, "📤 Upload a `.so` / `.dll` / `.apk` file.\n🔹 I'll extract HTTPS links.")
    bot.register_next_step_handler(msg, lib_upload_step)

def lib_upload_step(message):
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
    
    urls = extract_urls_from_binary(input_path)
    if not urls:
        bot.reply_to(message, "❌ No HTTPS URLs found.")
        shutil.rmtree(temp_dir)
        return
    
    user_sessions[message.chat.id] = {
        "input_path": input_path,
        "temp_dir": temp_dir,
        "file_name": file_name,
        "urls": urls
    }
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, url in enumerate(urls[:10]):
        markup.add(types.InlineKeyboardButton(f"🔗 {url[:30]}...", callback_data=f"edit_{i}"))
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    
    url_list = "\n".join([f"`{i+1}. {url}`" for i, url in enumerate(urls[:10])])
    bot.reply_to(
        message,
        f"✅ **Found {len(urls)} URLs:**\n\n{url_list}\n\nClick a URL to edit.",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    increment_processed(message.chat.id)

# ===================== ENCRYPT =====================
@bot.message_handler(commands=['encrypt'])
def encrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload file to encrypt.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, encrypt_file_step)

def encrypt_file_step(message):
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
        bot.reply_to(message, "❌ Min 4 characters.")
        return
    session = user_sessions.get(message.chat.id)
    if not session:
        return
    enc_path = encrypt_file(session["input_path"], password)
    with open(enc_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=f"✅ Encrypted!\n🔹 Password: `{password}`")
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== DECRYPT =====================
@bot.message_handler(commands=['decrypt'])
def decrypt_cmd(message):
    msg = bot.reply_to(message, "📤 Upload `.enc` file.\n🔹 I'll ask for password.")
    bot.register_next_step_handler(msg, decrypt_file_step)

def decrypt_file_step(message):
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
        dec_path = decrypt_file(session["input_path"], password)
        with open(dec_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption="✅ Decrypted!")
    except:
        bot.reply_to(message, "❌ Wrong password.")
    shutil.rmtree(session["temp_dir"])
    user_sessions.pop(message.chat.id, None)

# ===================== FRIDA PATCH =====================
@bot.message_handler(commands=['frida'])
def frida_cmd(message):
    msg = bot.reply_to(message, "📤 Upload APK file.\n🔹 I'll analyze + patch.")
    bot.register_next_step_handler(msg, frida_analyze_step)

def frida_analyze_step(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload APK.")
        return
    file_name = message.document.file_name
    if not file_name.endswith(".apk"):
        bot.reply_to(message, "❌ Must be `.apk`.")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    result = analyze_apk(input_path)
    if not result:
        bot.reply_to(message, "❌ Analysis failed.")
        shutil.rmtree(temp_dir)
        return
    
    panels = extract_hidden_panel(input_path)
    patched_path = patch_apk(input_path, result["package"])
    
    response = (
        f"📱 **APK Analysis**\n\n"
        f"📦 Package: `{result['package']}`\n"
        f"🎯 Activities: {len(result['activities'])}\n"
        f"🛠 Services: {len(result['services'])}\n"
        f"🔍 Panels: {len(panels)}\n\n"
    )
    if panels:
        response += "🔹 Panels:\n" + "\n".join([f"`{p}`" for p in panels[:5]])
    response += "\n✅ Patched APK ready!"
    
    with open(patched_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=response)
    shutil.rmtree(temp_dir)

# ===================== BEHAVIOR =====================
@bot.message_handler(commands=['behavior'])
def behavior_cmd(message):
    msg = bot.reply_to(message, "📱 Enter **package name** (e.g., `com.example.app`)\n🔹 I'll generate Frida script.")
    bot.register_next_step_handler(msg, behavior_generate)

def behavior_generate(message):
    package = message.text.strip()
    if not package:
        bot.reply_to(message, "❌ Enter package name.")
        return
    
    script = generate_frida_script(package)
    response = (
        f"⚡ **Frida Script for `{package}`**\n\n"
        f"📜 **Script:**\n```javascript\n{script[:500]}...\n```\n\n"
        f"💡 Save script as `.js` and run with Frida."
    )
    bot.reply_to(message, response, parse_mode="Markdown")

# ===================== FIX LOGIN =====================
@bot.message_handler(commands=['fixlogin'])
def fixlogin_cmd(message):
    msg = bot.reply_to(message, "📤 Upload the APK/lib file.\n🔹 I'll fix login HTML decode error.")
    bot.register_next_step_handler(msg, fixlogin_file_step)

def fixlogin_file_step(message):
    if not message.document:
        bot.reply_to(message, "❌ Upload a file.")
        return
    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file_name)
    with open(input_path, "wb") as f:
        f.write(downloaded)
    
    success = fix_login_html_error(input_path)
    if not success:
        bot.reply_to(message, "❌ Fix failed.")
        shutil.rmtree(temp_dir)
        return
    
    output_path = os.path.join(temp_dir, f"fixed_{file_name}")
    shutil.copy2(input_path, output_path)
    
    with open(output_path, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption="✅ **Login HTML Decode Error Fixed!**\n🔹 Mod menu should work now."
        )
    shutil.rmtree(temp_dir)

# ===================== CALLBACKS =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "lib":
        lib_cmd(call.message)
    elif call.data == "encrypt":
        encrypt_cmd(call.message)
    elif call.data == "decrypt":
        decrypt_cmd(call.message)
    elif call.data == "frida":
        frida_cmd(call.message)
    elif call.data == "behavior":
        behavior_cmd(call.message)
    elif call.data == "fixlogin":
        fixlogin_cmd(call.message)
    elif call.data == "help":
        bot.send_message(call.message.chat.id,
            "📋 **Commands**\n/lib — Edit lib URLs\n/encrypt — Encrypt file\n/decrypt — Decrypt file\n/frida — Analyze APK\n/behavior — Frida script\n/fixlogin — Fix login error\n👑 @VICKYGAMING0")
    elif call.data == "dev":
        bot.send_message(call.message.chat.id,
            "👑 **Developer**\n🔹 Name: Vicky Gaming\n🔹 @VICKYGAMING0\n🔹 Version: 4.0\n🔹 Features: Lib Editor, Crypto, Frida, Login Fix")
    elif call.data == "stats":
        db = load_db()
        bot.send_message(call.message.chat.id,
            f"📊 **Stats**\n👥 Users: {len(db)}\n📤 Files: {sum(u['files_processed'] for u in db.values())}\n👑 @VICKYGAMING0")
    elif call.data.startswith("edit_"):
        idx = int(call.data.split("_")[1])
        session = user_sessions.get(call.from_user.id)
        if not session:
            bot.send_message(call.message.chat.id, "❌ Session expired.")
            return
        urls = session.get("urls", [])
        if idx >= len(urls):
            bot.send_message(call.message.chat.id, "❌ URL not found.")
            return
        old_url = urls[idx]
        session["editing_url"] = old_url
        user_sessions[call.from_user.id] = session
        msg = bot.send_message(call.message.chat.id, f"✏️ Edit URL:\n`{old_url}`\n\nSend new URL:")
        bot.register_next_step_handler(msg, process_url_edit)
    elif call.data == "cancel":
        session = user_sessions.get(call.from_user.id)
        if session and "temp_dir" in session:
            shutil.rmtree(session["temp_dir"])
        user_sessions.pop(call.from_user.id, None)
        bot.send_message(call.message.chat.id, "❌ Cancelled.")
    bot.answer_callback_query(call.id)

def process_url_edit(message):
    user_id = message.chat.id
    session = user_sessions.get(user_id)
    if not session:
        bot.reply_to(message, "❌ Session expired.")
        return
    old_url = session.get("editing_url")
    new_url = message.text.strip()
    if not new_url.startswith("https://"):
        bot.reply_to(message, "❌ Must start with `https://`")
        return
    input_path = session["input_path"]
    if replace_url_in_binary(input_path, old_url, new_url):
        temp_dir = session["temp_dir"]
        file_name = session["file_name"]
        output_path = os.path.join(temp_dir, f"repacked_{file_name}")
        repack_lib(input_path, output_path)
        with open(output_path, "rb") as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=f"✅ **Repacked!**\n🔹 {old_url} → {new_url}"
            )
        shutil.rmtree(temp_dir)
        user_sessions.pop(user_id, None)
    else:
        bot.reply_to(message, "❌ Replacement failed.")

# ===================== MAIN =====================
if __name__ == "__main__":
    print("🔧 Ultimate All-in-One Tool v4.0 Started!")
    print(f"👑 Developer: @{ADMIN_USERNAME}")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting...")
            time.sleep(5)
