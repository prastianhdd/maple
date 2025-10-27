# main.py — batch runner (one browser per job; cookies reset each job)

import os
import time
from selenium.webdriver.support.ui import WebDriverWait
import maple  # asumsi maple.py ada di folder yang sama

OUTPUT_FILE = "licenses.txt"
DELAY_BETWEEN_JOBS = 2  # detik jeda antar job

def run_batch(count):
    obtained = []

    for i in range(1, count + 1):
        print(f"\n=== Job {i}/{count} — starting new browser session ===")

        # buat browser baru untuk setiap job (membersihkan cookies/session)
        driver = maple.setup_driver()
        wait = WebDriverWait(driver, maple.TIMEOUT)

        try:
            # 1) ambil temp email
            temp_email = maple.get_temp_email(driver)
            if not temp_email:
                print("[!] Failed to obtain temp email — closing this session.")
                continue

            print("[*] Temp email:", temp_email)

            # 2) isi form Maple
            try:
                maple.fill_maple_form(driver, wait, temp_email)
            except Exception as e:
                print("[!] Error filling Maple form:", e)
                continue

            # beri server waktu mengirim email
            time.sleep(5)

            # 3) temukan link konfirmasi (dalam iframe) dan buka
            href = maple.find_confirmation_link(driver, wait)
            if not href:
                print("[!] Confirmation link not found — this job failed.")
                continue

            # 4) ambil kode lisensi dari halaman konfirmasi
            code = None
            try:
                # open_confirmation_and_extract_code di maple.py mengunjungi href sendiri
                code = maple.open_confirmation_and_extract_code(driver, wait, href)
            except Exception as e:
                print("[!] Error extracting license code:", e)

            if code:
                print(f"[+] Got license: {code}")
                obtained.append(code)
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(code + "\n")
            else:
                print("[!] No license obtained for this job.")

        finally:
            # selalu tutup browser untuk memastikan sesi/cookie bersih
            try:
                driver.quit()
            except Exception:
                pass

        # jeda kecil sebelum job selanjutnya
        time.sleep(DELAY_BETWEEN_JOBS)

    # ringkasan
    print("\n=== Batch finished ===")
    print(f"Total licenses obtained: {len(obtained)}")
    if obtained:
        print("Saved to", os.path.abspath(OUTPUT_FILE))

if __name__ == "__main__":
    try:
        n = int(input("How many licenses do you want to obtain? ").strip())
        if n <= 0:
            print("Nothing to do.")
        else:
            run_batch(n)
    except Exception as e:
        print("Invalid input or error:", e)
