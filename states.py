from aiogram.dispatcher.filters.state import State, StatesGroup

class ProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_additional_info = State()

class EditProfileStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_value = State()

class ClassStates(StatesGroup):
    waiting_for_class_name = State()
    waiting_for_class_id = State()

class HomeworkStates(StatesGroup):
    waiting_for_subject_choice = State()
    waiting_for_subject_name = State()
    waiting_for_homework_text = State()

class InformationStates(StatesGroup):
    waiting_for_information = State()

class PersonalHomeworkStates(StatesGroup):
    waiting_for_personal_subject = State()
    waiting_for_personal_homework = State()