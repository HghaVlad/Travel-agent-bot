from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link, decode_payload
from bot import dp
from filters import IsLogin, IsJourneyShare
from base_req import get_user_journeys, get_journeys_by_traveller, make_journey, claim_journey, \
    update_journey_name, update_journey_description, update_journey_status, update_journey_locations, delete_journey
from states import NewJourney, EditJourney
from keyboards import cancel_keyboard, journey_menu_keyboard, new_journey_keyboard, main_menu_keyboard, \
    see_journey_back, see_journey_next, share_journey, edit_journey, journey_edit_keyboard, journey_edit_status_keyboard,\
    address_journey, remove_journey, journey_delete_keyboard
from utils import get_date
from api.openstreetmap import get_address

user_journey_data = {}


@dp.message_handler(IsLogin(), lambda message: message.text == "Мои путешествия")
async def my_journeys(message: Message):
    journeys, friends_journeys, travelers_journeys = get_user_journeys(message.chat.id)
    await message.answer("<b>Ваши путешествия</b>\n\n"
                         f"<b>Вы создали</b> {len(journeys)} <b>путешествий</b>\n"
                         f"<b>У вас есть доступ к </b>{len(friends_journeys)}<b> путешествию ваших друзей</b>\n"
                         f"<b>Вы добавили</b> {len(travelers_journeys)} <b>чужих путешествий</b>", reply_markup=journey_menu_keyboard)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith("journey"))
async def journeys_callback(call: CallbackQuery):
    if call.data == "journeys_see":
        journeys = get_journeys_by_traveller(call.message.chat.id)
        if len(journeys) == 0:
            await call.answer("У вас нет путешествий")
        else:
            user_journey_data.update({call.message.chat.id: {"journeys": journeys, "step": 0}})
            await see_journey(call.message)

    if call.data == "journeys_new":
        await NewJourney.name.set()
        await call.message.answer("<b>Введите название нового путешествия:</b>", reply_markup=cancel_keyboard)
    elif call.data == "journey_see_back":
        if user_journey_data[call.message.chat.id]['step'] > 0:
            user_journey_data[call.message.chat.id]['step'] -= 1
            await see_journey(call.message)
    elif call.data == "journey_see_next":
        if user_journey_data[call.message.chat.id]['step']+1 < len(user_journey_data[call.message.chat.id]["journeys"]):
            user_journey_data[call.message.chat.id]['step'] += 1
            await see_journey(call.message)

    elif call.data == "journey_share":
        journey_id = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id
        link = await get_start_link(f"journey_share?{journey_id}", encode=True)
        await call.message.answer("<b>Поделитесь этой ссылкой с другими пользователями, чтобы они получили доступ "
                                  f"просмотру путешествия:</b>\n<a href='{link}'>{link}</a>")

    elif call.data == "journey_address":
        locations = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].locations
        address_text = "\n".join([f"<i>{location.name}</i> - {location.address}" for location in locations])
        await call.message.answer(f"<b>Адреса локаций</b>\n\n{address_text}")
    elif call.data == 'journey_delete':
        await call.message.delete()
        await EditJourney.delete.set()
        await call.message.answer("<b>Вы хотите удалить это путешествие?</b>", reply_markup=journey_delete_keyboard)

    elif call.data == "journey_edit":
        await call.message.edit_text("<b>Выберите что вы хотите изменить</b>", reply_markup=journey_edit_keyboard)
    if call.data == "journey_edit_name":
        await call.message.delete()
        await call.message.answer("<b>Введите новое название путешествия:</b>", reply_markup=cancel_keyboard)
        await EditJourney.name.set()
    elif call.data == "journey_edit_description":
        await call.message.delete()
        await call.message.answer("<b>Введите новое описание путешествия:</b>", reply_markup=cancel_keyboard)
        await EditJourney.description.set()
    elif call.data == "journey_edit_status":
        await call.message.edit_text("<b>Выберите новый статус путешествия:</b>", reply_markup=journey_edit_status_keyboard)
    elif call.data == "journey_edit_locations":
        await call.message.delete()
        await call.message.answer("<b>Сколько локаций вы хотите посетить?</b>", reply_markup=cancel_keyboard)
        await EditJourney.location_count.set()
    elif call.data == "journey_edit_status_public":
        journey_id = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id
        update_journey_status(journey_id, 1)
        await call.message.edit_text(f"Статус путешествия изменен")
        await see_journey(call.message)
    elif call.data == "journey_edit_status_private":
        journey_id = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id
        update_journey_status(journey_id, 0)
        await call.message.edit_text(f"Статус путешествия изменен")
        await see_journey(call.message)


