import requests
import time
import logging
import json
from datetime import datetime
import os
import re
import random
import telebot
from telebot import types

# ==================== التكوين الأساسي والمحدث ====================
BOT_TOKEN = "8794664378:AAFcVsAZYI88fNjHk35sBZ-xwe0ZfjPo5uE"
ADMIN_ID = 6532494160  
BOT_NAME = "Radwan Djezzy Bot"
LOGS_CHANNEL_USERNAME = "@Djezey_3"  # قناة الإثباتات والنشاطات

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ==================== إعدادات البروكسي (Proxy Configuration) ====================
PROXIES = {
    "http": "http://5St6utdnmV30_custom_zone_DZ_st__city_sid_34680749_time_10:3242070@change4.owlproxy.com:7778",
    "https": "http://5St6utdnmV30_custom_zone_DZ_st__city_sid_34680749_time_10:3242070@change4.owlproxy.com:7778"
}

# ==================== الملفات وقواعد البيانات المبسطة ====================
REGISTERED_NUMBERS_FILE = "registered_numbers.json"
CHANNELS_FILE = "channels.json"
USERS_FILE = "users.json"

if not os.path.exists(CHANNELS_FILE) or os.path.getsize(CHANNELS_FILE) == 0:
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# ==================== الإعدادات وسجلات الـ Logs ====================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==================== المتغيرات العامة والجلسات ====================
user_sessions = {}
user_numbers = {}
pending_otp = {}

otp_cache_dict = {}
token_cache_dict = {}

def clean_expired_cache():
    current_time = time.time()
    for k, v in list(otp_cache_dict.items()):
        if current_time - v['timestamp'] > 60:
            otp_cache_dict.pop(k, None)
    for k, v in list(token_cache_dict.items()):
        if current_time - v['timestamp'] > 3600:
            token_cache_dict.pop(k, None)

# ==================== قائمة العروض الثابتة والقوية ====================
OFFER_CODES = {
    'offer_1': "GIFTWALKWIN2GO",
    'offer_2': "BTLINTSPEEDDAY2Go",
    'offer_3': "BTL500MBDAY",
    'offer_4': "BTLINTSPEED300DA10GO",
    'offer_5': "BTLINTSPEED1000DA30GO",
    'offer_6': "BTLINTSPEED1500DA60GO",
    'offer_7': "BTLHYBMONTHLY800DA",
    'offer_8': "BTLHYBMONTHLY1000DA",
    'offer_9': "BTL2C2000"
}

ALL_OFFERS = {
    'offer_1': {'offer_id': "offer_1", 'name': "🎁 2GB مجاناً", 'code': OFFER_CODES['offer_1'], 'amount': "2GB", 'type': "free", 'price': "مجاني", 'duration': "24 ساعة"},
    'offer_2': {'offer_id': "offer_2", 'name': "⚡ 4GB (70 DA)", 'code': OFFER_CODES['offer_2'], 'amount': "4GB", 'type': "paid", 'price': "70 DA", 'duration': "24 ساعة"},
    'offer_3': {'offer_id': "offer_3", 'name': "🤝 5GB (90 DA)", 'code': OFFER_CODES['offer_3'], 'amount': "5GB", 'type': "paid", 'price': "90 DA", 'duration': "24 ساعة"},
    'offer_4': {'offer_id': "offer_4", 'name': "🚀 10GB (300 DA)", 'code': OFFER_CODES['offer_4'], 'amount': "10GB", 'type': "paid", 'price': "300 DA", 'duration': "3 أيام"},
    'offer_5': {'offer_id': "offer_5", 'name': "💎 30GB (1000 DA)", 'code': OFFER_CODES['offer_5'], 'amount': "30GB", 'type': "paid", 'price': "1000 DA", 'duration': "30 يوم"},
    'offer_6': {'offer_id': "offer_6", 'name': "👑 60GB (1500 DA)", 'code': OFFER_CODES['offer_6'], 'amount': "60GB", 'type': "paid", 'price': "1500 DA", 'duration': "30 يوم"},
    'offer_7': {'offer_id': "offer_7", 'name': "👑 IMTIYAZ 800DA", 'code': OFFER_CODES['offer_7'], 'amount': "15GB + 2000DA", 'type': "paid", 'price': "800 DA", 'duration': "30 يوم"},
    'offer_8': {'offer_id': "offer_8", 'name': "👑 IMTIYAZ 1000DA", 'code': OFFER_CODES['offer_8'], 'amount': "20GB + 3000DA", 'type': "paid", 'price': "1000 DA", 'duration': "30 يوم"},
    'offer_9': {'offer_id': "offer_9", 'name': "👑 IMTIYAZ 2000DA", 'code': OFFER_CODES['offer_9'], 'amount': "70GB", 'type': "paid", 'price': "2000 DA", 'duration': "30 يوم"}
}

