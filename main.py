import os
import logging
import random
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

logger.info("=== 🔮 Tarot Bot ===")

# === FLASK ДЛЯ RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🔮 Tarot Bot is running!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    logger.info("Starting Flask on port %s", port)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# === КАРТЫ ТАРО ===
TAROT_CARDS = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Сила", "Отшельник",
    "Колесо Фортуны", "Справедливость", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце",
    "Суд", "Мир"
]

# === КЛАВИАТУРА ===
keyboard = [["🔮 На сегодня", "🃏 На неделю"], ["📅 На месяц"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# === ФУНКЦИИ БОТА ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Получена команда /start")
    await update.message.reply_text(
        "👋 Привет! Я — Tarot Wisdom Bot!\nВыбери расклад:", 
        reply_markup=reply_markup
    )

def get_cards(count):
    return random.sample(TAROT_CARDS, count)

def interpret_card(card_name, spread_type):
    try:
        prompt = f"Объясни значение карты Таро '{card_name}' для {spread_type} (2 предложения)"
        
        response = requests.post(
            url="https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        return f"Карта {card_name} говорит: доверяй интуиции."
    except:
        return f"✨ {card_name}: всё идет по плану."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logger.info("Получено сообщение: %s", text)
    
    if text == "🔮 На сегодня":
        card = get_cards(1)[0]
        interpretation = interpret_card(card, "сегодня")
        await update.message.reply_text(f"Карта дня: {card}\n\n{interpretation}")
        
    elif text == "🃏 На неделю":
        cards = get_cards(3)
        response = "Твой расклад на неделю:\n\n"
        for i, card in enumerate(cards, 1):
            interpretation = interpret_card(card, "недели")
            response += f"{i}. {card}\n{interpretation}\n\n"
        await update.message.reply_text(response)
        
    elif text == "📅 На месяц":
        cards = get_cards(5)
        response = "Твой расклад на месяц:\n\n"
        for i, card in enumerate(cards, 1):
            interpretation = interpret_card(card, "месяца")
            response += f"{i}. {card}\n{interpretation}\n\n"
        await update.message.reply_text(response)

def run_bot():
    """Запуск бота в отдельном потоке"""
    import asyncio
    
    async def main():
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🔮 Бот запущен!")
        await application.run_polling()
    
    asyncio.run(main())

def main():
    # Запускаем Flask в основном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()

if __name__ == '__main__':
    main()
