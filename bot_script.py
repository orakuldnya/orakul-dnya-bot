import os
import requests
import google.generativeai as genai
import google.api_core.exceptions # Добавляем этот импорт для более точной обработки ошибок Google API

# --- 1. Настройка API-ключей и идентификаторов ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Инициализация модели Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Использование 'gemini-1.5-flash' - более новой и часто доступной модели
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Модель Gemini успешно инициализирована: gemini-1.5-flash")
except Exception as e:
    print(f"Ошибка инициализации Gemini API: {e}")
    exit(1)

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
    gemini_response = model.generate_content(horoscope_prompt)
    generated_horoscope = gemini_response.text
    print("Гороскоп успешно сгенерирован Gemini.")

    # Подготовка сообщения для Telegram
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message_text = f"Ваш ежедневный гороскоп:\n\n{generated_horoscope}\n\nНадеемся, день принесет вам удачу!"

    telegram_payload = {
        "chat_id": CHANNEL_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }

    print("Попытка отправки гороскопа в Telegram...")
    telegram_response = requests.post(telegram_url, json=telegram_payload)
    telegram_response.raise_for_status()

    print("Гороскоп успешно отправлен в Telegram!")

except google.api_core.exceptions.GoogleAPICallError as e:
    # Более общий обработчик для ошибок Google API
    print(f"Ошибка Google API: {e}")
    error_message_tg = f"❌ Ошибка Google API: {e}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP ошибка при отправке в Telegram: {http_err}")
    error_message_tg = f"❌ Ошибка отправки в Telegram (HTTP): {http_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.ConnectionError as conn_err:
    print(f"Ошибка соединения с Telegram API: {conn_err}")
    error_message_tg = f"❌ Ошибка соединения с Telegram: {conn_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.Timeout as timeout_err:
    print(f"Таймаут запроса к Telegram API: {timeout_err}")
    error_message_tg = f"❌ Таймаут Telegram API: {timeout_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except requests.exceptions.RequestException as req_err:
    print(f"Неизвестная ошибка при запросе к Telegram API: {req_err}")
    error_message_tg = f"❌ Неизвестная ошибка Telegram API: {req_err}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

except Exception as e:
    print(f"Непредвиденная ошибка: {e}")
    error_message_tg = f"❌ Непредвиденная ошибка скрипта: {e}"
    try:
        requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg})
    except Exception as tg_err:
        print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")
