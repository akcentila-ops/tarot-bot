import os
import random
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print("=== 🔮 Tarot Bot запущен ===")

# === КАРТЫ ТАРО ===
TAROT_CARDS = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Сила", "Отшельник", 
    "Колесо Фортуны", "Справедливость", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

# === КЛАВИАТУРА ===
keyboard = [["🔮 На сегодня", "🃏 На неделю"], ["📅 На месяц"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# === ФУНКЦИИ БОТА ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Привет! Я — Tarot Bot!\nВыбери расклад:", 
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
            return response.json()['choices'][0]['message']['content']
    except:
        pass
    return f"Карта {card_name} говорит: доверяй интуиции."

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    if text == "🔮 На сегодня":
        card = get_cards(1)[0]
        interpretation = interpret_card(card, "сегодня")
        update.message.reply_text(f"Карта дня: {card}\n\n{interpretation}")
        
    elif text == "🃏 На неделю":
        cards = get_cards(3)
        response = "Расклад на неделю:\n\n"
        for i, card in enumerate(cards, 1):
            response += f"{i}. {card}\n{interpret_card(card, 'недели')}\n\n"
        update.message.reply_text(response)
        
    elif text == "📅 На месяц":
        cards = get_cards(5)
        response = "Расклад на месяц:\n\n"
        for i, card in enumerate(cards, 1):
            response += f"{i}. {card}\n{interpret_card(card, 'месяца')}\n\n"
        update.message.reply_text(response)

# === ЗАПУСК БОТА ===
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    print("🤖 Бот работает и слушает сообщения...")
    updater.idle()

if __name__ == '__main__':
    main()
