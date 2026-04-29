from __future__ import annotations

from contextlib import contextmanager

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from spider.storage.models import Base
from spider.utils import config as config_module
from spider.utils.config import ensure_runtime_paths


_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker | None = None


def build_database_url() -> str:
    if config_module.settings.DB_ENGINE.lower() == "postgresql":
        return config_module.settings.POSTGRES_URL
    ensure_runtime_paths(config_module.settings)
    return f"sqlite:///{config_module.settings.sqlite_abspath}"



def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        kwargs = {"pool_pre_ping": True}
        if config_module.settings.DB_ENGINE.lower() == "sqlite":
            kwargs["connect_args"] = {"check_same_thread": False}
        _ENGINE = create_engine(build_database_url(), **kwargs)
    return _ENGINE



def get_session_factory() -> sessionmaker:
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SESSION_FACTORY



def reset_engine() -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        _ENGINE.dispose()
    _ENGINE = None
    _SESSION_FACTORY = None



def init_db() -> None:
    ensure_runtime_paths(config_module.settings)
    Base.metadata.create_all(bind=get_engine())
    logger.success("Database initialised successfully")


@contextmanager
def session_scope() -> Session:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
