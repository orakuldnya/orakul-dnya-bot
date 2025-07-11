import os
import requests
import google.generativeai as genai
import google.api_core.exceptions
import html # Импортируем модуль html для экранирования

# --- 1. Настройка API-ключей и идентификаторов ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Инициализация модели Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Модель Gemini успешно инициализирована: gemini-1.5-flash")
except Exception as e:
    print(f"Ошибка инициализации Gemini API: {e}")
    if BOT_TOKEN and CHANNEL_ID:
        try:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": f"❌ Бот: Ошибка инициализации Gemini API: {e}"})
        except:
            pass # Игнорируем ошибку отправки ошибки
    exit(1)

# --- 2. Список знаков зодиака и их смайлики ---
zodiac_signs_with_emojis = {
    "Овен": "♈",
    "Телец": "♉",
    "Близнецы": "♊",
    "Рак": "♋",
    "Лев": "♌",
    "Дева": "♍",
    "Весы": "♎",
    "Скорпион": "♏",
    "Стрелец": "♐",
    "Козерог": "♑",
    "Водолей": "♒",
    "Рыбы": "♓"
}

# --- 3. Генерация и отправка гороскопов для каждого знака ---
print("Начинаем генерацию и отправку гороскопов для всех знаков зодиака (каждый в отдельном сообщении)...")

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

for sign, emoji in zodiac_signs_with_emojis.items():
    # Подготовка промпта для конкретного знака
    horoscope_prompt = f"""
    Ты - мудрый астролог, который составляет ежедневный гороскоп.
    Напиши сегодняшний гороскоп для знака зодиака "{sign}".
    Он должен быть:
    - Воодушевляющим и позитивным.
    - Содержать один-два полезных совета на день.
    - Не слишком длинным, 2-3 предложения. # Сохраняем компактность для стабильности
    - Начинаться сразу с текста гороскопа (без заголовка типа "Гороскоп для ...").
    - Пиши на русском языке.
    """

    try:
        print(f"Попытка генерации гороскопа для {sign}...")
        gemini_response = model.generate_content(horoscope_prompt)
        generated_horoscope = gemini_response.text

        # Удаляем лишние звездочки или другие символы, которые Gemini может добавить в начало/конец
        generated_horoscope = generated_horoscope.strip('*').strip()

        # Экранируем специальные HTML-символы в сгенерированном гороскопе
        escaped_generated_horoscope = html.escape(generated_horoscope)

        print(f"Гороскоп для {sign} успешно сгенерирован Gemini.")

        # Подготовка сообщения для Telegram с использованием HTML-форматирования
        message_text = (
            f"{emoji} Гороскоп для <b>{sign}</b> на сегодня:\n\n"
            f"{escaped_generated_horoscope}\n\n"
            f"💫 Надеемся, день принесет вам удачу!" # Общая фраза для каждого гороскопа
        )

        telegram_payload = {
            "chat_id": CHANNEL_ID,
            "text": message_text,
            "parse_mode": "HTML"
        }
        
        # *** ОТПРАВКА СООБЩЕНИЯ ВНУТРИ ЦИКЛА ***
        print(f"Попытка отправки гороскопа для {sign} в Telegram...")
        telegram_response = requests.post(telegram_url, json=telegram_payload)
        telegram_response.raise_for_status() # Проверит ошибки HTTP

        print(f"Гороскоп для {sign} успешно отправлен в Telegram!")

    except google.api_core.exceptions.GoogleAPICallError as e:
        print(f"Ошибка Google API для {sign}: {e}")
        error_message_tg = f"❌ Ошибка Google API для <b>{sign}</b>: {html.escape(str(e))}"
        try:
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
        except Exception as tg_err:
            print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка при отправке в Telegram для {sign}: {http_err}")
        error_message_tg = f"❌ HTTP ошибка отправки в Telegram для <b>{sign}</b>: {html.escape(str(http_err))}"
        try:
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
        except Exception as tg_err:
            print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

    except requests.exceptions.RequestException as req_err:
        print(f"Неизвестная ошибка при запросе (Telegram) для {sign}: {req_err}")
        error_message_tg = f"❌ Неизвестная ошибка Telegram для <b>{sign}</b>: {html.escape(str(req_err))}"
        try:
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
        except Exception as tg_err:
            print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

    except Exception as e:
        print(f"Непредвиденная ошибка для {sign}: {e}")
        error_message_tg = f"❌ Непредвиденная ошибка скрипта для <b>{sign}</b>: {html.escape(str(e))}"
        try:
            requests.post(telegram_url, json={"chat_id": CHANNEL_ID, "text": error_message_tg, "parse_mode": "HTML"})
        except Exception as tg_err:
            print(f"Не удалось отправить сообщение об ошибке в Telegram: {tg_err}")

print("\nПроцесс генерации и отправки гороскопов для всех знаков завершен.")
