from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine
from typing import AsyncIterator, Annotated
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends

from contextlib import asynccontextmanager
import os

class Base(DeclarativeBase):
    pass

class DBSessionManager:
    def __init__(self, uri:str):
        self._engine = create_async_engine(uri)
        self._sessionmaker = async_sessionmaker(bind=self._engine,autocommit=False)
    
    async def create_tables(self):
        if self._engine is None:
            raise Exception("Database engine is not initialized")
        
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncConnection]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.rollback()

database_url = os.environ.get("DB_URI")
# use the session manager instance for the sockets, consumers and non fastapi related modules
sessionmanager = DBSessionManager(database_url)

# for fastapi http endpoints
async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

def get_db_session_from_app(app)->DBSessionManager:
    return app.state.db_session
DBSesionDep = Annotated[AsyncSession,Depends(get_db_session)]