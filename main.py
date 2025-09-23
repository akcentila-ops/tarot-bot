import os
import asyncio
import random
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print("=== 🔮 Tarot Bot ===")
print("TELEGRAM_TOKEN:", "ЕСТЬ" if TELEGRAM_TOKEN else "НЕТ")
print("DEEPSEEK_API_KEY:", "ЕСТЬ" if DEEPSEEK_API_KEY else "НЕТ")

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
    print("📨 Получена команда /start")
    await update.message.reply_text(
        "👋 Привет! Я — Tarot Wisdom Bot!\n\n"
        "Выбери расклад:", 
        reply_markup=reply_markup
    )
    print("✅ Клавиатура отправлена")

def get_cards(count):
    return random.sample(TAROT_CARDS, count)

def interpret_card(card_name, spread_type):
    try:
        prompt = f"Объясни значение карты Таро '{card_name}' для {spread_type} на русском (2-3 предложения)"
        
        response = requests.post(
            url="https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Карта {card_name} советует доверять своей интуиции."
            
    except Exception as e:
        return f"✨ {card_name} говорит: всё идет своим чередом."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    print(f"📨 Получено сообщение: {text}")
    
    if text == "🔮 На сегодня":
        card = get_cards(1)[0]
        interpretation = interpret_card(card, "сегодняшнего дня")
        await update.message.reply_text(f"*Карта дня:* **{card}**\n\n{interpretation}", parse_mode='Markdown')
        print(f"✅ Отправлена карта дня: {card}")
        
    elif text == "🃏 На неделю":
        cards = get_cards(3)
        response = "*Твой расклад на неделю:*\n\n"
        for i, card in enumerate(cards, 1):
            interpretation = interpret_card(card, "предстоящей недели")
            response += f"{i}. **{card}**\n{interpretation}\n\n"
        await update.message.reply_text(response, parse_mode='Markdown')
        print("✅ Отправлен расклад на неделю")
        
    elif text == "📅 На месяц":
        cards = get_cards(5)
        response = "*Твой расклад на месяц:*\n\n"
        for i, card in enumerate(cards, 1):
            interpretation = interpret_card(card, "предстоящего месяца")
            response += f"{i}. **{card}**\n{interpretation}\n\n"
        await update.message.reply_text(response, parse_mode='Markdown')
        print("✅ Отправлен расклад на месяц")
        
    else:
        await update.message.reply_text("Используй кнопки ниже 👇")
        print("❌ Неизвестная команда")

async def main():
    """Основная функция бота"""
    try:
        print("🚀 Инициализация бота...")
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Очищаем предыдущие состояния
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук очищен")
        
        print("🔮 Бот запущен и слушает сообщения...")
        await application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    # Простой запуск
    asyncio.run(main())
