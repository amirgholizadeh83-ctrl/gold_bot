import time
import json
import requests
from bs4 import BeautifulSoup

# ========= تنظیمات =========
URL = "https://horsegold.ir/dashboard"
CHECK_INTERVAL = 300  # هر 5 دقیقه
THRESHOLD = 800000  # آستانه اختلاف (قابل تغییر)

BOT_TOKEN = "8799479898:AAEgSnqoYO2NbrobWyDRHr4wHxuut3RTjcM"
CHAT_ID = "_1003825615784"

# ========= لود کوکی =========
with open("cookies.json", "r", encoding="utf-8") as f:
    cookies_list = json.load(f)

cookies = {c["name"]: c["value"] for c in cookies_list}

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def extract_prices(html):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find_all("tr")

    buy_price = None
    sell_price = None

    for row in rows:
        text = row.get_text(strip=True)

        # خرید نقد فردا (سبز)
        if "نقد فردا" in text and "خرید" in text:
            price_td = row.find_all("td")[-1]
            if "text-success" in str(price_td):  # سبز یعنی فعال
                buy_price = int(price_td.text.replace(",", "").strip())

        # فروش نقد پس فردا (قرمز)
        if "نقد پس فردا" in text and "فروش" in text:
            price_td = row.find_all("td")[-1]
            if "text-danger" in str(price_td):  # قرمز یعنی فعال
                sell_price = int(price_td.text.replace(",", "").strip())

    return buy_price, sell_price

def check_prices():
    try:
        response = requests.get(URL, cookies=cookies, headers=headers)
        html = response.text

        buy, sell = extract_prices(html)

        if buy and sell:
            diff = sell - buy

            print(f"Buy: {buy} | Sell: {sell} | Diff: {diff}")

            if diff >= THRESHOLD:
                msg = (
                    f"🚨 اختلاف رسید به حد مجاز\n"
                    f"خرید نقد فردا: {buy:,}\n"
                    f"فروش نقد پس فردا: {sell:,}\n"
                    f"اختلاف: {diff:,}"
                )
                send_telegram(msg)

        else:
            print("⏸ سایت فعال نیست یا قیمت‌ها کدر هستند")

    except Exception as e:
        print("خطا:", e)

# ========= اجرای دائم =========
while True:
    check_prices()
    time.sleep(CHECK_INTERVAL)