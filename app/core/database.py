from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine_kwargs = {"pool_pre_ping": True}
database_url = make_url(settings.database_url)

if database_url.get_backend_name() == "sqlite":
	if database_url.database and database_url.database != ":memory:":
		Path(database_url.database).parent.mkdir(parents=True, exist_ok=True)
	engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()