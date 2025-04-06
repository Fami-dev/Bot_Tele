import time

# Membaca nama file input dan file blacklist
input_file = '@trxsecurity_org 56384995.txt'
blacklist_file = 'blacklist.txt'

def print_progress(step, total_steps, message):
    progress = (step / total_steps) * 100
    print(f"[{progress:.2f}%] {message}")

total_steps = 6  # Jumlah langkah yang dilakukan

# Langkah 1: Membaca data dari file input
print_progress(1, total_steps, "Membaca file input...")
with open(input_file, 'r') as file:
    lines = file.readlines()
time.sleep(0.5)

# Langkah 2: Membaca data dari file blacklist
print_progress(2, total_steps, "Membaca file blacklist...")
with open(blacklist_file, 'r') as file:
    blacklist = [line.strip() for line in file.readlines()]
time.sleep(0.5)

# Langkah 3: Menghapus prefix (https://, www., http://, dll.)
print_progress(3, total_steps, "Membersihkan prefix dari URL...")
cleaned_lines = []
for line in lines:
    line = line.strip()
    for prefix in ["https://", "http://", "www."]:
        if line.startswith(prefix):
            line = line.replace(prefix, "", 1)
    cleaned_lines.append(line)
time.sleep(0.5)

# Langkah 4: Mengubah domain menjadi hanya nama utama dan validasi format
print_progress(4, total_steps, "Memproses domain dan validasi format...")
domain_dict = {}
for line in cleaned_lines:
    parts = line.split(':')
    if len(parts) < 3:  # Validasi format (minimal ada domain, username, password)
        continue
    domain_parts = parts[0].split('/')
    domain = domain_parts[0]  # Mengambil domain utama saja
    username = parts[1]
    password = parts[2]
    
    # Mengecek apakah domain masuk dalam blacklist
    if domain in blacklist:
        continue  # Lewati domain yang ada di blacklist
    
    # Menggabungkan data berdasarkan domain
    if domain not in domain_dict:
        domain_dict[domain] = []
    domain_dict[domain].append((username, password))
time.sleep(0.5)

# Langkah 5: Menyaring hanya domain yang mengandung "smm"
print_progress(5, total_steps, "Menyaring domain dengan kata kunci 'smm'...")
filtered_domains = {domain: creds for domain, creds in domain_dict.items() if "smm" in domain}
time.sleep(0.5)

# Langkah 6: Membuat layout berdasarkan data yang difilter dan diurutkan
print_progress(6, total_steps, "Membuat output dan menyimpan hasil...")
sorted_domains = sorted(filtered_domains.keys())  # Mengurutkan domain berdasarkan abjad
output = []
for domain in sorted_domains:
    output.append(f"[ {domain} ] Status : ✅ ❌\n")
    for username, password in filtered_domains[domain]:
        output.append(f"Username: {username}\nPassword: {password}\n")
    output.append("")  # Menambahkan baris kosong untuk pemisah

# Mengubah nama file output secara dinamis
output_file = f"Output_{input_file.split('.')[0]}.txt"

# Menyimpan hasil ke file output
with open(output_file, 'w') as file:
    file.writelines('\n'.join(output))

print(f"[100.00%] Proses selesai. Data telah disimpan di '{output_file}'.")
