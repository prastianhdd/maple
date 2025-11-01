# Bot License Maple

## ⚙️ Instalasi

Pastikan Anda memiliki [Python 3.10+](https://www.python.org/downloads/) terinstal.

1.  **Clone repositori ini (jika ada):**
    ```bash
    git clone https://github.com/prastianhdd/maple.git
    cd maple
    ```

2.  **Instal dependensi Python:**
    ```bash
    pip install selenium names pyperclip pyautogui barnum requests
    ```

3.  **Unduh ChromeDriver:**
    Skrip ini memerlukan `chromedriver` agar Selenium dapat mengontrol Google Chrome.
    * Periksa versi Google Chrome Anda (Ketik `chrome://version` di browser).
    * Unduh `chromedriver` yang **sesuai** dari: [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)

## Cara Menjalankan
Untuk memulai proses batch, jalankan file main.py dari terminal Anda:

```bash
python main.py
```

> Skrip akan meminta input jumlah tugas yang ingin dijalankan:
```
How many licenses do you want to obtain? 5
```
>Bot akan berjalan, membuka dan menutup browser untuk setiap siklus.

# Output
Semua hasil yang berhasil diekstraksi akan disimpan secara otomatis di file `licenses.txt.`
