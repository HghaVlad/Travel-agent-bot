from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

journey_menu_keyboard = InlineKeyboardMarkup(row_width=1)
see_journeys = InlineKeyboardButton("Просмотр путешествий", callback_data="journeys_see")
new_journey = InlineKeyboardButton("Создать путешествие", callback_data="journeys_new")
journey_menu_keyboard.add(see_journeys, new_journey)

see_journey_keyboard = InlineKeyboardMarkup()

confirm_keyboard = ReplyKeyboardMarkup()
confirm_keyboard.add("Да", "Нет")

see_journey_back = InlineKeyboardButton("⬅️", callback_data="journey_see_back")
see_journey_next = InlineKeyboardButton("➡️️", callback_data="journey_see_next")

journey_comeback_keyboard = InlineKeyboardMarkup()
journey_comeback_button = InlineKeyboardButton("Вернуться к путешествию", callback_data="journeys_comeback")
journey_comeback_keyboard.add(journey_comeback_button)

share_journey = InlineKeyboardButton("Поделиться", callback_data="journey_share")
edit_journey = InlineKeyboardButton("Редактировать", callback_data="journey_edit")
address_journey = InlineKeyboardButton("Адреса", callback_data="journey_address")
route_journey = InlineKeyboardButton("Построить маршрут", callback_data="journey_make_route")
weather_journey = InlineKeyboardButton("Погода", callback_data="journey_weather")
tasks_journey = InlineKeyboardButton("Цели", callback_data="journey_tasks")
expenses_journey = InlineKeyboardButton(text="Расходы", callback_data="journey_expenses")
remove_journey = InlineKeyboardButton("Удалить", callback_data="journey_delete")
notes_journey = InlineKeyboardButton("Заметки", callback_data="journey_notes")
notes_journey_create = InlineKeyboardButton("Создать заметку", callback_data="journey_notes_crate")

journey_delete_keyboard = ReplyKeyboardMarkup()
journey_delete_keyboard.add("Да", "Нет")

journey_edit_keyboard = InlineKeyboardMarkup()
journey_edit_name = InlineKeyboardButton("Название", callback_data="journey_edit_name")
journey_edit_description = InlineKeyboardButton("Описание", callback_data="journey_edit_description")
journey_edit_status = InlineKeyboardButton("Статус", callback_data="journey_edit_status")
journey_edit_locations = InlineKeyboardButton("Локации", callback_data="journey_edit_locations")
journey_edit_keyboard.row(journey_edit_name, journey_edit_description)
journey_edit_keyboard.row(journey_edit_status, journey_edit_locations)
journey_edit_keyboard.add(journey_comeback_button)

journey_edit_status_keyboard = InlineKeyboardMarkup(row_width=2)
edit_status_public = InlineKeyboardButton("Доступен друзьям", callback_data="journey_edit_status_public")
edit_status_private = InlineKeyboardButton("Приватный", callback_data="journey_edit_status_private")
journey_edit_status_keyboard.add(edit_status_public, edit_status_private)


notes_back = InlineKeyboardButton("⬅️", callback_data="journey_notes_back")
notes_next = InlineKeyboardButton("➡️️", callback_data="journey_notes_next")
notes_back_to_journey = InlineKeyboardButton("Вернуться к путешествию", callback_data="journey_notest_back_to_journey")
notes_delete = InlineKeyboardButton("Удалить", callback_data="journey_notes_delete")
notes_public = InlineKeyboardButton("Сделать публичной", callback_data="journey_notes_public")
notes_private = InlineKeyboardButton("Сделать приватной", callback_data="journey_notes_private")

notes_type_keyboard = InlineKeyboardMarkup()
notes_type_text = InlineKeyboardButton("Текст", callback_data="journey_notes_createText")
notes_type_photo = InlineKeyboardButton("Фото", callback_data="journey_notes_createPhoto")
notes_type_file = InlineKeyboardButton("Файл", callback_data="journey_notes_createFile")
notes_type_keyboard.add(notes_type_text, notes_type_photo, notes_type_file, journey_comeback_button)


journey_route_keyboard = InlineKeyboardMarkup(row_width=1)
journey_route_car = InlineKeyboardButton("Машина", callback_data="journey_make_route_car")
journey_route_feet = InlineKeyboardButton("Пешком", callback_data="journey_make_route_feet")
journey_route_cycling = InlineKeyboardButton("Велосипед", callback_data="journey_make_route_cycling")
journey_route_keyboard.add(journey_route_car, journey_route_feet, journey_route_cycling, journey_comeback_button)

journey_route_change_zoom = InlineKeyboardMarkup(row_width=2)
journey_route_zoom_lower = InlineKeyboardButton("Уменьшить масштаб", callback_data="journey_route_zoom_lower")
journey_route_zoom_higher = InlineKeyboardButton("Увеличить масштаб", callback_data="journey_route_zoom_higher")
journey_route_change_zoom.add(journey_route_zoom_lower, journey_route_zoom_higher, journey_comeback_button)

journey_route_my_location = ReplyKeyboardMarkup()
journey_route_my_location.add(KeyboardButton("Отправить местолположение", request_location=True))
journey_route_my_location.add("Отмена")

journey_weather_back = InlineKeyboardButton("⬅️", callback_data="journey_weather_back")
journey_weather_next = InlineKeyboardButton("➡️️", callback_data="journey_weather_next")

journey_task_keyboard = InlineKeyboardMarkup()
journey_tasks_delete = InlineKeyboardButton('Удалить цель', callback_data="journey_tasks_delete")
journey_tasks_add = InlineKeyboardButton("Добавить цель", callback_data="journey_tasks_add")
journey_task_keyboard.row(InlineKeyboardButton("Мои цели", callback_data="journey_tasks_my"))
journey_task_keyboard.row(journey_tasks_add, journey_tasks_delete)
journey_task_keyboard.row(journey_comeback_button)

expenses_keyboard = InlineKeyboardMarkup(row_width=2)
my_debts = InlineKeyboardButton(text="Мои долги", callback_data="journey_my_debts")
my_expenses = InlineKeyboardButton(text="Мои траты", callback_data="journey_my_expenses")
expenses_keyboard.add(my_debts, my_expenses)
expenses_keyboard.row(InlineKeyboardButton(text="Создать новую трату", callback_data="journey_new_expense"))
expenses_keyboard.row(journey_comeback_button)

expenses_back_keyboard = InlineKeyboardMarkup()
expenses_back_keyboard.add(InlineKeyboardButton("Отметить трату выплаченной", callback_data="journey_expenses_settle"))
expenses_back_keyboard.add(InlineKeyboardButton("Назад к расходам", callback_data="journey_expenses"))

debts_back_keyboard = InlineKeyboardMarkup()
debts_back_keyboard.add(InlineKeyboardButton("Назад к расходам", callback_data="journey_expenses"))