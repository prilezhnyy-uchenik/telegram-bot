import asyncio
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from aiogram.types import LabeledPrice
from aiogram.types import PreCheckoutQuery


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
# Временное хранилище данных форм до оплаты
pending_forms = {}


# Обработка PreCheckoutQuery
@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    """
    Telegram ожидает ответ на PreCheckoutQuery в течение 10 секунд.
    Этот метод сообщает, что оплата возможна.
    """
    await bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)

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
            [KeyboardButton(text="📚 Записаться на годовой курс"), KeyboardButton(text="👨‍🏫 Индивидуальное занятие")],
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
        "• Стоимость: 2000 ₽\n"
        "2️⃣ <b>Годовой курс</b>\n"
        "• Формат: 3 занятия в неделю, 90 минут онлайн, домашка с \n"
        " проверкой и комментариями, доступ к материалам и пробникам. \n"
        "• Стоимость:\n"
        "   • 10 000 ₽ / месяц\n"
        "   • 18 000 ₽ / месяц - комбо"
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

# ---------- Индивидуальное занятие ----------
@dp.message(F.text == "👨‍🏫 Индивидуальное занятие")
async def handle_individual(message: types.Message):
    text = (
        "Перед записью ознакомьтесь с условиями оферты:\n\n"
        "Дальнейшее обучение осуществляется на платной основе. "
        "Нажимая кнопку ниже, вы соглашаетесь с условиями."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен(а)", callback_data="individual_accept")],
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


    # ---------- Материалы ----------
@dp.message(F.text == "📂 Материалы")
async def handle_materials(message: types.Message):
    text = "📚 Выберите нужный материал для скачивания:"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📘 Физика ЕГЭ",
                url="https://telegram-bot-production-534b.up.railway.app/physics_ege")],
            [InlineKeyboardButton(
                text="📗 Физика ОГЭ",
                url="https://telegram-bot-production-534b.up.railway.app/physics_oge")],
            [InlineKeyboardButton(
                text="📙 Стереометрия",
                url="https://telegram-bot-production-534b.up.railway.app/stereometry")],
            [InlineKeyboardButton(
                text="📕 Геометрия ОГЭ + ЕГЭ",
                url="https://telegram-bot-production-534b.up.railway.app/geometry")]
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

@dp.callback_query(F.data == "individual_accept")
async def individual_accept(callback: types.CallbackQuery, state: FSMContext):
    await start_form(callback, state, "Индивидуальное занятие")

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

    booking_type = data["booking_type"]

    # === ГОДОВОЙ КУРС ===
    if booking_type == "Годовой курс":
        pending_forms[message.from_user.id] = data

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить месяц — 10 000 ₽", callback_data="pay_month")],
                [InlineKeyboardButton(text="💳 Оплатить комбо — 18 000 ₽", callback_data="pay_combo")],
                [InlineKeyboardButton(text="💳 Оплатить год — 75 000 ₽", callback_data="pay_year")]
            ]
        )
        await message.answer(
            "✅ Форма заполнена!\n\n"
            "Теперь выберите способ оплаты:",
            reply_markup=kb
        )

    # === ИНДИВИДУАЛЬНОЕ ЗАНЯТИЕ ===
    elif booking_type == "Индивидуальное занятие":
        pending_forms[message.from_user.id] = data

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить занятие — 2 000 ₽", callback_data="pay_individual")]
            ]
        )
        await message.answer(
            "✅ Форма заполнена!\n\n"
            "Теперь оплатите индивидуальное занятие:",
            reply_markup=kb
        )

    # === ДИАГНОСТИКА (бесплатная) ===
    else:
        with open("bookings.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {booking_type} | "
                f"{data['name']} | {data['school_class']} | {data['subject']} | "
                f"{data['contact']} | TelegramID: {message.from_user.id}\n"
            )

        await bot.send_message(
            ADMIN_ID,
            f"📩 Новая заявка ({booking_type}):\n\n"
            f"👤 ФИО: {data['name']}\n"
            f"🏫 Класс: {data['school_class']}\n"
            f"📘 Предмет: {data['subject']}\n"
            f"☎ Контакт: {data['contact']}\n"
            f"🆔 TelegramID: {message.from_user.id}"
        )

        await message.answer("✅ Ваша заявка успешно принята! Мы скоро свяжемся 💬")

    await state.clear()



