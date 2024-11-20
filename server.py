import os
from dotenv import load_dotenv
import telebot
from telebot import types
import monitoring
from outline_api_service import get_new_key
from config import BOT_API_TOKEN, DEFAULT_SERVER_ID, BLOCKED_CHAT_IDS, TELEGRAM_GROUP_ID
from exceptions import KeyCreationError, KeyRenamingError, InvalidServerIdError
import message_formatter as f
from message_formatter import make_message_for_new_key
from aliases import ServerId
import time

# Загружаем переменные окружения
load_dotenv(dotenv_path="C:/Users/abdux/OneDrive/Рабочий стол/telegram-bot-for-outline-vpn-main/.env")

BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')

assert BOT_API_TOKEN is not None
bot = telebot.TeleBot(BOT_API_TOKEN, parse_mode='HTML')

# Хранилище для ключей (для упрощения используем словарь)
user_keys = {}

# Проверка чатов на блокировку
def check_blacklist(func):
    def wrapper(message):
        chat_id_to_check = message.chat.id

        if str(chat_id_to_check) in BLOCKED_CHAT_IDS:
            print('Blocked chat detected')
            return
        else:
            return func(message)

    return wrapper

# Проверка подписки на группу
def is_user_subscribed(chat_id):
    try:
        member = bot.get_chat_member(TELEGRAM_GROUP_ID, chat_id)
        if member.status in ['member', 'administrator', 'creator']:  # Статус подписчика
            return True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
    return False

# Команды и действия бота
@check_blacklist
@bot.message_handler(commands=['status'])
def send_status(message):
    monitoring.send_api_status()

@check_blacklist
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Если у пользователя уже есть ключ, не будем отправлять приветственное сообщение с предложением получить новый ключ
    if message.chat.id in user_keys:
        existing_key = user_keys[message.chat.id]
        bot.send_message(message.chat.id,
                         f"👋 Добро пожаловать! Ваш ключ: {existing_key}\nВы уже получили ключ, если что-то нужно — напишите администратору.",
                         reply_markup=_make_main_menu_markup())
    else:
        bot.send_message(message.chat.id,
                         "Привет! Этот бот для создания ключей Outline VPN. Подпишитесь на нашу группу, чтобы получить ключ. 👇",
                         reply_markup=_make_main_menu_markup())

@check_blacklist
@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "<b>❓ Инструкция по использованию:</b>\n\n"
        "1. Скачайте приложение Outline VPN с официальных источников:\n"
        "   - Для Android: [Скачать на Google Play](https://play.google.com/store/apps/details?id=org.outline.android)\n"
        "   - Для iOS: [Скачать на App Store](https://apps.apple.com/us/app/outline-vpn/id1451076367)\n"
        "   - Для Windows/macOS: [Скачать с официального сайта](https://getoutline.org)\n\n"
        "2. Вставьте полученный ключ в приложение и наслаждайтесь безопасным интернет-соединением.\n\n"
        
        "<b>🌐 Почему Outline VPN?</b>\n"
        "Outline VPN — это инструмент для приватного и защищенного интернета, который предоставляется бесплатно с помощью этого бота. "
        "Мы стремимся предоставить вам самые высокие стандарты безопасности и конфиденциальности при использовании сети.\n\n"
        
        "<b>💡 Наши преимущества:</b>\n"
        "✅ Легкость в использовании — никаких сложных настроек!\n"
        "✅ Бесплатные ключи для всех пользователей.\n"
        "✅ Простой и удобный интерфейс.\n\n"
        
        "<b>✉️ Связь с администратором:</b>\n"
        "Если у вас возникли вопросы или проблемы, всегда можно обратиться к нашему администратору: @thehumbleone11\n"
        "Мы всегда готовы помочь вам с настройкой или решением любых технических вопросов.\n\n"
        
        "<b>📌 Почему стоит использовать Outline VPN?</b>\n"
        "🌐 Outline VPN предоставляет безопасное и приватное интернет-соединение, которое легко настроить.\n"
        "🚀 Быстрое подключение, стабильно работающее по всему миру.\n"
        "🔒 Защита ваших данных от несанкционированного доступа в сети.\n\n"
    )
    bot.send_message(message.chat.id, help_message, disable_web_page_preview=True)

@check_blacklist
@bot.message_handler(commands=['servers'])
def send_servers_list(message):
    bot.send_message(message.chat.id, f.make_servers_list())

