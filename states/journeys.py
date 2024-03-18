from aiogram.dispatcher.filters.state import State, StatesGroup


class NewJourney(StatesGroup):
    name = State()
    description = State()
    location_count = State()
    locations = State()
    confirm = State()