@dp.callback_query(F.data == "pay_month")
async def pay_month(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Оплата месяца обучения", amount=10000 * 100)]  # *100 = копейки
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Месячный курс «ФизМатиум»",
        description="Доступ к групповым занятиям по математике или физике (1 месяц, 3 раза в неделю).",
        payload="month_course_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="month_course",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()

@dp.callback_query(F.data == "pay_combo")
async def pay_combo(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Оплата комбо-курса", amount=18000 * 100)]  # *100 = копейки
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Комбо-курс «ФизМатиум»",
        description="Доступ к групповым занятиям по математике и физике  (1 месяц, 6 раз в неделю).",
        payload="combo_course_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="combo_course",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()



@dp.callback_query(F.data == "pay_year")
async def pay_year(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Оплата годового курса", amount=75000 * 100)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Годовой курс «ФизМатиум»",
        description="Доступ к групповым занятиям по математике или физике  (1 год, 3 раза в неделю).",
        payload="year_course_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="year_course",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()

@dp.callback_query(F.data == "pay_individual")
async def pay_individual(callback: types.CallbackQuery):
    prices = [LabeledPrice(label="Индивидуальное занятие", amount=2000 * 100)]  # *100 = копейки
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Индивидуальное занятие «ФизМатиум»",
        description="90-минутное онлайн-занятие с преподавателем по выбранному предмету.",
        payload="individual_lesson_payment",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="individual_lesson",
        need_email=True,
        send_email_to_provider=True,
    )
    await callback.answer()



@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    payment = message.successful_payment
    user_id = message.from_user.id

    print("=== УСПЕШНАЯ ОПЛАТА ===")
    print("Сумма:", payment.total_amount / 100, payment.currency)

    # Проверяем, есть ли форма, ожидающая оплату
    data = pending_forms.pop(user_id, None)

    if data:
        # Отправляем админу заполненные данные
        await bot.send_message(
            ADMIN_ID,
            f"💰 Оплата подтверждена ({payment.invoice_payload})!\n\n"
            f"👤 ФИО: {data['name']}\n"
            f"🏫 Класс: {data['school_class']}\n"
            f"📘 Предмет: {data['subject']}\n"
            f"☎ Контакт: {data['contact']}\n"
            f"🆔 TelegramID: {user_id}\n\n"
            f"💳 Сумма: {payment.total_amount / 100} {payment.currency}"
        )

        # Сохраняем всё в bookings.txt
        with open("bookings.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {data['booking_type']} | "
                f"{data['name']} | {data['school_class']} | {data['subject']} | "
                f"{data['contact']} | TelegramID: {user_id} | "
                f"Оплачено: {payment.total_amount / 100} {payment.currency}\n"
            )

    await message.answer(
        "✅ Оплата успешно прошла!\n\n"
        "Спасибо за доверие 💙\n"
        "Мы уже видим ваш платёж и скоро активируем доступ."
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

@app.get("/physics_ege")
def get_physics_ege():
    return FileResponse("static/physics_ege.pdf", media_type="application/pdf")

@app.get("/physics_oge")
def get_physics_oge():
    return FileResponse("static/physics_oge.pdf", media_type="application/pdf")

@app.get("/stereometry")
def get_stereometry():
    return FileResponse("static/stereometry.pdf", media_type="application/pdf")

@app.get("/geometry")
def get_geometry():
    return FileResponse("static/geometry.pdf", media_type="application/pdf")

@app.get("/image_1")
def get_image_1():
    return FileResponse("static/1.jpg", media_type="image/jpeg")

@app.get("/image_2")
def get_image_2():
    return FileResponse("static/2.jpg", media_type="image/jpeg")

@app.get("/image_3")
def get_image_3():
    return FileResponse("static/3.jpg", media_type="image/jpeg")

@app.get("/image_4")
def get_image_4():
    return FileResponse("static/4.jpg", media_type="image/jpeg")

@app.get("/image_5")
def get_image_5():
    return FileResponse("static/5.jpg", media_type="image/jpeg")

@app.get("/image_6")
def get_image_6():
    return FileResponse("static/6.jpg", media_type="image/jpeg")

@app.get("/image_7")
def get_image_7():
    return FileResponse("static/7.jpg", media_type="image/jpeg")

@app.get("/image_8")
def get_image_8():
    return FileResponse("static/8.jpg", media_type="image/jpeg")

@app.get("/image_9")
def get_image_9():
    return FileResponse("static/9.jpg", media_type="image/jpeg")

@app.get("/image_10")
def get_image_10():
    return FileResponse("static/10.jpg", media_type="image/jpeg")



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
