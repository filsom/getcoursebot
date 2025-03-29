from aiogram.fsm.state import State, StatesGroup
    

class EmailInputeDialog(StatesGroup):
    start = State()
    confirmed = State()


class FreeStartingDialog(StatesGroup):
    start = State()


class TrySubDialog(StatesGroup):
    start = State()
    paid = State()


class PaidStartingDialog(StatesGroup):
    start = State()
    not_access = State()


class AdminStartingDialog(StatesGroup):
    start = State()


class UsersGroupsDialog(StatesGroup):
    start = State()
    profile = State()
    inpute_email = State()
    change_email = State()
    empty_email = State()


class AddAccessDialog(StatesGroup):
    start = State()
    access = State()
    not_access = State()


class CloseAccessDialog(StatesGroup):
    start = State()
    close_access = State()
    not_close_access = State()


class ContentBotDialog(StatesGroup):
    start = State()
    training = State()
    upload_food = State()


class AddCategoryDialog(StatesGroup):
    start = State()
    confirm = State()


class SendMailingDialog(StatesGroup):
    start = State()
    text = State()
    plan_end = State()
    send_end = State()