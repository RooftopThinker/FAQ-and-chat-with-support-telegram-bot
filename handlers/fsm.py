from aiogram.fsm.state import State, StatesGroup

class RegisterUser(StatesGroup):
    fetch_number = State()
    check_subscription = State()


class GetBonus(StatesGroup):
    fetch_bank_requisite = State()
    send_for_approval = State()

class SendMailing(StatesGroup):
    approve = State()
    send_mailing = State()


class FAQ(StatesGroup):
    good_chosen = State()


class Problems(StatesGroup):
    good_chosen = State()
    problem_chosen = State()
    problem_reported = State()


class IsProblemSolved(StatesGroup):
    question = State()
    problem = State()