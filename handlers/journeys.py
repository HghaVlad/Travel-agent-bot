from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.utils.deep_linking import get_start_link, decode_payload
from bot import dp, bot
from filters import IsLogin, IsJourneyShare
from base_req import get_user_journeys, get_journeys_by_traveller, make_journey, claim_journey, \
    update_journey_name, update_journey_description, update_journey_status, update_journey_locations, delete_journey, \
    get_notes, create_note, change_note_public, get_location, delete_task, add_new_task, get_tasks, change_status_task, \
    get_user_debts, settle_expense, get_non_settled_expenses, get_user_expenses, add_transaction, get_journey_users
from states import NewJourney, EditJourney, CreateNote, JourneyActions, CreateExpense
from keyboards import cancel_keyboard, journey_menu_keyboard, confirm_keyboard, main_menu_keyboard, \
    see_journey_back, see_journey_next, share_journey, edit_journey, journey_edit_keyboard, journey_edit_status_keyboard,\
    address_journey, remove_journey, journey_delete_keyboard, notes_back, notes_next, notes_public, notes_private, \
    notes_delete, notes_journey, notes_journey_create, notes_type_keyboard, notes_back_to_journey, route_journey, \
    journey_comeback_keyboard, journey_route_keyboard, journey_route_change_zoom, journey_route_my_location,\
    weather_journey, journey_comeback_button, journey_weather_back, journey_weather_next, journey_task_keyboard, tasks_journey, \
    expenses_keyboard, expenses_journey, expenses_back_keyboard, debts_back_keyboard
