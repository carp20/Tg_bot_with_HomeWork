import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.classes_file = os.path.join(self.data_dir, "classes.json")
        self._ensure_directories()
        self._init_files()
    
    def _ensure_directories(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _init_files(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(self.classes_file):
            with open(self.classes_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    # === User Operations ===
    def get_user(self, user_id: int) -> Optional[Dict]:
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        return users.get(str(user_id))
    
    def save_user(self, user_id: int, user_data: Dict):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[str(user_id)] = user_data
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def create_user_profile(self, user_id: int, name: str):
        user_data = {
            "id": user_id,
            "name": name,
            "profile": {
                "birth_date": "",
                "phone": "",
                "email": "",
                "additional_info": ""
            },
            "projectStatus": "Member",
            "class_id": None,
            "teamRole": None,
            "personal_homework": {},
            "join_requests": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_user(user_id, user_data)
        return user_data
    
    def update_user_profile(self, user_id: int, profile_data: Dict):
        user = self.get_user(user_id)
        if user:
            user["profile"].update(profile_data)
            self.save_user(user_id, user)
    
    def update_user_status(self, user_id: int, status: str):
        user = self.get_user(user_id)
        if user:
            user["projectStatus"] = status
            self.save_user(user_id, user)
    
    def update_user_class(self, user_id: int, class_id: Optional[str], team_role: Optional[str] = None):
        user = self.get_user(user_id)
        if user:
            user["class_id"] = class_id
            if team_role:
                user["teamRole"] = team_role
            self.save_user(user_id, user)
    
    def add_personal_homework(self, user_id: int, subject: str, homework: str):
        user = self.get_user(user_id)
        if user:
            if "personal_homework" not in user:
                user["personal_homework"] = {}
            user["personal_homework"][subject] = homework
            self.save_user(user_id, user)
    
    # === Class Operations ===
    def get_class(self, class_id: str) -> Optional[Dict]:
        with open(self.classes_file, 'r', encoding='utf-8') as f:
            classes = json.load(f)
        return classes.get(class_id)
    
    def save_class(self, class_id: str, class_data: Dict):
        with open(self.classes_file, 'r', encoding='utf-8') as f:
            classes = json.load(f)
        
        classes[class_id] = class_data
        
        with open(self.classes_file, 'w', encoding='utf-8') as f:
            json.dump(classes, f, ensure_ascii=False, indent=2)
    
    def create_class(self, class_id: str, class_name: str, creator_id: int):
        class_data = {
            "id": class_id,
            "name": class_name,
            "homework": {},
            "information": "",
            "members": [creator_id],
            "join_requests": [],
            "created_at": datetime.now().isoformat(),
            "created_by": creator_id
        }
        self.save_class(class_id, class_data)
        return class_data
    
    def add_join_request(self, class_id: str, user_id: int):
        class_data = self.get_class(class_id)
        if class_data:
            if user_id not in class_data["join_requests"]:
                class_data["join_requests"].append(user_id)
                self.save_class(class_id, class_data)
    
    def process_join_request(self, class_id: str, user_id: int, accept: bool):
        class_data = self.get_class(class_id)
        if class_data:
            if user_id in class_data["join_requests"]:
                class_data["join_requests"].remove(user_id)
                
                if accept:
                    class_data["members"].append(user_id)
                    self.update_user_class(user_id, class_id, "участник")
                
                self.save_class(class_id, class_data)
                return True
        return False
    
    def remove_member(self, class_id: str, user_id: int):
        class_data = self.get_class(class_id)
        if class_data and user_id in class_data["members"]:
            class_data["members"].remove(user_id)
            self.save_class(class_id, class_data)
            self.update_user_class(user_id, None)
            return True
        return False
    
    def update_class_homework(self, class_id: str, homework_data: Dict):
        class_data = self.get_class(class_id)
        if class_data:
            class_data["homework"] = homework_data
            self.save_class(class_id, class_data)
    
    def update_class_information(self, class_id: str, information: str):
        class_data = self.get_class(class_id)
        if class_data:
            class_data["information"] = information
            self.save_class(class_id, class_data)
    
    def get_class_homework(self, class_id: str, subject: str = None) -> Dict:
        class_data = self.get_class(class_id)
        if class_data:
            if subject:
                return {subject: class_data["homework"].get(subject, "ДЗ не задано")}
            return class_data["homework"]
        return {}
    
    # === Utility Methods ===
    def get_all_classes(self) -> Dict:
        with open(self.classes_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_users(self) -> Dict:
        with open(self.users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_users_in_class(self, class_id: str) -> List[int]:
        class_data = self.get_class(class_id)
        return class_data.get("members", []) if class_data else []
    
    def get_user_class(self, user_id: int) -> Optional[Dict]:
        user = self.get_user(user_id)
        if user and user.get("class_id"):
            return self.get_class(user["class_id"])
        return None

db = Database()