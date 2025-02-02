import json
from datetime import datetime
import pandas as pd

def load_data():
    with open('user_logs.json', 'r', encoding='utf-8') as f:
        logs = json.load(f)
    with open('users_db.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    return logs, users

def analyze_data():
    logs, users = load_data()
    
    # Создаем DataFrame из логов
    df = pd.DataFrame(logs)
    
    # Базовая статистика
    print("\n=== Общая статистика ===")
    print(f"Всего операций: {len(logs)}")
    print(f"Уникальных пользователей: {df['user_id'].nunique()}")
    
    # Статистика по типам операций
    print("\n=== Статистика по операциям ===")
    print(df['operation_type'].value_counts())
    
    # Статистика по дням
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_stats = df.groupby('date').size()
    print("\n=== Активность по дням ===")
    print(daily_stats)
    
    # Топ активных пользователей
    top_users = df['user_id'].value_counts().head(5)
    print("\n=== Топ-5 активных пользователей ===")
    for user_id, count in top_users.items():
        user = users.get(str(user_id), {})
        username = user.get('username', 'Неизвестно')
        print(f"ID: {user_id}, Username: {username}, Операций: {count}")

if __name__ == "__main__":
    analyze_data() 