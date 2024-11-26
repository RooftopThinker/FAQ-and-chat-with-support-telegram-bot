from aiogram_album.ttl_cache_middleware import TTLCacheAlbumMiddleware
import asyncio
import logging
# from asyncio import WindowsSelectorEventLoopPolicy
from aiogram import types
from aiogram import Bot, Dispatcher
from setup_dispatcher import setup_dispatcher
import config
from aiogram_album import AlbumMessage
from data.database import SqlAlchemyBase, engine
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
# asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
dp = Dispatcher()

TTLCacheAlbumMiddleware(router=dp)
# async def create_metadata():
#     async with engine.begin() as conn:
#         await conn.run_sync(SqlAlchemyBase.metadata.create_all)


async def main():
    await setup_dispatcher(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # asyncio.run(create_metadata())
    asyncio.run(main())

