import os
from flask import Flask, request
import telebot
from telebot.types import Update, InlineKeyboardMarkup, InlineKeyboardButton
# mirror bot token

# данные админа
TOKEN = '8110184384:AAFFQcAUV1dt7pJ8P7VU-tLAYt3CnG3a6Rk'



bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = '-1003745866965'
TARGET_CHAT_ID = -1003745866965
PRIVATE_CHANNEL_ID = -1003749499975
PRIVATE_CHANNEL_IDM = [-1003749499975, -1003749499975]
ADMIN_ID = 8265255633
SECRET_PASSWORD = "test"
TEMP_BROADCAST = ""
TEMP_PHOTO = None  # Сюда сохраним ID картинки
TEMP_CAPTION = ""  # Сюда сохраним текст
BOT_EMAIL = "grapusemedisse123@gmail.com"
MASTER_KEY = "007n7"
temp_data = {}  # Временное хранилище для кода и нового пароля
temp_vip_data = {} # Временное хранилище для процесса выдачи
user_last_msg_time = {} # {user_id: время}
spam_warnings = {} # {user_id: кол-во быстрых сообщений}
user_messages = {}
app = Flask(__name__)
DELTA_ID = "BQACAgIAAxkBAAIMZ2oEhLfeXWJzbxROi0nrRif4d81RAALSpAACg4MoSNgrogsqSaxjOwQ"
SPONSOR_CHANNEL = os.getenv("SPONSOR_CHANNEL")  # ID канала, например, -100123456789
SPONSOR_LINK = os.getenv("SPONSOR_LINK")


@app.route('/')
def index():
    return "Бот работает 24/7 и не спит!", 200


# 2. Эндпоинт для приема вебхуков от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Forbidden', 403


# 3. Обработка команды /start (просто проверка связи)
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, "Привет! Я бот-приемщик заявок. Я готов к работе.")


# 4. ПЕРЕХВАТ ЗАЯВКИ В ЗАКРЫТЫЙ КАНАЛ
@bot.chat_join_request_handler()
def handle_join_request(event):
    user_id = event.from_user.id
    chat_id = event.chat.id  # ID основного закрытого канала

    try:
        # Проверяем статус пользователя в рекламном канале
        member = bot.get_chat_member(chat_id=SPONSOR_CHANNEL, user_id=user_id)

        if member.status in ['member', 'administrator', 'creator']:
            # Если уже подписан — одобряем вход
            bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            bot.send_message(user_id, "Ваша заявка одобрена! Добро пожаловать.")
        else:
            # Если не подписан — отправляем инструкцию с кнопками
            kb = InlineKeyboardMarkup()
            kb.row(InlineKeyboardButton(text="1. Подписаться на канал 📢", url=SPONSOR_LINK))
            kb.row(InlineKeyboardButton(text="2. Проверить подписку 🔄", callback_data=f"check_{chat_id}"))

            bot.send_message(
                user_id,
                "Привет! Чтобы попасть в закрытый канал, вам нужно подписаться на нашего спонсора. "
                "После подписки нажмите кнопку «Проверить подписку».",
                reply_markup=kb
            )
    except Exception as e:
        print(f"Ошибка при обработке заявки: {e}")


# 5. ПРОВЕРКА ПОДПИСКИ ПО КНОПКЕ
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_subscription(call):
    user_id = call.from_user.id
    target_chat_id = int(call.data.split("_")[1])  # Достаем ID основного канала

    try:
        member = bot.get_chat_member(chat_id=SPONSOR_CHANNEL, user_id=user_id)

        if member.status in ['member', 'administrator', 'creator']:
            # Одобряем заявку в закрытый канал
            bot.approve_chat_join_request(chat_id=target_chat_id, user_id=user_id)
            # Показываем всплывающее окно и удаляем сообщение бота
            bot.answer_callback_query(call.id, "Успешно! Доступ открыт.", show_alert=True)
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, "Вы успешно приняты! Канал появился в вашем списке чатов.")
        else:
            bot.answer_callback_query(call.id, "Вы всё еще не подписались на спонсора!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, "Ошибка проверки. Попробуйте позже.", show_alert=True)
        print(f"Ошибка клика: {e}")


# Автоматическая установка вебхука при старте на Render
if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render создает эту переменную сам
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/webhook")

    # Запуск Flask-сервера
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)