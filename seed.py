import csv
from datetime import datetime
from peewee import chunked
from app.database import db
from app.models import user, url, event

def parse_datetime(dt_str):
    if not dt_str:
        return None
    # Parses the format from your CSV: DD-MM-YYYY HH:MM
    return datetime.strptime(dt_str, "%d-%m-%Y %H:%M")

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
    print(f"Loading {filepath} into {model.__name__}...")
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Clean the data before inserting
        rows = [clean_row(row) for row in reader]

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).execute()
    print(f"Done loading {filepath}!")

if __name__ == "__main__":
    db.create_tables([user, url, event])
    
    # Order matters to satisfy Foreign Key constraints
    load_csv(user, "data/users.csv")
    load_csv(url, "data/urls.csv")
    load_csv(event, "data/events.csv")