HEADERS = {
    'User-Agent': "MobileApp/3.0.0",
    'Accept': "application/json",
    'Content-Type': "application/json",
    'accept-language': "fr",
    'Connection': "keep-alive"
}

# ==================== دوال المساعدة لوحة التحكم ====================
def log_user_action(user_id, username, action):
    print(f" LOG | [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] User: {username} ({user_id}) -> Action: {action}")

def load_json_file(filename, default_val):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return default_val
    return default_val

def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user_to_db(user_id, username):
    users = load_json_file(USERS_FILE, [])
    if str(user_id) not in [str(u['id']) for u in users]:
        users.append({'id': user_id, 'username': username, 'date': datetime.now().strftime("%Y-%m-%d")})
        save_json_file(USERS_FILE, users)

# ==================== [تحديث] فحص الاشتراك الإجباري والفرز الذكي ====================
def get_unjoined_channels(user_id):
    """ترجع قائمة بالقنوات التي لم يشترك فيها المستخدم بعد"""
    if user_id == ADMIN_ID:
        return []
        
    channels = load_json_file(CHANNELS_FILE, [])
    if not channels:
        return []
        
    unjoined = []
    for ch in channels:
        try:
            member = bot.get_chat_member(ch['username'], user_id)
            if member.status in ['left', 'kicked', 'None', None]:
                unjoined.append(ch)
        except Exception:
            # إذا فشل البوت في جلب العضو (مثلاً القناة غير موجودة أو البوت ليس أدمن)، يتم فرض الاشتراك احتياطاً
            unjoined.append(ch)
    return unjoined

def check_must_join(user_id):
    """ترجع True إذا كان مشترك في كل القنوات، وإلا ترجع False"""
    return len(get_unjoined_channels(user_id)) == 0

# ==================== دوال دجيزي الأساسية بالبروكسي ====================
def format_num(phone):
    phone = re.sub(r'\D', '', str(phone))
    if phone.startswith('0'):
        return "213" + phone[1:]
    return "213" + phone

def format_phone(phone):
    if phone.startswith('0'):
        return phone
    return "0" + phone[3:]

def mask_phone(phone):
    if len(phone) >= 10:
        return phone[:4] + "xxxx" + phone[-2:]
    return phone

def request_otp(msisdn):
    clean_expired_cache()
    cache_key = f"otp_{msisdn}"
    if cache_key in otp_cache_dict:
        return True
        
    url = "https://apim.djezzy.dz/mobile-api/oauth2/registration"
    params = {'msisdn': msisdn, 'client_id': "87pIExRhxBb3_wGsA5eSEfyATloa", 'scope': "smsotp"}
    payload = {"consent-agreement": [{"marketing-notifications": False}], "is-consent": True}
    for attempt in range(3):
        try:
            response = requests.post(url, params=params, json=payload, headers=HEADERS, proxies=PROXIES, timeout=12)
            if response.status_code in [200, 201, 202]:
                otp_cache_dict[cache_key] = {'timestamp': time.time()}
                return True
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return False

def login_with_otp(mobile_number, otp):
    clean_expired_cache()
    cache_key = f"token_{mobile_number}_{otp}"
    if cache_key in token_cache_dict:
        return token_cache_dict[cache_key]['token']
        
    payload = {'otp': otp, 'mobileNumber': mobile_number, 'scope': "djezzyAppV2", 'client_id': "87pIExRhxBb3_wGsA5eSEfyATloa", 'client_secret': "uf82p68Bgisp8Yg1Uz8Pf6_v1XYa", 'grant_type': "mobile"}
    for attempt in range(3):
        try:
            res = requests.post("https://apim.djezzy.dz/mobile-api/oauth2/token", data=payload, headers={'User-Agent': "MobileApp/3.0.0"}, proxies=PROXIES, timeout=12)
            if res.status_code == 200:
                token = f"Bearer {res.json().get('access_token')}"
                token_cache_dict[cache_key] = {'token': token, 'timestamp': time.time()}
                return token
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return None

