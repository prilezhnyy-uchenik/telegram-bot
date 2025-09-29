import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Берём токен из переменных окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 👉 Укажи свой Telegram ID (узнать можно у @userinfobot)
ADMIN_ID = 708095106

# ---------- Машина состояний для записи ----------
class BookingForm(StatesGroup):
    name = State()
    school_class = State()
    subject = State()
    contact = State()

# ---------- /start ----------
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться на диагностику")],
            [KeyboardButton(text="ℹ️ О школе"), KeyboardButton(text="📂 Материалы")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! 👋 Добро пожаловать в нашу онлайн-школу!\n\nВыберите действие:",
        reply_markup=keyboard
    )

# ---------- Нажатие "Записаться на диагностику" ----------
@dp.message(F.text == "📅 Записаться на годовой курс")
async def handle_booking(message: types.Message):
    offer_text = (
        "Перед записью ознакомьтесь с условиями оферты:\n\n"
        "Мы предоставляем бесплатную диагностику знаний. "
        "Дальнейшее обучение осуществляется на платной основе. "
        "Нажимая кнопку ниже, вы соглашаетесь с условиями."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен", callback_data="accept_offer")],
            [InlineKeyboardButton(text="📄 Полная оферта (PDF)", url="https://example.com/offer.pdf")]
        ]
    )

    await message.answer(offer_text, reply_markup=kb)

# ---------- Нажатие "Согласен" ----------
@dp.callback_query(F.data == "accept_offer")
async def accept_offer(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Сохраняем факт акцепта в файл (можно заменить на БД)
    with open("offers_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now} | {user_id} | @{username}\n")

    await callback.message.answer("Спасибо! Теперь заполните форму для записи.\n\nВведите ФИО:")
    await state.set_state(BookingForm.name)

# ---------- Пошаговая форма ----------
@dp.message(BookingForm.name)
async def form_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш класс:")
    await state.set_state(BookingForm.school_class)

@dp.message(BookingForm.school_class)
async def form_class(message: types.Message, state: FSMContext):
    await state.update_data(school_class=message.text)
    await message.answer("Введите предмет (например, математика):")
    await state.set_state(BookingForm.subject)

@dp.message(BookingForm.subject)
async def form_subject(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("Введите контакт (телефон или Telegram):")
    await state.set_state(BookingForm.contact)

@dp.message(BookingForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    # Сохраняем анкету в файл (потом можно в БД)
    with open("bookings.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{data['name']} | {data['school_class']} | {data['subject']} | {data['contact']} | "
            f"TelegramID: {message.from_user.id}\n"
        )

    # 👉 Отправляем админу заявку
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая заявка:\n\n"
        f"👤 ФИО: {data['name']}\n"
        f"🏫 Класс: {data['school_class']}\n"
        f"📘 Предмет: {data['subject']}\n"
        f"☎ Контакт: {data['contact']}\n"
        f"🆔 TelegramID: {message.from_user.id}"
    )

    await message.answer(
        "✅ Ваша заявка успешно принята!\n\n"
        "Реквизиты для оплаты будут отправлены отдельно.\n"
        "Спасибо, что выбрали нашу школу!"
    )
    await state.clear()

# ---------- Запуск ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
