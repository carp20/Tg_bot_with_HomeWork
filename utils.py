from typing import Dict, Any
from database import db

def has_permission(user_id: int, required_status: str = None, required_team_role: str = None) -> bool:
    """Проверка прав пользователя"""
    user = db.get_user(user_id)
    if not user:
        return False
    
    # Проверка статуса проекта
    if required_status:
        status_hierarchy = {"Owner": 4, "Admin": 3, "Staff": 2, "Member": 1}
        user_status = user.get("projectStatus", "Member")
        
        if status_hierarchy.get(user_status, 0) < status_hierarchy.get(required_status, 0):
            return False
    
    # Проверка роли в классе
    if required_team_role:
        user_team_role = user.get("teamRole")
        if user_team_role != required_team_role:
            return False
    
    return True

def can_edit_class(user_id: int, class_id: str) -> bool:
    """Может ли пользователь редактировать класс"""
    user = db.get_user(user_id)
    if not user:
        return False
    
    # Проверка статуса проекта
    user_status = user.get("projectStatus", "Member")
    if user_status in ["Owner", "Admin", "Staff"]:
        return True
    
    # Проверка роли в классе
    if user.get("class_id") != class_id:
        return False
    
    user_role = user.get("teamRole")
    return user_role in ["староста", "помощник старосты"]

def can_manage_roles(user_id: int, class_id: str) -> bool:
    """Может ли пользователь управлять ролями в классе"""
    user = db.get_user(user_id)
    if not user:
        return False
    
    # Статусы проекта
    user_status = user.get("projectStatus", "Member")
    if user_status in ["Owner", "Admin", "Staff"]:
        return True
    
    # Только староста может управлять ролями
    if user.get("class_id") != class_id:
        return False
    
    return user.get("teamRole") == "староста"

def format_homework(homework_dict: Dict) -> str:
    """Форматирование ДЗ для отображения"""
    if not homework_dict:
        return "ДЗ не задано"
    
    result = []
    for subject, hw in homework_dict.items():
        result.append(f"📘 <b>{subject}:</b>\n{hw}")
    
    return "\n\n".join(result)

def format_user_profile(user_data: Dict) -> str:
    """Форматирование профиля пользователя"""
    profile = user_data.get("profile", {})
    
    text = f"👤 <b>Профиль пользователя</b>\n\n"
    text += f"📝 <b>Имя:</b> {user_data.get('name', 'Не указано')}\n"
    text += f"🎂 <b>Дата рождения:</b> {profile.get('birth_date', 'Не указано')}\n"
    text += f"📞 <b>Телефон:</b> {profile.get('phone', 'Не указано')}\n"
    text += f"📧 <b>Email:</b> {profile.get('email', 'Не указано')}\n"
    text += f"ℹ️ <b>Доп. информация:</b> {profile.get('additional_info', 'Не указано')}\n\n"
    text += f"🏷️ <b>Статус:</b> {user_data.get('projectStatus', 'Member')}\n"
    text += f"👥 <b>Роль в классе:</b> {user_data.get('teamRole', 'Не состоит в классе')}\n"
    
    if user_data.get("class_id"):
        class_data = db.get_class(user_data["class_id"])
        if class_data:
            text += f"🏫 <b>Класс:</b> {class_data.get('name', 'Неизвестно')}\n"
    
    return text