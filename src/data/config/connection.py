from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
import sys


caminho_absoluto = os.path.abspath(os.curdir)
sys.path.insert(0, caminho_absoluto)
# Conexão não está estruturada corretamente ainda

class DBConnectionHandler:
    BASE_DIR = Path(r"backend/database/wappscall_db.db")
    def __init__(self,BASE_DIR=BASE_DIR):
        self.db_path = BASE_DIR
        self.__engine = self.__create_database_engine()
        self.session = None

    def get_session(self):
        return self.session
    
    def __create_database_engine(self):
        engine = create_engine(f'sqlite:///{self.db_path}')
        return engine

    def get_engine(self):
        return self.__engine

    def __enter__(self):
        session_maker= sessionmaker(bind=self.__engine)
        self.session = session_maker()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def create_tables(self, Base):
        Base.metadata.create_all(self.__engine)

class Database:
    def __init__(self, url):
        engine = create_engine(url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_session(self):
        return self.SessionLocal()