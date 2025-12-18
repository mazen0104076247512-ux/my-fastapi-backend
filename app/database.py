from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
 
# --- Local Database Connection (XAMPP) ---
# This is the recommended setup for development.
# Make sure you have a database named 'semester_history_db' in your local phpMyAdmin.
DATABASE_URL = "mysql+pymysql://root:@localhost/semester_history_db"

# --- Cloud Database Connection (Render/Production) ---
# DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
