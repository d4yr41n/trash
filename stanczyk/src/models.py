from asyncio import run

from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_async_engine("sqlite+aiosqlite:///db.db")
Session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(33), unique=True)
    poker: Mapped[int] = mapped_column(default=0)
    chests: Mapped[int] = mapped_column(default=0)

    @classmethod
    async def get(cls, session, name):
        user = await session.scalar(select(cls).where(cls.name == name))
        return user


async def main():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    run(main())
