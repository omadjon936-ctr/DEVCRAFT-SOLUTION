import os
import json
import html
import telebot
from telebot import types

# ==========================================
# ⚙️ SOZLAMALAR VA XAVFSIZLIK
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "9061254691:AAFIqZCo_QzCVq9pX-5oPiv53MF-febAMf0")
ADMIN_ID = int(os.getenv("ADMIN_ID", 8958237379))
DB_FILE = "orders_db.json"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
user_data = {}

SERVICES = [
    "🌐 Web-Sayt Yaratish",
    "🤖 Python va Botlar",
    "🎓 Kurs Ishlari",
    "📚 Mustaqil Ish va Referat",
    "📄 Word va Excel Hujjat",
    "📊 Slayd va Taqdimot",
    "🥽 360° VR va Simulyatsiya",
    "💻 Amaliy va Lab. Ishlar",
]

DEADLINES = [
    "🔥 Shoshilinch (Tez)",
    "⏳ 2-3 kun ichida",
    "📅 1 hafta ichida",
]

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"order_count": 0, "orders": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def format_phone_for_url(phone_str):
    """Telefon raqamni 998XXXXXXXXX formatiga moslash"""
    digits = "".join(filter(str.isdigit, str(phone_str)))
    if len(digits) == 9:
        digits = "998" + digits
    return digits if len(digits) >= 9 else ""

def setup_bot_info():
    try:
        description_text = (
            "💻 DevCraft Solutions — Dasturlash va talabalar uchun elektron hujjatlar xizmati!\n\n"
            "🛠 Bizning xizmatlar:\n"
            "• 🌐 Web-sayt va Telegram botlar yaratish\n"
            "• 🎓 Kurs ishi, Mustaqil ish va Referatlar\n"
            "• 📄 Word, Excel va kreativ Slaydlar\n"
            "• 🥽 360° VR sayohat va laboratoriya ishlari\n\n"
            "💰 Hamyonbop narxlar — talabalar uchun qulay!\n"
            "👇 Boshlash uchun «START» tugmasini bosing!"
        )
        bot.set_my_description(description_text)
    except Exception as e:
        print(f"Tavsifni yangilashda xato: {e}")

    try:
        short_desc = (
            "💻 DevCraft Solutions — Dasturlash va talabalar uchun elektron hujjatlar xizmati. "
            "Admin: @Omadjon121"
        )
        bot.set_my_short_description(short_desc)
    except Exception as e:
        print(f"Qisqa tavsifni yangilashda xato: {e}")

    try:
        bot.set_my_commands([
            types.BotCommand("start", "🔄 Botni ishga tushirish / Asosiy menyu"),
            types.BotCommand("admin", "👨‍💻 Admin panel (Faqat admin uchun)")
        ])
    except Exception as e:
        print(f"Buyruqlarni yangilashda xato: {e}")

