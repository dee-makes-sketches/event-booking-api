from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings

#create engine
engine = create_async_engine(settings.database_url)

#create session factory 
AsyncSessionLocal = async_sessionmaker(engine, class_= AsyncSession, expire_on_commit = False)


#get session per request (session:workspace)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
