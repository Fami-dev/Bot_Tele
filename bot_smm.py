import telebot
import os
import datetime
import requests
import re
from telebot import types

BOT_TOKEN = '8151707833:AAHJZWErtOkPCwbbwgZ3oyf0-NtZ17nCLIM'
ALLOWED_USERS = [1374294212]  # Ganti dengan user_id kamu
bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}
file_store = {}

# Fungsi untuk escape karakter MarkdownV2
def escape_md(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def clean_domain(line):
    for prefix in ["https://www.", "http://www.", "https://", "http://", "www."]:
        if line.startswith(prefix):
            line = line.replace(prefix, "", 1)
    return line.strip()

def process_file(input_path, keyword, blacklist_path):
    with open(input_path, 'r') as file:
        lines = file.readlines()

    with open(blacklist_path, 'r') as file:
        blacklist = [b.strip() for b in file.readlines()]

    domain_dict = {}
    for line in lines:
        line = clean_domain(line)
        parts = line.split(':')
        if len(parts) < 3:
            continue
        domain_full = parts[0].split('/')[0]
        if domain_full in blacklist:
            continue
        if keyword.lower() not in domain_full.lower():
            continue
        username = parts[1]
        password = parts[2]
        if domain_full not in domain_dict:
            domain_dict[domain_full] = []
        domain_dict[domain_full].append((username, password))

    sorted_domains = sorted(domain_dict.items())

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"""🔎 Pencarian Selesai

👤 Username: 
📅 Tanggal: {now}
📁 File: {os.path.basename(input_path)}
🏷️ Kata Kunci: {keyword}

🤖 @cloudfami_bot
"""

    result = [escape_md(header)]
    for domain, creds in sorted_domains:
        result.append(escape_md(f"[ {domain} ] Status : ✅ ❌\n"))
        for user, pwd in creds:
            result.append(f"Username: ```{escape_md(user)}```\nPassword: ```{escape_md(pwd)}```\n")
        result.append("")

    output_filename = f"Output_{os.path.basename(input_path)}"
    with open(output_filename, 'w') as f:
        f.write('\n'.join(result))

    return output_filename, '\n'.join(result)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ALLOWED_USERS:
        return bot.reply_to(message, "Kamu tidak punya akses.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📁 Upload File"), types.KeyboardButton("🏷️ Masukkan Kata Kunci"))
    markup.add(types.KeyboardButton("▶️ Jalankan"))
    bot.send_message(message.chat.id, "Selamat datang! Silakan upload file dan masukkan kata kunci.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📁 Upload File")
def upload_file_prompt(message):
    bot.send_message(message.chat.id, "Silakan kirim file .txt kamu.")
    user_state[message.chat.id] = 'awaiting_file'

@bot.message_handler(func=lambda message: message.text == "🏷️ Masukkan Kata Kunci")
def keyword_prompt(message):
    bot.send_message(message.chat.id, "Masukkan kata kunci pencarian:")
    user_state[message.chat.id] = 'awaiting_keyword'

@bot.message_handler(func=lambda message: message.text == "▶️ Jalankan")
def run_script(message):
    user_id = message.chat.id
    if user_id not in file_store or 'file' not in file_store[user_id] or 'keyword' not in file_store[user_id]:
        return bot.send_message(user_id, "Pastikan kamu sudah upload file dan memasukkan kata kunci.")

    input_file = file_store[user_id]['file']
    keyword = file_store[user_id]['keyword']
    blacklist_file = 'blacklist.txt'

    if not os.path.exists(blacklist_file):
        return bot.send_message(user_id, "File blacklist.txt tidak ditemukan.")

    output_file, result_text = process_file(input_file, keyword, blacklist_file)
    try:
        with open(output_file, 'rb') as doc:
            bot.send_document(user_id, doc)
        if len(result_text) > 4000:
            bot.send_message(user_id, "Hasil terlalu panjang, silakan lihat di file.")
        else:
            bot.send_message(user_id, result_text, parse_mode="MarkdownV2")
    except Exception as e:
        bot.send_message(user_id, f"Terjadi kesalahan: {e}")

@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    if user_state.get(message.chat.id) != 'awaiting_file':
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded)

    file_store[message.chat.id] = file_store.get(message.chat.id, {})
    file_store[message.chat.id]['file'] = file_name
    bot.send_message(message.chat.id, f"File {file_name} berhasil diupload!")
    user_state[message.chat.id] = None

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'awaiting_keyword')
def handle_keyword_input(message):
    file_store[message.chat.id] = file_store.get(message.chat.id, {})
    file_store[message.chat.id]['keyword'] = message.text.strip()
    bot.send_message(message.chat.id, f"Kata kunci disimpan: {message.text}")
    user_state[message.chat.id] = None

print("Bot aktif...")
bot.infinity_polling()
