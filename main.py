from telebot import TeleBot, types
from deep_translator import GoogleTranslator
from gtts import gTTS
import random
import os

# Bot tokenini shu yerga yoz
BOT_TOKEN = "8447205700:AAHU9UkAFGScLLyanAe5ZF7MY0PPzyowG-A"
bot = TeleBot(BOT_TOKEN)

# Foydalanuvchi tanlagan yo'nalishlarni saqlash uchun
user_languages = {}

# Statistika uchun
user_stats = {}

# Random reaksiyalar (emoji)
REACTIONS = ["👍", "🔥", "🤩", "👌", "❤️", "🥳"]

# Inline tugmalar yaratamiz
def get_language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # 1-qator (UZ → EN, UZ → RU)
    uz_row = [
        types.InlineKeyboardButton("🇺🇿 Uzbek → 🇬🇧 English", callback_data="uz-en"),
        types.InlineKeyboardButton("🇺🇿 Uzbek → 🇷🇺 Russian", callback_data="uz-ru"),
    ]
    keyboard.row(*uz_row)

    # 2-qator (EN → UZ, EN → RU)
    en_row = [
        types.InlineKeyboardButton("🇬🇧 English → 🇺🇿 Uzbek", callback_data="en-uz"),
        types.InlineKeyboardButton("🇬🇧 English → 🇷🇺 Russian", callback_data="en-ru"),
    ]
    keyboard.row(*en_row)

    # 3-qator (RU → UZ, RU → EN)
    ru_row = [
        types.InlineKeyboardButton("🇷🇺 Russian → 🇺🇿 Uzbek", callback_data="ru-uz"),
        types.InlineKeyboardButton("🇷🇺 Russian → 🇬🇧 English", callback_data="ru-en"),
    ]
    keyboard.row(*ru_row)

    return keyboard


# "Tilni o'zgartirish" tugmasi
def get_change_language_button():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔄 Tilni o‘zgartirish", "📊 Statistikam")
    return keyboard


# /start buyrug'i
@bot.message_handler(commands=["start"])
def start_cmd(message):
    text = "🌐 Tilni tanlang:"
    bot.send_message(message.chat.id, text, reply_markup=get_language_keyboard())


# Inline tugmalarni bosganda
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_languages[call.message.chat.id] = call.data  # Masalan: "uz-en"
    bot.answer_callback_query(call.id, "✅ Til tanlandi!")
    bot.send_message(
        call.message.chat.id,
        "✍️ So‘zni kiriting, men tarjima qilib beraman.\n\n⬇️ Pastdagi tugma orqali tilni o‘zgartirishingiz mumkin.",
        reply_markup=get_change_language_button(),
    )


# Oddiy xabarlarni ushlash
@bot.message_handler(func=lambda message: True)
def translate_text(message):
    chat_id = message.chat.id

    if message.text == "🔄 Tilni o‘zgartirish":
        bot.send_message(chat_id, "🌐 Tilni qayta tanlang:", reply_markup=get_language_keyboard())
        return

    if message.text == "📊 Statistikam":
        count = user_stats.get(chat_id, 0)
        bot.send_message(chat_id, f"📊 Siz hozirgacha {count} ta so‘z/matn tarjima qildingiz!")
        return

    if chat_id not in user_languages:
        bot.send_message(chat_id, "Iltimos, avval tilni tanlang: /start")
        return

    # Tanlangan yo'nalishni ajratamiz (masalan: "uz-en")
    lang_pair = user_languages[chat_id]
    src, dest = lang_pair.split("-")

    try:
        # Tarjima qilish
        translated = GoogleTranslator(source=src, target=dest).translate(message.text)

        # Statistikani yangilash
        user_stats[chat_id] = user_stats.get(chat_id, 0) + 1

        # Javob yuborish
        bot.send_message(chat_id, f"🔤 Tarjima:\n\n{translated}")

        # Random reaktsiya
        reaction = random.choice(REACTIONS)
        try:
            bot.set_message_reaction(message.chat.id, message.id, [types.ReactionTypeEmoji(reaction)])
        except Exception:
            pass  # agar reaction ishlamasa, e'tiborsiz qoldiramiz

        # Bonus: uzun matn bo‘lsa rag‘bat
        if len(message.text) > 100:
            bot.send_message(chat_id, "📖 Juda zo‘r matn tarjima qildingiz! 👏")

        # Voice yuborish
        tts = gTTS(translated, lang=dest)
        file_path = f"voice_{chat_id}.mp3"
        tts.save(file_path)

        with open(file_path, "rb") as audio:
            bot.send_voice(chat_id, audio)

        os.remove(file_path)

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Xatolik yuz berdi: {e}")


print("✅ Bot ishga tushdi...")
bot.infinity_polling()
