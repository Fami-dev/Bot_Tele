# bot_smm.py
import telebot
import time
import os

BOT_TOKEN = '8151707833:AAHJZWErtOkPCwbbwgZ3oyf0-NtZ17nCLIM'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Halo! Kirim perintah /run untuk menjalankan proses.")

@bot.message_handler(commands=['run'])
def run_script(message):
    try:
        output_file = run_smm_script()
        with open(output_file, 'rb') as doc:
            bot.send_document(message.chat.id, doc)
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan: {str(e)}")

def run_smm_script():
    input_file = '@trxsecurity_org 56384995.txt'
    blacklist_file = 'blacklist.txt'

    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(blacklist_file, 'r') as file:
        blacklist = [line.strip() for line in file.readlines()]

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
        domain = parts[0].split('/')[0]
        username = parts[1]
        password = parts[2]
        if domain in blacklist:
            continue
        if domain not in domain_dict:
            domain_dict[domain] = []
        domain_dict[domain].append((username, password))

    filtered_domains = {d: c for d, c in domain_dict.items() if "smm" in d}
    sorted_domains = sorted(filtered_domains.keys())

    output = []
    for domain in sorted_domains:
        output.append(f"[ {domain} ] Status : ✅ ❌\n")
        for username, password in filtered_domains[domain]:
            output.append(f"Username: {username}\nPassword: {password}\n")
        output.append("")

    output_file = f"Output_{input_file.split('.')[0]}.txt"
    with open(output_file, 'w') as f:
        f.writelines('\n'.join(output))
    return output_file

# Jalankan polling agar bot aktif terus
print("Bot is running...")
bot.infinity_polling()