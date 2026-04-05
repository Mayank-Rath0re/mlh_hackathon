import os
from peewee import PostgresqlDatabase, fn

# Import the proxy and models
from app.database import db
from app.models.user import User
from app.models.url import Url
from app.models.event import Event

def reset_sequences():
    # 1. Initialize the DB directly (bypassing the broken Flask app factory)
    if db.obj is None:
        pg_db = PostgresqlDatabase(
            os.getenv("DB_NAME", "hackathon_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        db.initialize(pg_db)
    
    # 2. Loop through and fix the sequences
    models = [User, Url, Event]
    for model in models:
        table_name = model._meta.table_name
        try:
            # Find the actual maximum ID in the table right now
            max_id = model.select(fn.MAX(model.id)).scalar()
            
            if max_id is None:
                max_id = 1
                
            # Force Postgres to set the sequence to this max_id
            seq_name = f"{table_name}_id_seq"
            db.execute_sql(f"SELECT setval('{seq_name}', {max_id});")
            
            # Commit the transaction so it actually saves!
            db.commit()
            
            print(f"✅ {table_name.upper()} sequence reset! Next ID will be {max_id + 1}.")
        except Exception as e:
            print(f"⚠️ Error resetting {table_name}: {e}")

if __name__ == "__main__":
    reset_sequences()