@check_blacklist
@bot.message_handler(commands=['about'])
def send_about(message):
    about_message = (
        "<b>💡 О боте Outline VPN</b>\n\n"
        "<b>Этот бот предназначен для быстрого и удобного получения ключей для VPN-серверов Outline.</b>\n\n"
        "👨‍💻 <b>Что может этот бот?</b>\n"
        "1. 🚀 Создание новых ключей для подключения к серверу Outline VPN.\n"
        "2. 🛡️ Удаление и управление ключами.\n"
        "3. 🖥️ Проверка статуса API сервера.\n"
        "4. 📥 Доступ к приложениям для всех платформ (Windows, macOS, Android, iOS).\n\n"
        
        "<b>🔒 Почему стоит использовать Outline VPN?</b>\n"
        "🌐 Outline VPN предоставляет безопасное и приватное интернет-соединение, которое легко настроить.\n"
        "🚀 Быстрое подключение, стабильно работающее по всему миру.\n"
        "🔒 Защита ваших данных от несанкционированного доступа в сети.\n\n"
        
        "<b>👨‍💻 Как использовать бот?</b>\n"
        "1. Подпишитесь на нашу группу в Telegram, чтобы получить доступ к ключам.\n"
        "2. Получите свой персональный ключ для подключения к VPN.\n"
        "3. Вставьте ключ в приложение Outline и наслаждайтесь безопасным интернет-соединением.\n\n"
        
        "<b>💡 Наши преимущества:</b>\n"
        "✅ Легкость в использовании — никаких сложных настроек!\n"
        "✅ Бесплатные ключи для всех пользователей.\n"
        "✅ Простой и удобный интерфейс.\n\n"
        
        "<b>✉️ Связь с администратором:</b>\n"
        "Если у вас возникли вопросы или проблемы, всегда можно обратиться к нашему администратору: @thehumbleone11\n"
        "Мы всегда готовы помочь вам с настройкой или решением любых технических вопросов.\n\n"
        
        "<b>📌 Инструкция по использованию:</b>\n"
        "1. Скачайте приложение Outline VPN с официальных источников:\n"
        "   - Для Android: [Скачать на Google Play](https://play.google.com/store/apps/details?id=org.outline.android)\n"
        "   - Для iOS: [Скачать на App Store](https://apps.apple.com/us/app/outline-vpn/id1451076367)\n\n"
        "2. Вставьте полученный ключ в приложение и наслаждайтесь безопасным интернет-соединением.\n\n"
        
        "<b>🌐 Почему Outline VPN?</b>\n"
        "Outline VPN — это инструмент для приватного и защищенного интернета, который предоставляется бесплатно с помощью этого бота. "
        "Мы стремимся предоставить вам самые высокие стандарты безопасности и конфиденциальности при использовании сети.\n\n"
        "<b>✨ Наслаждайтесь безопасным интернетом с Outline VPN!</b>"
    )
    bot.send_message(message.chat.id, about_message, disable_web_page_preview=True)

@bot.message_handler(content_types=['text'])
@check_blacklist
def anwser(message):
    if message.text == "Новый ключ":
        # Проверка, был ли уже выдан ключ
        if message.chat.id in user_keys:
            existing_key = user_keys[message.chat.id]
            bot.send_message(message.chat.id,
                             f"🔑 Ваш ключ: {existing_key}\nВы уже получили ключ, если что-то нужно — напишите администратору.")
        else:
            server_id = DEFAULT_SERVER_ID
            key_name = _form_key_name(message)
            _make_new_key(message, server_id, key_name)

    elif message.text == "Скачать приложение":
        bot.send_message(message.chat.id,
                         f.make_download_message(),
                         disable_web_page_preview=True)

    elif message.text == "Помощь":
        send_help(message)

    elif message.text == "О боте":
        send_about(message)

    elif message.text[:7] == "/newkey":
        server_id, key_name = _parse_the_command(message)
        _make_new_key(message, server_id, key_name)

    else:
        bot.send_message(message.chat.id,
                         "❗ Команда не распознана.\nИспользуйте /help, чтобы узнать список доступных команд.",
                         reply_markup=_make_main_menu_markup())

# Функции для создания нового ключа
def _make_new_key(message, server_id: ServerId, key_name: str):
    # Проверка подписки
    if not is_user_subscribed(message.chat.id):
        bot.send_message(message.chat.id, "Для получения ключа необходимо подписаться на нашу группу в Telegram. 📱")
        return

    # Проверка, был ли уже выдан ключ для этого пользователя
    if message.chat.id in user_keys:
        # Если ключ уже существует, отправляем его снова
        existing_key = user_keys[message.chat.id]
        bot.send_message(message.chat.id,
                         f"🔑 Ваш ключ: {existing_key}\nВы уже получили ключ, если что-то нужно — напишите администратору.")
        return

    try:
        key = get_new_key(key_name, server_id)
        # Сохраняем ключ в словарь
        user_keys[message.chat.id] = key.access_url
        _send_key(message, key, server_id)

    except KeyCreationError:
        error_message = "⚠️ API error: cannot create the key"
        _send_error_message(message, error_message)

    except KeyRenamingError:
        error_message = "⚠️ API error: cannot rename the key"
        _send_error_message(message, error_message)

    except InvalidServerIdError:
        message_to_send = "Сервер с таким ID отсутствует в списке серверов. 🤔\n" \
                          "Введите /servers, чтобы узнать доступные ID"
        bot.send_message(message.chat.id, message_to_send)

# Отправка ключа пользователю
def _send_key(message, key, server_id):
    bot.send_message(
        message.chat.id,
        make_message_for_new_key(key.access_url, server_id)
    )
    monitoring.new_key_created(key.kid, key.name, message.chat.id, server_id)

# Отправка сообщения об ошибке
def _send_error_message(message, error_message):
    bot.send_message(message.chat.id, error_message)
    monitoring.send_error(error_message, message.from_user.username,
                          message.from_user.first_name, message.from_user.last_name)

# Меню бота
def _make_main_menu_markup() -> types.ReplyKeyboardMarkup:
    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keygen_server1_button = types.KeyboardButton("Новый ключ")
    download_button = types.KeyboardButton("Скачать приложение")
    help_button = types.KeyboardButton("Помощь")
    about_button = types.KeyboardButton("О боте")

    menu_markup.add(
        keygen_server1_button,
        download_button,
        help_button,
        about_button
    )
    return menu_markup

# Разбор команды /newkey
def _parse_the_command(message) -> list:
    arguments = message.text[8:].split()

    if arguments != []:
        server_id = arguments[0]
    else:
        server_id = DEFAULT_SERVER_ID

    key_name = ''.join(arguments[1:])

    if key_name == '':
        key_name = _form_key_name(message)

    return [server_id, key_name]

# Формирование имени ключа
def _form_key_name(message) -> str:
    key_name = message.from_user.username
    return key_name

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
