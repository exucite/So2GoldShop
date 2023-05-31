from aiogram.dispatcher.filters.state import StatesGroup, State

class PriceState(StatesGroup):
    price = State()
    call = State()
    transaction_status = State()

class MailingState(StatesGroup):
    mailing = State()

class UpdateUserBalanceState(StatesGroup):
    username = State()
    gold = State()

class GoldWithdraw(StatesGroup):
    gold = State()
    screenshot = State()

class ApplicationAproove(StatesGroup):
    call = State()

class HelpQuestion(StatesGroup):
    text = State()

class AnswerQuestion(StatesGroup):
    text = State()

class TextReview(StatesGroup):
    text = State()

class Change_Exch_Course(StatesGroup):
    course = State()

class Change_Minimum_Of_Replenishment(StatesGroup):
    number = State()

class Change_Minimum_Of_Withdraw(StatesGroup):
    number = State()

class Change_Compulsory_Subscribe(StatesGroup):
    url = State()

class ChangeProcentForReferrer(StatesGroup):
    number = State()

class AddPromo(StatesGroup):
    promo = State()
    gold = State()
    limit = State()

class DeletePromo(StatesGroup):
    promos_array = State()
    promo = State()

class SetDice(StatesGroup):
    bet_sum = State()
    dice_value = State()

class CheckPromo(StatesGroup):
    promo = State()

