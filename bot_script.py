import os
import requests
import google.generativeai as genai

# --- 1. Настройка API-ключей и идентификаторов ---
# Получаем API-ключ Gemini из переменной окружения GitHub Secrets
# Убедитесь, что в GitHub Secrets у вас есть секрет с именем GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Получаем токен вашего Telegram бота из переменной окружения GitHub Secrets
# Убедитесь, что в GitHub Secrets у вас есть секрет с именем BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Получаем ID вашего Telegram канала из переменной окружения GitHub Secrets
# Убедитесь, что в GitHub Secrets у вас есть секрет с именем CHANNEL_ID
# Это может быть числовой ID канала (например, -1001234567890)
# или @username_канала (если он публичный).
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Инициализация модели Gemini
# Если GEMINI_API_KEY не установлен, этот шаг выдаст ошибку
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Используем 'gemini-pro' для текстовых задач
    # Если столкнетесь с ошибками или ограничениями, можно попробовать другие доступные модели,
    # например, 'models/text-bison-001' (старая, но иногда доступная модель),
    # но 'gemini-pro' предпочтительнее.
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Ошибка инициализации Gemini API: {e}")
    # Если API-ключ неверный или отсутствует, мы не сможем продолжить
    # и бот не сможет отправить сообщение об ошибке в Telegram, так как Telegram еще не настроен.
    exit(1) # Выходим из скрипта, так как нет смысла продолжать

# --- 2. Подготовка промпта для гороскопа ---
horoscope_prompt = """
Ты - мудрый астролог, который составляет ежедневный гороскоп.
Напиши сегодняшний гороскоп. Он должен быть:
- Воодушевляющим и позитивным.
- Содержать один-два полезных совета на день.
- Не слишком длинным, 3-5 предложений.
- Пиши на русском языке.
"""

# --- 3. Генерация гороскопа и отправка в Telegram ---
try:
    print("Попытка генерации гороскопа с помощью Gemini...")
    # Генерируем гороскоп с помощью Gemini
    gemini_response = model.generate_content(horoscope_prompt)
    generated_horoscope = gemini_response.text
    print("Гороскоп успешно сгенерирован Gemini.")

    # Подготовка сообщения для Telegram
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message_text = f"Ваш ежедневный гороскоп:\n\n{generated_horoscope}\n\nНадеемся, день принесет вам удачу!"

    telegram_payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML" # Можно использовать HTML для форматирования, если нужно
                             # или "MarkdownV2"
    }

    print("Попытка отправки гороскопа в Telegram...")
    # Отправка сообщения в Telegram
    telegram_response = requests.post(telegram_url, json=telegram_payload)
    telegram_response.raise_for_status()  # Вызовет исключение для HTTP ошибок (4xx или 5xx)

    print("Гороскоп успешно отправлен в Telegram!")

except genai.GenerativeContentError as e:
    # Ошибка, если Gemini не смог сгенерировать контент (например, контент заблокирован, лимиты)
    print(f"Ошибка Gemini API при генерации контента: {e}")
    error_message_tg = f"❌ Ошибка Gemini API при генерации гороскопа: {e}"
    # Попытка отправить сообщение об ошибке в Telegram
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.HTTPError as http_err:
    # Ошибка HTTP при отправке в Telegram (например, неверный BOT_TOKEN или CHANNEL_ID)
    print(f"HTTP ошибка при отправке в Telegram: {http_err}")
    error_message_tg = f"❌ Ошибка отправки в Telegram (HTTP): {http_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.ConnectionError as conn_err:
    # Ошибка соединения с Telegram API (например, проблемы с сетью на GitHub Actions)
    print(f"Ошибка соединения с Telegram API: {conn_err}")
    error_message_tg = f"❌ Ошибка соединения с Telegram: {conn_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.Timeout as timeout_err:
    # Таймаут при запросе к Telegram API
    print(f"Таймаут запроса к Telegram API: {timeout_err}")
    error_message_tg = f"❌ Таймаут Telegram API: {timeout_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.RequestException as req_err:
    # Любая другая ошибка, связанная с requests (Telegram)
    print(f"Неизвестная ошибка при запросе к Telegram API: {req_err}")
    error_message_tg = f"❌ Неизвестная ошибка Telegram API: {req_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except Exception as e:
    # Любая другая непредвиденная ошибка
    print(f"Непредвиденная ошибка: {e}")
    error_message_tg = f"❌ Непредвиденная ошибка скрипта: {e}"
    # Попытка отправить сообщение об этой ошибке в Telegram, если это возможно
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")
