"""
D&S Coffee and Sweet — Telegram Bot
Arxitektura: sample botdan o'rganilgan (JSONBin + ConversationHandler)
Ishga tushirish: python bot.py
"""

import json
import logging
import httpx
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from config import BOT_TOKEN, ADMIN_ID, MINI_APP_URL, JSONBIN_ID, JSONBIN_KEY

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ── Conversation states ──
ADD_NAME, ADD_PRICE, ADD_CAT, ADD_DESC, ADD_IMG, EDIT_FIELD, EDIT_VALUE = range(7)

# ── JSONBin ──
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"
HEADERS = {"X-Master-Key": JSONBIN_KEY, "Content-Type": "application/json"}

async def get_products():
    async with httpx.AsyncClient() as c:
        r = await c.get(JSONBIN_URL, headers={"X-Master-Key": JSONBIN_KEY})
        return r.json().get("record", {}).get("products", [])

async def save_products(products):
    async with httpx.AsyncClient() as c:
        await c.put(JSONBIN_URL, headers=HEADERS, json={"products": products})

# ── /start ──
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kb = [[InlineKeyboardButton("☕ D&S Coffee — Buyurtma berish", web_app=WebAppInfo(url=MINI_APP_URL))]]
    await update.message.reply_text(
        f"☕ *Assalomu alaykum, {user.first_name}!*\n\n"
        "🏪 *D&S Coffee and Sweet*ga xush kelibsiz!\n\n"
        "Bizda nima bor:\n"
        "• ☕ Espresso, Latte, Cappuccino, Maxito va boshqalar\n"
        "• 🍰 Cheesecake, Tiramisu, Brownie, Makaron...\n"
        "• 🍽️ Lag'mon, Manty, Kabob, Shurva va milliy taomlar\n\n"
        "👇 Tugmani bosib buyurtma bering!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    await ctx.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp(text="☕ Menu", web_app=WebAppInfo(url=MINI_APP_URL))
    )

# ── /help ──
async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Yordam*\n\n"
        "• 🛒 Buyurtma → /start tugmasi yoki pastdagi *Menu* tugmasi\n"
        "• 📞 Muammo: @ds\\_coffee\\_sweet\n"
        "• 📍 Manzil: Toshkent, Chilonzor\n"
        "• 🕐 Ish vaqti: 08:00—23:00",
        parse_mode="Markdown"
    )

# ── Buyurtma qabul qilish (WebApp dan) ──
async def handle_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception as e:
        logging.error(f"WebApp data xatosi: {e}")
        return

    user  = update.effective_user
    items = data.get("items", {})
    total = data.get("total", 0)
    name  = data.get("name", "—")
    phone = data.get("phone", "—")
    addr  = data.get("addr", "—")
    note  = data.get("note", "")

    items_text = "\n".join(
        f"  • {v['em']} {v['name']} x{v['qty']} = {v['price']*v['qty']:,.0f} so'm"
        for v in items.values()
    )

    # Foydalanuvchiga tasdiq
    await update.message.reply_text(
        f"✅ *Buyurtmangiz qabul qilindi!*\n\n"
        f"👤 {name}\n📞 {phone}\n🏠 {addr}\n"
        f"{('💬 '+note+chr(10)) if note else ''}\n"
        f"🛒 *Mahsulotlar:*\n{items_text}\n\n"
        f"💰 *Jami: {total:,.0f} so'm*\n\n"
        f"☕ Tez orada tayyorlab beramiz!",
        parse_mode="Markdown"
    )

    # Adminga xabar
    admin_msg = (
        f"🔔 *YANGI BUYURTMA!*\n\n"
        f"👤 {name} (@{user.username or '—'})\n"
        f"📞 {phone}\n🏠 {addr}\n"
        f"{('💬 '+note+chr(10)) if note else ''}\n"
        f"🛒 *Mahsulotlar:*\n{items_text}\n\n"
        f"💰 *Jami: {total:,.0f} so'm*"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Qabul",         callback_data=f"st_{user.id}_accepted"),
         InlineKeyboardButton("👨‍🍳 Tayyorlanmoqda", callback_data=f"st_{user.id}_cooking")],
        [InlineKeyboardButton("🎉 Tayyor!",       callback_data=f"st_{user.id}_done"),
         InlineKeyboardButton("❌ Bekor",         callback_data=f"st_{user.id}_cancelled")],
    ])
    try:
        await ctx.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logging.error(f"Admin xabari yuborilmadi: {e}")

