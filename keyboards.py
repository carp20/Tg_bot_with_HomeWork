from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(user_status: str):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton("👤 Мой профиль"))
    keyboard.add(KeyboardButton("📚 Моё ДЗ"))
    
    if user_status in ["Owner", "Admin", "Staff"]:
        keyboard.add(KeyboardButton("⚙️ Админ-панель"))
    
    keyboard.add(KeyboardButton("🏫 Класс"), KeyboardButton("ℹ️ Информация класса"))
    keyboard.add(KeyboardButton("📝 ДЗ класса"))
    
    return keyboard

def get_admin_keyboard(user_status: str):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton("👥 Управление пользователями"))
    keyboard.add(KeyboardButton("🏫 Управление классами"))
    
    if user_status in ["Owner", "Admin"]:
        keyboard.add(KeyboardButton("🔧 Изменить статусы"))
    
    keyboard.add(KeyboardButton("⬅️ Назад"))
    
    return keyboard

def get_profile_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("✏️ Редактировать профиль"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_edit_profile_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("Дата рождения"),
        KeyboardButton("Телефон"),
        KeyboardButton("Email"),
        KeyboardButton("Доп. информация")
    )
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_class_keyboard(team_role: str = None):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton("Вступить в класс"))
    
    if team_role:
        keyboard.add(KeyboardButton("Покинуть класс"))
        if team_role in ["староста", "помощник старосты"]:
            keyboard.add(KeyboardButton("Управление классом"))
    
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_class_management_keyboard(team_role: str):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add(KeyboardButton("Изменить ДЗ"))
    keyboard.add(KeyboardButton("Изменить информацию"))
    keyboard.add(KeyboardButton("Заявки на вступление"))
    keyboard.add(KeyboardButton("Участники класса"))
    
    if team_role == "староста":
        keyboard.add(KeyboardButton("Назначить помощника"))
    
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_homework_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📚 Все предметы"))
    keyboard.add(KeyboardButton("🔍 Конкретный предмет"))
    keyboard.add(KeyboardButton("➕ Добавить личное ДЗ"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_homework_edit_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Выбрать из списка"))
    keyboard.add(KeyboardButton("Написать самому"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def get_yes_no_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton("✅ Да"), KeyboardButton("❌ Нет"))
    return keyboard

def get_status_keyboard(current_status: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    statuses = ["Owner", "Admin", "Staff", "Member"]
    for status in statuses:
        if status != "Owner" or current_status == "Owner":
            callback_data = f"set_status_{status}"
            keyboard.insert(InlineKeyboardButton(
                text=f"{'✅ ' if status == current_status else ''}{status}",
                callback_data=callback_data
            ))
    
    return keyboard

def get_team_role_keyboard(current_role: str = None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    roles = ["староста", "помощник старосты", "участник"]
    for role in roles:
        callback_data = f"set_role_{role}"
        keyboard.insert(InlineKeyboardButton(
            text=f"{'✅ ' if role == current_role else ''}{role}",
            callback_data=callback_data
        ))
    
    return keyboard

def get_join_request_keyboard(request_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_request_{request_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_request_{request_id}")
    )
    return keyboard

def get_member_management_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👑 Изменить роль", callback_data=f"change_role_{user_id}"),
        InlineKeyboardButton("❌ Удалить", callback_data=f"remove_member_{user_id}")
    )
    return keyboard