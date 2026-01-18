import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from config import BOT_TOKEN, ADMIN_IDS, OWNER_ID, PROJECT_STATUSES, TEAM_ROLES
from database import db
from states import *
from keyboards import *
from utils import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ========== COMMON HANDLERS ==========
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("👋 Добро пожаловать! Для начала создайте свой профиль.\nВведите ваше имя:")
        await ProfileStates.waiting_for_name.set()
    else:
        await message.answer(
            f"👋 С возвращением, {user['name']}!",
            reply_markup=get_main_keyboard(user.get("projectStatus", "Member"))
        )

@dp.message_handler(state=ProfileStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id
    
    # Создаем профиль с минимальными данными
    db.create_user_profile(user_id, name)
    
    # Устанавливаем статус Owner для указанного пользователя
    if user_id == OWNER_ID:
        db.update_user_status(user_id, "Owner")
    
    await state.finish()
    await message.answer(
        f"✅ Профиль создан! Добро пожаловать, {name}!\n"
        f"Вы можете заполнить дополнительные данные в разделе 'Мой профиль'.",
        reply_markup=get_main_keyboard("Member")
    )

@dp.message_handler(lambda message: message.text == "⬅️ Назад")
async def cmd_back(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    status = user.get("projectStatus", "Member") if user else "Member"
    await message.answer("Главное меню:", reply_markup=get_main_keyboard(status))

@dp.message_handler(lambda message: message.text == "👤 Мой профиль")
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("Профиль не найден. Начните с /start")
        return
    
    await message.answer(
        format_user_profile(user),
        parse_mode="HTML",
        reply_markup=get_profile_keyboard()
    )

@dp.message_handler(lambda message: message.text == "✏️ Редактировать профиль")
async def cmd_edit_profile_start(message: types.Message):
    await message.answer("Выберите поле для редактирования:", reply_markup=get_edit_profile_keyboard())
    await EditProfileStates.waiting_for_field.set()

@dp.message_handler(state=EditProfileStates.waiting_for_field)
async def process_edit_field(message: types.Message, state: FSMContext):
    field_map = {
        "Дата рождения": "birth_date",
        "Телефон": "phone",
        "Email": "email",
        "Доп. информация": "additional_info"
    }
    
    if message.text == "⬅️ Назад":
        await state.finish()
        user = db.get_user(message.from_user.id)
        status = user.get("projectStatus", "Member") if user else "Member"
        await message.answer("Главное меню:", reply_markup=get_main_keyboard(status))
        return
    
    field = field_map.get(message.text)
    if field:
        await state.update_data(field=field)
        await message.answer(f"Введите новое значение для '{message.text}':")
        await EditProfileStates.waiting_for_value.set()
    else:
        await message.answer("Пожалуйста, выберите поле из клавиатуры:")

@dp.message_handler(state=EditProfileStates.waiting_for_value)
async def process_edit_value(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    field = user_data.get('field')
    
    if field:
        db.update_user_profile(message.from_user.id, {field: message.text})
        await message.answer("✅ Профиль обновлен!")
    
    await state.finish()
    await cmd_profile(message)

# ========== CLASS HANDLERS ==========
@dp.message_handler(lambda message: message.text == "🏫 Класс")
async def cmd_class(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("Профиль не найден")
        return
    
    class_id = user.get("class_id")
    team_role = user.get("teamRole")
    
    if class_id:
        class_data = db.get_class(class_id)
        if class_data:
            text = f"🏫 <b>Класс:</b> {class_data['name']}\n"
            text += f"👥 <b>Участников:</b> {len(class_data['members'])}\n"
            text += f"👑 <b>Ваша роль:</b> {team_role}"
            await message.answer(text, parse_mode="HTML")
    
    await message.answer("Выберите действие:", reply_markup=get_class_keyboard(team_role))

@dp.message_handler(lambda message: message.text == "Вступить в класс")
async def cmd_join_class_start(message: types.Message):
    await message.answer("Введите ID класса для вступления:")
    await ClassStates.waiting_for_class_id.set()

@dp.message_handler(state=ClassStates.waiting_for_class_id)
async def process_join_class(message: types.Message, state: FSMContext):
    class_id = message.text
    user_id = message.from_user.id
    
    class_data = db.get_class(class_id)
    if not class_data:
        await message.answer("❌ Класс не найден")
        await state.finish()
        return
    
    # Проверяем, состоит ли уже в классе
    user = db.get_user(user_id)
    if user.get("class_id"):
        await message.answer("❌ Вы уже состоите в классе")
        await state.finish()
        return
    
    # Staff, Admin, Owner могут вступать без запроса
    if user.get("projectStatus") in ["Staff", "Admin", "Owner"]:
        db.update_user_class(user_id, class_id, "участник")
        class_data["members"].append(user_id)
        db.save_class(class_id, class_data)
        await message.answer(f"✅ Вы вступили в класс '{class_data['name']}'")
    else:
        db.add_join_request(class_id, user_id)
        await message.answer(f"✅ Заявка на вступление в класс '{class_data['name']}' отправлена")
    
    await state.finish()
    await cmd_class(message)

@dp.message_handler(lambda message: message.text == "Покинуть класс")
async def cmd_leave_class(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    # Staff, Admin, Owner не могут быть удалены обычным способом
    if user.get("projectStatus") in ["Staff", "Admin", "Owner"]:
        await message.answer("❌ Вы не можете покинуть класс из-за вашего статуса")
        return
    
    class_id = user["class_id"]
    class_data = db.get_class(class_id)
    
    if class_data and user_id in class_data["members"]:
        class_data["members"].remove(user_id)
        db.save_class(class_id, class_data)
    
    db.update_user_class(user_id, None)
    await message.answer("✅ Вы покинули класс")

@dp.message_handler(lambda message: message.text == "Управление классом")
async def cmd_manage_class(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    # Проверяем права на управление классом
    if not can_edit_class(user_id, user["class_id"]):
        await message.answer("❌ У вас нет прав для управления классом")
        return
    
    await message.answer(
        "Управление классом:",
        reply_markup=get_class_management_keyboard(user.get("teamRole"))
    )

# ========== HOMEWORK HANDLERS ==========
@dp.message_handler(lambda message: message.text == "📝 ДЗ класса")
async def cmd_class_homework_menu(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    await message.answer("Просмотр ДЗ:", reply_markup=get_homework_keyboard())

@dp.message_handler(lambda message: message.text == "📚 Все предметы")
async def cmd_all_homework(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    class_data = db.get_class(user["class_id"])
    if class_data:
        homework = class_data.get("homework", {})
        if homework:
            text = f"📚 <b>ДЗ класса '{class_data['name']}':</b>\n\n"
            text += format_homework(homework)
        else:
            text = "📭 ДЗ не задано"
        
        await message.answer(text, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "🔍 Конкретный предмет")
async def cmd_specific_homework_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    class_data = db.get_class(user["class_id"])
    if class_data:
        subjects = list(class_data.get("homework", {}).keys())
        if subjects:
            text = "Доступные предметы:\n" + "\n".join([f"• {subj}" for subj in subjects])
            text += "\n\nВведите название предмета:"
        else:
            text = "❌ Нет заданных предметов"
        
        await message.answer(text)

@dp.message_handler(lambda message: message.text == "Изменить ДЗ")
async def cmd_edit_homework_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    if not can_edit_class(user_id, user["class_id"]):
        await message.answer("❌ У вас нет прав для изменения ДЗ")
        return
    
    await message.answer("Как вы хотите задать ДЗ?", reply_markup=get_homework_edit_keyboard())
    await HomeworkStates.waiting_for_subject_choice.set()

@dp.message_handler(state=HomeworkStates.waiting_for_subject_choice)
async def process_homework_choice(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.finish()
        user = db.get_user(message.from_user.id)
        if user and user.get("teamRole"):
            await message.answer("Управление классом:", reply_markup=get_class_management_keyboard(user["teamRole"]))
        return
    
    if message.text == "Выбрать из списка":
        user = db.get_user(message.from_user.id)
        class_data = db.get_class(user["class_id"])
        subjects = list(class_data.get("homework", {}).keys())
        
        if subjects:
            text = "Выберите предмет из списка:\n" + "\n".join([f"• {subj}" for subj in subjects])
            text += "\n\nВведите название предмета:"
            await message.answer(text)
            await HomeworkStates.waiting_for_homework_text.set()
            await state.update_data(edit_existing=True)
        else:
            await message.answer("❌ Нет заданных предметов. Выберите 'Написать самому'")
    
    elif message.text == "Написать самому":
        await message.answer("Введите название предмета:")
        await HomeworkStates.waiting_for_subject_name.set()

@dp.message_handler(state=HomeworkStates.waiting_for_subject_name)
async def process_subject_name(message: types.Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)
    await message.answer(f"Введите ДЗ для предмета '{subject}':")
    await HomeworkStates.waiting_for_homework_text.set()

@dp.message_handler(state=HomeworkStates.waiting_for_homework_text)
async def process_homework_text(message: types.Message, state: FSMContext):
    homework = message.text
    user_data = await state.get_data()
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await state.finish()
        return
    
    class_data = db.get_class(user["class_id"])
    if not class_data:
        await state.finish()
        return
    
    subject = user_data.get('subject')
    edit_existing = user_data.get('edit_existing', False)
    
    if edit_existing and not subject:
        # Если редактируем существующий, берем предмет из сообщения
        subject = message.text
        await state.update_data(subject=subject)
        await message.answer(f"Введите новое ДЗ для предмета '{subject}':")
        return
    
    if not subject:
        subject = message.text  # Если предмет еще не задан
    
    # Обновляем ДЗ
    homework_dict = class_data.get("homework", {})
    homework_dict[subject] = homework
    db.update_class_homework(user["class_id"], homework_dict)
    
    await message.answer(f"✅ ДЗ по предмету '{subject}' обновлено!")
    await state.finish()

# ========== PERSONAL HOMEWORK HANDLERS ==========
@dp.message_handler(lambda message: message.text == "📚 Моё ДЗ")
async def cmd_personal_homework(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("Профиль не найден")
        return
    
    personal_hw = user.get("personal_homework", {})
    if personal_hw:
        text = "📚 <b>Ваше личное ДЗ:</b>\n\n"
        text += format_homework(personal_hw)
    else:
        text = "📭 Личное ДЗ не задано"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_homework_keyboard())

@dp.message_handler(lambda message: message.text == "➕ Добавить личное ДЗ")
async def cmd_add_personal_hw_start(message: types.Message):
    await message.answer("Введите название предмета для личного ДЗ:")
    await PersonalHomeworkStates.waiting_for_personal_subject.set()

@dp.message_handler(state=PersonalHomeworkStates.waiting_for_personal_subject)
async def process_personal_subject(message: types.Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)
    await message.answer(f"Введите ДЗ для предмета '{subject}':")
    await PersonalHomeworkStates.waiting_for_personal_homework.set()

@dp.message_handler(state=PersonalHomeworkStates.waiting_for_personal_homework)
async def process_personal_homework(message: types.Message, state: FSMContext):
    homework = message.text
    user_data = await state.get_data()
    subject = user_data.get('subject')
    
    db.add_personal_homework(message.from_user.id, subject, homework)
    
    await message.answer(f"✅ Личное ДЗ по предмету '{subject}' добавлено!")
    await state.finish()

# ========== CLASS MANAGEMENT HANDLERS ==========
@dp.message_handler(lambda message: message.text == "Заявки на вступление")
async def cmd_join_requests(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or not user.get("class_id"):
        await message.answer("❌ Вы не состоите в классе")
        return
    
    if not can_edit_class(user_id, user["class_id"]):
        await message.answer("❌ У вас нет прав для просмотра заявок")
        return
    
   