def main_menu(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🚀 Buyurtma berish")
    btn2 = types.KeyboardButton("🧮 Narxni hisoblash")
    btn3 = types.KeyboardButton("💼 Xizmatlar va Portfolio")
    btn4 = types.KeyboardButton("📞 Bog'lanish")
    markup.add(btn1, btn2, btn3, btn4)

    # To'g'rilandi: user_id to'g'ridan-to'g'ri ADMIN_ID bilan solishtirilmoqda
    if user_id and int(user_id) == ADMIN_ID:
        markup.row(types.KeyboardButton("👨‍💻 Admin Panel"))
    return markup

def check_cancel_or_start(message):
    if not message.text:
        return False
    if message.text == "/start":
        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_data.pop(message.chat.id, None)
        send_welcome(message)
        return True
    if message.text == "🔙 Bekor qilish":
        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_data.pop(message.chat.id, None)
        bot.send_message(message.chat.id, "🏠 Asosiy menyu:", reply_markup=main_menu(message.from_user.id))
        return True
    return False

def build_order_card(order_id, order_info, include_actions=True):
    client_id = order_info.get("client_id")
    safe_name = html.escape(str(order_info.get("name", "Mijoz")))
    username = html.escape(str(order_info.get("username", "Mavjud emas")))
    safe_service = html.escape(str(order_info.get("service", "")))
    safe_deadline = html.escape(str(order_info.get("deadline", "")))
    safe_details = html.escape(str(order_info.get("details", "")))
    phone = str(order_info.get("phone", ""))
    clean_phone = phone.lstrip("+")
    url_phone = format_phone_for_url(phone)

    text = (
        f"🚨 <b>BUYURTMA #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>"
        f"👤 <b>Mijoz:</b> {safe_name} ({username})\n"
        f"🛠 <b>Xizmat:</b> {safe_service}\n"
        f"⏰ <b>Muddat:</b> {safe_deadline}\n"
        f"📞 <b>Telefon:</b> <code>+{clean_phone}</code>"
        f"</blockquote>\n"
        f"📝 <b>Buyurtma tavsifi:</b>\n"
        f"<blockquote>{safe_details}</blockquote>"
    )

    kb = types.InlineKeyboardMarkup(row_width=2)
    btn_user = types.InlineKeyboardButton(f"👤 {order_info.get('name', 'Mijoz')}", callback_data="info_only")
    btn_phone = types.InlineKeyboardButton(f"📞 +{clean_phone}", callback_data="info_only")
    btn_serv = types.InlineKeyboardButton(f"{order_info.get('service', '')}", callback_data="info_only")
    btn_time = types.InlineKeyboardButton(f"{order_info.get('deadline', '')}", callback_data="info_only")
    kb.add(btn_user, btn_phone)
    kb.add(btn_serv, btn_time)

    if include_actions and order_info.get("status") == "kutilmoqda":
        btn_accept = types.InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_{client_id}_{order_id}")
        btn_reject = types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{client_id}_{order_id}")
        kb.add(btn_accept, btn_reject)
    else:
        status_map = {
            "qabul_qilindi": "✅ HOLATI: QABUL QILINDI",
            "rad_etildi": "❌ HOLATI: RAD ETILDI",
            "kutilmoqda": "⏳ HOLATI: KUTILMOQDA"
        }
        status_text = status_map.get(order_info.get("status"), "⏳ HOLATI: KUTILMOQDA")
        kb.row(types.InlineKeyboardButton(status_text, callback_data="info_only"))

    raw_uname = str(order_info.get("username", ""))
    if raw_uname.startswith("@"):
        chat_url = f"https://t.me/{raw_uname[1:]}"
    else:
        chat_url = f"tg://user?id={client_id}"

    kb.row(types.InlineKeyboardButton("💬 Mijozga yozish (Lichka)", url=chat_url))
    return text, kb, url_phone

# ==========================================
# 👨‍💻 ADMIN PANEL FUNKSIYALARI
# ==========================================
def get_admin_dashboard():
    db = load_db()
    orders = db.get("orders", {})

    total = len(orders)
    pending = sum(1 for o in orders.values() if o.get("status") == "kutilmoqda")
    accepted = sum(1 for o in orders.values() if o.get("status") == "qabul_qilindi")
    rejected = sum(1 for o in orders.values() if o.get("status") == "rad_etildi")

    text = (
        "👨‍💻 <b>DEVCRAFT SOLUTIONS — ADMIN PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Umumiy statistika:</b>\n"
        f"• 📦 Jami buyurtmalar: <b>{total} ta</b>\n"
        f"• ⏳ Kutilayotganlar: <b>{pending} ta</b>\n"
        f"• ✅ Qabul qilinganlar: <b>{accepted} ta</b>\n"
        f"• ❌ Rad etilganlar: <b>{rejected} ta</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Kerakli amalni tanlang:"
    )

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(f"⏳ Kutilayotgan buyurtmalar ({pending} ta)", callback_data="admin_pending"),
        types.InlineKeyboardButton("📋 Oxirgi 5 ta buyurtma", callback_data="admin_last5"),
        types.InlineKeyboardButton("📥 Bazani yuklab olish (JSON)", callback_data="admin_export"),
        types.InlineKeyboardButton("🔄 Statistikani yangilash", callback_data="admin_refresh"),
    )
    return text, kb

@bot.message_handler(commands=["admin"])
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin Panel")
def open_admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Kechirasiz, bu bo'lim faqat bot administratori uchun!")
        return

    text, kb = get_admin_dashboard()
    bot.send_message(message.chat.id, text, reply_markup=kb)