from utils import get_date
from api.osm import get_address, route_between_locations
from api.weather import get_weather_forecast

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
        await call.message.edit_text(f"<b>Адреса локаций</b>\n\n{address_text}", reply_markup=journey_comeback_keyboard)
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

    elif call.data == 'journey_notes':
        journey_id = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id
        notes = get_notes(journey_id, call.message.chat.id)
        if len(notes) == 0:
            await call.answer("У вас еще нет заметок")
        else:
            user_journey_data[call.message.chat.id]["notes"] = notes
            user_journey_data[call.message.chat.id]["notes_step"] = 0
            await see_note(call.message)
    elif call.data == "journey_notes_back":
        if user_journey_data[call.message.chat.id]['notes_step'] > 0:
            user_journey_data[call.message.chat.id]['notes_step'] -= 1
            await see_note(call.message)
    elif call.data == "journey_notes_next":
        if user_journey_data[call.message.chat.id]['notes_step']+1 < len(user_journey_data[call.message.chat.id]["notes"]):
            user_journey_data[call.message.chat.id]['notes_step'] += 1
            await see_note(call.message)

    elif call.data == "journey_notes_crate":
        await call.message.edit_text("<b>Какой тип заметки вы хотите создать?</b>", reply_markup=notes_type_keyboard)
    elif call.data == "journey_notes_createText":
        await call.message.delete()
        await CreateNote.text.set()
        await call.message.answer("<b>Отправьте текст заметки</b>", reply_markup=cancel_keyboard)
    elif call.data == "journey_notes_createPhoto":
        await call.message.delete()
        await CreateNote.photo.set()
        await call.message.answer("<b>Отправьте фотографии</b>", reply_markup=cancel_keyboard)
    elif call.data == "journey_notes_createFile":
        await call.message.delete()
        await CreateNote.file.set()
        await call.message.answer("<b>Отправьте файл</b>", reply_markup=cancel_keyboard)

    elif call.data == "journey_notest_back_to_journey":
        await call.message.delete()
        await see_journey(call.message)
    elif call.data == "journey_notes_public":
        note_id = user_journey_data[call.message.chat.id]["notes"][user_journey_data[call.message.chat.id]["notes_step"]].id
        change_note_public(note_id, 1)
        await see_note(call.message)
    elif call.data == "journey_notes_private":
        note_id = user_journey_data[call.message.chat.id]["notes"][user_journey_data[call.message.chat.id]["notes_step"]].id
        change_note_public(note_id, 0)
        await see_note(call.message)

    elif call.data == "journey_make_route":
        keyboard = InlineKeyboardMarkup()
        for location in user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].locations:
            keyboard.add(InlineKeyboardButton(location.name, callback_data=f"journey_route_first_location?{location.id}"))
        keyboard.add(InlineKeyboardButton("Мое текущее местоположение", callback_data="journey_route_first_My"))
        await call.message.edit_text("<b>Выберите первую локацию</b>", reply_markup=keyboard)

    elif call.data == "journey_route_first_My":
        await call.message.delete()
        await JourneyActions.my_location.set()
        await call.message.answer("<b>Отправьте ваше местоположение</b>", reply_markup=journey_route_my_location)

    elif call.data.startswith("journey_route_first_location"):
        first_location = int(call.data.split("?")[1])
        user_journey_data[call.message.chat.id]["first_locations"] = first_location
        keyboard = InlineKeyboardMarkup()
        for location in user_journey_data[call.message.chat.id]['journeys'][
            user_journey_data[call.message.chat.id]['step']].locations:
            if location.id != first_location:
                keyboard.add(
                    InlineKeyboardButton(location.name, callback_data=f"journey_route_second_location?{location.id}"))
        await call.message.edit_text("<b>Выберите вторую локацию</b>", reply_markup=keyboard)

    elif call.data.startswith("journey_route_second_location"):
        second_location = int(call.data.split("?")[1])
        user_journey_data[call.message.chat.id]["second_location"] = second_location
        await call.message.edit_text("<b>Выберите способ передвижения</b>", reply_markup=journey_route_keyboard)

    elif call.data == "journey_make_route_car":
        user_journey_data[call.message.chat.id]["route_type"] = "driving-car"
        user_journey_data[call.message.chat.id]["zoom"] = 11
        await show_route(call.message)
    elif call.data == "journey_make_route_feet":
        user_journey_data[call.message.chat.id]["route_type"] = "foot-walking"
        user_journey_data[call.message.chat.id]["zoom"] = 11
        await show_route(call.message)
    elif call.data == "journey_make_route_cycling":
        user_journey_data[call.message.chat.id]["route_type"] = "cycling-road"
        user_journey_data[call.message.chat.id]["zoom"] = 11
        await show_route(call.message)
    elif call.data == "journey_route_zoom_lower":
        if user_journey_data[call.message.chat.id]["zoom"] > 1:
            user_journey_data[call.message.chat.id]["zoom"] -= 1
            await call.answer("Пожалуйста подождите")
            await show_route(call.message, edit=False)
    elif call.data == "journey_route_zoom_higher":
        if user_journey_data[call.message.chat.id]["zoom"] < 19:
            user_journey_data[call.message.chat.id]["zoom"] += 1
            await call.answer("Пожалуйста подождите")
            await show_route(call.message, edit=False)

    elif call.data == "journey_weather":
        locations = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].locations
        keyboard = InlineKeyboardMarkup(row_width=1)
        for i, location in enumerate(locations):
            keyboard.add(InlineKeyboardButton(location.name, callback_data=f"journey_weather_choose?{i}"))
        keyboard.add(journey_comeback_button)
        await call.message.edit_text("<b>Выберите локацию, в которой хотите посмотреть прогноз погоды на следующие 15 суток</b>", reply_markup=keyboard)
    elif call.data.startswith("journey_weather_choose"):
        i = int(call.data.split("?")[1])
        location = user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].locations[i]
        data = get_weather_forecast(location.lat, location.lon)
        user_journey_data[call.message.chat.id]["weather_list"] = data
        user_journey_data[call.message.chat.id]["weather_step"] = 0
        await see_weather(call.message)
    elif call.data == "journey_weather_back":
        if user_journey_data[call.message.chat.id]["weather_step"] > 0:
            user_journey_data[call.message.chat.id]["weather_step"] -=1
            await see_weather(call.message)
    elif call.data == "journey_weather_next":
        if user_journey_data[call.message.chat.id]["weather_step"] < 14:
            user_journey_data[call.message.chat.id]["weather_step"] +=1
            await see_weather(call.message)

    elif call.data == "journey_tasks":
        await call.message.edit_text("<b>Вы можете поставить цели на свое путешествие и отмечать выполненные задачи</b>", reply_markup=journey_task_keyboard)
    elif call.data == "journey_tasks_my":
        tasks = get_tasks(user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id, call.message.chat.id)
        if len(tasks) == 0:
            await call.answer("У вас еще нет целей")
        else:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for task in tasks:
                if task.is_completed == 1:
                    keyboard.add(InlineKeyboardButton(f"{task.name} - ✅", callback_data=f"journey_tasks_change_status?{task.id}"))
                else:
                    keyboard.add(InlineKeyboardButton(f"{task.name} - ☑️", callback_data=f"journey_tasks_change_status?{task.id}"))
            keyboard.add(journey_comeback_button)
            await call.message.edit_text("<b>Ваши цели:</b>\n<i>Нажимайте, чтобы изменить статус</i>", reply_markup=keyboard)

    elif call.data.startswith("journey_tasks_change_status"):
        task_id = call.data.split("?")[1]
        change_status_task(task_id)
        tasks = get_tasks(user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id, call.message.chat.id)
        keyboard = InlineKeyboardMarkup(row_width=1)
        for task in tasks:
            if task.is_completed == 1:
                keyboard.add(
                    InlineKeyboardButton(f"{task.name} - ✅", callback_data=f"journey_tasks_change_status?{task.id}"))
            else:
                keyboard.add(
                    InlineKeyboardButton(f"{task.name} - ☑️", callback_data=f"journey_tasks_change_status?{task.id}"))
        keyboard.add(journey_comeback_button)
        await call.message.edit_reply_markup(keyboard)

    elif call.data == "journey_tasks_add":
        await JourneyActions.new_task.set()
        await call.message.delete()
        await call.message.answer("<b>Введите новую цель</b>", reply_markup=cancel_keyboard)
    elif call.data == "journey_tasks_delete":
        tasks = get_tasks(
            user_journey_data[call.message.chat.id]['journeys'][user_journey_data[call.message.chat.id]['step']].id,
            call.message.chat.id)
        keyboard = InlineKeyboardMarkup(row_width=1)
        for task in tasks:
            keyboard.add(InlineKeyboardButton(f"{task.name}", callback_data=f"journey_tasks_delete?{task.id}"))
        keyboard.add(journey_comeback_button)
        await call.message.edit_text("<b>Выберите цель, которую хотите удалить</b>", reply_markup=keyboard)
    elif call.data.startswith("journey_tasks_delete?"):
        taskid = call.data.split("?")[1]
        await JourneyActions.delete_task.set()
        user_journey_data[call.message.chat.id]["delete_task"] = taskid
        await call.message.delete()
        await call.message.answer("<b>Вы хотите удалить эту цель?</b>", reply_markup=confirm_keyboard)

    elif call.data == "journey_expenses":
        await call.message.edit_text("<b>Управление расходами:</b>", reply_markup=expenses_keyboard)

    elif call.data == "journey_my_debts":
        debts = get_user_debts(call.message.chat.id)
        if len(debts) == 0:
            await call.answer("У вас еще нет долгов")
        else:
            debts_text = "\n".join([f"<b>{debt.name} - {debt.date} - {'✅' if debt.is_settled else ''}</b>\n<i>- {debt.amount} руб.</i><i>{debt.payer.name}</i>" for debt in debts])
            await call.message.edit_text(f"<b>Ваши долги:</b>\n\n{debts_text}", reply_markup=debts_back_keyboard)
    elif call.data == "journey_my_expenses":
        expenses = get_user_expenses(call.message.chat.id)
        if len(expenses) == 0:
            await call.answer("У вас еще нет трат")
        else:
            expenses_text = "\n".join([f"<b>{expense.name} - {expense.date}{' ✅ ' if expense.is_settled else ' '}</b><i>-{expense.amount}</i> руб. <i>{expense.payer.name}</i>" for expense in expenses])
            await call.message.edit_text(f"<b>Ваши траты</b>\n\n{expenses_text}", reply_markup=expenses_back_keyboard)
    elif call.data == "journey_expenses_settle":
        expenses = get_non_settled_expenses(call.message.chat.id)
        keyboard = InlineKeyboardMarkup()
        for expense in expenses:
            keyboard.add(InlineKeyboardButton(f"{expense.name} - {expense.debtor.name}", callback_data=f"journey_expense_settle?{expense.id}"))
        keyboard.add(InlineKeyboardButton("Назад к расходам", callback_data="journey_expenses"))
        await call.message.edit_text("<b>Выберите долг, который вам вернули</b>", reply_markup=keyboard)
    elif call.data.startswith("journey_expense_settle"):
        expense_id = int(call.data.split("?")[1])
        await call.message.delete()
        await JourneyActions.settle_expense.set()
        user_journey_data[call.message.chat.id]["expense_id"] = expense_id
        await call.message.answer("<b>Вы хотите отметить трату как зачтенную(вам вернули деньги)?</b>", reply_markup=confirm_keyboard)
    elif call.data == "journey_new_expense":
        await call.message.delete()
        await call.message.answer("<b>Введите название траты</b>", reply_markup=cancel_keyboard)
        await CreateExpense.name.set()


    elif call.data == "journeys_comeback":
        await see_journey(call.message)


