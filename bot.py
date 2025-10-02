import asyncio
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

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

# 👉 Укажи свой Telegram ID
ADMIN_ID = 708095106

# ---------- Машина состояний ----------
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
            [KeyboardButton(text="📅 Записаться на годовой курс")],
            [KeyboardButton(text="ℹ️ О школе"), KeyboardButton(text="📂 Материалы")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! 👋 Добро пожаловать в нашу онлайн-школу!\n\nВыберите действие:",
        reply_markup=keyboard
    )

# ---------- Диагностика ----------
@dp.message(F.text == "📅 Записаться на диагностику")
async def handle_diagnostic(message: types.Message):
    text = (
        "Перед записью ознакомьтесь с условиями:\n\n"
        "Мы предоставляем бесплатную диагностику знаний. "
        "Дальнейшее обучение осуществляется на платной основе. "
        "Нажимая кнопку ниже, вы соглашаетесь с условиями."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен", callback_data="diagnostic_accept")],
            [InlineKeyboardButton(text="📝 Согласие на обработку персональных данных", callback_data="diagnostic_personal")]
        ]
    )

    await message.answer(text, reply_markup=kb)

# ---------- Годовой курс ----------
@dp.message(F.text == "📅 Записаться на годовой курс")
async def handle_course(message: types.Message):
    text = (
        "Перед записью ознакомьтесь с условиями оферты:\n\n"
        "Дальнейшее обучение осуществляется на платной основе. "
        "Нажимая кнопку ниже, вы соглашаетесь с условиями."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен", callback_data="course_accept")],
            [InlineKeyboardButton(text="📝 Согласие на обработку персональных данных", callback_data="course_personal")],
            [InlineKeyboardButton(text="📄 Полная оферта (PDF)", url="https://telegram-bot-production-4201.up.railway.app/offer")]
        ]
    )

    await message.answer(text, reply_markup=kb)

# ---------- Обработка согласия (общая функция) ----------
async def start_form(callback: types.CallbackQuery, state: FSMContext, booking_type: str):
    user_id = callback.from_user.id
    username = callback.from_user.username
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("offers_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now} | {booking_type} | {user_id} | @{username}\n")

    await callback.message.answer(f"Спасибо! Теперь заполните форму для записи ({booking_type}).\n\nВведите ФИО:")
    await state.update_data(booking_type=booking_type)  # сохраняем тип заявки
    await state.set_state(BookingForm.name)

# ---------- Callbacks ----------
@dp.callback_query(F.data == "diagnostic_accept")
async def diagnostic_accept(callback: types.CallbackQuery, state: FSMContext):
    await start_form(callback, state, "Диагностика")

@dp.callback_query(F.data == "course_accept")
async def course_accept(callback: types.CallbackQuery, state: FSMContext):
    await start_form(callback, state, "Годовой курс")

@dp.callback_query(F.data.contains("personal"))
async def personal_data(callback: types.CallbackQuery):
    await callback.message.answer("Вы дали согласие на обработку персональных данных ✅")
    await callback.answer()

# ---------- Форма ----------
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

    # Сохраняем в файл
    with open("bookings.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {data['booking_type']} | "
            f"{data['name']} | {data['school_class']} | {data['subject']} | {data['contact']} | TelegramID: {message.from_user.id}\n"
        )

    # Отправляем админу
    await bot.send_message(
        ADMIN_ID,
        f"📩 Новая заявка ({data['booking_type']}):\n\n"
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

# ===== СЕРВЕР =====
app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Bot + Server running"}

@app.get("/offer")
def get_offer():
    return FileResponse("static/offer.pdf", media_type="application/pdf")

# ---------- Запуск ----------
async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
