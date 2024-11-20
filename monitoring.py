import telebot
from outline_api_service import check_api_status
from config import MONITOR_API_TOKEN, ADMIN_CHAT_ID

# Инициализация бота для мониторинга
monitor = telebot.TeleBot(MONITOR_API_TOKEN)


def new_key_created(key_id: int, key_name: str, chat_id: int, server_id: int) -> None:
    try:
        print(f"Отправка сообщения: Новый ключ создан (key_id: {key_id})")  # Логируем перед отправкой
        answer = (
            f"New key created:\n"
            f"key_id: {key_id}\n"
            f"key_name: {key_name}\n"
            f"chat_id: {chat_id}\n"
            f"server_id: {server_id}"
        )
        monitor.send_message(ADMIN_CHAT_ID, answer)
        print("Сообщение о создании ключа отправлено.")  # Логируем успешную отправку
    except Exception as e:
        print(f"Ошибка при отправке сообщения о создании ключа: {e}")  # Логируем ошибку


def send_error(error_message: str, username: str | None, firstname: str | None,
               lastname: str | None) -> None:
    try:
        print("Отправка сообщения: Ошибка обнаружена...")  # Логируем перед отправкой
        answer = (
            f"Error detected!\n"
            f"error_message: {error_message}\n"
            f"user_name: {username}\n"
            f"first_name: {firstname}\n"
            f"last_name: {lastname}"
        )
        monitor.send_message(ADMIN_CHAT_ID, answer)
        print("Сообщение об ошибке отправлено.")  # Логируем успешную отправку
    except Exception as e:
        print(f"Ошибка при отправке сообщения об ошибке: {e}")  # Логируем ошибку


def send_api_status() -> None:
    try:
        print("Отправка сообщения: Проверка состояния API...")  # Логируем перед отправкой
        api_status_codes = check_api_status()  # Получаем статус от outline_api_service
        message_to_send = ''
        for server_id, status_code in api_status_codes.items():
            message_to_send += f"server id: {server_id}, api_status_code: {status_code}\n"
        
        monitor.send_message(ADMIN_CHAT_ID, message_to_send)
        print("Сообщение о статусе API отправлено.")  # Логируем успешную отправку
    except Exception as e:
        print(f"Ошибка при отправке статуса API: {e}")  # Логируем ошибку


def send_start_message():
    try:
        print("Отправка сообщения: Бот запущен...")  # Логируем перед отправкой
        monitor.send_message(ADMIN_CHAT_ID, "-----BOT-STARTED!-----")
        send_api_status()
        print("Сообщение о запуске бота отправлено.")  # Логируем успешную отправку
    except Exception as e:
        print(f"Ошибка при отправке сообщения о запуске бота: {e}")  # Логируем ошибку
