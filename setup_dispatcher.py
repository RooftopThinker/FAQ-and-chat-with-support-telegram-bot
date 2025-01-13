from handlers import approve_review, start, get_bonus, problems, cancellation, contacts, faq, instructions, unendified_message
from handlers.admin import export_to_excel, respond_to_appeal, show_menu, mailing, stats

from aiogram import Dispatcher
from middlewares.db import DbSessionMiddleware
from data.database import sessionmaker


async def setup_dispatcher(dispatcher: Dispatcher):
    dispatcher.include_routers(start.router, approve_review.router, export_to_excel.router,
                               get_bonus.router, problems.router, cancellation.router, contacts.router, faq.router,
                               respond_to_appeal.router, show_menu.router, mailing.router, stats.router, instructions.router,
                               unendified_message.router)
    dispatcher.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