async def see_journey(message: Message):
    journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]

    location_text = "\n".join([f"<i>{location.name}</i> {location.start_date}-{location.end_date}" for location in journey.locations])
    keyboard = InlineKeyboardMarkup()
    step_button = InlineKeyboardButton(f"{user_journey_data[message.chat.id]['step'] + 1}/{len(user_journey_data[message.chat.id]['journeys'])}", callback_data="-")
    keyboard.add(see_journey_back, step_button, see_journey_next)
    if journey.user.telegram_id == str(message.chat.id):
        keyboard.add(edit_journey, share_journey, remove_journey)
    keyboard.add(address_journey, route_journey, weather_journey, tasks_journey, expenses_journey, notes_journey, notes_journey_create)
    try:
        await message.edit_text("<b>Ваши путешествия</b>\n\n"
                                f"<b>Id путешествия:</b> {journey.id}\n"
                                f"<b>Название:</b> {journey.name}\n"
                                f"<b>Описание:</b> {journey.description}\n"
                                f"<b>Автор:</b> {journey.user.name}\n"
                                f"<b>Статус:</b> {'Доступен друзьям' if journey.is_public else 'Приватный'}\n"
                                f"<b>Локации:</b>\n{location_text}", reply_markup=keyboard)
    except:
        await message.answer("<b>Ваши путешествия</b>\n\n"
                                f"<b>Id путешествия:</b> {journey.id}\n"
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
                        data["locations"].append([address, date1, date2, requested_address['display_name'], requested_address["lon"], requested_address["lat"]])
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
                                                 f"<b>Локации:</b>\n{location_text}", reply_markup=confirm_keyboard)
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
                        data["locations"].append([address, date1, date2, requested_address['display_name'], requested_address["lon"], requested_address["lat"]])
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