# ── Status callback (admin tugmalari) ──
async def status_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID:
        return

    _, uid, status = q.data.split("_", 2)
    labels = {
        "accepted":  "✅ Buyurtmangiz qabul qilindi! Tayyorlanmoqda ☕",
        "cooking":   "👨‍🍳 Buyurtmangiz tayyorlanmoqda, biroz kuting...",
        "done":      "🎉 Buyurtmangiz tayyor! Marhamat oling 🍽️",
        "cancelled": "❌ Buyurtmangiz bekor qilindi. Muammo uchun @ds_coffee_sweet ga yozing."
    }
    msg = labels.get(status, "")
    if msg:
        try:
            await ctx.bot.send_message(int(uid), msg)
        except Exception as e:
            logging.warning(f"Mijozga xabar yuborilmadi: {e}")
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text(f"Holat yangilandi: {status}")

# ── /admin panel ──
async def admin_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="adm_add")],
        [InlineKeyboardButton("📋 Mahsulotlar ro'yxati", callback_data="adm_list")],
        [InlineKeyboardButton("☕ Mini Appni ochish", web_app=WebAppInfo(url=MINI_APP_URL))],
    ])
    await update.message.reply_text(
        "👨‍💼 *D&S Coffee — Admin Panel*",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ── Admin callbacks ──
async def adm_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID:
        return

    if q.data == "adm_add":
        await q.edit_message_text("📝 Mahsulot nomini kiriting:\n\n/cancel — bekor qilish")
        return ADD_NAME

    elif q.data == "adm_list":
        products = await get_products()
        if not products:
            await q.edit_message_text("Hozircha mahsulotlar yo'q.")
            return
        txt = "📋 *Mahsulotlar:*\n\n"
        kb = []
        for p in products:
            txt += f"{p.get('em','🍽')} *{p['name']}* — {p['price']:,.0f} so'm ({p['cat']})\n"
            kb.append([
                InlineKeyboardButton(f"✏️ {p['name']}", callback_data=f"edit_{p['id']}"),
                InlineKeyboardButton("🗑", callback_data=f"del_{p['id']}")
            ])
        kb.append([InlineKeyboardButton("➕ Yangi qo'shish", callback_data="adm_add")])
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("del_"):
        pid = int(q.data.replace("del_", ""))
        products = await get_products()
        products = [p for p in products if p["id"] != pid]
        await save_products(products)
        await q.edit_message_text(
            "✅ Mahsulot o'chirildi!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Ro'yxat", callback_data="adm_list")]])
        )

    elif q.data.startswith("edit_"):
        pid = int(q.data.replace("edit_", ""))
        ctx.user_data["edit_id"] = pid
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Nom",        callback_data="ef_name"),
             InlineKeyboardButton("💰 Narx",       callback_data="ef_price")],
            [InlineKeyboardButton("📂 Kategoriya", callback_data="ef_cat"),
             InlineKeyboardButton("📄 Tavsif",     callback_data="ef_desc")],
            [InlineKeyboardButton("🖼 Rasm URL",   callback_data="ef_img")],
        ])
        await q.edit_message_text("Nimani o'zgartirmoqchisiz?", reply_markup=kb)
        return EDIT_FIELD

    elif q.data.startswith("ef_"):
        field = q.data.replace("ef_", "")
        ctx.user_data["edit_field"] = field
        hints = {
            "name":  "Yangi nomni kiriting:",
            "price": "Yangi narxni kiriting (so'mda, faqat raqam):",
            "cat":   "Yangi kategoriyani kiriting:\nIchimliklar / Shirinliklar / Milliy Taomlar",
            "desc":  "Yangi tavsifni kiriting:",
            "img":   "Rasm URL kiriting (https://...):\n\nRasm yo'q bo'lsa /skip yozing"
        }
        await q.edit_message_text(hints.get(field, "Yangi qiymatni kiriting:"))
        return EDIT_VALUE