def get_balance(token, phone):
    try:
        headers_with_auth = {**HEADERS, 'authorization': token}
        response_main = requests.get(f"https://apim.djezzy.dz/mobile-api/api/v1/subscribers/main-balance/{phone}", headers=headers_with_auth, proxies=PROXIES, timeout=12)
        if response_main.status_code == 200:
            data = response_main.json()
            balance = data.get('data', {}).get('mainBalance', 0)
            due = data.get('data', {}).get('due', 0)
            return True, f"💰 رصيدك: <b>{balance:,.2f} DA</b>\n📅 متبقي: <b>{due} يوم</b>"
        return False, "❌ فشل جلب الرصيد"
    except:
        return False, "❌ خطأ في الاتصال بالسيرفر"

def activate_product_offer(token, phone, package_code):
    for attempt in range(3):
        try:
            url = f"https://apim.djezzy.dz/mobile-api/api/v1/subscribers/activate-product/{phone}"
            payload = {"packageCode": package_code}
            headers_with_auth = {**HEADERS, 'authorization': token}
            response = requests.post(url, json=payload, headers=headers_with_auth, proxies=PROXIES, timeout=12)
            if response.status_code in [200, 201, 202]:
                return True
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return False

def activate_weekly_gift(token, phone):
    for attempt in range(3):
        try:
            url = f"https://apim.djezzy.dz/mobile-api/api/v1/services/walk/activate-reward/{phone}"
            payload = {"packageCode": OFFER_CODES['offer_1']}
            headers_with_auth = {**HEADERS, 'authorization': token}
            response = requests.post(url, json=payload, headers=headers_with_auth, proxies=PROXIES, timeout=12)
            if response.status_code in [200, 201, 202]:
                return True
            time.sleep(0.5)
        except:
            time.sleep(0.5)
    return False

# ==================== دوال نظام الدعوات (MGM) المتزامنة ====================
def get_invitations(token, msisdn):
    try:
        headers = {**HEADERS, "authorization": token}
        res = requests.get(f"https://apim.djezzy.dz/mobile-api/api/v1/services/mgm/invitations/{msisdn}", headers=headers, proxies=PROXIES, timeout=10)
        if res.status_code == 200:
            all_inv = res.json().get("data", {}).get("invitations", [])
            return [inv for inv in all_inv if inv.get("status") == "PENDING"]
    except:
        pass
    return []

def delete_invitation(token, msisdn, receiver):
    try:
        headers = {**HEADERS, "authorization": token}
        requests.post(f"https://apim.djezzy.dz/mobile-api/api/v1/services/mgm/delete-invitation/{msisdn}", json={"msisdnReceiver": receiver}, headers=headers, proxies=PROXIES, timeout=10)
    except:
        pass

def activate_reward_check(token, msisdn):
    try:
        headers = {**HEADERS, "authorization": token}
        res = requests.post(f"https://apim.djezzy.dz/mobile-api/api/v1/services/mgm/activate-reward/{msisdn}", json={"packageCode": "MGMBONUS1Go"}, headers=headers, proxies=PROXIES, timeout=10)
        data = res.json() if res.status_code in [200, 201] else {}
        msg = data.get("message", {})
        ar = msg.get("ar", "") if isinstance(msg, dict) else str(msg)
        if res.status_code in [200, 201]:
            return True, ar or "تم التفعيل"
        return False, ar or "لا توجد مكافأة"
    except:
        return False, "خطأ في الاتصال"

def send_invite_random(token, msisdn):
    try:
        headers = {**HEADERS, "authorization": token}
        for _ in range(20):
            prefix = random.choice(["077", "079"])
            receiver = format_num(prefix + str(random.randint(1000000, 9999999)))
            res = requests.post(f"https://apim.djezzy.dz/mobile-api/api/v1/services/mgm/send-invitation/{msisdn}", json={"msisdnReciever": receiver}, headers=headers, proxies=PROXIES, timeout=10)
            data = res.json()
            if res.status_code in [200, 201]:
                return True, receiver
            msg = data.get("message", {})
            if isinstance(msg, dict) and "الحد الأقصى" in msg.get("ar", ""):
                return False, "max"
    except:
        pass
    return False, None