async def see_note(message: Message):
    note = user_journey_data[message.chat.id]["notes"][user_journey_data[message.chat.id]["notes_step"]]
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(
        f"{user_journey_data[message.chat.id]['notes_step'] + 1}/{len(user_journey_data[message.chat.id]['notes'])}",
        callback_data="-")
    keyboard.add(notes_back, button, notes_next)
    if note.user.telegram_id == str(message.chat.id) and note.is_public == 1:
        keyboard.add(notes_private, notes_delete)
    elif note.user.telegram_id == str(message.chat.id):
        keyboard.add(notes_public, notes_delete)
    keyboard.add(notes_back_to_journey)
    await message.delete()
    if note.text:
        await bot.send_message(message.chat.id, note.text, reply_markup=keyboard)
    elif note.photo_file_id:
        await bot.send_photo(message.chat.id, note.photo_file_id, reply_markup=keyboard)
    else:
        await bot.send_document(message.chat.id, note.document_file_id, reply_markup=keyboard)


@dp.message_handler(state=CreateNote.text)
async def create_note_text(message: Message, state: FSMContext):
    note_text = message.text
    if len(note_text) > 4000:
        await message.answer("<b>Заметка слишком большая. Размер не должен превышать 4000 символов.")
    else:
        await message.answer(f"<b>Вы хотите создать заметку со следующим текстом?</b>\n\n<i>{note_text}</i>", reply_markup=confirm_keyboard)
        await state.update_data(text=note_text)
        await CreateNote.confirm.set()


