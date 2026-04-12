# ☕ D&S Coffee and Sweet — Bot O'rnatish

## Loyiha tuzilmasi
```
ds-coffee/
├── mini-app/
│   ├── index.html     ← Mini App (Vercelga yuklanadi)
│   └── vercel.json
└── bot/
    ├── bot.py         ← Telegram Bot
    ├── config.py      ← Sozlamalar (TOKEN va boshqalar)
    ├── requirements.txt
    └── railway.toml
```

---

## 1-qadam: Telegram Bot yaratish

1. [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting: `D&S Coffee`
4. Username kiriting: `ds_coffee_sweet_bot`
5. **BOT_TOKEN** ni oling va `config.py` ga qo'ying

---

## 2-qadam: JSONBin.io sozlash (mahsulotlar DB)

1. [jsonbin.io](https://jsonbin.io) ga kiring
2. Ro'yxatdan o'ting (bepul)
3. **New Bin** yarating, ichiga: `{"products": []}` qo'ying
4. Bin ID va Master Key ni `config.py` ga qo'ying

---

## 3-qadam: Mini Appni Vercelga yuklash

1. [vercel.com](https://vercel.com) ga kiring (GitHub bilan)
2. **Add New Project** → `mini-app` papkasini yuklang
3. Deploy tugmasini bosing
4. Berilgan URL ni (`https://xxx.vercel.app`) `config.py` → `MINI_APP_URL` ga qo'ying

---

## 4-qadam: Botni Railwayga yuklash

1. [railway.app](https://railway.app) ga kiring (GitHub bilan)
2. **New Project** → `bot` papkasini yuklang
3. Environment Variables qo'shing:
   ```
   BOT_TOKEN    = sizning_token
   ADMIN_ID     = sizning_telegram_id
   MINI_APP_URL = https://sizning-app.vercel.app
   JSONBIN_ID   = sizning_jsonbin_id
   JSONBIN_KEY  = sizning_jsonbin_key
   ```
4. Deploy!

---

## 5-qadam: Mini App URL ni Botga ulash

Botni deploy qilgandan keyin `/start` yuboring — 
Mini App tugmasi avtomatik paydo bo'ladi.

---

## Admin buyruqlari

| Buyruq | Vazifasi |
|--------|---------|
| `/admin` | Admin panel |
| `/start` | Botni qayta ishga tushirish |
| `/help` | Yordam |

### Admin paneldan:
- ➕ **Mahsulot qo'shish** — nom, narx, kategoriya, tavsif, rasm URL
- ✏️ **Tahrirlash** — mavjud mahsulotni o'zgartirish
- 🗑 **O'chirish** — mahsulotni o'chirish

### Buyurtma holatlari:
- ✅ Qabul → mijozga xabar ketadi
- 👨‍🍳 Tayyorlanmoqda → mijozga xabar
- 🎉 Tayyor → mijozga xabar
- ❌ Bekor → mijozga xabar

---

## Mahsulot rasmlari haqida

Rasmlar uchun bepul manbalar:
- **Unsplash**: `https://images.unsplash.com/photo-ID?w=400&q=80`
- **Pexels**: `https://images.pexels.com/...`
- O'z rasmlaringizni **Imgur**, **Cloudinary** yoki **Telegra.ph** ga yuklab URL olishingiz mumkin

### Telegra.ph orqali rasm yuklash:
1. [telegra.ph](https://telegra.ph) ga kiring
2. Post yarating, rasm yuklang
3. Rasmning to'g'ridan-to'g'ri URL ini oling

---

## Muammo bo'lsa

Telegram: @ds_coffee_sweet