def register_random(receiver):
    try:
        requests.post(f"https://apim.djezzy.dz/mobile-api/oauth2/registration?msisdn={receiver}&client_id=87pIExRhxBb3_wGsA5eSEfyATloa&scope=smsotp", json={"consent-agreement": [{"marketing-notifications": False}], "is-consent": True}, headers=HEADERS, proxies=PROXIES, timeout=10)
    except:
        pass

def activate_reward(token, msisdn):
    try:
        headers = {**HEADERS, "authorization": token}
        res = requests.post(f"https://apim.djezzy.dz/mobile-api/api/v1/services/mgm/activate-reward/{msisdn}", json={"packageCode": "MGMBONUS1Go"}, headers=headers, proxies=PROXIES, timeout=10)
        data = res.json()
        msg = data.get("message", {})
        ar = msg.get("ar", "") if isinstance(msg, dict) else ""
        if res.status_code in [200, 201]:
            return True, ar or "تم التفعيل"
        return False, ar or "تعذر الاستلام"
    except:
        return False, "خطأ"

def handle_invitations_flow_return(chat_id, token, msisdn):
    ok, msg = activate_reward_check(token, msisdn)
    if ok:
        return True

    invitations = get_invitations(token, msisdn)
    for inv in invitations:
        receiver = inv.get("msisdnReceiver") or ""
        if receiver:
            delete_invitation(token, msisdn, receiver)
            time.sleep(0.5)
    if invitations:
        time.sleep(1)

    for _ in range(5):
        ok2, receiver = send_invite_random(token, msisdn)
        if not ok2:
            if receiver == "max":
                bot.send_message(chat_id, "⛔ <b>وصلت للحد الأقصى من الدعوات اليوم!</b>\n\n📌 حاول مجدداً غداً.", parse_mode="HTML")
                return False
            time.sleep(1)
            continue

        register_random(receiver)
        time.sleep(1)
        ok3, _ = activate_reward(token, msisdn)
        if ok3:
            return True
        delete_invitation(token, msisdn, receiver)
        time.sleep(1)

    return False

# ==================== [تحديث] محرك البوت ومعالجة الاشتراك الديناميكي ====================

def send_join_msg(chat_id):
    """توليد أزرار القنوات غير المشترك فيها فقط ديناميكياً"""
    unjoined_channels = get_unjoined_channels(chat_id)
    if not unjoined_channels:
        return
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in unjoined_channels:
        markup.add(types.InlineKeyboardButton(text=ch['title'], url=ch['link']))
    markup.add(types.InlineKeyboardButton(text="🔄 تم الاشتراك، تأكيد ✅", callback_data="check_subscription"))
    
    bot.send_message(chat_id, "⚠️ <b>عذراً عزيزي، يجب عليك الاشتراك في القنوات المتبقية أولاً لتتمكن من استخدام البوت:</b>", reply_markup=markup, protect_content=True)

def show_main_menu(chat_id, display_phone):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buttons = []
    for off_id, off_info in ALL_OFFERS.items():
        btn_buttons.append(types.InlineKeyboardButton(text=off_info['name'], callback_data=f"show_{off_id}"))
    
    markup.add(*btn_buttons)
    markup.add(types.InlineKeyboardButton(text="🎁 تفعيل ميزة هدايا الدعوات (MGM)", callback_data="activate_mgm_flow"))
    markup.add(types.InlineKeyboardButton(text="💰 فحص رصيد الحساب", callback_data="balance"))
    markup.add(types.InlineKeyboardButton(text="🔄 تسجيل خروج / رقم جديد", callback_data="logout"))
    
    msg_text = f"✨ <b>مرحباً بك في بوت عروض جيزي المتكامل</b> ✨\n\n📱 الرقم النشط حالياً: <code>{mask_phone(display_phone)}</code>\n\nاختر العرض أو الخدمة المطلوبة من الأسفل مباشرة:"
    bot.send_message(chat_id, msg_text, reply_markup=markup, protect_content=True)

