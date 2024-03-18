from datetime import timedelta, datetime
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from bot import dp, bot
from filters import IsLogin
from states import EditProfileState, Profile
from base_req import get_user_data, update_user_value, delete_user, get_friends, is_friend, get_user_name, \
    is_sent_request, new_friend_request, get_friend_request, make_friends
from keyboards import my_profile_keyboard, profile_edit_keyboard, cancel_keyboard, gender_edit_keyboard, \
    delete_profile_keyboard, my_friends_keyboard, main_menu_keyboard


@dp.message_handler(IsLogin(), lambda message: message.text == "Мой профиль")
async def my_profile(message: Message):
    user_data = get_user_data(message.chat.id)
    gender = "Мужчина" if user_data.gender == "M" else "Женщина"
    await message.answer("<b>Ваш профиль</b>\n\n"
                         f"<b>Ваш id:</b> {message.chat.id}\n"
                         f"<b>Вас зовут:</b> {user_data.name}\n"
                         f"<b>Ваш пол:</b> {gender}\n"
                         f"<b>Вам</b> {user_data.age} <b>лет\n"
                         f"Ваша страна:</b> {user_data.country}\n"
                         f"<b>Ваш город:</b> {user_data.city}\n"
                         f"<b>Вы хотели бы посетить</b> {','.join(user_data.locations)}\n"
                         f"<b>Немного о вас:</b> {user_data.bio}\n", reply_markup=my_profile_keyboard)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith("my_profile"))
async def my_profile_inline(call: CallbackQuery):
    if call.data == "my_profile_edit":
        await call.message.answer(f"Что вы хотите изменить?", reply_markup=profile_edit_keyboard)

    elif call.data == "my_profile_edit_name":
        await EditProfileState.name.set()
        await call.message.delete()
        await call.message.answer(f"Введите новое имя:", reply_markup=cancel_keyboard)
    elif call.data == "my_profile_edit_age":
        await EditProfileState.age.set()
        await call.message.delete()
        await call.message.answer(f"Введите новый возраст:", reply_markup=cancel_keyboard)
    elif call.data == "my_profile_edit_gender":
        await EditProfileState.gender.set()
        await call.message.delete()
        await call.message.answer(f"Выберите пол:", reply_markup=gender_edit_keyboard)
    elif call.data == "my_profile_edit_country":
        await EditProfileState.country.set()
        await call.message.delete()
        await call.message.answer(f"Введите новую страну:", reply_markup=cancel_keyboard)
    elif call.data == "my_profile_edit_city":
        await EditProfileState.city.set()
        await call.message.delete()
        await call.message.answer(f"Введите новый город:", reply_markup=cancel_keyboard)
    elif call.data == "my_profile_edit_locations":
        await EditProfileState.locations.set()
        await call.message.delete()
        await call.message.answer(f"Введите новые локации через запятую:", reply_markup=cancel_keyboard)
    elif call.data == "my_profile_edit_bio":
        await EditProfileState.bio.set()
        await call.message.delete()
        await call.message.answer(f"Введите новую информацию о себе:", reply_markup=cancel_keyboard)

    elif call.data == "my_profile_delete":
        await Profile.delete_profile.set()
        await call.message.delete()
        await call.message.answer("<b>Вы уверены, что хотите удалить профиль?</b>", reply_markup=delete_profile_keyboard)


