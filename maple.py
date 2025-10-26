# ==============================================================
# maple.py — automated Maple free trial claim (clean structure)
# ==============================================================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import names, random, string, re, pyperclip, pyautogui
from barnum import gen_data
import requests
import re
import json

# ======================== CONFIG ==============================
CHROMEDRIVER_PATH = r"C:\Bot\Cmap\chromedriver.exe"
HEADLESS = False
TIMEOUT = 30
# ==============================================================


# ------------------ Utility Functions --------------------------
def setup_driver():
    """Initialize Chrome WebDriver with custom options"""
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1200, 900)
    return driver


def safe_click(driver, element):
    """Safely click an element, scroll into view if needed"""
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        driver.execute_script("arguments[0].click();", element)


def set_input(driver, element, value):
    """Set input value via send_keys or JS fallback"""
    try:
        element.clear()
        element.send_keys(value)
    except Exception:
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, element, value)


def extract_key_from_url(url):
    """Extract ?key=XXXX from a URL"""
    m = re.search(r"[?&]key=([A-Za-z0-9\-]+)", url)
    return m.group(1) if m else None
# ----------------------------------------------------------------



# ------------------ Step 1: eTempMail ---------------------------
def get_temp_email(driver):
    """Open eTempMail, click copy, and return the copied email"""
    driver.get("https://etempmail.com/")
    # print("[+] Opened etempmail.com")
    sleep(4)

    temp_email = None

    # Try click copy button and read clipboard
    try:
        copy_btn = driver.find_element(By.ID, "copyEmailAddress")
        safe_click(driver, copy_btn)
        # print("[+] Clicked copyEmailAddress button")
        for _ in range(8):
            sleep(0.3)
            clip = pyperclip.paste()
            if clip and "@" in clip:
                temp_email = clip.strip()
                break
    except Exception as e:
        print("[!] copy button not found/clickable:", e)

    # Fallback: read from visible text
    if not temp_email:
        try:
            el = driver.find_element(By.ID, "email_ch_text")
            val = (el.text or el.get_attribute("innerText") or "").strip()
            if val and "@" in val:
                temp_email = val
                print("[+] Fallback email_ch_text found:", temp_email)
        except Exception:
            pass

    if not temp_email:
        print("[!] Could not get email. Check site manually.")
        return None

    # print(f"[+] Temporary email obtained: {temp_email}")
    return temp_email
# ----------------------------------------------------------------



