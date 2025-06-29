import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import re

# Токен бота
TOKEN = "8050530823:AAFKuT-0BbVsPw9mR1JoTVxv-zSYhr46FGY"

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Функция для определения языка текста
def detect_language(text):
    """Определяет вероятный язык текста по используемым символам"""
    # Проверяем наличие китайских иероглифов
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'

    # Проверяем наличие кириллицы
    if re.search(r'[а-яА-ЯёЁ]', text):
        return 'ru'

    # Если не кириллица и не иероглифы, считаем что это другой язык
    return 'other'


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        f"你好, {message.from_user.first_name}!\n"
        "Я умный переводчик:\n"
        "- Отправьте текст на русском - переведу на китайский\n"
        "- Отправьте текст на китайском - переведу на русский\n"
        "- Текст на других языках буду переводить на русский\n\n"
        "<b>Просто выделите и скопируйте нужный текст!</b>",
        parse_mode="HTML"
    )


# Обработчик текстовых сообщений
@dp.message()
async def translate_message(message: types.Message):
    if message.text.startswith('/'):
        return

    try:
        text = message.text
        lang = detect_language(text)

        # Определяем направление перевода
        if lang == 'zh':  # Если китайский - переводим на русский
            source = 'zh-CN'
            target = 'ru'
            target_name = "русский"
        else:  # Любой другой текст переводим на китайский
            source = 'auto'
            target = 'zh-CN'
            target_name = "китайский"

        # Используем Google Translate API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": source,
                        "tl": target,
                        "dt": "t",
                        "q": text
                    }
            ) as response:
                data = await response.json()
                # Извлекаем переведенный текст из ответа
                translation = ''.join([part[0] for part in data[0]])

                # Форматируем ответ для удобного копирования
                response_text = (
                    f"🔤 <b>Исходный текст</b>:\n"
                    f"<code>{text}</code>\n\n"
                    f"🌍 <b>Перевод на {target_name}</b>:\n"
                    f"<code>{translation}</code>\n\n"
                    f"📋 Просто выделите нужный текст и скопируйте!"
                )

                await message.answer(response_text, parse_mode="HTML")

    except Exception as e:
        print(f"Ошибка перевода: {e}")
        await message.answer("⚠️ Ошибка перевода, попробуйте позже")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Бот запущен и готов к переводу...")
    asyncio.run(main())