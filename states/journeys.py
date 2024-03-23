from aiogram.dispatcher.filters.state import State, StatesGroup


class NewJourney(StatesGroup):
    name = State()
    description = State()
    location_count = State()
    locations = State()
    confirm = State()


class EditJourney(StatesGroup):
    name = State()
    description = State()
    location_count = State()
    locations = State()
    delete = State()


class CreateNote(StatesGroup):
    text = State()
    photo = State()
    file = State()
    confirm = State()


class JourneyActions(StatesGroup):
    my_location = State()
    new_task = State()
    confirm_new_task = State()
    delete_task = State()