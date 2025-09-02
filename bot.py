import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Берём токен из переменных окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться на диагностику")]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! 👋 Добро пожаловать в нашу онлайн-школу!", reply_markup=keyboard)

@dp.message(lambda message: message.text == "📅 Записаться на диагностику")
async def handle_booking(message: types.Message):
    await message.answer("Отлично! Напишите, когда вам удобно, и мы свяжемся.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
