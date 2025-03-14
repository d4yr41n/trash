import re

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select, func

from .models import Session, User


router = Router()


def validate_username(function):
    async def wrapper(msg):
        args = msg.text.split()[1:]
        if not args:
            await msg.answer("Введите имя пользователя")
        elif not re.match(r"@?[A-z0-9]{1,32}", (username := args[0])):
            await msg.answer("Некорректное имя пользователя")
        else:
            await function(msg, username)
    return wrapper


@router.message(CommandStart())
async def start(msg: Message) -> None:
    await msg.answer("К вашим услугам")


@router.message(Command("adduser"))
@validate_username
async def adduser(msg: Message, username: str) -> None:
    async with Session() as session:
        if await User.get(session, username):
            await msg.answer("Пользователь с таким именем уже существует")
        else:
            session.add(User(name=username))
            await session.commit()
            await msg.answer("Пользователь создан")


@router.message(Command("deluser"))
@validate_username
async def deluser(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            await session.delete(user)
            await session.commit()
            await msg.answer("Пользователь удалён")
        else:
            await msg.answer("Пользователь с таким именем не найден")


@router.message(Command("poker"))
@validate_username
async def poker(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            user.poker += 1
            await session.commit()
            await msg.answer(username + " победил в покер")
        else:
            await msg.answer("Пользователь с таким именем не найден")


@router.message(Command("unpoker"))
@validate_username
async def unpoker(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            if user.poker > 0:
                user.poker -= 1
                await session.commit()
                await msg.answer("Аннулирование победы " + username + " в покер")
            else:
                await msg.answer("У " + username + " нет побед в покер")
        else:
            await msg.answer("Пользователь с таким именем не найден")


@router.message(Command("chests"))
@validate_username
async def chests(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            user.chests += 1
            await session.commit()
            await msg.answer(username + " победил в сундучки")
        else:
            await msg.answer("Пользователь с таким именем не найден")


@router.message(Command("unchests"))
@validate_username
async def unchests(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            if user.chests > 0:
                user.chests -= 1
                await session.commit()
                await msg.answer("Аннулирование победы " + username + " в сундучки")
            else:
                await msg.answer("У " + username + " нет побед в сундучки")
        else:
            await msg.answer("Пользователь с таким именем не найден")


@router.message(Command("score"))
async def score(msg: Message) -> None:
    answer = "Имя: Покер, Сундучки\n\n"
    async with Session() as session:
        users = await session.scalars(select(User))
        for user in users:
            answer += f"{user.name}: {user.poker}, {user.chests}\n"
        poker_champion = tuple(await session.scalars(
            select(User).where(User.poker == select(func.max(User.poker)).scalar_subquery()))
        )
        chests_champion = tuple(await session.scalars(
            select(User).where(User.chests == select(func.max(User.chests)).scalar_subquery()))
        )
        if len(poker_champion) == 1:
            answer += "\nЧемпион по покеру: " + poker_champion[0].name
        if len(chests_champion) == 1:
            answer += "\nЧемпион по сундучкам: " + chests_champion[0].name            
    await msg.answer(answer)


@router.message(Command("profile"))
@validate_username
async def profile(msg: Message, username: str) -> None:
    async with Session() as session:
        user = await User.get(session, username)
        if user:
            await msg.answer(f"{user.name}: покер - {user.poker}, сундучки - {user.chests}")
        else:
            await msg.answer("Пользователь с таким именем не найден")
