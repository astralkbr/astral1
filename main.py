# -*- coding: utf-8 -*-
import asyncio
import csv
import base64
import tempfile
import requests
from urllib.parse import unquote
import os

# Licensing kutubxonasini import qilish
from licensing.methods import Helpers # Bu qism qurilma tekshiruvi uchun muhim

import aiohttp
import aiohttp_proxy
import fake_useragent

from termcolor import colored
from telethon import TelegramClient
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import RequestAppWebViewRequest, ImportChatInviteRequest
from telethon.tl.types import InputUser, InputBotAppShortName

from twocaptcha import TwoCaptcha

# --- Qurilma tekshiruvi uchun zarur qism ---
UNIVERSAL_CSV_URL = "https://raw.githubusercontent.com/azaboi/web/main/main/random.csv"

def get_authorized_machine_codes():
    """URL'dan universal.csv faylini yuklab oladi va tozalangan hash qiymatlarini qaytaradi."""
    try:
        response = requests.get(UNIVERSAL_CSV_URL)
        response.raise_for_status()  # HTTP xatolarini tekshirish
        lines = response.text.splitlines()
        return [line.strip() for line in lines if line.strip()] # Bo'sh qatorlarni o'tkazib yuborish
    except requests.exceptions.RequestException as e:
        print(colored(f"URL'dan universal.csv yuklashda xatolik: {e}", "red"))
        return []

def get_current_machine_code():
    """Joriy mashina kodini qaytaradi."""
    try:
        machine_code = Helpers.GetMachineCode(v=2)
        return machine_code
    except Exception as e:
        print(colored(f"Mashina kodini olishda xatolik: {e}", "red"))
        return None

# Qurilma tekshiruvi amalga oshiriladi
authorized_hash_values = get_authorized_machine_codes()
current_machine_code = get_current_machine_code()

if not current_machine_code or current_machine_code not in authorized_hash_values:
    print(colored(f"Device id: {current_machine_code}", "red"))
    print(colored(f"Kod: @RandomGodBot", "red"))
    print(colored(f"@Azamatjon yoki @astralkibr ga murojat qiling. Sizning qurilmangiz ruxsat berilmagan. ", "red"))
    exit() # Agar ruxsat berilmagan bo'lsa, dasturni tugatish
# --- Qurilma tekshiruvi tugadi ---


# === 2Captcha API kalit ===
TWO_CAPTCHA_API_KEY = "3772d342f0cb22b105a5bef8d0677fa9"

# === Solver ===
solver = TwoCaptcha(TWO_CAPTCHA_API_KEY)

# === API ID va HASH ===
API_ID = 22962676
API_HASH = '543e9a4d695fe8c6aa4075c9525f7c57'

# === Proxy yuklash ===
ROTATED_PROXY = None
PROXY_FILE_PATH = "proxy.csv"
try:
    if os.path.exists(PROXY_FILE_PATH):
        with open(PROXY_FILE_PATH) as f:
            reader = csv.reader(f)
            ROTATED_PROXY = next(reader)[0].strip()
            print(colored(f"Proxy: {ROTATED_PROXY}", "cyan"))
    else:
        print(colored("Proxy fayli topilmadi.", "yellow"))
except Exception as e:
    print(colored(f"Proxy yuklashda xatolik: {e}", "yellow"))

# === Giv ID ===
givs = []
GIVS_FILE_PATH = "rangiv.csv"
if os.path.exists(GIVS_FILE_PATH):
    with open(GIVS_FILE_PATH) as f:
        givs = [row[0].strip() for row in csv.reader(f) if row]
    print(colored(f"Giv ID'lar: {len(givs)} ta.", "cyan"))
else:
    print(colored("Giv ID'lari fayli topilmadi!", "red"))

# === Kanallar ===
ochiq = []
yopiq = []
OCHIQ_KANAL_PATH = "ranochiqkanal.csv"
YOPIQ_KANAL_PATH = "ranyopiqkanal.csv"