async def see_journey(message: Message):
    journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]

    location_text = "\n".join([f"<i>{location.name}</i> {location.start_date}-{location.end_date}" for location in journey.locations])
    keyboard = InlineKeyboardMarkup()
    step_button = InlineKeyboardButton(f"{user_journey_data[message.chat.id]['step'] + 1}/{len(user_journey_data[message.chat.id]['journeys'])}", callback_data="-")
    keyboard.add(see_journey_back, step_button, see_journey_next)
    if journey.user.telegram_id == str(message.chat.id):
        keyboard.add(edit_journey, share_journey, remove_journey)
    keyboard.add(address_journey)
    await message.edit_text("<b>Ваши путешествия</b>\n\n"
                            f"<b>Название:</b> {journey.name}\n"
                            f"<b>Описание:</b> {journey.description}\n"
                            f"<b>Автор:</b> {journey.user.name}\n"
                            f"<b>Статус:</b> {'Доступен друзьям' if journey.is_public else 'Приватный'}\n"
                            f"<b>Локации:</b>\n{location_text}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Отмена", state=NewJourney)
async def cancel_create(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>Создание отменено</b>", reply_markup=main_menu_keyboard)
    await my_journeys(message)


@dp.message_handler(state=NewJourney.name)
async def new_journey_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("<b>Название не должно содержать больше 50 символов</b>")
        return

    await state.update_data(name=message.text)
    await message.answer("<b>Введите описание:</b>")
    await NewJourney.next()


@dp.message_handler(state=NewJourney.description)
async def new_journey_description(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer("<b>Описание не должно содержать больше 200 символов</b>")
        return

    await state.update_data(description=message.text)
    await message.answer("Сколько локаций вы хотите посетить?")
    await NewJourney.next()


@dp.message_handler(state=NewJourney.location_count)
async def new_journey_description(message: Message, state: FSMContext):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 16:
            await state.update_data(location_count=int(message.text))
            await NewJourney.locations.set()
            await state.update_data(locations=[])
            await message.answer("<b>Вводите локации в том порядке, в котором вы хотите их посетить</b>\n<i>Дата окончания первой локации должна быть раньше чем дата начала второй</i>")
            await message.answer(f"<b>Введите адрес, дату начала и дату окончания 1 локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")


@dp.message_handler(state=NewJourney.locations)
async def new_journey_location_name(message: Message, state: FSMContext):
    if len(message.text.split("/")) == 3:
        address, start_date, end_date = message.text.split("/")
        requested_address = get_address(address)
        if requested_address:
            date1 = get_date(start_date)
            date2 = get_date(end_date)
            if date1 and date2:
                async with state.proxy() as data:
                    if len(data["locations"]) > 0:
                        cond = data["locations"][-1][2] <= date1 <= date2
                    else:
                        cond = date1 <= date2
                    if cond:
                        data["locations"].append([address, date1, date2, requested_address['display_name']])
                        if len(data["locations"]) < data['location_count']:
                            await message.answer(f"<b>Найдена следующая локация:</b> {requested_address['display_name']}")
                            await message.answer(
                                f"<b>Введите адрес, дату начала и дату окончания {len(data['locations'])+1} локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")
                        else:
                            await message.answer(f"<b>Найдена следующая локация:</b> {requested_address['display_name']}")
                            location_text = "\n".join([f"{data[0]} {data[1].strftime('%d.%m.%Y')}-{data[2].strftime('%d.%m.%Y')}" for data in data['locations']])
                            await message.answer("<b>Вы хотите создать новое путешествие?</b>\n\n"
                                                 f"<b>Название:</b> {data['name']}\n"
                                                 f"<b>Описание:</b> {data['description']}\n"
                                                 f"<b>Локации:</b>\n{location_text}", reply_markup=new_journey_keyboard)
                            await NewJourney.confirm.set()
                    elif date2 < date1:
                        await message.answer("<b>Дата окончания должна быть позже даты начала</b>")
                    else:
                        await message.answer("<b>Дата начала новой локации должна быть позже даты окончания предыдущей</b>")

            else:
                await message.answer("Введите дату в верном формате")
        else:
            await message.answer("<b>Адрес не распознан. Проверьте введенные данные</b>")

    else:
        await message.answer("<b>Введите локацию в верном формате</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")


@dp.message_handler(state=NewJourney.confirm)
async def new_journey_confirm(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        make_journey(data, message.chat.id)
        await message.answer("<b>Вы успешно добавили путешествие</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Вы отменили добавление путешествия</b>", reply_markup=main_menu_keyboard)

    await state.finish()


@dp.message_handler(IsLogin(), IsJourneyShare(), commands=['start'])
async def claim_shared_journey(message: Message):
    args = message.get_args()
    payload = decode_payload(args)
    if claim_journey(message.chat.id, int(payload.split("?")[1])):
        await message.answer("<b>Вы успешно добавили путешествие к себе в библиотеку</b>")
    else:
        await message.answer("<b>Путешествие уже и так есть в вашей библиотеке</b>")


@dp.message_handler(lambda message: message.text == "Отмена", state=EditJourney)
async def cancel_update_journey(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>Редактирование отменено</b>", reply_markup=main_menu_keyboard)
    await my_journeys(message)


@dp.message_handler(state=EditJourney.name)
async def edit_journey_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("<b>Название не должно содержать больше 50 символов</b>")
        return

    journey_id = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].id
    update_journey_name(journey_id, message.text)
    await message.answer("<b>Название успешно изменено</b>", reply_markup=main_menu_keyboard)
    await state.finish()


@dp.message_handler(state=EditJourney.description)
async def edit_journey_description(message: Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer("<b>Описание не должно содержать больше 200 символов</b>")
        return

    journey_id = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].id
    update_journey_description(journey_id, message.text)
    await message.answer("<b>Описание успешно изменено</b>", reply_markup=main_menu_keyboard)
    await state.finish()


@dp.message_handler(state=EditJourney.location_count)
async def edit_journey_location_count(message: Message, state: FSMContext):
    if message.text.isdigit():
        location_count = int(message.text)
        if 1 <= location_count <= 16:
            await state.update_data(location_count=location_count, locations=[])
            await message.answer("<b>Введите адрес, дату начала и дату окончания 1 локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")
            await EditJourney.locations.set()
        else:
            await message.answer("<b>Введите число от 1 до 16</b>")
    else:
        await message.answer("<b>Введите число</b>")


@dp.message_handler(state=EditJourney.locations)
async def edit_journey_location_name(message: Message, state: FSMContext):
    if len(message.text.split("/")) == 3:
        address, start_date, end_date = message.text.split("/")
        requested_address = get_address(address)
        if requested_address:
            date1 = get_date(start_date)
            date2 = get_date(end_date)
            if date1 and date2:
                async with state.proxy() as data:
                    if len(data["locations"]) > 0:
                        cond = data["locations"][-1][2] <= date1 <= date2
                    else:
                        cond = date1 <= date2
                    if cond:
                        data["locations"].append([address, date1, date2, requested_address['display_name']])
                        if len(data["locations"]) < data['location_count']:
                            await message.answer(f"<b>Найдена следующая локация:</b> {requested_address['display_name']}")
                            await message.answer(
                                f"<b>Введите адрес, дату начала и дату окончания {len(data['locations'])+1} локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")
                        else:
                            journey_id = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].id
                            update_journey_locations(journey_id, data["locations"], message.chat.id)
                            await message.answer(f"<b>Найдена следующая локация:</b> {requested_address['display_name']}")
                            await message.answer("<b>Локации успешно изменены</b>", reply_markup=main_menu_keyboard)
                            await state.finish()
                    elif date2 < date1:
                        await message.answer("<b>Дата окончания должна быть позже даты начала</b>")
                    else:
                        await message.answer("<b>Дата начала новой локации должна быть позже даты окончания предыдущей</b>")

            else:
                await message.answer("<b>Введите дату в верном формате</b>")
        else:
            await message.answer("<b>Адрес не распознан. Проверьте введенные данные</b>")
    else:
        await message.answer("<b>Введите локацию в верном формате</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")


@dp.message_handler(state=EditJourney.delete)
async def edit_journey_delete(message: Message, state: FSMContext):
    if message.text == "Да":
        journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]
        delete_journey(journey)
        await message.answer("<b>Вы успешно удалили путешествие</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Вы отменили удаление путешествия</b>", reply_markup=main_menu_keyboard)

    await state.finish()