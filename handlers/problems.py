from aiogram import Router, F, types
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from keyboards.all_keyboards import dispenser_or_humidifier, menu, dispenser_problems, humidifier_problems, cancel
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_album import AlbumMessage
import sqlalchemy
from data import User, Appeal, Thread
import aiofiles
from .fsm import Problems
from config import ADMINS_CHAT_ID
router = Router()
router.message.filter(F.chat.type == ChatType.PRIVATE)
@router.message(F.text == 'Проблемы с товаром')
async def problems(message: types.Message, state: FSMContext):
    await message.answer('Мы подготовили ответы на часто задаваемые вопросы. Выберите категорию товара.',
                         reply_markup=dispenser_or_humidifier())
    await state.set_state(Problems.good_chosen)


@router.callback_query(F.data == 'dispenser', Problems.good_chosen)
async def problems_dispenser(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(good='dispenser')
    await callback.message.edit_text(text='''Выберите проблему для обращения в поддержку:
1. Проблема: Дозатор 174805080 самопроизвольно срабатывает.
2. Проблема: Не работает дозатор/нет подачи пены/брак.
3. Проблема: Не работает сенсор у дозатора 174805080.''', reply_markup=dispenser_problems())
    await state.set_state(Problems.problem_chosen)


@router.callback_query(F.data == 'humidifier', Problems.good_chosen)
async def problems_humidifier(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(good='humidifier')
    await callback.message.edit_text(text='''Выберите проблему для обращения в поддержку:
1. Проблема: Не работают/некорректно работают увлажнители 182308427, 221426427.
2. Проблема: Идет пар из одной форсунки/не идет пар вовсе.
3. Проблема: Не рабfull_nameотают/некорректно работают увлажнители 182307898, 182307913.
4. Проблема: Нет пара/слабый пар у увлажнителя 174808327.
5. Проблема: После работы увлажнителя 182307913 остается лужа на поверхности/конденсат на крышке?''', reply_markup=humidifier_problems())
    await state.set_state(Problems.problem_chosen)


@router.callback_query(F.data.startswith('problem'), Problems.problem_chosen)
async def problem_chosen(callback: types.CallbackQuery, state: FSMContext):
    good = await state.get_value('good')
    problem = callback.data.split('_')[1]
    await state.update_data(problem=problem)
    if good == 'humidifier':
        f = await aiofiles.open('static/problems_humidifier.txt', mode='r')
    else:
        f = await aiofiles.open('static/problems_dispenser.txt', mode='r')
    problem = [str(i)+'\n\nК видео вы можете добавить текстовое сообщение с описанием проблемы.' for i in await f.readlines()][int(problem)-1]
    await callback.message.edit_text(text=problem, reply_markup=cancel())
    await state.set_state(Problems.problem_reported)


@router.message(~F.text.in_(('Получить бонус', 'Контакты', 'Вопросы', 'Проблемы с товаром')),Problems.problem_reported,
                F.media_group_id)
async def mediagroup_problem_reported(message: AlbumMessage, state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)
    user: User = list(await session.scalars(request))[0]
    request = sqlalchemy.select(Thread).filter(Thread.by_user == message.from_user.id, Thread.is_open == True)
    try:
        topic: Thread = list(await session.scalars(request))[0]
    except IndexError:
        topic: types.ForumTopic = await message.bot.create_forum_topic(chat_id=ADMINS_CHAT_ID,
                                                     name=f'❌ОТКРЫТАЯ проблема {message.from_user.name}')

        session.add(Thread(by_user=message.from_user.id, name=topic.name, message_thread_id=topic.message_thread_id))
        await session.commit()
    try:
        text = message.caption
    except TelegramBadRequest:
        text = ''
    msg_text = ('Новое обращение по проблеме:'
                f'Username: {user.telegram_username}\n'
                f'Отображаемое имя: {user.telegram_name}\n'
                f'Номер телефона: {user.phone}\n\n'
                f'Сообщение пользователя {": " + text if text else "пусто"}\n'
                f'Вложения пользователя показаны выше🔝'
                f'\n'
                f'Ответьте на это сообщение бота, и Ваш ответ отправится пользователю\n\n'
                f'#N{user.telegram_id}'
                )
    media_group = []
    for m in message:
        if m.content_type == 'photo':
            media_group.append(types.InputMediaPhoto(media=m.photo[-1].file_id))
        elif m.content_type == 'video':
            media_group.append(types.InputMediaVideo(media=m.video[-1].file_id))
        else:
            await message.answer('Пришлите или видео, или фото. Другие типы медиа не принимаются')
            return

    appeal_media = await message.bot.send_media_group(chat_id=ADMINS_CHAT_ID, media=media_group, message_thread_id=topic.message_thread_id)
    for i in appeal_media:
        new_appeal = Appeal(by_user=message.from_user.id, message_id=i.message_id)
        session.add(new_appeal)
    appeal_message = await message.bot.send_message(chat_id=ADMINS_CHAT_ID, text=msg_text, message_thread_id=topic.message_thread_id)
    request = sqlalchemy.update(User).filter(User.telegram_id == message.from_user.id).values({'problems_appealed': User.problems_appealed+1})
    new_appeal = Appeal(by_user=message.from_user.id, message_id=appeal_message.message_id)
    session.add(new_appeal)
    await session.execute(request)
    await session.commit()
    await message.answer("Сообщение о проблеме отправлено сотрудникам. Ожидайте ответа", reply_markup=menu())
    await state.clear()


@router.message(~F.text.in_(('Получить бонус', 'Контакты', 'Вопросы', 'Проблемы с товаром')),Problems.problem_reported)
async def problem_reported(message: types.Message, state: FSMContext, session: AsyncSession):
    request = sqlalchemy.select(User).filter(User.telegram_id == message.from_user.id)
    user: User = list(await session.scalars(request))[0]
    request = sqlalchemy.select(Thread).filter(Thread.by_user == message.from_user.id, Thread.is_open == True)
    try:
        topic: Thread = list(await session.scalars(request))[0]
    except IndexError:
        topic: types.ForumTopic = await message.bot.create_forum_topic(chat_id=ADMINS_CHAT_ID,
                                                     name=f'❌ОТКРЫТАЯ проблема {message.from_user.id}')

        session.add(Thread(by_user=message.from_user.id, name=topic.name, message_thread_id=topic.message_thread_id))
        await session.commit()
    msg_text = ('Новое обращение по проблеме:'
                f'Username: {user.telegram_username}\n'
                f'Отображаемое имя: {user.telegram_name}\n'
                f'Номер телефона: {user.phone}\n\n'
                f'Сообщение пользователя показано выше🔝'
                f'\n'
                f'Ответьте на это сообщение бота, и Ваш ответ отправится пользователю\n\n'
                f'#N{user.telegram_id}'
                )
    appeal_message = await message.bot.copy_message(chat_id=ADMINS_CHAT_ID, from_chat_id=message.chat.id, message_id=message.message_id,
                                                    message_thread_id=topic.message_thread_id)
    appeal_info = await message.bot.send_message(chat_id=ADMINS_CHAT_ID, text=msg_text, message_thread_id=topic.message_thread_id)
    request = sqlalchemy.update(User).filter(User.telegram_id == message.from_user.id).values(
        {'problems_appealed': User.problems_appealed + 1})
    new_appeal = Appeal(by_user=message.from_user.id, message_id=appeal_message.message_id)
    session.add(new_appeal)
    new_appeal = Appeal(by_user=message.from_user.id, message_id=appeal_info.message_id)
    await session.execute(request)
    session.add(new_appeal)
    await session.commit()
    await message.answer("Сообщение о проблеме отправлено сотрудникам. Ожидайте ответа", reply_markup=menu())
    await state.clear()