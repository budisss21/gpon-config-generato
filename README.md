# GPON Config Generator

Aplikasi berbasis Python GUI untuk membantu teknisi OLT GPON dalam menghasilkan konfigurasi otomatis, khususnya untuk mode PPPoE dengan opsi SN-auth dan OMCI. Dirancang untuk mempercepat proses provisioning pelanggan baru.

## ✨ Fitur Utama
- Konfigurasi PPPoE otomatis untuk OLT Huawei
- Mode penggantian service-port jika diperlukan
- Dukungan SN-auth dan OMCI provisioning
- Otomatisasi service-port dan konfigurasi VLAN
- Output konfigurasi siap ditempel ke CLI OLT

## 🖥️ Teknologi yang Digunakan
- Python 3.x
- Tkinter (GUI)
- PyInstaller (untuk membuat file `.exe`)
- Logika konfigurasi berbasis template

## 📦 Instalasi

```bash
git clone https://github.com/budisss21/gpon-config-generato.git
cd gpon-config-generato
pip install -r requirements.txt
python main.py