# ── Add product conversation ──
async def add_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["pname"] = update.message.text.strip()
    await update.message.reply_text("💰 Narxini kiriting (faqat raqam, so'mda):")
    return ADD_PRICE

async def add_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        ctx.user_data["pprice"] = float(update.message.text.replace(" ", "").replace(",", ""))
    except:
        await update.message.reply_text("❌ Xato! Faqat raqam kiriting:"); return ADD_PRICE
    kb = [[InlineKeyboardButton(c, callback_data=f"cat_{c}")] for c in ["Ichimliklar", "Shirinliklar", "Milliy Taomlar"]]
    await update.message.reply_text("📂 Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(kb))
    return ADD_CAT

async def add_cat_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    cat_em = {"Ichimliklar": "☕", "Shirinliklar": "🍰", "Milliy Taomlar": "🍽️"}
    cat = q.data.replace("cat_", "")
    ctx.user_data["pcat"] = cat
    ctx.user_data["pem"]  = cat_em.get(cat, "🍽️")
    await q.edit_message_text("📝 Qisqa tavsif kiriting:")
    return ADD_DESC

async def add_desc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["pdesc"] = update.message.text.strip()
    await update.message.reply_text(
        "🖼 Rasm URL kiriting (https://...)\n\n"
        "Unsplash yoki boshqa saytdan rasm URL:\n"
        "Masalan: https://images.unsplash.com/photo-...\n\n"
        "Rasm yo'q bo'lsa /skip yozing"
    )
    return ADD_IMG

async def add_img(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    img_url = None if txt.lower() in ["/skip", "skip"] else txt
    products = await get_products()
    new_id = max([p["id"] for p in products], default=100) + 1
    new_p = {
        "id":    new_id,
        "name":  ctx.user_data["pname"],
        "price": ctx.user_data["pprice"],
        "cat":   ctx.user_data["pcat"],
        "em":    ctx.user_data["pem"],
        "desc":  ctx.user_data["pdesc"],
        "img":   img_url
    }
    products.append(new_p)
    await save_products(products)
    await update.message.reply_text(
        f"✅ *{new_p['name']}* qo'shildi!\n"
        f"💰 {new_p['price']:,.0f} so'm | {new_p['cat']}\n"
        f"{'🖼 Rasm: '+img_url if img_url else '🚫 Rasm yo\'q'}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ── Edit product ──
async def edit_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    val   = update.message.text.strip()
    pid   = ctx.user_data.get("edit_id")
    field = ctx.user_data.get("edit_field")
    products = await get_products()
    for p in products:
        if p["id"] == pid:
            if field == "price":
                try: p["price"] = float(val.replace(" ", "").replace(",", ""))
                except: await update.message.reply_text("❌ Xato narx!"); return EDIT_VALUE
            elif field == "img":
                p["img"] = None if val.lower() in ["/skip","skip"] else val
            else:
                p[field] = val
            break
    await save_products(products)
    await update.message.reply_text("✅ Muvaffaqiyatli yangilandi!")
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END

# ── MAIN ──
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add product conversation
    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_cb, pattern="^adm_add$")],
        states={
            ADD_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price)],
            ADD_CAT:   [CallbackQueryHandler(add_cat_cb, pattern="^cat_")],
            ADD_DESC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_desc)],
            ADD_IMG:   [MessageHandler(filters.TEXT & ~filters.COMMAND, add_img)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Edit product conversation
    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(adm_cb, pattern="^edit_\\d+$")],
        states={
            EDIT_FIELD: [CallbackQueryHandler(adm_cb, pattern="^ef_")],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(add_conv)
    app.add_handler(edit_conv)
    # status_cb AVVAL qo'shilishi kerak — aniq pattern bor
    app.add_handler(CallbackQueryHandler(status_cb, pattern="^st_"))
    app.add_handler(CallbackQueryHandler(adm_cb))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_order))

    print("☕ D&S Coffee Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