@dp.message_handler(state=CreateNote.photo, content_types=["photo"])
async def create_note_photo(message: Message, state: FSMContext):
    photo = message.photo
    if photo:
        photo_id = photo[-1].file_id
        await bot.send_photo(message.chat.id, photo=photo_id, caption="<b>Вы хотите создать заметку со следующим изображением?</b>", reply_markup=confirm_keyboard)
        await state.update_data(photo=photo_id)
        await CreateNote.confirm.set()


@dp.message_handler(state=CreateNote.file, content_types=["document"])
async def create_note_file(message: Message, state: FSMContext):
    file = message.document
    if file:
        await bot.send_document(message.chat.id, document=file.file_id, caption="<b>Вы хотите создать заметку со следующим файлом?</b>", reply_markup=confirm_keyboard)
        await state.update_data(file=file.file_id)
        await CreateNote.confirm.set()
    else:
        await message.answer("<b>Документ не распознан</b>")


@dp.message_handler(state=CreateNote.confirm)
async def confirm_note_text(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        journey_id = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].id
        create_note(journey_id, message.chat.id, data.get("text"), data.get("photo"), data.get("file"))
        await message.answer("<b>Вы успешно создали заметку</b>", reply_markup=main_menu_keyboard)
        await state.finish()
        return

    await message.answer("<b>Вы отменили создание заметки</b>", reply_markup=main_menu_keyboard)
    await state.finish()


async def show_route(message: Message, edit=True):
    first_location = user_journey_data[message.chat.id]["first_locations"]
    second_location = user_journey_data[message.chat.id]["second_location"]
    route_type = user_journey_data[message.chat.id]["route_type"]
    zoom = user_journey_data[message.chat.id]["zoom"]
    way = "Машина"
    if route_type == "foot-walking":
        way = "Пешком"
    elif route_type == "cycling-road":
        way = "Велосипед"
    if first_location == "my":
        location1 = (user_journey_data[message.chat.id]["first_locations_lat"], user_journey_data[message.chat.id]["first_locations_lon"])
    else:
        address1 = get_location(first_location)
        location1 = (address1.lat, address1.lon)
    address2 = get_location(second_location)
    location2 = (address2.lat, address2.lon)
    if edit:
        await message.edit_text("<b>Пожалуйста подождите</b>")
    image, distance = route_between_locations(location1, location2, route_type, zoom)
    await message.delete()
    with open(image, "rb") as image:
        await bot.send_photo(message.chat.id, image, caption=f"<b>Маршрут от</b> {'Ваше текущее местоположение' if first_location == 'my' else address1.address}"
                                                             f"<b>до</b> {address2.address}\n"
                                                             f"<b>Расстояние:</b> {distance} метров\n"
                                                             f"<b>Способ передвижения:</b> {way}",
                             reply_markup=journey_route_change_zoom)


