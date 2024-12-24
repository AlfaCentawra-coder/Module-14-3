from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from crud_function import *
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = '7883671956:AAHsUyMrGEaMflW9nvuj0XmjF9oOHLjiprE'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = types.KeyboardButton('Рассчитать')
button_info = types.KeyboardButton('Информация')
button_buy = types.KeyboardButton('Купить')
button_register = types.KeyboardButton('Регистрация')
keyboard.add(button_calculate, button_info, button_buy, button_register)

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    products = get_all_products("initiate.db")
    dp.data["products"] = products
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(text='Регистрация')
async def sing_up(message: types.Message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    if not is_included(message.text, "initiate.db"):
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для возраста.')
        return
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], int(data['age']), "initiate.db")
    await message.answer("Регистрация завершена!")
    await state.finish()

@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    products = dp.data.get("products")

    if products:
        for product in products:
            product_id, title, description, price = product
            inline_keyboard = InlineKeyboardMarkup(row_width=1)
            inline_keyboard.add(InlineKeyboardButton(f"Buy {title}", callback_data=f"buy_{product_id}"))
            with open(f'product{product_id}.jpg', 'rb') as photo:
                await message.answer_photo(photo, f"Название: {title} | Описание: {description} | Цена: {price}", reply_markup=inline_keyboard)
    else:
        await message.answer("No products found.")

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def send_confirm_message(call: types.CallbackQuery):
    product_id = call.data.split("_")[1]
    await bot.answer_callback_query(call.id, text=f"You selected product with ID: {product_id}")
    await call.message.answer(f"Вы выбрали продукт с ID: {product_id}!")

class UserStates(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    activity = State()

@dp.message_handler(text='Рассчитать')
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст')
    await UserStates.age.set()

@dp.message_handler(state=UserStates.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для возраста.')
        return
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserStates.growth.set()

@dp.message_handler(state=UserStates.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для роста.')
        return
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserStates.weight.set()

@dp.message_handler(state=UserStates.weight)
async def set_activity(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для веса.')
        return
    await state.update_data(weight=message.text)
    await message.answer('Выберите свою активность \n'
                         'Минимальная активность 1.2 \n'
                         'Слабая активность 1.375 \n'
                         'Средняя активность 1.55 \n'
                         'Высокая активность 1.725 \n'
                         'Экстрa-активность 1.9')
    await UserStates.activity.set()

@dp.message_handler(state=UserStates.activity)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        activity = float(message.text)
        if activity not in [1.2, 1.375, 1.55, 1.725, 1.9]:
            raise ValueError
    except ValueError:
        await message.answer('Пожалуйста, выберите корректное значение активности.')
        return

    await state.update_data(activity=activity)
    data = await state.get_data()
    calories = (10 * float(data["weight"]) + 6.25 * float(data["growth"]) - 5 * float(data["age"]) - 161) * activity
    await message.answer(f'Необходимое количество каллорий в день для вас {calories}')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)