# ==========================================
# 🚀 ASOSIY BOT HANDLERLARI
# ==========================================
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user_data.pop(message.chat.id, None)
    safe_name = html.escape(message.from_user.first_name or "Mijoz")
    welcome_text = (
        f"👋 Assalomu alaykum, <b>{safe_name}</b>!\n\n"
        f"💻 <b>DevCraft Solutions</b> — IT loyihalar va o'quv ishlari markazining rasmiy botiga xush kelibsiz!\n\n"
        f"👇 Marhamat, kerakli bo'limni tanlang:"
    )
    # To'g'rilandi: message.chat.id o'rniga message.from_user.id uzatildi
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "🚀 Buyurtma berish")
def start_order(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*SERVICES, "🔙 Bekor qilish")
    msg = bot.send_message(
        message.chat.id,
        "🛠 <b>1-qadam:</b> Qaysi xizmat turidan foydalanmoqchisiz?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_service_type)

def get_service_type(message):
    if check_cancel_or_start(message):
        return

    if not message.text or message.text not in SERVICES:
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Iltimos, pastdagi tugmalardan birini tanlang yoki «🔙 Bekor qilish» tugmasini bosing:"
        )
        bot.register_next_step_handler(msg, get_service_type)
        return

    user_data[message.chat.id] = {"service": message.text}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 Bekor qilish")

    msg = bot.send_message(
        message.chat.id,
        "📝 <b>2-qadam:</b> Ishning mavzusi yoki texnik topshiriq haqida batafsil yozing:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_task_details)

def get_task_details(message):
    if check_cancel_or_start(message):
        return

    if not message.text or message.text.startswith("/"):
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Iltimos, buyurtma tavsifini matn ko'rinishida yozing:"
        )
        bot.register_next_step_handler(msg, get_task_details)
        return

    user_data.setdefault(message.chat.id, {})["details"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*DEADLINES, "🔙 Bekor qilish")

    msg = bot.send_message(
        message.chat.id,
        "⏰ <b>3-qadam:</b> Buyurtma qachonga tayyor bo'lishi kerak?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_deadline)

def get_deadline(message):
    if check_cancel_or_start(message):
        return

    if not message.text or message.text.startswith("/"):
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Iltimos, muddatni tugmalardan tanlang yoki yozing:"
        )
        bot.register_next_step_handler(msg, get_deadline)
        return

    user_data.setdefault(message.chat.id, {})["deadline"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    markup.add(contact_btn)
    markup.add("🔙 Bekor qilish")

    msg = bot.send_message(
        message.chat.id,
        "📞 <b>Oxirgi qadam:</b> Siz bilan bog'lanishimiz uchun pastdagi tugmani bosib raqamingizni yuboring yoki yozib qoldiring:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, finish_order)

def finish_order(message):
    if check_cancel_or_start(message):
        return

    raw_phone = message.contact.phone_number if message.contact else (message.text or "")
    url_phone = format_phone_for_url(raw_phone)

    if not url_phone:
        msg = bot.send_message(
            message.chat.id,
            "⚠️ Telefon raqam noto'g'ri kiritildi! Iltimos, «📱 Telefon raqamni yuborish» tugmasini bosing yoki raqamingizni to'g'ri yozing (masalan: 901234567):"
        )
        bot.register_next_step_handler(msg, finish_order)
        return

    formatted_phone = f"+{url_phone}"
    data = user_data.pop(message.chat.id, {})

    db = load_db()
    db["order_count"] += 1
    current_order_id = str(db["order_count"])

    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    order_info = {
        "client_id": message.chat.id,
        "name": message.from_user.first_name,
        "username": username,
        "service": data.get("service", "Noma'lum"),
        "details": data.get("details", "Kiritilmagan"),
        "deadline": data.get("deadline", "Kiritilmagan"),
        "phone": formatted_phone,
        "status": "kutilmoqda"
    }
    db["orders"][current_order_id] = order_info
    save_db(db)

    bot.send_message(
        message.chat.id,
        f"✅ <b>Buyurtmangiz #{current_order_id}-raqam bilan qabul qilindi!</b>\n\n"
        f"👨‍💻 <b>DevCraft Solutions</b> mutaxassisi buyurtmangizni ko'rib chiqib, tez orada siz bilan bog'lanadi!",
        reply_markup=main_menu(message.from_user.id),
    )

    admin_text, admin_kb, backup_phone = build_order_card(current_order_id, order_info, include_actions=True)

    try:
        bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_kb)
    except Exception:
        try:
            admin_kb.keyboard[-1] = [types.InlineKeyboardButton("💬 Mijozga yozish (Lichka)", url=f"https://t.me/+{backup_phone}")]
            bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_kb)
        except Exception as e:
            print(f"Adminga yuborishda xato: {e}")

