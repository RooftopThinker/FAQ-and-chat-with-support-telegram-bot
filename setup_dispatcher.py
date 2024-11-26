from handlers import approve_review, start, get_bonus
from handlers.admin import export_to_excel
from aiogram import Dispatcher
from middlewares.db import DbSessionMiddleware
from data.database import sessionmaker


async def setup_dispatcher(dispatcher: Dispatcher):
    dispatcher.include_routers(start.router, approve_review.router, export_to_excel.router,
                               get_bonus.router)
    dispatcher.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