try:
    if os.path.exists(OCHIQ_KANAL_PATH):
        with open(OCHIQ_KANAL_PATH) as f:
            ochiq = [row[0].strip() for row in csv.reader(f) if row]
    if os.path.exists(YOPIQ_KANAL_PATH):
        with open(YOPIQ_KANAL_PATH) as f:
            yopiq = [row[0].strip() for row in csv.reader(f) if row]
except Exception as e:
    print(colored(f"Kanallar yuklashda xatolik: {e}", "yellow"))

print(colored(f"Ochiq kanallar: {len(ochiq)} ta yopiq kanallar: {len(yopiq)} ta", "cyan"))

# === Bitta akkaunt ishlash ===
async def run(phone, current_index, total_accounts): # Yangi parametrlar qo'shildi
    tg_client = TelegramClient(f"sessions/{phone}", API_ID, API_HASH)
    await tg_client.start()
    me = await tg_client.get_me()
    await tg_client(UpdateStatusRequest(offline=False))

    name = me.username or me.first_name
    # Bu yerda akkaunt indeksi va umumiy soni ko'rsatiladi
    print(colored(f"\n\n[{current_index}/{total_accounts}] {name} ({phone}) | Akkauntga kirildi.", "blue"))

    # Kanallarga qo'shilish
    print(colored(f"[{current_index}/{total_accounts}] {name} | Kanallarga qo'shilmoqda", "yellow"))
    for ch in ochiq:
        try:
            await tg_client(JoinChannelRequest(ch))
            print(colored(f"[{current_index}/{total_accounts}] {name} | Ochiq kanal: {ch} qo'shildi", "green"))
        except Exception as e:
            print(colored(f"[{current_index}/{total_accounts}] {name} | Ochiq kanalga qo'shilishda xato: {e}", "yellow"))

    for ch in yopiq:
        try:
            await tg_client(ImportChatInviteRequest(ch))
            print(colored(f"[{current_index}/{total_accounts}] {name} | Yopiq kanal: {ch} qo'shildi", "green"))
        except Exception as e:
            print(colored(f"[{current_index}/{total_accounts}] {name} | Yopiq kanalga qo'shilishda xato: {e}", "yellow"))
    print(colored(f"[{current_index}/{total_accounts}] {name} | Kanallarga qo'shilish yakunlandi.", "yellow"))


    # Bot bilan ishlash
    bot_entity = await tg_client.get_entity("@RandomGodBot")
    bot = InputUser(user_id=bot_entity.id, access_hash=bot_entity.access_hash)
    bot_app = InputBotAppShortName(bot_id=bot, short_name="JoinLot")

    for giv_id in givs:
        print(colored(f"[{current_index}/{total_accounts}] {name} | Giv ID: {giv_id} qoshilmoqda...", "yellow"))
        retries = 4  # Qayta urinishlar soni
        joined = False

        for attempt in range(retries):
            if joined:
                break

            print(colored(f"[{current_index}/{total_accounts}] {name} | Giv ID: {giv_id} uchun {attempt + 1}-urinish...", "cyan"))
            try:
                web_view = await tg_client(
                    RequestAppWebViewRequest(
                        peer=bot,
                        app=bot_app,
                        platform="android",
                        write_allowed=True,
                        start_param=giv_id
                    )
                )
                init_data = unquote(web_view.url.split("tgWebAppData=",1)[1].split("&")[0])
                encoded_init_data = base64.b64encode(init_data.encode()).decode()

                proxy_conn = aiohttp_proxy.ProxyConnector().from_url(ROTATED_PROXY) if ROTATED_PROXY else None

                headers = {
                    'user-agent': fake_useragent.UserAgent().random,
                    'accept': '*/*',
                    'x-requested-with': 'XMLHttpRequest',
                    'referer': f'https://randomgodbot.com/api/lottery/snow/main.html?tgWebAppStartParam={giv_id}'
                }

                async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as session:
                    url = f"https://randomgodbot.com/lot_join?userId={me.id}&startParam={giv_id}&id={encoded_init_data}"
                    resp = await session.get(url, ssl=False)

                    res_json = None # Default qiymat
                    try:
                        res_json = await resp.json()
                    except aiohttp.ContentTypeError:
                        response_text = await resp.text()
                        print(colored(f"[{current_index}/{total_accounts}] {name} | Serverdan kutilmagan javob turi (JSON emas): {response_text[:100]}", "yellow"))
                        if "ALREADY_JOINED" in response_text:
                            print(colored(f"[{current_index}/{total_accounts}] {name} | 🔵 Allaqachon qatnashgan (matnli javob orqali aniqlandi).", "blue"))
                            joined = True
                            break
                        else:
                            print(colored(f"[{current_index}/{total_accounts}] {name} | ❌ Serverdan noto'g'ri matnli javob. Qayta urinamiz.", "red"))
                            await asyncio.sleep(0)
                            continue

                    # === Kapcha tekshir va natijani umumiy joyda tekshir ===
                    if res_json and res_json.get('result', {}).get('base64'):
                        b64 = res_json['result']['base64']
                        hsh = res_json['result']['hash']

                        captcha_path = ""
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                            f.write(base64.b64decode(b64))
                            captcha_path = f.name

                        print(colored(f"[{current_index}/{total_accounts}] {name} | Kapcha yechilmoqda", "cyan"))
                        try:
                            result = solver.normal(file=captcha_path)
                            solved = result['code']
                            print(colored(f"[{current_index}/{total_accounts}] {name} | Kapcha yechildi: {solved}", "green"))

                            final_url = f"{url}&captcha_hash={hsh}&captcha_value={solved}"
                            resp = await session.get(final_url, ssl=False)

                            res_json = None # Default qiymat
                            try:
                                res_json = await resp.json()
                            except aiohttp.ContentTypeError:
                                response_text = await resp.text()
                                print(colored(f"[{current_index}/{total_accounts}] {name} | Kapcha yechilgandan keyingi serverdan kutilmagan javob (JSON emas): {response_text[:100]}", "yellow"))
                                if "ALREADY_JOINED" in response_text:
                                    print(colored(f"[{current_index}/{total_accounts}] {name} | 🔵 Allaqachon qatnashgan (kapchadan keyingi matnli javob orqali).", "blue"))
                                    joined = True
                                    break
                                else:
                                    print(colored(f"[{current_index}/{total_accounts}] {name} | ❌ Kapcha yechilgandan keyin noto'g'ri matnli javob. Qayta urinamiz.", "red"))
                                    await asyncio.sleep(0)
                                    continue
                        except Exception as captcha_error:
                            print(colored(f"[{current_index}/{total_accounts}] {name} | Kapcha yechishda xato qayta urinamiz: {captcha_error}", "red"))
                            if os.path.exists(captcha_path):
                                os.remove(captcha_path)
                            await asyncio.sleep(2)
                            continue
                        finally:
                            if os.path.exists(captcha_path):
                                os.remove(captcha_path)

                    else:
                        print(colored(f"[{current_index}/{total_accounts}] {name} | Giv ID: {giv_id} uchun kapcha talab qilinmadi.", "light_green"))

                    # --- Natijani tekshirish logikasi umumiy joyga ko'chirildi ---
                    if res_json and res_json.get('ok') and res_json.get('result') == 'success':
                        print(colored(f"[{current_index}/{total_accounts}] {name} | ✅ Giv muvaffaqiyatli qo'shildi!", "green"))
                        joined = True
                    elif res_json and res_json.get('description') == 'ALREADY_JOINED':
                        print(colored(f"[{current_index}/{total_accounts}] {name} | ✅ Giv muvaffaqiyatli qo'shildi yoki oldin qatnashgan.", "blue"))
                        joined = True
                    else:
                        if isinstance(res_json, dict):
                            print(colored(f"[{current_index}/{total_accounts}] {name} | ❌ Giv qo'shilmadi. Javob: {res_json}. \nQayta urinamiz", "red"))
                        elif res_json is None:
                             print(colored(f"[{current_index}/{total_accounts}] {name} | ❌ Giv qo'shilmadi. Serverdan javob olinmadi yoki noto'g'ri formatda. Qayta urinamiz", "red"))
                        else:
                            print(colored(f"[{current_index}/{total_accounts}] {name} | ❌ Giv qo'shilmadi. Noto'g'ri javob turi. Qayta urinamiz", "red"))
                        await asyncio.sleep(0)

            except Exception as e:
                # Kengaytirilgan xato xabarini chiqarish
                print(colored(f"[{current_index}/{total_accounts}] {name} | Giv ID: {giv_id} ni qayta ishlashda kutilmagan xatolik: {e}", "red"))
                await asyncio.sleep(1) # Bir oz kutib, keyingi urinishga o'tish

        if not joined:
            print(colored(f"[{current_index}/{total_accounts}] {name} | ⚠️ Giv ID: {giv_id} ga qo'shib bo'lmadi barcha urinishlardan keyin.", "red"))

    await tg_client.disconnect()
    print(colored(f"[{current_index}/{total_accounts}] {name} ({phone}) | Akkauntdan chiqildi.", "blue"))

