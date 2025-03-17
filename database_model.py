from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "sqlite:///./test.db"

# Синхронный движок для создания таблиц
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Асинхронное подключение к базе данных
database = Database(DATABASE_URL)

# Создание сессии для синхронных операций
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Метаданные
metadata = MetaData()