import telebot
import os
import datetime
import requests
from telebot import types

BOT_TOKEN = '8151707833:AAHJZWErtOkPCwbbwgZ3oyf0-NtZ17nCLIM'
bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi untuk escape karakter spesial MarkdownV2
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

# Fungsi utama untuk memproses file input

def process_file(input_file, blacklist_file, keyword):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(blacklist_file, 'r') as file:
        blacklist = [line.strip() for line in file.readlines()]

    cleaned_lines = []
    for line in lines:
        line = line.strip()
        for prefix in ["https://www.", "http://www.", "https://", "http://", "www."]:
            if line.startswith(prefix):
                line = line.replace(prefix, "", 1)
        cleaned_lines.append(line)

    domain_dict = {}
    for line in cleaned_lines:
        parts = line.split(':')
        if len(parts) < 3:
            continue
        domain = parts[0].split('/')[0]
        username = parts[1]
        password = parts[2]
        if domain in blacklist:
            continue
        if keyword.lower() not in domain.lower():
            continue
        if domain not in domain_dict:
            domain_dict[domain] = []
        domain_dict[domain].append((username, password))

    sorted_domains = sorted(domain_dict.keys())
    content = ""
    for domain in sorted_domains:
        content += f"[ {escape_markdown(domain)} ] Status : \u2705 \u274C\n\n"
        for username, password in domain_dict[domain]:
            escaped_user = escape_markdown(username)
            escaped_pass = escape_markdown(password)
            content += f"Username: ```{escaped_user}```\nPassword: ```{escaped_pass}```\n\n"
        content += "\n"

    # Header teks tambahan
    date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = (
        f"\ud83d\udd0e Pencarian Selesai\n\n"
        f"\ud83d\udc64 Username: ```@cloudfami_user```\n"
        f"\ud83d\udcc5 Tanggal: ```{escape_markdown(date_str)}```\n"
        f"\ud83d\udcc1 File: ```{escape_markdown(os.path.basename(input_file))}```\n"
        f"\ud83c\udff7\ufe0f Kata Kunci: ```{escape_markdown(keyword)}```\n\n"
        f"\ud83e\udd16 @cloudfami_bot\n\n"
    ) + content

    output_file = f"Output_{os.path.splitext(os.path.basename(input_file))[0]}.txt"
    with open(output_file, 'w') as f:
        f.write(content)
    return output_file, content

# Handler /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/run')
    bot.send_message(message.chat.id, "Halo! Kirim /run untuk memulai proses.", reply_markup=markup)

# Handler /run
@bot.message_handler(commands=['run'])
def ask_keyword(message):
    msg = bot.send_message(message.chat.id, "Masukkan kata kunci pencarian:")
    bot.register_next_step_handler(msg, ask_file_link)

def ask_file_link(message):
    keyword = message.text
    msg = bot.send_message(message.chat.id, "Kirim link file (harus file .txt dari Telegram):")
    bot.register_next_step_handler(msg, process_all, keyword)

def process_all(message, keyword):
    if not message.text.startswith("https://"):
        bot.send_message(message.chat.id, "Link tidak valid.")
        return

    file_url = message.text
    try:
        file_response = requests.get(file_url)
        file_response.raise_for_status()
        input_file = "input_temp.txt"
        with open(input_file, 'wb') as f:
            f.write(file_response.content)

        blacklist_file = 'blacklist.txt'
        output_file, result_text = process_file(input_file, blacklist_file, keyword)

        with open(output_file, 'rb') as doc:
            bot.send_document(message.chat.id, doc)

        bot.send_message(message.chat.id, result_text, parse_mode='MarkdownV2')

    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan: {str(e)}")

print("Bot is running...")
bot.infinity_polling()