@bot.message_handler(func=lambda m: m.text == "🧮 Narxni hisoblash")
def price_calculator(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🌐 Web-sayt / Dasturlash", callback_data="calc_dev"),
        types.InlineKeyboardButton("🎓 Kurs ishi", callback_data="calc_kurs"),
        types.InlineKeyboardButton("📚 Mustaqil ish / Referat", callback_data="calc_mustaqil"),
        types.InlineKeyboardButton("📄 Word / Excel hujjat", callback_data="calc_word"),
        types.InlineKeyboardButton("📊 Slayd va Taqdimot", callback_data="calc_slayd"),
    )
    bot.send_message(
        message.chat.id,
        "🧮 <b>Avto-Narx Kalkulyatori</b>\nTaxminiy narxni bilish uchun xizmat turini tanlang (Narxini o'zaro kelishamiz):",
        reply_markup=kb,
    )

@bot.message_handler(func=lambda m: m.text == "💼 Xizmatlar va Portfolio")
def show_portfolio(message):
    text = (
        "💎 <b>DEVCRAFT SOLUTIONS XIZMATLARI:</b>\n\n"
        "🔹 <b>Dasturlash:</b> HTML, CSS web-saytlar, Python botlar, 360° VR sayohat va simulyatsiyalar.\n"
        "🔹 <b>O'quv ishlari:</b> Kurs ishi, Mustaqil ish, Referat va amaliyot hisobotlari.\n"
        "🔹 <b>Hujjatlar:</b> Word va Excel'da murakkab jadvallar, matn terish.\n"
        "🔹 <b>Taqdimot:</b> Kreativ PowerPoint va Canva slaydlar."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📞 Bog'lanish")
def show_contacts(message):
    text = (
        "📞 <b>BIZ BILAN ALOQA:</b>\n\n"
        "🏢 <b>Brend:</b> DevCraft Solutions\n"
        "📲 <b>Telefon:</b> +998 50 716 71 74\n"
        "💬 <b>Telegram:</b> @Omadjon121\n"
        "🤖 <b>Bot:</b> @devcraft_solutions_bot\n"
        "📧 <b>Email:</b> Omadjon936@gmail.com"
    )
    bot.send_message(message.chat.id, text)

# ==========================================
# 🔘 CALLBACK (INLINE TUGMALAR) BOSHQARUVI
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data

    if data == "info_only":
        bot.answer_callback_query(call.id, "📋 Buyurtma ma'lumoti")
        return

    if data.startswith("admin_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⛔ Faqat admin uchun!", show_alert=True)
            return

        if data == "admin_refresh":
            text, kb = get_admin_dashboard()
            try:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
            except Exception:
                pass
            bot.answer_callback_query(call.id, "✅ Statistika yangilandi!")

        elif data == "admin_pending":
            db = load_db()
            orders = db.get("orders", {})
            pending_orders = [(oid, o) for oid, o in orders.items() if o.get("status") == "kutilmoqda"]

            if not pending_orders:
                bot.answer_callback_query(call.id, "🎉 Hozircha kutilayotgan buyurtmalar yo'q!", show_alert=True)
                return

            bot.answer_callback_query(call.id, f"⏳ {len(pending_orders)} ta buyurtma yuklanmoqda...")
            for oid, oinfo in pending_orders:
                card_text, card_kb, backup_phone = build_order_card(oid, oinfo, include_actions=True)
                try:
                    bot.send_message(ADMIN_ID, card_text, reply_markup=card_kb)
                except Exception:
                    card_kb.keyboard[-1] = [types.InlineKeyboardButton("💬 Mijozga yozish (Lichka)", url=f"https://t.me/+{backup_phone}")]
                    bot.send_message(ADMIN_ID, card_text, reply_markup=card_kb)

        elif data == "admin_last5":
            db = load_db()
            orders = db.get("orders", {})
            if not orders:
                bot.answer_callback_query(call.id, "📭 Bazada buyurtmalar yo'q!", show_alert=True)
                return

            sorted_ids = sorted(orders.keys(), key=lambda x: int(x) if str(x).isdigit() else 0, reverse=True)[:5]
            status_icons = {"qabul_qilindi": "✅", "rad_etildi": "❌", "kutilmoqda": "⏳"}

            lines = ["📋 <b>OXIRGI 5 TA BUYURTMA:</b>\n━━━━━━━━━━━━━━━━━━━━"]
            for oid in sorted_ids:
                o = orders[oid]
                icon = status_icons.get(o.get("status"), "⏳")
                safe_name = html.escape(str(o.get("name", "Mijoz")))
                safe_serv = html.escape(str(o.get("service", "")))
                safe_det = html.escape(str(o.get("details", "")))
                lines.append(
                    f"<b>#{oid}</b> | {icon} <b>{safe_serv}</b>\n"
                    f"👤 {safe_name} | 📞 <code>{o.get('phone', '')}</code>\n"
                    f"📝 <i>{safe_det}</i>\n"
                )

            bot.answer_callback_query(call.id)
            bot.send_message(ADMIN_ID, "\n".join(lines))

        elif data == "admin_export":
            if os.path.exists(DB_FILE):
                bot.answer_callback_query(call.id, "📥 Baza fayli yuborilmoqda...")
                with open(DB_FILE, "rb") as f:
                    bot.send_document(ADMIN_ID, f, caption="📦 <b>orders_db.json</b> — Buyurtmalar bazasining zaxira nusxasi.")
            else:
                bot.answer_callback_query(call.id, "⚠️ Baza fayli hali yaratilmagan!", show_alert=True)
        return

    prices = {
        "calc_dev": "🌐 <b>Web-sayt va Dasturlash:</b>\nKelishilgan holda hamyonbop narxlarda.",
        "calc_kurs": "🎓 <b>Kurs ishi:</b>\nTalabalar uchun qulay narxda kelishamiz.",
        "calc_mustaqil": "📚 <b>Mustaqil ish / Referat:</b>\nTez va hamyonbop narxda.",
        "calc_word": "📄 <b>Word / Excel hujjat:</b>\nSahifasi kelishilgan holda.",
        "calc_slayd": "📊 <b>Slayd va Taqdimot:</b>\nKreativ dizayn va hamyonbop narx.",
    }

    if data in prices:
        bot.answer_callback_query(call.id, "Ma'lumot berildi!")
        bot.send_message(
            call.message.chat.id,
            f"{prices[data]}\n\n👉 <i>Aniq buyurtma berish uchun «🚀 Buyurtma berish» tugmasini bosing!</i>",
        )

    elif data.startswith("accept_") or data.startswith("reject_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "⛔ Faqat admin uchun!", show_alert=True)
            return

        parts = data.split("_")
        action, client_id, ord_num = parts[0], int(parts[1]), parts[2]

        db = load_db()
        if str(ord_num) in db["orders"]:
            db["orders"][str(ord_num)]["status"] = "qabul_qilindi" if action == "accept" else "rad_etildi"
            save_db(db)
        order_info = db["orders"].get(str(ord_num), {})

        try:
            if action == "accept":
                bot.send_message(
                    client_id,
                    f"🎉 <b>Xushxabar!</b> Sizning <b>#{ord_num}</b>-sonli buyurtmangiz <b>DevCraft Solutions</b> tomonidan rasman <b>QABUL QILINDI!</b>\nTez orada siz bilan bog'lanamiz.",
                )
            else:
                bot.send_message(
                    client_id,
                    f"⚠️ Kechirasiz, <b>#{ord_num}</b>-sonli buyurtmangiz hozirgi bandlik sababli rad etildi.",
                )
        except Exception as e:
            print(f"Mijozga xabar yuborishda xatolik: {e}")

        _, updated_kb, backup_phone = build_order_card(ord_num, order_info, include_actions=False)

        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=updated_kb
            )
        except Exception:
            updated_kb.keyboard[-1] = [types.InlineKeyboardButton("💬 Mijozga yozish (Lichka)", url=f"https://t.me/+{backup_phone}")]
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=updated_kb
            )

        bot.answer_callback_query(call.id, "Holat yangilandi va mijozga xabar yuborildi!")

if __name__ == "__main__":
    setup_bot_info()
    print("✅ DevCraft Solutions boti xatosiz ishga tushdi va buyurtmalarni kutmoqda...")
    bot.infinity_polling(skip_pending=True)