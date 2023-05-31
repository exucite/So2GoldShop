from aiogram import types
import config as cfg
import database as db
import sqlite3

db = db.Database()
db.connection = sqlite3.connect('database.db')
db.cursor = db.connection.cursor()

def menu(id):
    if str(id) in cfg.admin:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_gold = types.KeyboardButton("🪙Купить золото")
        button_withdraw = types.KeyboardButton("📦Вывести золото")
        button_profile = types.KeyboardButton("👤Профиль")
        button_reviews = types.KeyboardButton("📄Информация")
        button_adm = types.KeyboardButton("💻Админ панель")
        button_games = types.KeyboardButton("🎰Мини-игры")
        button_promocode = types.KeyboardButton("Активировать промокод")
        kb.add(button_gold, button_withdraw)
        kb.add(button_profile)
        kb.insert(button_reviews)
        kb.insert(button_games)
        kb.add(button_promocode)
        return kb.add(button_adm)
    else:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button_gold = types.KeyboardButton("🪙Купить золото")
        button_withdraw = types.KeyboardButton(f"📦Вывести золото")
        button_profile = types.KeyboardButton("👤Профиль")
        button_reviews = types.KeyboardButton("📄Информация")
        button_games = types.KeyboardButton("🎰Мини-игры")
        button_promocode = types.KeyboardButton("Активировать промокод")
        kb.add(button_gold, button_withdraw, button_profile)
        kb.insert(button_games)
        kb.add(button_promocode)
        return kb.insert(button_reviews)


def payment_menu(payment_id, url):
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_payment = types.InlineKeyboardButton(text="Оплатить", url=url)
    button_check_payment = types.InlineKeyboardButton(text="Проверить оплату",
                                                      callback_data=f"check_payment_{payment_id}")
    button_cancel = types.InlineKeyboardButton(text="Отменить оплату", callback_data=f"cancel_payment_{payment_id}")
    return kb.add(button_payment, button_check_payment, button_cancel)


def communication_with_adm():
    kb = types.InlineKeyboardMarkup()
    button_communicate = types.InlineKeyboardButton(text="Связаться", url='https://t.me/imusya')
    return kb.add(button_communicate)


def adm_panel(len_application, len_questions):
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_mailing = types.InlineKeyboardButton(text='Рассылка', callback_data='mailing')
    button_update_user_balance = types.InlineKeyboardButton(text='Управление балансом',
                                                            callback_data='update_user_balance')
    button_get_statistic = types.InlineKeyboardButton(text='Статистика', callback_data='statistic')
    button_applications = types.InlineKeyboardButton(text=f"Заявки({len_application})", callback_data='applications')
    button_questions = types.InlineKeyboardButton(text=f"Вопросы({len_questions})", callback_data='questions')
    button_info_about_settings = types.InlineKeyboardButton(text="Инфо о настройках",
                                                            callback_data='info_about_settings')
    button_change_exch_course = types.InlineKeyboardButton(text=f"Изм. курс золота", callback_data='change_exch_course')
    button_change_minimum_of_replenishment = types.InlineKeyboardButton(text="Изм. мин. сумму пополнения",
                                                                        callback_data='change_minimum_of_replenish')
    button_change_minimum_of_withdraw = types.InlineKeyboardButton(text="Изм. мин. сумму вывода",
                                                                   callback_data='change_minimum_of_withdraw')
    button_change_compulsory_subscribe = types.InlineKeyboardButton(text="Изм. обяз. подписку",
                                                                    callback_data='change_compulsory_subscribe')
    button_change_procent_for_referrer = types.InlineKeyboardButton(text="Изм. % пополнения реферала",callback_data='change_procent_for_referrer')
    button_promos = types.InlineKeyboardButton(text="Настройки промокодов",callback_data='promo')

    return kb.add(button_mailing, button_update_user_balance, button_get_statistic, button_applications,
                  button_questions, button_info_about_settings, button_change_exch_course,
                  button_change_minimum_of_replenishment, button_change_minimum_of_withdraw,
                  button_change_compulsory_subscribe,
                  button_change_procent_for_referrer,
                  button_promos)


def adm_panel_settings():
    kb = types.InlineKeyboardMarkup()
    button_change_exchange_rate = types.InlineKeyboardButton(text='Изменить курс', callback_data='change_exchange_rate')
    return kb.add(button_change_exchange_rate)


