from aiogram.types import ReplyKeyboardMarkup

reg_menu_keyboard = ReplyKeyboardMarkup()
reg_menu_keyboard.add("Регистрация")

main_menu_keyboard = ReplyKeyboardMarkup()
main_menu_keyboard.add("Мой профиль", "Мои друзья")
main_menu_keyboard.add("Мои путешествия")
main_menu_keyboard.add("Популярные путешествия", "Поиск попутчиков")


gender_keyboard = ReplyKeyboardMarkup()
gender_keyboard.add("Мужчина", "Женщина")

reg_end_keyboard = ReplyKeyboardMarkup()
reg_end_keyboard.add("Да", "Нет")