# === Barcha akkauntlar ===
async def main():
    PHONES_FILE_PATH = 'phone.csv'
    if not os.path.exists(PHONES_FILE_PATH):
        print(colored(f"Xatolik: '{PHONES_FILE_PATH}' fayli topilmadi. Iltimos, telefon raqamlaringizni ushbu faylga kiriting.", "red"))
        return

    with open(PHONES_FILE_PATH) as f:
     phones = [line.strip().lstrip('+') for line in f if line.strip()]

    if not phones:
        print(colored(f"Xatolik: '{PHONES_FILE_PATH}' faylida telefon raqamlari topilmadi. Iltimos, raqamlarni kiriting.", "red"))
        return

    total_accounts = len(phones) # Umumiy akkauntlar soni
    print(colored(f"Jami {total_accounts} ta akkaunt topildi.", "magenta"))

    while True:
        mode = input(colored("Qaysi rejimda ishlashni xohlaysiz? ('tez' yoki 'sekin'): ", "cyan")).lower()
        if mode in ['tez', 'sekin']:
            break
        else:
            print(colored("Noto'g'ri rejim tanlandi. Iltimos, 'tez' yoki 'sekin' kiriting.", "red"))

    if mode == 'tez':
        print(colored("Tez rejim tanlandi: Akkauntlar 15 tadan partiyalar bilan parallel ishga tushiriladi.", "green"))
        chunk_size = 15 
        for i in range(0, total_accounts, chunk_size):
            chunk = phones[i:i + chunk_size]
            tasks = []
            print(colored(f"\n[{i+1}-{min(i+chunk_size, total_accounts)}] partiya ishga tushirilmoqda...", "yellow"))
            for j, phone in enumerate(chunk):
                current_index = i + j + 1
                tasks.append(run(phone, current_index, total_accounts))
            await asyncio.gather(*tasks)
            print(colored(f"[{i+1}-{min(i+chunk_size, total_accounts)}] partiya yakunlandi.", "green"))
            await asyncio.sleep(0) # Partiyalar orasida biroz kutish
    elif mode == 'sekin':
        print(colored("Sekin rejim tanlandi: Barcha akkauntlar birma-bir ishga tushiriladi.", "green"))
        for i, phone in enumerate(phones):
            current_index = i + 1
            await run(phone, current_index, total_accounts)

if __name__ == "__main__":
    asyncio.run(main())
# -*- coding: utf-8 -*-