def back_to_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_back = types.KeyboardButton(text='📍В главное меню')
    return kb.add(button_back)


def to_reviews():
    kb = types.InlineKeyboardMarkup()
    button_url = types.InlineKeyboardButton(text='Отзывы', url=f"{cfg.channel_with_reviews}",
                                            callback_data='to_reviews')
    return kb.add(button_url)


def aproove_send_gold_withdraw(application):
    kb = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data=f"aproove_gold_yes_{application}")
    button_no = types.InlineKeyboardButton(text='Нет', callback_data=f"aproove_gold_no_{application}")
    return kb.add(button_yes, button_no)


def aproove_taken_application(application):
    kb = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Принять', callback_data=f"accept_{application}")
    button_no = types.InlineKeyboardButton(text='Отклонить', callback_data=f"reject_{application}")
    return kb.add(button_yes, button_no)


def info_about_shop():
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_news = types.InlineKeyboardButton(text="Новостник", url=cfg.channel_with_news)
    button_reviews = types.InlineKeyboardButton(text="Отзывы", url=cfg.channel_with_reviews)
    button_help = types.InlineKeyboardButton(text="Поддержка", callback_data='help')
    return kb.add(button_news, button_reviews, button_help)


def help_menu():
    kb = types.InlineKeyboardMarkup(row_width=3)
    button_1 = types.InlineKeyboardButton(text='1', callback_data='answer_1')
    button_2 = types.InlineKeyboardButton(text='2', callback_data='answer_2')
    button_3 = types.InlineKeyboardButton(text='3', callback_data='answer_3')
    button_4 = types.InlineKeyboardButton(text='4', callback_data='answer_4')
    button_help = types.InlineKeyboardButton(text='Обратиться', callback_data='to_helpers')
    return kb.add(button_1, button_2, button_3, button_4, button_help)


def aproove_send_question(question_id):
    kb = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data=f"question_send_accept_{question_id}")
    button_no = types.InlineKeyboardButton(text='Нет', callback_data=f"question_send_reject_{question_id}")
    return kb.add(button_yes, button_no)


def aproove_taken_question(question_id):
    kb = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text="Ответить на вопрос",
                                            callback_data=f"taken_question_answer_{question_id}")
    button_no = types.InlineKeyboardButton(text="Удалить вопрос", callback_data=f"taken_question_reject_{question_id}")
    return kb.add(button_no, button_yes)


def compulsory_subscribe():
    kb = types.InlineKeyboardMarkup()
    button_url = types.InlineKeyboardButton(text=f"Подписаться", url=f"https://t.me/{db.select_from_settings()[0][3]}")
    button_check = types.InlineKeyboardButton(text=f"Проверить подписку", callback_data="check_subscribe")
    return kb.add(button_url, button_check)

def promos():
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_check_all_promos = types.InlineKeyboardButton(text=f"Посмотреть все промокоды",callback_data="check_all_promos")
    button_add_promo = types.InlineKeyboardButton(text="Добавить промокод", callback_data="add_promo")
    button_delete_promo = types.InlineKeyboardButton(text="Удалить промокод",callback_data='delete_promo')
    button_delete_all_promos = types.InlineKeyboardButton(text="Удалить все промокоды",callback_data='delete_all_promos')
    return kb.add(button_check_all_promos,button_add_promo,button_delete_promo,button_delete_all_promos)

def back_to_help_menu():
    kb = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton(text="Вернуться в меню поддержки", callback_data='back_to_help_menu')
    return kb.add(button_back)

def ref_system():
    kb = types.InlineKeyboardMarkup()
    button_ref = types.InlineKeyboardButton(text="Реферальная система",callback_data='ref_system')
    return kb.add(button_ref)

def back_to_profile():
    kb = types.InlineKeyboardMarkup()
    button_back = types.InlineKeyboardButton(text="Назад в профиль",callback_data='back_to_profile')
    return kb.add(button_back)

def mini_games():
    kb = types.InlineKeyboardMarkup()
    button_dice = types.InlineKeyboardButton(text="Брось кубик",callback_data='throw_dice')
    return kb.add(button_dice)

def cancel_dice():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_cancel = types.KeyboardButton("Отменить ставку")
    return kb.add(button_cancel)
