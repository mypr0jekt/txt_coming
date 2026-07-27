# Broadcast Bot

Bir nechta guruhga bir vaqtda matn yuboradigan Telegram bot.

## O'rnatish

```bash
pip install -r requirements.txt
```

## Ishga tushirish

Environment variable orqali token va bosh admin ID ni bering:

```bash
export BOT_TOKEN="123456:ABC-your-bot-token"
export OWNER_ID="123456789"   # sizning Telegram ID raqamingiz
python bot.py
```

ID raqamingizni bilish uchun Telegram'da @userinfobot ga /start bosing.

## Qanday ishlaydi

1. Botni istalgan guruhga **oddiy a'zo sifatida** qo'shing — admin qilish shart emas
   (faqat guruhda "faqat adminlar yoza oladi" cheklovi bo'lsa, admin qilish kerak bo'ladi).
2. Bot guruhga qo'shilganda avtomatik ravishda o'sha guruhni ro'yxatiga saqlab oladi.
3. Botga shaxsiy (private) chatda `/start` yozing — sizga menyu chiqadi.
4. **📢 Xabar yuborish** — matn yozasiz, tasdiqlaysiz, barcha guruhlarga yuboriladi.
5. **➕ Admin qo'shish** — do'stingizning Telegram ID sini yuborsangiz, u ham botdan
   foydalana oladigan (guruhlarga xabar yubora oladigan) admin bo'ladi.
6. **➖ Admin o'chirish** — kerak bo'lmagan adminni ID orqali o'chirasiz.
7. **📋 Guruhlar ro'yxati** — bot qo'shilgan barcha guruhlarni ko'rsatadi.

## Eslatma

- Bot faqat o'zi a'zo bo'lgan guruhlarga xabar yubora oladi.
- Guruhdan chiqarilsa, avtomatik ravishda ro'yxatdan o'chib ketadi.
- Ma'lumotlar `bot.db` (SQLite) faylida saqlanadi — serverni qayta ishga tushirsangiz ham
  guruhlar va adminlar ro'yxati saqlanib qoladi.
