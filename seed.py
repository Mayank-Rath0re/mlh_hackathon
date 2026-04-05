import os
import csv
from datetime import datetime
from peewee import chunked, PostgresqlDatabase

# Import the Database Proxy
from app.database import db

# FIX 1: Import the uppercase Classes directly from their respective files
from app.models.user import User
from app.models.url import Url
from app.models.event import Event

def parse_datetime(dt_str):
    if not dt_str:
        return None
    
    # A list of possible formats your CSVs might throw at us
    formats = [
        "%Y-%m-%d %H:%M:%S",  # Matches: 2025-06-06 04:37:40 (Your current error)
        "%d-%m-%Y %H:%M",     # Matches: 20-04-2025 09:26 (Your original sample)
        "%Y-%m-%d %H:%M",     # Matches: 2025-06-06 04:37
        "%Y-%m-%dT%H:%M:%S",  # Standard ISO format just in case
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            # If it fails, try the next format in the list
            continue
            
    # If it goes through all formats and still fails, print a helpful error
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
    print(f"Loading {filepath} into {model.__name__}...")
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [clean_row(row) for row in reader]

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).execute()
    print(f"Done loading {filepath}!")

if __name__ == "__main__":
    # FIX 2: Manually initialize the Proxy with a direct Postgres connection
    # Check your .env file and update these defaults if your local setup is different!
    if db.obj is None:
        pg_db = PostgresqlDatabase(
            os.getenv("DB_NAME", "hackathon_db"),
            user=os.getenv("DB_USER", "postgres"),     # Often 'postgres' or your OS username
            password=os.getenv("DB_PASSWORD", "postgres"), # Update if you have a DB password
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        db.initialize(pg_db)
    
    # Use the uppercase Classes here
    db.create_tables([User, Url, Event])
    
    # Order matters to satisfy Foreign Key constraints
    load_csv(User, "data/users.csv")
    load_csv(Url, "data/urls.csv")
    load_csv(Event, "data/events.csv")