# ------------------ Step 2: Maple Form --------------------------
def fill_maple_form(driver, wait, email):
    """Open Maple trial form, paste email, and submit"""
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://www.maplesoft.com/products/maple/free-trial/")
    print("[+] Opened Maplesoft free trial page")

    # Paste email with clipboard
    email_input = wait.until(EC.presence_of_element_located((By.ID, "EmailAddress")))
    pyperclip.copy(email)
    email_input.click()
    sleep(0.4)
    pyautogui.hotkey("ctrl", "v")
    sleep(0.6)
    # print("[+] Pasted email using clipboard simulation")

    # Click "Get your free trial"
    try:
        btn = wait.until(EC.element_to_be_clickable((By.ID, "btnSubmitEmail")))
        safe_click(driver, btn)
    except Exception:
        email_input.send_keys(Keys.ENTER)
    print("[+] Submitted email")

    # Fill Step 2 form if it appears
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "FirstName")))
        fn, ln = names.get_first_name(), names.get_last_name()
        set_input(driver, driver.find_element(By.ID, "FirstName"), fn)
        set_input(driver, driver.find_element(By.ID, "LastName"), ln)
        # print(f"[+] Filled names: {fn} {ln}")

        set_input(driver, driver.find_element(By.ID, "Company"), gen_data.create_company_name() + " University")
        set_input(driver, driver.find_element(By.ID, "JobTitle"), "Student")

        # Country
        try:
            Select(driver.find_element(By.ID, "CountryDropDownList")).select_by_value("ID")
        except Exception:
            driver.execute_script("arguments[0].value='ID'; arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                                  driver.find_element(By.ID, "CountryDropDownList"))
        # print("[+] Country set")

        # Segment
        try:
            Select(driver.find_element(By.ID, "ddlSegment")).select_by_visible_text("Student")
        except Exception:
            pass
        # print("[+] Segment set to Student")

        # Checkbox GDPR
        try:
            cb = driver.find_element(By.ID, "chkAgreeToGDPR")
            if not cb.is_selected():
                safe_click(driver, cb)
                # print("[+] Checked box: chkAgreeToGDPR")
        except Exception as e:
            print("[!] Could not click GDPR checkbox:", e)

        # Final submit
        safe_click(driver, driver.find_element(By.ID, "SubmitButton"))
        print("[+] Clicked final SubmitButton")

    except Exception:
        print("[*] Step 2 not visible — maybe email sent directly.")
# ----------------------------------------------------------------



# ------------------ Step 3: Read Mail & Confirm -----------------
def find_confirmation_link(driver, wait):
    """
    Buka halaman email eTempMail, lalu ambil link konfirmasi Maplesoft
    dari dalam iframe di .card-body.px-3 dan buka di tab baru.
    """
    driver.switch_to.window(driver.window_handles[0])
    # print("[+] Switched back to etempmail tab")

    # buka halaman email
    driver.get("https://etempmail.com/email?id=1")
    # print("[+] Opened https://etempmail.com/email?id=1 (latest email view)")
    sleep(5)

    href = None

    try:
        # tunggu sampai iframe muncul
        iframe = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".card-body.px-3 iframe")
        ))
        # print("[+] Found email iframe, switching to it...")
        driver.switch_to.frame(iframe)
        sleep(1)

        # jalankan JS untuk ambil href dari link di email body
        href = driver.execute_script("""
            let a = document.querySelector('body > ol > li:nth-child(1) > a');
            return a ? a.href : null;
        """)
        driver.switch_to.default_content()

        # jika tidak ketemu, fallback pakai XPath
        if not href:
            driver.switch_to.frame(iframe)
            try:
                elem = driver.find_element(By.XPATH, "/html/body/ol/li[1]/a")
                href = elem.get_attribute("href")
            except Exception:
                pass
            driver.switch_to.default_content()

        # kalau ketemu
        if href and "InstantEvalConfirmation" in href:
            # print("[+] Found confirmation link:", href)
            driver.execute_script("window.open(arguments[0], '_blank');", href)
            driver.switch_to.window(driver.window_handles[-1])
            print("[+] Opened confirmation link in new tab")
            return href
        else:
            print("[!] Confirmation link not found inside iframe content.")
            return None

    except Exception as e:
        driver.switch_to.default_content()
        print("[!] Error fetching confirmation link:", e)
        return None




def open_confirmation_and_extract_code(driver, wait, href):
    """Extract evaluationPurchaseCode from confirmation page"""
    try:
        driver.get(href)
        wait_short = WebDriverWait(driver, 20)
        el = wait_short.until(EC.presence_of_element_located((By.ID, "evaluationPurchaseCode")))
        code = el.get_attribute("value") or el.text
        if code:
            print(f"[RESULT] License code: {code.strip()}")
            return code.strip()
    except Exception as e:
        print("[!] Could not extract code:", e)
    return None
# ----------------------------------------------------------------



# ------------------ MAIN WORKFLOW -------------------------------
def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, TIMEOUT)

    try:
        # Step 1: get temp email
        temp_email = get_temp_email(driver)
        if not temp_email:
            input("Press Enter to close...")
            return

        # Step 2: fill Maple form
        fill_maple_form(driver, wait, temp_email)
        sleep(5)

        # Step 3: find link & extract license
        href = find_confirmation_link(driver, wait)
        if href:
            open_confirmation_and_extract_code(driver, wait, href)

    finally:
        input("\nPress Enter to close browser and exit...")
        driver.quit()


# ----------------------------------------------------------------
if __name__ == "__main__":
    main()
