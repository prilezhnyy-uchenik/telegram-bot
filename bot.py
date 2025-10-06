import asyncio
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from aiogram.types import LabeledPrice


from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Токен на оплату
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

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
            [KeyboardButton(text="📊 Тарифы и цены")], 
            [KeyboardButton(text="📅 Записаться на диагностику")],
            [KeyboardButton(text="📚 Записаться на годовой курс")],
            [KeyboardButton(text="👨‍🏫 Индивидуальное занятие")],
            [KeyboardButton(text="ℹ️ О школе"), KeyboardButton(text="📂 Материалы")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! 👋 Добро пожаловать в нашу онлайн-школу!\n\nВыберите действие:",
        reply_markup=keyboard
    )


# ---------- Тарифы и цены ----------
@dp.message(F.text == "📊 Тарифы и цены")
async def handle_prices(message: types.Message):
    text = (
        "📊 <b>Тарифы и цены</b>\n\n"
        "1️⃣ <b>Индивидуальное занятие</b>\n"
        "• Формат: 90 минут, онлайн\n"
        "• Стоимость: 2500 ₽\n"
        "2️⃣ <b>Годовой курс (групповой формат)</b>\n"
        "• Формат: 3 занятия/нед.(математика и физика), 90 минут, онлайн\n"
        "• Включает: доступ к материалам, домашним заданиям, пробникам\n"
        "• Стоимость:\n"
        "   • 10 000 ₽ / месяц\n"
        "   • 75 000 ₽ / за год (экономия 15 000 ₽)"
    )
    await message.answer(text, parse_mode="HTML")

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
            [InlineKeyboardButton(text="✅ Согласен(а)", callback_data="diagnostic_accept")],
            [InlineKeyboardButton(
                text="📝 Согласие на обработку персональных данных (PDF)",
                url="https://telegram-bot-production-534b.up.railway.app/consent")]
        ]
    )

    await message.answer(text, reply_markup=kb)

# ---------- Годовой курс ----------
@dp.message(F.text == "📚 Записаться на годовой курс")
async def handle_course(message: types.Message):
    text = (
        "Перед записью ознакомьтесь с условиями оферты:\n\n"
        "Дальнейшее обучение осуществляется на платной основе. "
        "Нажимая кнопку ниже, вы соглашаетесь с условиями."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен(а)", callback_data="course_accept")],
            [InlineKeyboardButton(
                text="📝 Согласие на обработку персональных данных (PDF)",
                url="https://telegram-bot-production-534b.up.railway.app/consent")],
            [InlineKeyboardButton(
                text="📝 Полная оферта (PDF)",
                url="https://telegram-bot-production-534b.up.railway.app/offer")]
        ]
    )

    await message.answer(text, reply_markup=kb)

# ---------- О школе ----------
@dp.message(F.text == "ℹ️ О школе")
async def handle_about(message: types.Message):
    text = (
        "📌 <b>О школе «ФизМатиум»</b>\n\n"
        "Добро пожаловать в онлайн-школу <b>«ФизМатиум»</b> — пространство, где математика и физика "
        "становятся понятными, а экзамены перестают быть стрессом.\n\n"
        "🎓 <b>Для школьников 8–11 классов:</b>\n"
        "• Объясняем сложные темы простым языком\n"
        "• Готовим к ОГЭ и ЕГЭ без заучивания\n"
        "• Даём материалы, которые закрывают пробелы навсегда\n\n"
        "👨‍👩‍👧 <b>Для родителей:</b>\n"
        "• Прозрачная система обучения\n"
        "• Регулярная диагностика и отчёты\n"
        "• Уверенность, что ребёнок идёт по плану, а не хаотично\n\n"
        "💡 <b>Почему мы?</b>\n"
        "• Преподаватели, которые «говорят на одном языке» с учениками\n"
        "• Полный годовой курс → от базы до сложных задач второй части\n"
        "• Мини-группы → каждому уделяется внимание\n"
        "• Пробные уроки и бесплатная диагностика уровня\n\n"
        "📈 Наша цель — результат, а не просто «галочка».\n\n"
        "ФизМатиум — развиваем ум, умножаем результат! 🚀"
    )
    await message.answer(text, parse_mode="HTML")


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

    # Кнопки выбора тарифа
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить месяц — 10 000 ₽", callback_data="pay_month")],
            [InlineKeyboardButton(text="💳 Оплатить год — 75 000 ₽", callback_data="pay_year")]
        ]
    )

    await message.answer(
        "✅ Ваша заявка успешно принята!\n\n"
        "Теперь выберите способ оплаты:",
        reply_markup=kb
    )
    
    await state.clear()

@dp.callback_query(F.data == "pay_month")
async def pay_month(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Оплата месяца обучения", amount=200 * 100)]  # *100 = копейки
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Месячный курс «ФизМатиум»",
        description="Доступ к групповым занятиям по физике иили математике (1 месяц).",
        payload="month_course_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="month_course",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()


@dp.callback_query(F.data == "pay_year")
async def pay_year(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Оплата годового курса", amount=200 * 100)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Годовой курс «ФизМатиум»",
        description="Групповой формат: 3 занятия в неделю (математика или физика).",
        payload="year_course_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="year_course",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()

@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    payment = message.successful_payment

    # Можно вывести данные о платеже в консоль (для теста)
    print("=== УСПЕШНАЯ ОПЛАТА ===")
    print("Сумма:", payment.total_amount / 100, payment.currency)
    print("Платёжные данные:", payment.to_python())

    # Просто ответ пользователю без отправки формы
    await message.answer(
        "✅ Оплата успешно прошла!\n\n"
        "Спасибо за доверие 💙\n"
        "Мы уже видим ваш платёж, доступ будет активирован в ближайшее время."
    )


# ===== СЕРВЕР =====
app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Bot + Server running"}

@app.get("/offer")
def get_offer():
    return FileResponse("static/offer.pdf", media_type="application/pdf")

@app.get("/consent")
def get_consent():
    return FileResponse("static/consent.pdf", media_type="application/pdf")

# ---------- Запуск ----------
async def start_bot():
    await dp.start_polling(bot)

async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        start_bot(),
        start_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
