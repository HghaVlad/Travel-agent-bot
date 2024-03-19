from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from base_req import get_user_name, make_user
from keyboards import reg_menu_keyboard, main_menu_keyboard, gender_keyboard, reg_end_keyboard
from states import RegistrationState
from filters import IsNotLink
from bot import dp


@dp.message_handler(IsNotLink(), commands=["start"])
async def start_message(message: Message):
    user = get_user_name(message.chat.id)
    if user is None:
        await message.answer(f"Привет, {message.from_user.first_name}, я бот Travel agent.\nС помощью меня вы сможете спланировать путешествия.")
        await message.answer("Вижу тебя нет в нашей базе, давай зарегистрируемся!", reply_markup=reg_menu_keyboard)
    else:
        text_menu = f"Привет, {user[0]}, я бот Travel agent.С помощью меня вы сможете спланировать путешествия."
        await message.answer(text_menu, reply_markup=main_menu_keyboard)


@dp.message_handler(lambda message: message.text == "Регистрация")
async def reg_start(message: Message):
    user = get_user_name(message.chat.id)
    if user is None:
        await RegistrationState.name.set()
        await message.answer("Как вас зовут?", reply_markup=ReplyKeyboardRemove())
        return

    await message.answer("Вы уже зарегистрированы", reply_markup=main_menu_keyboard)


@dp.message_handler(state=RegistrationState.name)
async def registration_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Имя должно содержать не больше 50 символов.")
        return

    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.age)
async def registration_age(message: Message, state: FSMContext):
    if message.text.isdigit() and 1 <= int(message.text) <= 100:
        await state.update_data(age=int(message.text))
        await message.answer("Укажите ваш пол (мужчина/женщина):", reply_markup=gender_keyboard)
        await RegistrationState.next()
        return

    await message.answer("Возраст должен быть целым числом от 1 до 100")


@dp.message_handler(state=RegistrationState.gender)
async def registration_gender(message: Message, state: FSMContext):

    if message.text not in ("Мужчина", "Женщина"):
        await message.answer("Укажите пол корректно (Мужчина/Женщина).", reply_markup=gender_keyboard)
        return

    await state.update_data(gender=message.text)
    await message.answer("Из какой вы страны?", reply_markup=ReplyKeyboardRemove())
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.country)
async def registration_country(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Название страны не должно содержать больше 50 символов")
        return

    await state.update_data(country=message.text)
    await message.answer("Из какого вы города?", reply_markup=ReplyKeyboardRemove())
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.city)
async def registration_city(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Название города не должно содержать больше 50 символов")
        return

    await state.update_data(city=message.text)
    await message.answer("Какие места вы хотели бы посетить? <i>Вводите города через запятую без пробелов</i>", reply_markup=ReplyKeyboardRemove())
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.locations)
async def registration_locations(message: Message, state: FSMContext):
    locations = message.text.split(",")
    if len(locations) > 20:
        await message.answer("Вы можете ввести не больше 20 локаций")
        return
    if max(map(lambda x: len(x), locations)) > 50:
        await message.answer("Название локации не должно содержать больше 50 символов")
        return

    await state.update_data(locations=message.text)
    await message.answer("Укажите описание вашего профиля")
    await RegistrationState.next()
    print("df")


@dp.message_handler(state=RegistrationState.bio)
async def registration_bio(message: Message, state: FSMContext):
    if len(message.text) > 500:
        await message.answer("Информация о вас должна содержать не больше 500 символов")
        return

    await state.update_data(bio=message.text)
    data = await state.get_data()
    await message.answer(
        "<b>Отлично, проверьте введенные данные:</b>\n\n"
        f"<b>Вас зовут:</b> {data['name']}\n"
        f"<b>Вам</b> {data['age']} <b>лет</b>\n"
        f"<b>Пол:</b> {data['gender']}\n"
        f"<b>Ваша страна:</b> {data['country']}\n"
        f"<b>Ваш город:</b> {data['city']}\n"
        f"<b>Вы хотели бы посетить:</b> {data['locations']}\n"
        f"<b>Немного о вас:</b> {data['bio']}\n\n"
        "<b>Регистрируемся?</b>",
        reply_markup=reg_end_keyboard)

    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.confirm)
async def registration_confirm(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        telegram_id = message.chat.id
        make_user(data, telegram_id)

        await message.answer("<b>Вы успешно зарегистрировались</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Регистрация отменена</b>", reply_markup=reg_menu_keyboard)

    await state.finish()
