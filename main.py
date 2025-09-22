import random
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === КЛЮЧИ БУДУТ В RAILWAY (не здесь!) ===
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# === КАРТЫ ТАРО ===
TAROT_CARDS = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
    "Ace of Cups", "Two of Cups", "Three of Cups", "Four of Cups", "Five of Cups",
    "Six of Cups", "Seven of Cups", "Eight of Cups", "Nine of Cups", "Ten of Cups",
    "Page of Cups", "Knight of Cups", "Queen of Cups", "King of Cups",
    "Ace of Pentacles", "Two of Pentacles", "Three of Pentacles", "Four of Pentacles", "Five of Pentacles",
    "Six of Pentacles", "Seven of Pentacles", "Eight of Pentacles", "Nine of Pentacles", "Ten of Pentacles",
    "Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles",
    "Ace of Swords", "Two of Swords", "Three of Swords", "Four of Swords", "Five of Swords",
    "Six of Swords", "Seven of Swords", "Eight of Swords", "Nine of Swords", "Ten of Swords",
    "Page of Swords", "Knight of Swords", "Queen of Swords", "King of Swords",
    "Ace of Wands", "Two of Wands", "Three of Wands", "Four of Wands", "Five of Wands",
    "Six of Wands", "Seven of Wands", "Eight of Wands", "Nine of Wands", "Ten of Wands",
    "Page of Wands", "Knight of Wands", "Queen of Wands", "King of Wands"
]

# === КЛАВИАТУРА ===
keyboard = [["🔮 На сегодня", "🃏 На неделю"], ["📅 На месяц"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет, искатель истины! Я — *Tarot Wisdom Bot*.\n\n"
        "Я помогу тебе заглянуть в будущее с помощью карт Таро.\n\n"
        "Выбери расклад:", 
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# === Генерация случайных карт ===
def get_cards(count):
    return random.sample(TAROT_CARDS, min(count, len(TAROT_CARDS)))

# === Запрос к DeepSeek для интерпретации ===
def interpret_card(card_name, spread_type):
    prompt = f"Объясни значение карты Таро '{card_name}' в контексте расклада на {spread_type}. Ответь на русском языке, мягко, с элементами мистики, но без жестких формулировок. Не более 100 слов."
    
    try:
        response = requests.post(
            url="https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            }
        )
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"✨ Карта '{card_name}' говорит: доверься интуиции. Всё идёт по плану."

# === Обработка сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔮 На сегодня":
        card = get_cards(1)[0]
        interpretation = interpret_card(card, "день")
        await update.message.reply_text(f"*Карта дня:* **{card}**\n\n{interpretation}", parse_mode='Markdown')
        
    elif text == "🃏 На неделю":
        cards = get_cards(3)
        result = "*Расклад на неделю:*\n\n"
        for card in cards:
            interpretation = interpret_card(card, "неделю")
            result += f"**{card}**\n{interpretation}\n\n"
        await update.message.reply_text(result, parse_mode='Markdown')
        
    elif text == "📅 На месяц":
        cards = get_cards(5)
        result = "*Расклад на месяц:*\n\n"
        for card in cards:
            interpretation = interpret_card(card, "месяц")
            result += f"**{card}**\n{interpretation}\n\n"
        await update.message.reply_text(result, parse_mode='Markdown')

# === Запуск бота ===
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🔮 Tarot Bot запущен и слушает сообщения...")
    app.run_polling()

if __name__ == '__main__':
    main()
