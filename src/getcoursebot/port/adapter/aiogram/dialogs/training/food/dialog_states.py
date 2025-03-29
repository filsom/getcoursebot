from aiogram.fsm.state import State, StatesGroup


class TrainingDialog(StatesGroup):
    start = State()
    categories = State()
    view = State()


class NewTrainingDialog(StatesGroup):
    start = State()
    send = State()


class UploadMediaDialog(StatesGroup):
    start = State()
    text = State()
    view = State()



class InputDialog(StatesGroup):
    start = State()
    b = State()
    j = State()
    u = State()
    activity = State()
    target = State()
    end = State()

    
class CalculateDialog(StatesGroup):
    start = State()
    hieght = State()
    age = State()
    activity = State()
    target = State()
    end = State()


class WithDataDialog(StatesGroup):
    start = State()


# class DayMenuDialog(StatesGroup):
#     breakfast = State()
#     lunch = State()
#     dinner = State()
#     snack= State()
#     end = State()
#     end_my_snack = State()


class DayMenuDialog(StatesGroup):
    start = State()
    view = State()


class FoodDialog(StatesGroup):
    start = State()