@dp.message_handler(state=JourneyActions.my_location, content_types=['location'])
async def journey_route_get_location(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.finish()
    user_journey_data[message.chat.id]["first_locations"] = "my"
    user_journey_data[message.chat.id]["first_locations_lat"] = lat
    user_journey_data[message.chat.id]["first_locations_lon"] = lon
    await message.answer("<b>Местоположение принято</b>", reply_markup=main_menu_keyboard)
    keyboard = InlineKeyboardMarkup()
    for location in user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].locations:
        keyboard.add(InlineKeyboardButton(location.name, callback_data=f"journey_route_second_location?{location.id}"))
    await message.answer("<b>Выберите вторую локацию</b>", reply_markup=keyboard)


@dp.message_handler(state=JourneyActions.my_location)
async def journey_route_get_location_text(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await state.finish()
        await message.answer("<b>Построение маршрута отменено</b>", reply_markup=main_menu_keyboard)
        await my_journeys(message)
    else:
        await message.answer("<b>Отправьте местоположение</b>")


async def see_weather(message: Message):
    data = user_journey_data[message.chat.id]["weather_list"][user_journey_data[message.chat.id]["weather_step"]]
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text=f"{user_journey_data[message.chat.id]['weather_step']+1}/15", callback_data="-")
    keyboard.add(journey_weather_back, button, journey_weather_next, journey_comeback_button)
    await message.edit_text(f"📅 <b>Дата:</b> {data[0]}\n"
                            f"🌡️ <b>Температура:</b> {data[1]}°C\n"
                            f"🌞 <b>Ощущается как:</b> {data[2]}°C\n"
                            f"💧 <b>Влажность:</b> {data[3]}%\n"
                            f"💨 <b>Скорость ветра: </b> {data[4]} км/ч\n"
                            f"🌅 <b>Восход:</b> {data[5]}\n"
                            f"🌇 <b>Закат:</b> {data[6]}"
                            , reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Отмена", state=JourneyActions.new_task)
async def cancel_new_task(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>Вы отменили добавление</b>", reply_markup=main_menu_keyboard)
    await see_journey(message)


@dp.message_handler(state=JourneyActions.new_task)
async def new_task(message: Message, state: FSMContext):
    await state.update_data(new_task=message.text)
    await message.answer("<b>Вы хотите создать новую цель?</b>", reply_markup=confirm_keyboard)
    await JourneyActions.confirm_new_task.set()


@dp.message_handler(state=JourneyActions.confirm_new_task)
async def confirm_new_task(message: Message, state: FSMContext):
    if message.text == "Да":
        journey_id = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']].id
        data = await state.get_data()
        add_new_task(journey_id, message.chat.id, data["new_task"])
        await message.answer("<b>Вы успешно добавили новую цель</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Добавление отменено</b>", reply_markup=main_menu_keyboard)
    await state.finish()
    await see_journey(message)


@dp.message_handler(state=JourneyActions.delete_task)
async def confirm_delete_task(message: Message, state: FSMContext):
    if message.text == "Да":
        delete_task(user_journey_data[message.chat.id]["delete_task"])
        await state.finish()
        await message.answer("<b>Вы успешно удалили цель</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Вы отменили удаление</b>", reply_markup=main_menu_keyboard)
    await state.finish()


@dp.message_handler(state=JourneyActions.settle_expense)
async def confirm_settle_expense(message: Message, state: FSMContext):
    if message.text == "Да":
        settle_expense(user_journey_data[message.chat.id]["expense_id"])
        await state.finish()
        await message.answer("<b>Вы успешно зачли трату</b>", reply_markup=main_menu_keyboard)
    else:
        await state.finish()
        await message.answer("<b>Вы отменили зачтение траты</b>", reply_markup=main_menu_keyboard)

    await message.answer("<b>Управление расходами:</b>", reply_markup=expenses_keyboard)


@dp.message_handler(lambda message: message.text == "Отмена", state=CreateExpense)
async def cancel_create_expense(message: Message, state: FSMContext):
    await message.answer("<b>Вы отменили создание траты</b>", reply_markup=main_menu_keyboard)
    await state.finish()
    await message.answer("<b>Управление расходами:</b>", reply_markup=expenses_keyboard)


@dp.message_handler(state=CreateExpense.name)
async def create_expense_name(message: Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("<b>Название расхода не должно превышать 50 символов</b>")
        return
    await state.update_data(name=message.text)
    await message.answer("<b>Введите сумму траты</b>")
    await CreateExpense.next()


@dp.message_handler(state=CreateExpense.amount)
async def create_expense_amount(message: Message, state: FSMContext):
    if message.text.isdigit() and int(message.text) > 0:
        journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]
        users = get_journey_users(journey.id)
        await state.update_data(amount=int(message.text), expenses_users=[], journey_users=users)
        keyboard = InlineKeyboardMarkup(row_width=2)
        for user in users:
            if user.telegram_id != message.chat.id:
                keyboard.add(InlineKeyboardButton(text=user.name, callback_data=f"journey_new_expense_user?{user.id}"))
        keyboard.add(InlineKeyboardButton("📝Создать трату", callback_data="journey_create_expense"))
        await message.answer("<b>Выберите пользователей для распределения расхода:</b>", reply_markup=keyboard)
        await CreateExpense.next()
    else:
        await message.answer("<b>Сумма траты должна быть целым числом большим 0</b>")


@dp.message_handler(state=CreateExpense.confirm)
async def confirm_create_expense(message: Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        journey = user_journey_data[message.chat.id]['journeys'][user_journey_data[message.chat.id]['step']]
        for user in data["expenses_users"]:
            add_transaction(message.chat.id, user, data["transaction_amount"], journey.id, data["name"])
        await message.answer("<b>Трата успешно создана</b>", reply_markup=main_menu_keyboard)
    else:
        await message.answer("<b>Вы отменили создание траты", reply_markup=main_menu_keyboard)
    await state.finish()
    await message.answer("<b>Управление расходами:</b>", reply_markup=expenses_keyboard)


@dp.callback_query_handler(state=CreateExpense)
async def create_expense_callback(call: CallbackQuery, state: FSMContext):
    if call.data.startswith("journey_new_expense_user"):
        userid = int(call.data.split("?")[1])
        data = await state.get_data()
        expenses_users = data["expenses_users"]
        journey_users = data["journey_users"]
        if userid in expenses_users:
            expenses_users.remove(userid)
        else:
            expenses_users.append(userid)
        await state.update_data(expenses_users=expenses_users)
        keyboard = InlineKeyboardMarkup(row_width=2)
        for user in journey_users:
            if user.telegram_id != call.message.chat.id:
                keyboard.add(InlineKeyboardButton(
                    text=f"{user.name} {'✅' if user.id in expenses_users else ''}", callback_data=f"journey_new_expense_user?{user.id}"))
        keyboard.add(InlineKeyboardButton("📝Создать трату", callback_data="journey_create_expense"))
        await call.message.edit_reply_markup(keyboard)

    elif call.data == "journey_create_expense":
        data = await state.get_data()
        expenses_users = data["expenses_users"]
        if len(expenses_users) == 0:
            await call.answer("Вы должны выбрать хотя бы одного пользователя")
        else:
            await call.message.delete()

            transaction_amount = data['amount'] // len(expenses_users)
            await call.message.answer("<b>Новая трата:</b>\n"
                                         f"<b>Название:</b> {data['name']}\n"
                                         f"<b>Общая сумма:</b> {data['amount']} руб.\n"
                                         f"<b>Количество пользователей:</b> {len(expenses_users)}\n"
                                         f"<b>Долг каждого: </b> {transaction_amount} руб.\n\n"
                                         f"<b>Вы подтверждаете создание?</b>", reply_markup=confirm_keyboard)
            await state.update_data(transaction_amount=transaction_amount)
            await CreateExpense.confirm.set()


@dp.message_handler()
async def any_text(message: Message):
    await message.answer("Welcome", reply_markup=main_menu_keyboard)