@dp.message_handler(lambda message: message.text == "Отмена", state=EditProfileState)
async def cancel_edit(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Редактирование отменено", reply_markup=ReplyKeyboardRemove())
    await my_profile(message)


@dp.message_handler(state=EditProfileState.name)
async def process_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Имя должно содержать не больше 50 символов.")
        return

    update_user_value(message.from_user.id, message.text, "name")
    await state.finish()
    await message.answer("Имя успешно изменено!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=EditProfileState.age)
async def process_age(message: Message, state: FSMContext):
    if message.text.isdigit() and 1 <= int(message.text) <= 100:
        await state.finish()
        update_user_value(message.from_user.id, int(message.text), "age")
        await message.answer("Возраст успешно изменен!", reply_markup=main_menu_keyboard)
        await my_profile(message)
        return

    await message.answer("Возраст должен быть целым числом от 1 до 100")


@dp.message_handler(state=EditProfileState.gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text not in ("Мужчина", "Женщина"):
        await message.answer("Пожалуйста, укажите пол корректно (Мужчина/Женщина).")
        return

    gender = "M"
    if message.text == "Женщина":
        gender = "F"
    update_user_value(message.from_user.id, gender, "gender")
    await state.finish()
    await message.answer("Пол успешно изменен!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=EditProfileState.country)
async def process_country(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Название страны не должно содержать больше 50 символов.")
        return

    update_user_value(message.from_user.id, message.text, "country")
    await state.finish()
    await message.answer("Страна успешно изменена!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=EditProfileState.city)
async def process_city(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Название города не должно содержать больше 50 символов.")
        return

    update_user_value(message.from_user.id, message.text, "city")
    await state.finish()
    await message.answer("Город успешно изменен!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=EditProfileState.locations)
async def process_locations(message: Message, state: FSMContext):
    locations = message.text.split(",")
    if len(locations) > 20:
        await message.answer("Вы можете ввести не более 20 локаций.")
        return
    if any(len(location) > 50 for location in locations):
        await message.answer("Название локации не должно содержать больше 50 символов.")
        return

    update_user_value(message.from_user.id, locations, "locations")
    await state.finish()
    await message.answer("Локации успешно изменены!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=EditProfileState.bio)
async def process_bio(message: Message, state: FSMContext):
    if len(message.text) > 500:
        await message.answer("Информация о вас должна содержать не более 500 символов.")
        return

    update_user_value(message.from_user.id, message.text, "bio")
    await state.finish()
    await message.answer("Информация о вас успешно изменена!", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(state=Profile.delete_profile)
async def profile_delete(message: Message, state: FSMContext):
    await state.finish()
    if message.text == "Да":
        await message.answer("<b>Пользователь был успешно удален</b>", reply_markup=main_menu_keyboard)
        delete_user(message.chat.id)

        return

    await message.answer("<b>Вы отменили удаление</b>", reply_markup=main_menu_keyboard)
    await my_profile(message)


@dp.message_handler(IsLogin(), lambda message: message.text == "Мои друзья")
async def my_friends(message: Message):
    user_friends = get_friends(message.chat.id)
    friend_list = '\n'.join([f"{user.name} - {user.telegram_id}" for user in user_friends])
    await message.answer("<b>Друзья\n"
                         f"У вас</b> {len(user_friends)} <b>друзей</b>\n\n"
                         f"{friend_list}", reply_markup=my_friends_keyboard)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith("my_friends"))
async def my_friends_inline(call: CallbackQuery):
    if call.data == "my_friends_add":
        await call.message.answer("<b>Введите Telegram ID пользователя, которого вы хотите добавить в друзья:</b>", reply_markup=cancel_keyboard)
        await Profile.add_friend.set()

    elif call.data == "my_friends_deny":
        await call.message.edit_text("<b>Вы отклонили заявку в друзья</b>")
    elif call.data.startswith("my_friends_new"):
        request_id = call.data.split("?")[1]
        print(request_id)
        friend_request = get_friend_request(int(request_id))
        seven_days_ago = datetime.now() - timedelta(days=7)
        if friend_request.date_created <= seven_days_ago:
            await call.message.edit_text("<b>Вы слишком поздно приняли заявку в друзья, попросите отправить ее еще раз</b>")
        else:
            if make_friends(friend_request):
                await call.message.edit_text("<b>Вы успешно добавили пользователя в друзья</b>")
            else:
                await call.message.edit_text("<b>Пользователь не найден</b>")


@dp.message_handler(state=Profile.add_friend)
async def add_friend(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await state.finish()
        await my_friends(message)
        return

    if message.text.isdigit():
        friend = get_user_data(message.text)
        if friend is None:
            await message.answer(f"<b>Пользователь с таким id не найден</b>")
        elif is_friend(message.chat.id, message.text):
            await message.answer(f"<b>Этот пользователь уже есть в вашем списке друзей</b>")
        elif is_sent_request(message.chat.id, message.text):
            await message.answer(f"<b>Вы уже подавали заявку. Новую заявку вы можете отправить только через 7 дней</b>")
        elif is_sent_request(message.text, message.chat.id):
            await message.answer(f"<b>Этот пользователь уже отправлял вам заявку в друзья</b>")
        else:
            request_id = new_friend_request(message.chat.id, message.text)
            await send_friend_request_notification(message.chat.id, message.text, request_id )
            await message.answer("<b>Вы отправили заявку в друзья</b>", reply_markup=ReplyKeyboardRemove())
            await state.finish()
            await my_friends(message)

    else:
        await message.answer("<b>Введите Telegram id в виде числа, например 3112313</b>")


async def send_friend_request_notification(telegram_id, friend_id, request_id):
    name = get_user_name(telegram_id)
    friend_request_keyboard = InlineKeyboardMarkup()
    approve_request = InlineKeyboardButton("Добавить", callback_data=f"my_friends_new?{request_id}")
    deny_request = InlineKeyboardButton("Отклонить", callback_data="my_friends_deny")
    friend_request_keyboard.add(approve_request, deny_request)

    await bot.send_message(friend_id, f"Пользователь {name[0]} отправил вам запрос в друзья. Хотите добавить его в друзья?", reply_markup=friend_request_keyboard)


@dp.message_handler()
async def text_type(message):
    print("here")
    await message.answer("g")