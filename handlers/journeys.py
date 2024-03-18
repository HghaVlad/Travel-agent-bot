from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link, decode_payload
from bot import dp
from filters import IsLogin, IsJourneyShare
from base_req import get_user_journeys, get_journeys_by_traveller, make_journey, claim_journey
from states import NewJourney
from keyboards import cancel_keyboard, journey_menu_keyboard, new_journey_keyboard, main_menu_keyboard, \
    see_journey_back, see_journey_next, share_journey, edit_journey
from utils import get_date

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
        print(journeys)
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


async def see_journey(message: Message):
    journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]

    location_text = "\n".join([f"<i>{location.name}</i> {location.start_date}-{location.end_date}" for location in journey.locations])
    keyboard = InlineKeyboardMarkup()
    step_button = InlineKeyboardButton(f"{user_journey_data[message.chat.id]['step'] + 1}/{len(user_journey_data[message.chat.id]['journeys'])}", callback_data="-")
    keyboard.add(see_journey_back, step_button, see_journey_next)
    if journey.user.telegram_id == str(message.chat.id):
        keyboard.add(edit_journey, share_journey)
    await message.edit_text("<b>Ваши путешествия</b>\n\n"
                         f"<b>Название:</b> {journey.name}\n"
                         f"<b>Описание:</b> {journey.description}\n"
                         f"<b>Автор:</b> {journey.user.name}\n"
                         f"<b>Статус:</b> {'Доступен друзьям' if journey.is_public else 'Приватный'}\n"
                         f"<b>Локации:</b>\n{location_text}", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Отмена", state=NewJourney)
async def cancel_edit(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Создание отменено", reply_markup=main_menu_keyboard)
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
            await message.answer(f"<b>Введите адрес, дату началы и дату окончания 1 локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")


@dp.message_handler(state=NewJourney.locations)
async def new_journey_location_name(message: Message, state: FSMContext):
    if len(message.text.split("/")) == 3:
        address, start_date, end_date = message.text.split("/")
        date1 = get_date(start_date)
        date2 = get_date(end_date)
        if date1 and date2:
            async with state.proxy() as data:
                data["locations"].append([address, date1, date2])
                print(data["location_count"])
                if len(data["locations"]) < data['location_count']:
                    await message.answer(
                        f"<b>Введите адрес, дату началы и дату окончания {len(data['locations'])+1} локации</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")
                else:

                    location_text = "\n".join([f"{data[0]} {data[1].strftime('%d.%m.%Y')}-{data[2].strftime('%d.%m.%Y')}" for data in data['locations']])
                    await message.answer("<b>Вы хотите создать новое путешествие?</b>\n\n"
                                         f"<b>Название:</b> {data['name']}\n"
                                         f"<b>Описание:</b> {data['description']}\n"
                                         f"<b>Локации:</b>\n{location_text}", reply_markup=new_journey_keyboard)
                    await NewJourney.confirm.set()
        else:
            await message.answer("Введите дату в верном формате")
    else:
        await message.answer("<b>Введите локацию в верном формате</b>\n<i>Например, 'Москва/01.01.2023/10.01.2023</i>")


@dp.message_handler(state=NewJourney.confirm)
async def new_journey_location_name(message: Message, state: FSMContext):
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
