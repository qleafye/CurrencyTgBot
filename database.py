import json
import os
from datetime import datetime

class Database:
    def __init__(self, users_file, logs_file, admin_file):
        self.users_db_file = users_file
        self.logs_file = logs_file
        self.admin_config_file = admin_file
        self._init_database()

    def _init_database(self):
        if not os.path.exists(self.users_db_file):
            with open(self.users_db_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        
        if not os.path.exists(self.admin_config_file):
            with open(self.admin_config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "admin_ids": [873278697]
                }, f, ensure_ascii=False, indent=4)

    def save_user(self, user_data):
        with open(self.users_db_file, 'r+', encoding='utf-8') as f:
            users = json.load(f)
            users[str(user_data.id)] = {
                'username': user_data.username,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'last_activity': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            f.seek(0)
            json.dump(users, f, ensure_ascii=False, indent=4)
            f.truncate()

    def log_operation(self, user_id, operation_type, details):
        with open(self.logs_file, 'r+', encoding='utf-8') as f:
            logs = json.load(f)
            logs.append({
                'user_id': user_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'operation_type': operation_type,
                'details': details
            })
            f.seek(0)
            json.dump(logs, f, ensure_ascii=False, indent=4)
            f.truncate()

    def load_admin_ids(self):
        try:
            with open(self.admin_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return set(config.get("admin_ids", [873278697]))
        except Exception:
            return {873278697}

    def save_admin_ids(self, admin_ids):
        with open(self.admin_config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "admin_ids": list(admin_ids)
            }, f, ensure_ascii=False, indent=4)

    def get_logs(self):
        with open(self.logs_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_users(self):
        with open(self.users_db_file, 'r', encoding='utf-8') as f:
            return json.load(f) 