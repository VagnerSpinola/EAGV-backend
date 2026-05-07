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
elif settings.database_hostaddr:
	database_url = database_url.update_query_dict({"hostaddr": settings.database_hostaddr})

engine = create_engine(database_url.render_as_string(hide_password=False), **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()