@bot.message_handler(commands=['start'])
def welcome_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    add_user_to_db(user_id, username)
    
    user_numbers.pop(user_id, None)
    pending_otp.pop(user_id, None)
    
    # الفحص الديناميكي: لو مش مشترك في كل القنوات تطلعله القنوات الناقصة بس
    if not check_must_join(user_id):
        send_join_msg(user_id)
        return

    if user_id in user_sessions:
        show_main_menu(user_id, user_sessions[user_id]['display_phone'])
    else:
        welcome_text = f"✨ <b>مرحباً بك في {BOT_NAME}</b> ✨\n\nالبوت الأسرع لتفعيل عروض جيزي المتكاملة ونظام الدعوات.\n\n📲 يرجى إرسال رقم هاتفك بصيغة (07XXXXXXXX) للبدء:"
        bot.send_message(user_id, welcome_text, protect_content=True)

# ==================== لوحة التحكم الخاصة بالمشرف ====================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text="➕ إضافة قناة (رابط فقط)", callback_data="adm_add"),
        types.InlineKeyboardButton(text="❌ حذف قناة", callback_data="adm_del"),
        types.InlineKeyboardButton(text="📊 الإحصائيات", callback_data="adm_stats")
    )
    bot.send_message(ADMIN_ID, "🛠️ <b>مرحباً بك يا مدير في لوحة تحكم البوت:</b>", reply_markup=markup, protect_content=True)

def process_add_channel(message):
    if message.from_user.id != ADMIN_ID:
        return
    url = message.text.strip()
    if "t.me/" not in url:
        bot.send_message(ADMIN_ID, "❌ الرابط غير صالح! أرسل رابطاً صحيحاً.", protect_content=True)
        return
    try:
        username_part = url.split("t.me/")[1].split("/")[0]
        ch_username = f"@{username_part}"
        chat_info = bot.get_chat(ch_username)
        ch_title = f"📢 قـنـاة {chat_info.title}"
        
        channels = load_json_file(CHANNELS_FILE, [])
        if ch_username in [c['username'] for c in channels]:
            bot.send_message(ADMIN_ID, "⚠️ هذه القناة مضافة بالفعل!", protect_content=True)
            return
        channels.append({'username': ch_username, 'link': url, 'title': ch_title})
        save_json_file(CHANNELS_FILE, channels)
        bot.send_message(ADMIN_ID, f"✅ <b>تمت الإضافة بنجاح!</b>\n\n📋 {ch_title}", protect_content=True)
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ <b>فشل جلب القناة!</b> تأكد من رفع البوت أدمن أولاً.\nالخطأ: {e}", protect_content=True)

def process_delete_channel(call, idx):
    if call.from_user.id != ADMIN_ID:
        return
    channels = load_json_file(CHANNELS_FILE, [])
    if 0 <= idx < len(channels):
        removed = channels.pop(idx)
        save_json_file(CHANNELS_FILE, channels)
        bot.answer_callback_query(call.id, f"✅ تم حذف {removed['title']}")
        
        channels = load_json_file(CHANNELS_FILE, [])
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, ch in enumerate(channels):
            markup.add(types.InlineKeyboardButton(text=f"❌ {ch['title']}", callback_data=f"delch_{i}"))
        markup.add(types.InlineKeyboardButton(text="🔙 عودة", callback_data="adm_back"))
        bot.edit_message_text("🗑️ اضغط على القناة لحذفها فوراً:", ADMIN_ID, call.message.message_id, reply_markup=markup)

