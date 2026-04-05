import os
import csv
from datetime import datetime
from peewee import chunked, PostgresqlDatabase, fn

# Import the Database Proxy
from app.database import db

# Import the Models
from app.models.user import User
from app.models.url import Url
from app.models.event import Event

def parse_datetime(dt_str):
    if not dt_str:
        return None
    
    formats = [
        "%Y-%m-%d %H:%M:%S",  # Matches: 2025-06-06 04:37:40 
        "%d-%m-%Y %H:%M",     # Matches: 20-04-2025 09:26 
        "%Y-%m-%d %H:%M",     # Matches: 2025-06-06 04:37
        "%Y-%m-%dT%H:%M:%S",  # Standard ISO format
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: '{dt_str}'. Unknown format.")

def clean_row(row):
    """Formats strings into native Python types for Peewee"""
    clean_data = {}
    for key, value in row.items():
        if not value:
            clean_data[key] = None
            continue
            
        if key in ['created_at', 'updated_at', 'timestamp']:
            clean_data[key] = parse_datetime(value)
        elif key == 'is_active':
            clean_data[key] = value.upper() == 'TRUE'
        else:
            clean_data[key] = value
    return clean_data

def load_csv(model, filepath):
    print(f"📦 Loading {filepath} into {model.__name__}...")
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [clean_row(row) for row in reader]

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).execute()

def reset_sequences():
    """Fixes PostgreSQL sequences after manual ID insertion"""
    print("\n🔧 Fixing database sequences...")
    for model in [User, Url, Event]:
        table_name = model._meta.table_name
        try:
            max_id = model.select(fn.MAX(model.id)).scalar() or 1
            db.execute_sql(f"SELECT setval('{table_name}_id_seq', {max_id});")
            db.commit()
            print(f"✅ {table_name.upper()} sequence synced (Next ID: {max_id + 1})")
        except Exception as e:
            print(f"⚠️ Error resetting {table_name}: {e}")

if __name__ == "__main__":
    # 1. Initialize the Database Directly
    if db.obj is None:
        pg_db = PostgresqlDatabase(
            os.getenv("DB_NAME", "hackathon_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        db.initialize(pg_db)
    
    print("Creating tables...")
    db.create_tables([User, Url, Event])
    
    # 2. Load the Data (Order matters for Foreign Keys!)
    load_csv(User, "data/users.csv")
    load_csv(Url, "data/urls.csv")
    load_csv(Event, "data/events.csv")
    
    # 3. Fix the PostgreSQL sequences
    reset_sequences()
    
    print("\nDatabase seeding complete! You are ready to run the app.")