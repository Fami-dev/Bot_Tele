import telebot
import os
import datetime
import requests

BOT_TOKEN = '8151707833:AAHJZWErtOkPCwbbwgZ3oyf0-NtZ17nCLIM'
ALLOWED_USERS = [1374294212]  # ganti dengan user_id yang diizinkan pakai bot

bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi pembersih domain
def clean_domain(line):
    for prefix in ["https://www.", "http://www.", "https://", "http://", "www."]:
        if line.startswith(prefix):
            line = line.replace(prefix, "", 1)
    return line.strip()

# Fungsi untuk memproses file dan menghasilkan output
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

    # Sort hasilnya
    sorted_domains = sorted(domain_dict.items())

    # Buat output string
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"""🔎 Pencarian Selesai

👤 Username: 
📅 Tanggal: {now}
📁 File: {os.path.basename(input_path)}
🏷️ Kata Kunci: {keyword}

🤖 @cloudfami_bot
"""

    result = [header]
    for domain, creds in sorted_domains:
        result.append(f"[ {domain} ] Status : ✅ ❌\n")
        for user, pwd in creds:
            result.append(f"Username: ```{user}```\nPassword: ```{pwd}```\n")
        result.append("")

    # Simpan ke file
    output_filename = f"Output_{os.path.basename(input_path)}"
    with open(output_filename, 'w') as f:
        f.write('\n'.join(result))
    
    return output_filename, '\n'.join(result)

# ========== HANDLER BOT ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo! Kirim perintah /run lalu upload file akun (txt) dan masukkan kata kunci pencarian.")

@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id not in ALLOWED_USERS:
        return bot.reply_to(message, "Kamu tidak punya akses.")
    
    msg = bot.reply_to(message, "Silakan kirim file txt akun kamu.")
    bot.register_next_step_handler(msg, handle_file)

def handle_file(message):
    if not message.document:
        return bot.reply_to(message, "Harap kirim file .txt")

    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded)

    msg = bot.reply_to(message, "File diterima. Sekarang, masukkan kata kunci pencarian (misal: smm)")
    bot.register_next_step_handler(msg, handle_keyword, file_name)

def handle_keyword(message, file_name):
    keyword = message.text.strip()
    blacklist_file = 'blacklist.txt'
    if not os.path.exists(blacklist_file):
        return bot.reply_to(message, "File blacklist.txt tidak ditemukan.")

    output_file, result_text = process_file(file_name, keyword, blacklist_file)
    try:
        with open(output_file, 'rb') as doc:
            bot.send_document(message.chat.id, doc)
        # Potong text kalau terlalu panjang untuk Telegram
        if len(result_text) > 4000:
            bot.send_message(message.chat.id, "Hasil terlalu panjang, silakan lihat di file.")
        else:
            bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"Terjadi kesalahan saat mengirim file atau hasil:\n{e}")

# ========== RUN ==========

print("Bot aktif...")
bot.infinity_polling()