# ==================== معالجة أزرار الـ Callback ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    user_id = call.from_user.id
    username = call.from_user.username or "No Username"
    first_name = call.from_user.first_name or "مستخدم"
    data = call.data

    # --- إدارة لوحة التحكم للأدمن ---
    if data.startswith("adm_") or data.startswith("delch_"):
        if user_id != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        if data == "adm_stats":
            users = load_json_file(USERS_FILE, [])
            reg_offers = load_json_file(REGISTERED_NUMBERS_FILE, [])
            channels = load_json_file(CHANNELS_FILE, [])
            stats_text = f"📊 <b>إحصائيات البوت:</b>\n\n👥 المستخدمين: <b>{len(users)}</b>\n✅ التفعيلات الناجحة: <b>{len(reg_offers)}</b>\n📢 القنوات: <b>{len(channels)}</b>"
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="🔙 عودة", callback_data="adm_back"))
            bot.edit_message_text(stats_text, ADMIN_ID, call.message.message_id, reply_markup=markup)
        elif data == "adm_add":
            msg = bot.send_message(ADMIN_ID, "📥 أرسل رابط القناة المراد إضافتها للاشتراك الإجباري:", protect_content=True)
            bot.register_next_step_handler(msg, process_add_channel)
        elif data == "adm_del":
            channels = load_json_file(CHANNELS_FILE, [])
            if not channels:
                bot.send_message(ADMIN_ID, "❌ لا توجد قنوات حالياً.", protect_content=True)
                return
            markup = types.InlineKeyboardMarkup(row_width=1)
            for idx, ch in enumerate(channels):
                markup.add(types.InlineKeyboardButton(text=f"❌ {ch['title']}", callback_data=f"delch_{idx}"))
            markup.add(types.InlineKeyboardButton(text="🔙 عودة", callback_data="adm_back"))
            bot.edit_message_text("🗑️ اضغط على القناة لحذفها فوراً:", ADMIN_ID, call.message.message_id, reply_markup=markup)
        elif data == "adm_back":
            admin_panel(call.message)
        elif data.startswith("delch_"):
            idx = int(data.replace("delch_", ""))
            process_delete_channel(call, idx)
        return

    # --- معالجة اشتراكات وقائمة المستخدمين العاديين ---
    if data == "check_subscription":
        if check_must_join(user_id):
            bot.answer_callback_query(call.id, "✅ شكراً لك على الاشتراك!")
            bot.delete_message(user_id, call.message.message_id)
            welcome_command(call.message)
        else:
            # تحديث القائمة ديناميكياً لإظهار المتبقي فقط لو ضغط تأكيد ولم يشترك في الباقي
            bot.answer_callback_query(call.id, "❌ لم تشترك في كل القنوات المطلوبة منك بعد!", show_alert=True)
            bot.delete_message(user_id, call.message.message_id)
            send_join_msg(user_id)
        return

    if data == "resend_otp":
        if user_id in user_numbers:
            bot.answer_callback_query(call.id, "🔄 جاري إعادة طلب رمز التحقق...")
            phone_data = user_numbers[user_id]
            if request_otp(phone_data['formatted']):
                bot.edit_message_text("✅ <b>تم إعادة إرسال رمز التحقق بنجاح!</b>\nأدخل الرمز المكون من 6 أرقام الذي تلقيته في رسالة نصية 📱\n\nأدخل الرمز المكون من 6 أرقام:", user_id, call.message.message_id, reply_markup=call.message.reply_markup)
            else:
                bot.send_message(user_id, "❌ فشل إعادة إرسال الرمز حالياً، حاول مجدداً لاحقاً.", protect_content=True)
        else:
            bot.answer_callback_query(call.id, "❌ لم يتم العثور على رقم نشط لإرسال الكود له.", show_alert=True)
        return

    if data == "cancel_otp":
        bot.answer_callback_query(call.id, "❌ تم إلغاء العملية")
        user_numbers.pop(user_id, None)
        pending_otp.pop(user_id, None)
        bot.delete_message(user_id, call.message.message_id)
        welcome_command(call.message)
        return

    # فحص الاشتراك الإجباري ديناميكياً قبل تنفيذ أي أمر آخر
    if not check_must_join(user_id):
        send_join_msg(user_id)
        return

    if data == "logout":
        user_sessions.pop(user_id, None)
        bot.edit_message_text("🔓 تم تسجيل الخروج بنجاح. أرسل رقم هاتف جديد عبر إرسال /start", user_id, call.message.message_id)
        return

    if user_id not in user_sessions:
        bot.answer_callback_query(call.id, "❌ انتهت الجلسة، يرجى إرسال /start من جديد", show_alert=True)
        return

    session = user_sessions[user_id]

    if data == "activate_mgm_flow":
        bot.answer_callback_query(call.id, "🔄 جاري معالجة طلب الدعوات المتقدم...")
        bot.edit_message_text("⏳ <b>جاري بدء عملية تخطي وتوليد مكافأة الدعوات... قد يستغرق الأمر دقيقة، يرجى الانتظار وعدم الضغط على أي زر آخر.</b>", user_id, call.message.message_id)
        
        success = handle_invitations_flow_return(user_id, session['token'], session['phone'])
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="main_menu"))
        if success:
            bot.send_message(user_id, "🎉 <b>مبروك! تم إنهاء فلو الدعوات وتفعيل مكافأة MGM بنجاح 1GB.</b>", reply_markup=markup)
            try:
                proof_msg = f"🎁 <b>عملية هدية دعوات MGM ناجحة!</b>\n\n👤 <b>الحساب:</b> <a href='tg://user?id={user_id}'>{first_name}</a>\n📲 <b>الرقم:</b> <code>{mask_phone(session['display_phone'])}</code>\n🤖 @{bot.get_me().username}"
                bot.send_message(LOGS_CHANNEL_USERNAME, proof_msg, protect_content=True)
            except:
                pass
        else:
            bot.send_message(user_id, "❌ <b>تعذر جلب مكافأة الدعوات حالياً.</b>\n\nتأكد من أن حسابك لم يستنزف الحد الأقصى اليومي المتاح له من شركة جيزي.", reply_markup=markup)

    elif data == "balance":
        bot.answer_callback_query(call.id, "🔄 جاري فحص الرصيد...")
        success, response_msg = get_balance(session['token'], session['phone'])
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="🔙 العودة للقائمة", callback_data="main_menu"))
        bot.edit_message_text(response_msg, user_id, call.message.message_id, reply_markup=markup)

    elif data.startswith("show_"):
        offer_id = data.replace("show_", "")
        offer = ALL_OFFERS.get(offer_id)
        if offer:
            markup = types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton(text="✅ تأكيد التفعيل", callback_data=f"activate_{offer_id}"),
                types.InlineKeyboardButton(text="🔙 إلغاء وعودة", callback_data="main_menu")
            )
            details = f"📋 <b> تفاصيل العرض:</b>\n\n📦 <b>الاسم:</b> {offer['name']}\n💰 <b>السعر:</b> {offer['price']}\n⏳ <b>الصلاحية:</b> {offer['duration']}\n\nهل أنت متأكد؟"
            bot.edit_message_text(details, user_id, call.message.message_id, reply_markup=markup)

    elif data.startswith("activate_"):
        offer_id = data.replace("activate_", "")
        offer = ALL_OFFERS.get(offer_id)
        bot.edit_message_text("🔄 جاري إرسال طلب التفعيل إلى جيزي، انتظر قليلاً...", user_id, call.message.message_id)
        
        success = activate_weekly_gift(session['token'], session['phone']) if offer_id == 'offer_1' else activate_product_offer(session['token'], session['phone'], offer['code'])
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="main_menu"))
        
        if success:
            registered = load_json_file(REGISTERED_NUMBERS_FILE, [])
            registered.append({'user_id': user_id, 'phone': session['display_phone'], 'offer': offer['name'], 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_json_file(REGISTERED_NUMBERS_FILE, registered)
            
            bot.edit_message_text(f"🎉 <b>مبروك! تم تفعيل العرض بنجاح</b>\n\n📱 الرقم: {session['display_phone']}\n📦 العرض: {offer['name']}", user_id, call.message.message_id, reply_markup=markup)
            try:
                proof_msg = f"⚡ <b>عملية تفعيل ناجحة عبر البوت!</b>\n\n👤 <b>المستخدم:</b> <a href='tg://user?id={user_id}'>{first_name}</a>\n📦 <b>العرض المفعل:</b> {offer['name']}\n📲 <b>الرقم:</b> <code>{mask_phone(session['display_phone'])}</code>\n🤖 @{bot.get_me().username}"
                bot.send_message(LOGS_CHANNEL_USERNAME, proof_msg, protect_content=True)
            except:
                pass
        else:
            bot.edit_message_text(f"❌ <b>فشل تفعيل العرض</b>\n\nيرجى التأكد من توفر رصيد كافٍ أو صلاحية العرض لشريحتك.", user_id, call.message.message_id, reply_markup=markup)

    elif data == "main_menu":
        bot.delete_message(user_id, call.message.message_id)
        show_main_menu(user_id, session['display_phone'])

# ==================== معالجة النصوص والـ OTP ====================
@bot.message_handler(func=lambda msg: True)
def handle_text_inputs(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    text = message.text.strip()
    
    if not check_must_join(user_id):
        send_join_msg(user_id)
        return

    if user_id in user_numbers and user_id in pending_otp:
        if text.isdigit() and len(text) == 6:
            msg_wait = bot.send_message(user_id, "🔄 جاري التحقق من الرمز وتوليد الجلسة...", protect_content=True)
            phone_data = user_numbers[user_id]
            token = login_with_otp(phone_data['formatted'], text)
            
            if token:
                user_sessions[user_id] = {'phone': phone_data['formatted'], 'display_phone': phone_data['display'], 'token': token}
                user_numbers.pop(user_id, None)
                pending_otp.pop(user_id, None)
                bot.delete_message(user_id, msg_wait.message_id)
                bot.send_message(user_id, "✅ تم تسجيل الدخول بنجاح!", protect_content=True)
                show_main_menu(user_id, user_sessions[user_id]['display_phone'])
            else:
                bot.delete_message(user_id, msg_wait.message_id)
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton(text="🔄 إعادة إرسال الرمز", callback_data="resend_otp"),
                    types.InlineKeyboardButton(text="❌ إلغاء وعودة", callback_data="cancel_otp")
                )
                bot.send_message(user_id, "❌ <b>الرمز الذي أدخلته غير صحيح أو انتهت صلاحيته.</b>\n\nأعد المحاولة بدقة أو اختر إجراءً من الأسفل:", reply_markup=markup, protect_content=True)
        else:
            bot.send_message(user_id, "⚠️ يرجى إدخال رمز التحقق المتكون من 6 أرقام فقط:", protect_content=True)
        return

    if text.startswith("07") and len(text) == 10 and text.isdigit():
        formatted = format_num(text)
        display_p = format_phone(text)
        user_numbers[user_id] = {'original': text, 'formatted': formatted, 'display': display_p}
        pending_otp[user_id] = formatted
        
        msg_send = bot.send_message(user_id, "🔄 جاري طلب الرمز من سيرفرات جيزي...", protect_content=True)
        if request_otp(formatted):
            bot.delete_message(user_id, msg_send.message_id)
            
            otp_markup = types.InlineKeyboardMarkup(row_width=2)
            otp_markup.add(
                types.InlineKeyboardButton(text="🔄 إعادة إرسال الرمز", callback_data="resend_otp"),
                types.InlineKeyboardButton(text="❌ إلغاء العملية", callback_data="cancel_otp")
            )
            
            bot.send_message(user_id, "✅ <b>تم إرسال رمز التحقق بنجاح!</b> ✅\nأدخل الرمز المكون من 6 أرقام الذي تلقيته في رسالة نصية 📱\n\nأدخل الرمز المكون من 6 أرقام:", reply_markup=otp_markup, protect_content=True)
        else:
            bot.delete_message(user_id, msg_send.message_id)
            bot.send_message(user_id, "❌ فشل إرسال الرمز للرقم المذكور. تأكد من صحة الشبكة وأعد المحاولة.", protect_content=True)
            user_numbers.pop(user_id, None)
            pending_otp.pop(user_id, None)
    elif (text.startswith("05") or text.startswith("06")) and len(text) == 10:
        bot.send_message(user_id, "⚠️ عذراً، هذا البوت يدعم أرقام جيزي فقط (07XXXXXXXX).", protect_content=True)
    else:
        if user_id not in user_sessions:
            bot.send_message(user_id, "⚠️ صيغة الرقم غير صحيحة، يرجى إرسال رقم يبدأ بـ 07 ويتكون من 10 أرقام.", protect_content=True)

# ==================== تشغيل البوت التلقائي ====================
if __name__ == '__main__':
    print("==========================================")
    print(f"🤖 Bot {BOT_NAME} with Dynamic Channels is active...")
    print("==========================================")
    try:
        bot.delete_webhook()
    except:
        pass
    bot.infinity_polling()
