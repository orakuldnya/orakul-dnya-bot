import os
import requests
import telegram
import logging
# Для более новых версий python-telegram-bot
from telegram import constants # Добавляем этот импорт

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Константы ---
# URL вашей модели на Hugging Face Inference API
# Замените этот URL на URL вашей конкретной модели, если хотите попробовать другую.
# Убедитесь, что вы приняли условия использования модели на HF, если она "gated".
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

# --- Функции ---

def generate_horoscope(prompt: str) -> str:
    """
    Генерирует текст гороскопа с использованием Hugging Face Inference API.
    """
    hf_api_token = os.getenv("HF_API_TOKEN")
    if not hf_api_token:
        logger.error("HF_API_TOKEN не установлен в переменных окружения.")
        return "Не удалось сгенерировать гороскоп: отсутствует токен API."

    headers = {
        "Authorization": f"Bearer {hf_api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150, # Максимальное количество генерируемых токенов
            "temperature": 0.7,    # Температура для генерации (контролирует случайность)
            "do_sample": True,     # Включить сэмплирование
            "return_full_text": False # Возвращать только сгенерированный текст
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Вызывает исключение для HTTP ошибок (4xx или 5xx)

        logger.info(f"API Response Status Code: {response.status_code}")
        logger.info(f"Raw API Response Text: {response.text}")

        result = response.json()

        # Hugging Face Inference API может возвращать список словарей.
        # Проверяем структуру ответа и извлекаем сгенерированный текст.
        if isinstance(result, list) and result and 'generated_text' in result[0]:
            generated_text = result[0]['generated_text'].strip()
            # Убираем возможный повтор промпта, если return_full_text=False не сработал идеально
            if generated_text.lower().startswith(prompt.lower()):
                generated_text = generated_text[len(prompt):].strip()
            return generated_text
        else:
            logger.error(f"Неожиданная структура ответа от Hugging Face API: {result}")
            return "Не удалось сгенерировать гороскоп: неожиданный формат ответа."

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP ошибка при запросе к Hugging Face API: {http_err} - {response.text}")
        return f"Ошибка API: {response.status_code} - {response.text[:200]}..."
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Ошибка соединения с Hugging Face API: {conn_err}")
        return "Не удалось соединиться с API Hugging Face."
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Таймаут запроса к Hugging Face API: {timeout_err}")
        return "Превышено время ожидания ответа от API Hugging Face."
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Неизвестная ошибка при запросе к Hugging Face API: {req_err}")
        return "Произошла ошибка при запросе к API Hugging Face."
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при генерации гороскопа: {e}", exc_info=True)
        return "Произошла внутренняя ошибка при генерации гороскопа."


async def send_telegram_message(bot_token: str, channel_id: str, message_text: str):
    """
    Отправляет сообщение в Telegram канал.
    """
    try:
        bot = telegram.Bot(token=bot_token)
        # Использование строки 'Markdown' для parse_mode
        await bot.send_message(chat_id=channel_id, text=message_text, parse_mode='Markdown')
        logger.info(f"Сообщение успешно отправлено в канал {channel_id}.")
    except telegram.error.BadRequest as e: # Обновлено для v20+
        logger.error(f"Ошибка Telegram BadRequest: {e}")
        if "chat not found" in str(e).lower():
            logger.error(f"Канал с ID {channel_id} не найден или бот не имеет к нему доступа. Проверьте CHANNEL_ID.")
        elif "unauthorized" in str(e).lower(): # Для Unauthorized ошибок в BadRequest
            logger.error("Ошибка авторизации Telegram: Неверный BOT_TOKEN. Убедитесь, что BOT_TOKEN правильный и бот добавлен в канал с правами администратора.")
        else:
            logger.error(f"Проверьте CHANNEL_ID или права бота: {e}")
    except telegram.error.TimedOut:
        logger.error("Таймаут при отправке сообщения в Telegram.")
    except telegram.error.TelegramError as e: # Более общий класс ошибок Telegram (для v20+)
        logger.error(f"Произошла общая ошибка Telegram: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке сообщения в Telegram: {e}", exc_info=True)


async def main():
    """
    Основная функция, запускаемая GitHub Actions.
    """
    bot_token = os.getenv("BOT_TOKEN")
    channel_id = os.getenv("CHANNEL_ID")

    if not bot_token:
        logger.error("BOT_TOKEN не установлен в переменных окружения. Выход.")
        return
    if not channel_id:
        logger.error("CHANNEL_ID не установлен в переменных окружения. Выход.")
        return

    logger.info("Запуск генерации гороскопа...")

    horoscope_prompt = "Напиши сегодняшний гороскоп, который будет воодушевлять и давать полезные советы на день."
    horoscope_text = generate_horoscope(horoscope_prompt)

    if horoscope_text.startswith("Не удалось сгенерировать гороскоп"):
        final_message = f"**Ошибка генерации гороскопа:** {horoscope_text}\n\nПожалуйста, проверьте логи."
    else:
        final_message = f"**Ваш ежедневный гороскоп:**\n\n{horoscope_text}\n\n_Надеемся, день принесет вам удачу!_"

    logger.info("Попытка отправить сообщение в Telegram...")
    await send_telegram_message(bot_token, channel_id, final_message)
    logger.info("Скрипт завершен.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())