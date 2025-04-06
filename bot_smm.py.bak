import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from datetime import datetime

BOT_TOKEN = '8151707833:AAHJZWErtOkPCwbbwgZ3oyf0-NtZ17nCLIM'  # Ganti dengan token asli bot kamu
bot = telebot.TeleBot(BOT_TOKEN)

PASSWORD = "admin123"
authorized_users = set()
user_keywords = {}
user_files = {}

def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Upload File", callback_data="upload_file"),
        InlineKeyboardButton("Ganti Kata Kunci", callback_data="set_keyword"),
        InlineKeyboardButton("Jalankan Script", callback_data="run_script")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Selamat datang! Silakan login.\nMasukkan password:")
    bot.register_next_step_handler(message, login)

def login(message):
    if message.text == PASSWORD:
        authorized_users.add(message.from_user.id)
        bot.send_message(message.chat.id, "Login berhasil!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Password salah. Coba lagi dengan /start.")

def is_logged_in(user_id):
    return user_id in authorized_users

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not is_logged_in(call.from_user.id):
        return bot.answer_callback_query(call.id, "Silakan login dulu dengan /start")

    if call.data == "set_keyword":
        bot.send_message(call.message.chat.id, "Masukkan kata kunci pencarian:")
        bot.register_next_step_handler(call.message, save_keyword)
    elif call.data == "upload_file":
        bot.send_message(call.message.chat.id, "Silakan kirim file `.txt` berisi data akun.")
    elif call.data == "run_script":
        user_id = call.from_user.id
        if user_id not in user_files:
            return bot.send_message(call.message.chat.id, "Anda belum mengupload file.")
        keyword = user_keywords.get(user_id, 'smm')
        result_text = process_file(user_files[user_id], keyword, call.from_user)
        if len(result_text) > 4000:
            for i in range(0, len(result_text), 4000):
                bot.send_message(call.message.chat.id, result_text[i:i+4000], parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, result_text, parse_mode='Markdown')

def save_keyword(message):
    user_keywords[message.from_user.id] = message.text.strip().lower()
    bot.send_message(message.chat.id, f"Kata kunci diatur ke: {message.text}", reply_markup=main_menu())

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if not is_logged_in(message.from_user.id):
        return bot.reply_to(message, "Silakan login dulu dengan /start.")

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"user_{message.from_user.id}_{message.document.file_name}"
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    user_files[message.from_user.id] = file_path
    bot.reply_to(message, "File berhasil diupload.", reply_markup=main_menu())

def process_file(input_file, keyword, user):
    blacklist_file = 'blacklist.txt'
    with open(blacklist_file, 'r') as file:
        blacklist = [line.strip().lower() for line in file.readlines()]

    with open(input_file, 'r') as file:
        lines = file.readlines()

    cleaned_lines = []
    for line in lines:
        line = line.strip()
        for prefix in ["https://", "http://", "www."]:
            if line.startswith(prefix):
                line = line.replace(prefix, "", 1)
        cleaned_lines.append(line)

    domain_dict = {}
    for line in cleaned_lines:
        parts = line.split(':')
        if len(parts) < 3:
            continue
        domain = parts[0].split('/')[0].lower()
        username = parts[1]
        password = parts[2]
        if domain in blacklist:
            continue
        if domain not in domain_dict:
            domain_dict[domain] = []
        domain_dict[domain].append((username, password))

    filtered = {d: c for d, c in domain_dict.items() if keyword.lower() in d}
    sorted_domains = sorted(filtered.keys())

    header = f"""🔎 *Pencarian Selesai*

👤 *Username:* @{user.username if user.username else user.first_name}
📅 *Tanggal:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 *File:* {os.path.basename(input_file)}
🏷️ *Kata Kunci:* `{keyword}`

🤖 @cloudfami_bot

"""

    content = ""
    for domain in sorted_domains:
        content += f"*[ {domain} ]* Status : ✅ ❌\n"
        for username, password in filtered[domain]:
            content += f"Username: ```{username}```\nPassword: ```{password}```\n\n"
        content += "\n"

    return header + content

print("Bot is running...")
bot.infinity_polling()
