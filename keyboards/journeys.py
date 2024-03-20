from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

journey_menu_keyboard = InlineKeyboardMarkup(row_width=1)
see_journeys = InlineKeyboardButton("Просмотр путешествий", callback_data="journeys_see")
new_journey = InlineKeyboardButton("Создать путешествие", callback_data="journeys_new")
journey_menu_keyboard.add(see_journeys, new_journey)

see_journey_keyboard = InlineKeyboardMarkup()

confirm_keyboard = ReplyKeyboardMarkup()
confirm_keyboard.add("Да", "Нет")

see_journey_back = InlineKeyboardButton("⬅️", callback_data="journey_see_back")
see_journey_next = InlineKeyboardButton("➡️️", callback_data="journey_see_next")

share_journey = InlineKeyboardButton("Поделиться", callback_data="journey_share")
edit_journey = InlineKeyboardButton("Редактировать", callback_data="journey_edit")
address_journey = InlineKeyboardButton("Посмотреть адреса", callback_data="journey_address")
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
notes_type_keyboard.add(notes_type_text, notes_type_photo, notes_type_file)
