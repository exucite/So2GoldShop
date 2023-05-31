import asyncio

import aiogram.utils.exceptions
from aiogram import Dispatcher, Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from asyncio import sleep
import paymentSystem as ps
import keyboard as kb
import config as cfg
import states
import database as db
import sqlite3

storage = MemoryStorage()
bot = Bot(cfg.TOKEN_API)
dp = Dispatcher(bot, storage=storage)

db = db.Database()
db.connection = sqlite3.connect('database.db')
db.cursor = db.connection.cursor()

async def on_startup(_):
    db.start()
    db.insert_into_settings()
    print("Бот успешно запущен")

@dp.message_handler(commands= ['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    # db.add_user(user_id,0,message.from_user.username)
    if not db.user_exists(message.from_user.id):
        start_command = message.text
        referrer_id = str(start_command[7:])
        if str(referrer_id) != "":
            if str(referrer_id) != message.from_user.id:
                db.add_user(user_id=message.from_user.id,referrer_id=referrer_id,gold=0,username=message.from_user.username)
                try:
                    await bot.send_message(chat_id=referrer_id,text="По вашей ссылке зарегистрировался новый пользователь")
                except:
                    pass
            else:
                await message.answer("Нельзя зарегистрироваться по собственной реферальной ссылке!")
        else:
            db.add_user(user_id=message.from_user.id,referrer_id=None,gold=0,username=message.from_user.username)

    try:
        get_chat_member = await bot.get_chat_member(chat_id=f"@{db.select_from_settings()[0][3]}",user_id=message.from_user.id)
        get_chat_member = get_chat_member['status']
    except aiogram.utils.exceptions.ChatNotFound:
        get_chat_member = 'okay'

    if get_chat_member == 'left':
        await bot.send_message(text=f"Подпишитесь на канал для продолжения",chat_id=message.from_user.id,reply_markup=kb.compulsory_subscribe())
    else:
        if str(user_id) in cfg.admin:
            await message.answer(text='adsa',reply_markup=kb.menu(message.from_user.id))
        else:
            await message.answer(text='привет, ты попал в голд шоп', reply_markup=kb.menu(message.from_user.id))

@dp.message_handler()
async def message_handler(message: types.Message):

    try:
        get_chat_member = await bot.get_chat_member(chat_id=f"@{db.select_from_settings()[0][3]}",user_id=message.from_user.id)
        get_chat_member = get_chat_member['status']
    except aiogram.utils.exceptions.ChatNotFound:
        get_chat_member = 'okay'

    if get_chat_member == 'left':
        await bot.send_message(text=f"Подпишитесь на канал для продолжения",chat_id=message.from_user.id,reply_markup=kb.compulsory_subscribe())
    else:

        if message.text == "🪙Купить золото":
            await message.answer("🪙Введите подходящую вам сумму, а я тем временем, посчитаю сколько это будет в золотом эквиваленте",reply_markup=kb.back_to_menu())
            await states.PriceState.price.set()

        if message.text == '👤Профиль':
            await message.answer(f"Информация по вашему профилю:\n\nЗолота: {0 if db.check_profile(message.from_user.id)[0][2] is None else db.check_profile(message.from_user.id)[0][2]}\n\nРефералы: {len(db.select_only_referrers(message.from_user.id))}",reply_markup=kb.ref_system())

        if message.text == "💻Админ панель":
            await message.answer('💻Админ панель:',reply_markup=kb.adm_panel(len(db.check_applications()),len(db.check_questions())))

        if message.text == '📄Информация':
            await message.answer("📄Информация о нашем магазине",reply_markup=kb.info_about_shop())

        if message.text == '📦Вывести золото':
            if len(db.check_withdraw_by_username(message.from_user.username)) == 1:
                await message.answer(f"Вы уже подавали заявку под номером {db.check_withdraw_by_username(message.from_user.username)[0][4]}\n\nПожалуйста, подождите, пока администратор обработает вашу заявку.")
            else:
                await message.answer(f"📦Ваш баланс золота: {0 if db.check_profile(message.from_user.id)[0][2] is None else db.check_profile(message.from_user.id)[0][2]}\n\nВведите количество золота, которое вы хотите вывести: ",reply_markup=kb.back_to_menu())
                await states.GoldWithdraw.gold.set()

        if message.text == '🎰Мини-игры':
            await message.answer(f'Здесь вы можете поставить ставку и выиграть, либо проиграть. Отменить ставку можно на любом моменте(после выброса кубика уже нельзя). \nИгра "Брось кубик"\nОписание:\n\nПосле выставления вами ставки, вы должны бросить кубик. Если вам выпадет четное число, то ваш баланс пополняется на ставку в удвоенном эквиваленте. Если выпадет нечетное число, то ваша ставка сгорит и баланс уменьшится на сумму ставки',reply_markup=kb.mini_games())

        if message.text == 'Активировать промокод':
            await message.answer("Введите промокод:")
            await states.CheckPromo.promo.set()

        if message.text == '📍В главное меню':
            await message.answer('📍Главное меню',reply_markup=kb.menu(message.from_user.id))

@dp.message_handler(state=states.PriceState.price)
async def get_price(message: types.Message, state: FSMContext):

    await state.update_data(price=message.text)
    data = await state.get_data()

    if 'В главное меню' in data['price']:
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))
    elif int(data['price']) < db.select_from_settings()[0][1]:
        await message.answer(f"Минимальная сумма пополнения - {db.select_from_settings()[0][1]} рублей!\n\nПопробуйте ввести сумму еще раз.")
    else:
        try:
            db.insert_into_payments(user_id=message.from_user.id,username=message.from_user.username,amount=int(data['price']))
            await message.answer(f"Я рассчитал!\n\nКоличество золота, доступное вам за {data['price']} рублей: {int(float(data['price'])/db.select_from_settings()[0][0])} золотых", reply_markup=kb.payment_menu(url=ps.create_pay(amount=int(data['price']),payment=db.select_from_payments(user_id=message.from_user.id,username=None,payment_id=None,amount=None)[0][3],desc='test',method=None),payment_id=db.select_from_payments(user_id=message.from_user.id,username=None,payment_id=None,amount=None)[0][3]))
            await states.PriceState.next()
        except ValueError:
            await message.answer("Вы вводите неправильные данные! Напишите количество золота, которое вы бы хотели купить.")

@dp.callback_query_handler(state=states.PriceState.call)
async def wait_for_callback(callback_query: types.CallbackQuery, state: FSMContext):

    call = callback_query.data
    await state.update_data(call=call)
    data = await state.get_data()

    if 'cancel_payment_' in data['call']:
        payment_id = int(callback_query.data.split('_')[2])
        db.delete_payment(None,None,None,payment_id)
        await bot.send_message(text="Вы отклонили платеж",chat_id=callback_query.from_user.id,reply_markup=kb.menu(callback_query.from_user.id))
        await bot.delete_message(chat_id=callback_query.from_user.id,message_id=callback_query.message.message_id)
        await state.finish()

    elif 'check_payment_' in data['call']:
        payment_id = int(callback_query.data.split('_')[2])
        transaction_status = ps.get_transaction(payment_id)['1']['transaction_status']
        print(transaction_status)

        if transaction_status in '0':
            await bot.send_message(text="Оплата по транзакции не прошла",chat_id=callback_query.from_user.id)
        elif transaction_status in '1':
            await bot.send_message(text="Оплата прошла успешно, ваш баланс пополнен",chat_id=callback_query.from_user.id)
            db.update_values(user_id=callback_query.from_user.id,gold=db.check_profile(callback_query.from_user.id)[0][2] + data['price'],username=None)
            if db.check_profile(callback_query.from_user.id)[0][1] is not None:
                db.update_values(user_id=db.check_profile(callback_query.from_user.id)[0][1],gold=db.check_profile(db.check_profile(callback_query.from_user.id)[0][1])[0][2] + data['price']-(data['price']//float(db.select_from_settings()[0][4])))
                await bot.send_message(chat_id=db.check_profile(callback_query.from_user.id)[0][1], text=f"Ваш реферал пополнил золото\n\nВаш баланс пополнен на {data['price']-(data['price']//float(db.select_from_settings()[0][4]))}")
            else:
                pass

@dp.message_handler(state=states.PriceState.call)
async def wait_for_callback(message: types.Message, state: FSMContext):

    call = message.text
    await state.update_data(call=call)
    data = await state.get_data()
    data = data['call']

    if "В главное меню" in data:
        await message.answer("Оплатите либо отклоните платеж, чтобы продолжить.")
    else:
        await message.answer("Оплатите либо отклоните платеж, чтобы продолжить.")

@dp.message_handler(state=states.MailingState.mailing)
async def start_mailing(message: types.Message, state: FSMContext):

    await state.update_data(mailing=message.text)
    data = await state.get_data()
    if 'В главное меню' in data['mailing']:
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))
    else:
        for i in range(len(db.check_only_ids())):
            await bot.send_message(text=data['mailing'], chat_id=db.check_only_ids()[i][0])
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))

@dp.message_handler(state=states.UpdateUserBalanceState.username)
async def destination_username(message: types.Message, state: FSMContext):

    await state.update_data(username=message.text)
    data = await state.get_data()
    if 'В главное меню' in data['username']:
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))
    else:
        await message.answer(text='Теперь укажи сумму пополнения баланса:')
        await states.UpdateUserBalanceState.next()

@dp.message_handler(state=states.UpdateUserBalanceState.gold)
async def balance_top_up(message: types.Message, state: FSMContext):

    await state.update_data(gold=message.text)
    data = await state.get_data()
    if 'В главное меню' in data['gold']:
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_values(gold=data['gold'], username=data['username'], user_id=None)
        await state.finish()
        await message.answer(f"Баланс: {data['username']} обновлен",reply_markup=kb.menu(message.from_user.id))

@dp.message_handler(state=states.GoldWithdraw.gold)
async def gold_withdraw(message: types.Message, state: FSMContext):

    await state.update_data(gold=message.text)
    data = await state.get_data()

    if 'В главное меню' in data['gold']:
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))
    elif db.check_profile(message.from_user.id)[0][2] < int(data['gold']):
        await message.answer("Ваш баланс меньше выводимой вами суммы, попробуйте изменить сумму вашего вывода.")
    elif int(data['gold']) <= 0:
        await message.answer("Невозможно вывести сумму меньше или равную нулю!")
    elif int(data['gold']) < int(db.select_from_settings()[0][2]):
        await message.answer(f"Минимальная сумма вывода - {db.select_from_settings()[0][2] } золота!")
    else:
        await bot.send_photo(caption=f"Итак, теперь выставите скин на торговую площадку игры за {int((float(data['gold']) * cfg.tp_procent) + float(data['gold']))} золотых и отправьте скрин", reply_markup=kb.back_to_menu(),chat_id=message.from_user.id,photo=open('img.png','rb'))
        await states.GoldWithdraw.next()

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=states.GoldWithdraw.screenshot)
async def gold_withdraw(message: types.Message, state: FSMContext):

    photo = message.photo[-1].file_id
    await state.update_data(screenshot=photo)
    data = await state.get_data()
    db.add_gold_withdraw(user_id=message.from_user.id, amount_of_gold=data['gold'],username = message.from_user.username, photo = data['screenshot'])
    application_id = db.check_withdraw_by_username(message.from_user.username)[-1][4]
    await bot.send_photo(photo=data['screenshot'],chat_id=message.from_user.id,caption=f"Вы уверены, что хотите отправить заявку на вывод?\n\nКоличество золота на вывод: {data['gold']}",reply_markup=kb.aproove_send_gold_withdraw(application_id))
    await state.finish()

@dp.message_handler(content_types=types.ContentTypes.TEXT,state=states.GoldWithdraw.screenshot)
async def gold_cancel_withdraw(message: types.Message, state: FSMContext):

    await state.update_data(screenshot=message.text)
    data = await state.get_data()
    if data['screenshot'] in 'В главное меню':
        await state.finish()
        await message.answer('Главное меню', reply_markup=kb.menu(message.from_user.id))

@dp.message_handler(state=states.HelpQuestion.text)
async def get_question_text(message: types.Message, state: FSMContext):

    await state.update_data(text=message.text)
    data = await state.get_data()
    if len(data['text']) < 15:
        await message.answer('Ваша заявка должна содержать хотя бы 15 символов\n\nПожалуйста, напишите текст заявки снова.')
    elif 'В главное меню' in data['text']:
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
        await state.finish()
    else:
        db.insert_into_questions(message.from_user.id,data['text'])
        await message.answer(f"Номер вашей заявки: {db.select_from_questions(user_id=message.from_user.id,id=None)[0][2]}\n\nТекст вашей заявки: {db.select_from_questions(message.from_user.id,id=None)[0][1]}\n\nВы уверены, что хотите отправить заявку?",reply_markup=kb.aproove_send_question(db.select_from_questions(message.from_user.id,id = None)[0][2]))
        await state.finish()

@dp.message_handler(state=states.AnswerQuestion.text)
async def answer_question(message: types.Message, state: FSMContext):

    await state.update_data(text=message.text)
    data = await state.get_data()
    if "Главное меню" in data['text']:
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        try:
            await bot.send_message(text=f"Ответ на ваш вопрос с ID {data['id']}:\n\n{data['text']}",chat_id=db.select_from_questions(user_id=None, id=data['id'])[0][0])
            await message.answer(f"Ответ на вопрос с ID {data['id']} был отправлен")
            db.delete_from_questions(user_id=None,id=data['id'])
            await state.finish()
        except IndexError:
            await message.answer("Вы отвечаете на не существующую заявку!")
            await state.finish()

@dp.message_handler(state=states.TextReview.text)
async def text_to_review(message: types.Message, state: FSMContext):

    await state.update_data(text=message.text)
    data = await state.get_data()
    if data['text'] == 'Не хочу ничего писать':
        await bot.send_message(text=f"{message.from_user.first_name}: промолчал...\n\nВывел",chat_id=-1001818629572)
    await bot.send_message(text=f"{message.from_user.first_name}:{data['text']}",chat_id=-1001818629572)
    await state.finish()

@dp.message_handler(state=states.Change_Exch_Course.course)
async def change_exch_course(message: types.Message, state: FSMContext):

    await state.update_data(course=message.text)
    data = await state.get_data()
    data = data['course']
    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_settings(exch_rate=float(data),minimum_of_replenishment=None,minimum_of_withdraw=None,compulsory_subscribe=None,procent_of_referrer=None)
        await message.answer(f"Курс покупки успешно изменен на {data}!",reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.Change_Minimum_Of_Replenishment.number)
async def change_min_of_replenish(message: types.Message, state: FSMContext):

    await state.update_data(number=message.text)
    data = await state.get_data()
    data = data['number']
    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_settings(exch_rate=None,minimum_of_replenishment=int(data),minimum_of_withdraw=None,compulsory_subscribe=None,procent_of_referrer=None)
        await message.answer(f"Минимальная сумма пополнения изменена на {data}!",reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.Change_Minimum_Of_Withdraw.number)
async def change_min_of_wihtdraw(message: types.Message, state: FSMContext):

    await state.update_data(number=message.text)
    data = await state.get_data()
    data = data['number']

    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_settings(exch_rate=None,minimum_of_replenishment=None,minimum_of_withdraw=int(data),compulsory_subscribe=None,procent_of_referrer=None)
        await message.answer(f"Минимальная сумма вывода золота изменена на {data}!", reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.Change_Compulsory_Subscribe.url)
async def change_compulsory_subscribe(message: types.Message, state: FSMContext):

    await state.update_data(url=message.text)
    data = await state.get_data()
    data = data['url']

    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_settings(exch_rate=None,minimum_of_replenishment=None,minimum_of_withdraw=None,compulsory_subscribe=data)
        await message.answer(f'Обязательная подписка теперь работает на <a href="https://t.me/{data}">этот</a> канал',parse_mode='HTML',reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.ChangeProcentForReferrer.number)
async def change_procent_for_referrer(message: types.Message, state: FSMContext):

    await state.update_data(number=message.text)
    data = await state.get_data()
    data = data['number']

    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.update_settings(exch_rate=None, minimum_of_replenishment=None,minimum_of_withdraw=None, compulsory_subscribe=None,procent_of_referrer=float(data)/100)
        await message.answer(f"Процент изменен на: {data}",reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.AddPromo.promo)
async def add_promo(message: types.Message, state: FSMContext):

    await state.update_data(promo=message.text)
    data = await state.get_data()
    data = data['promo']

    if "В главное меню" in data:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        await message.answer(f"Теперь введите сумму пополнения при активации промокода:")
        await states.AddPromo.next()

@dp.message_handler(state=states.DeletePromo.promo)
async def delete_promo(message: types.Message, state: FSMContext):

    await state.update_data(promo=message.text)
    data = await state.get_data()

    if "В главное меню" in data['promo']:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        for i in data['promos_array']:
            is_delete = False
            if i.startswith(f"{data['promo']}"):
                db.delete_promo(i[3:])
                await bot.send_message(text=f"Промокод {i[3:]} удален",chat_id=message.from_user.id)
                is_delete = True
        if is_delete is not True:
            await bot.send_message(text="Такого промокода не существует, введите цифру еще раз",chat_id=message.from_user.id,reply_markup=kb.back_to_menu())
        else:
            await state.finish()

@dp.message_handler(state=states.SetDice.bet_sum)
async def sum_of_bet(message: types.Message, state: FSMContext):

    await state.update_data(sum_of_bet=message.text)
    data = await state.get_data()

    if "Отменить ставку" in data['sum_of_bet']:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        try:
            if int(data['sum_of_bet']) > int(db.check_profile(message.from_user.id)[0][2]):
                print(data['sum_of_bet'])
                await message.answer("Ваш баланс меньше суммы ставки. Пожалуйста, введите сумму ставки меньше, либо пополните баланс.",reply_markup=kb.cancel_dice())
            else:
                await message.answer("Теперь бросьте кубик(напишите dice/кубик и нажмите на кубик в подсказке телеграмма)",reply_markup=kb.cancel_dice())
                await states.SetDice.next()
        except TypeError:
            await message.answer(
                "Ваш баланс меньше суммы ставки. Пожалуйста, введите сумму ставки меньше, либо пополните баланс.",
                reply_markup=kb.cancel_dice())

@dp.message_handler(state=states.SetDice.dice_value,content_types=['dice'])
async def dice_value(message: types.Message, state: FSMContext):

    await state.update_data(dice_value=message.dice.value)
    data = await state.get_data()

    if int(data['dice_value']) == 5:
        await asyncio.sleep(4)
        db.update_values(user_id=message.from_user.id,gold=int(db.check_profile(message.from_user.id)[0][2]) + (float(data['sum_of_bet']) * 1.1 - float(data['sum_of_bet'])),username=None)
        await message.answer(f"Вы выиграли! Ваш баланс пополнен на {(float(data['sum_of_bet']) * 1.1 - float(data['sum_of_bet']))} золотых",reply_markup=kb.menu(message.from_user.id))
        await state.finish()
    if int(data['dice_value']) == 6:
        await asyncio.sleep(4)
        db.update_values(user_id=message.from_user.id,gold=int(db.check_profile(message.from_user.id)[0][2]) + int(data['sum_of_bet']),username=None)
        await message.answer(f"Вы выиграли! Ваш баланс пополнен на {data['sum_of_bet']} золотых",reply_markup=kb.menu(message.from_user.id))
        await state.finish()
    if int(data['dice_value']) == 3:
        await asyncio.sleep(4)
        db.update_values(user_id=message.from_user.id,gold=int(db.check_profile(message.from_user.id)[0][2]) - (int(data['sum_of_bet']) - float(data['sum_of_bet']) * 0.9),username=None)
        await message.answer(f"Вы проиграли! Ваш баланс уменьшен на {(int(data['sum_of_bet']) - float(data['sum_of_bet']) * 0.9)} золотых",reply_markup=kb.menu(message.from_user.id))
        await state.finish()
    if int(data['dice_value']) == 4:
        await asyncio.sleep(4)
        await message.answer(f"Ничья! Ваш баланс остался прежним",reply_markup=kb.menu(message.from_user.id))
        await state.finish()
    if int(data['dice_value']) == 1 or int(data['dice_value']) == 2:
        await asyncio.sleep(4)
        db.update_values(user_id=message.from_user.id,gold=int(db.check_profile(message.from_user.id)[0][2]) - int(data['sum_of_bet']),username=None)
        await message.answer(f"Вы проиграли... Ваш баланс уменьшен на {data['sum_of_bet']} золотых",reply_markup=kb.menu(message.from_user.id))
        await state.finish()

@dp.message_handler(state=states.AddPromo.gold)
async def add_gold_to_promo(message: types.Message,state: FSMContext):

    await state.update_data(gold=message.text)
    data = await state.get_data()

    if "В главное меню" in data['gold']:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        await message.answer(f"Введите лимит пользователей на промокод")
        await states.AddPromo.next()

@dp.message_handler(state=states.AddPromo.limit)
async def add_limit_to_promo(message: types.Message, state: FSMContext):

    await state.update_data(limit=message.text)
    data = await state.get_data()

    if "В главное меню" in data['limit']:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        db.add_promo(promo=data['promo'],gold=data['gold'],limit=data['limit'])
        await message.answer(f"Промокод {data['promo']} c лимитом {data['limit']} и пополнением {data['gold']} золота добавлен!")
        await  state.finish()

@dp.message_handler(state=states.CheckPromo.promo)
async def activation_promo(message: types.Message, state: FSMContext):

    await state.update_data(promo=message.text)
    data = await state.get_data()

    if "В главное меню" in data['promo']:
        await state.finish()
        await message.answer("Главное меню",reply_markup=kb.menu(message.from_user.id))
    else:
        try:
            if len(db.select_by_promo(data['promo'])) != 0:
                if db.select_by_promo(data['promo'])[0][3] < 1:
                    await message.answer("Данный промокод больше на активен")
                    db.delete_promo(data['promo'])
                else:
                    if str(message.from_user.id) in ("" if db.select_by_promo(data['promo'])[0][2] is None else db.select_by_promo(data['promo'])[0][2]):
                        await message.answer("Вы уже активировали данный промокод")
                        await state.finish()
                    else:
                        await state.finish()
                        db.update_values(user_id=message.from_user.id,gold=int(db.check_profile(message.from_user.id)[0][2]) + int(db.select_by_promo(data['promo'])[0][1]),username=None)
                        await message.answer(f"Ваш баланс пополнен на {db.select_by_promo(data['promo'])[0][1]} золотых.")
                        db.insert_into_promo_activates(promo=data['promo'],user_id=(db.select_by_promo(data['promo'])[0][2] + f"{message.from_user.id} " if db.select_by_promo(data['promo'])[0][2] is not None else f"{message.from_user.id} "))
                        db.update_limit(limit=int(db.select_by_promo(data['promo'])[0][3]) - 1,promo=data['promo'])
                        if db.select_by_promo(data['promo'])[0][3] == 0:
                            db.delete_promo(data['promo'])
                        else:
                            pass
                        await state.finish()
            else:
                await message.answer("Такого промокода не существует",reply_markup=kb.back_to_menu())
        except IndexError:
            await message.answer("Такого промокода не существует",reply_markup=kb.back_to_menu())

@dp.callback_query_handler(lambda callback_query: True)
async def callback_handler(callback_query: types.CallbackQuery, state: FSMContext):

    try:
        get_chat_member = await bot.get_chat_member(chat_id=f"@{db.select_from_settings()[0][3]}",user_id=callback_query.from_user.id)
        get_chat_member = get_chat_member['status']
    except aiogram.utils.exceptions.ChatNotFound:
        get_chat_member = 'okay'

    if get_chat_member == 'left' and callback_query.data != 'check_subscribe':
        await bot.send_message(text=f"Подпишитесь на канал для продолжения",chat_id=callback_query.from_user.id,reply_markup=kb.compulsory_subscribe())
    else:
        if callback_query.data == 'mailing':
            await callback_query.answer()
            await bot.send_message(chat_id=callback_query.from_user.id, text='Напишите текст для рассылки:',reply_markup=kb.back_to_menu())
            await states.MailingState.mailing.set()

        if callback_query.data == 'update_user_balance':
            await callback_query.answer()
            await bot.send_message(chat_id=callback_query.from_user.id, text='Напиши юзернейм чела, без @:',reply_markup=kb.back_to_menu())
            await states.UpdateUserBalanceState.username.set()

        if callback_query.data == 'statistic':
            await callback_query.answer()
            await bot.send_message(chat_id=callback_query.from_user.id, text=f"Статистика бота:\n\nЧисло пользователей в боте: {len(db.check_all())}")

        if callback_query.data.startswith('aproove_gold_no_'):
            await callback_query.answer()
            application_id = int(callback_query.data.split('_')[3])
            db.delete_withdraw(id=application_id,username=None,user_id=None)
            await bot.send_message(text="Ваша заявка успешно удалена!",reply_markup=kb.menu(callback_query.from_user.id),chat_id=callback_query.from_user.id)
            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

        if callback_query.data.startswith('aproove_gold_yes_'):
            await callback_query.answer()
            application_id = int(callback_query.data.split('_')[3])
            await bot.send_message(text=f"Ваша заявка успешно отправлена!\nОжидайте пополнения баланса в игре.\n\nID вашей заявки: {application_id}", chat_id=callback_query.from_user.id,reply_markup=kb.menu(callback_query.from_user.id))
            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
            db.set_is_valid_withdraw_bool(bool=True, user_id=callback_query.from_user.id,username=None)
            for i in cfg.admin:
                await bot.send_message(text="Пришла новая заявка на вывод!",chat_id=int(i))

        if callback_query.data == 'applications':
            await callback_query.answer()
            if db.check_applications():
                for i in range(len(db.check_applications())):
                    await bot.send_photo(chat_id=callback_query.from_user.id,caption=f"ID заявки: {db.check_applications()[i][4]}\n\nКоличество голды на вывод: {db.check_applications()[i][1]}\nС учетом комиссии: {int((db.check_applications()[i][1] * cfg.tp_procent) + db.check_applications()[i][1])}\n\nСвязь с <a href='t.me/{db.check_applications()[i][2]}'>клиентом</a>",photo=db.check_applications()[i][3],reply_markup=kb.aproove_taken_application(db.check_applications()[i][4]), parse_mode="HTML")
            else:
                await bot.send_message(chat_id=callback_query.from_user.id,text='Упс... Похоже заявок нет')

        if callback_query.data.startswith('accept_'):
            await callback_query.answer()
            application_id = int(callback_query.data.split('_')[1])
            await bot.send_message(text=f"Заявка с ID {application_id} принята",chat_id=callback_query.from_user.id)
            await bot.send_message(chat_id=db.select_only_tg_id(application_id)[0][0], text=f"Ваша заявка с ID {application_id} принята.\n\nПожалуйста, напишите ваш отзыв, он отправится в группу отзывов!",reply_markup=kb.to_reviews())
            db.update_values(user_id=db.select_only_tg_id(application_id)[0][0],username=None, gold=db.check_profile(db.select_only_tg_id(application_id)[0][0])[0][2] - db.select_only_gold_withdraw(application_id)[0][0])
            db.delete_withdraw(username=None,user_id=None,id=application_id)
            await states.TextReview.text.set()

        if callback_query.data.startswith('reject_'):
            await callback_query.answer()
            application_id = int(callback_query.data.split('_')[1])
            await bot.send_message(chat_id=db.select_only_tg_id(application_id)[0][0],text=f"Ваша заявка с ID {application_id} отклонена.\n\nВозможно, мы не смогли найти ваш скин на торговой площадке, но не волнуйтесь, баланс вашего счета остался в прежнем состоянии, вы можете подать заявку на вывод еще раз!")
            await bot.send_message(text=f"Заявка с ID {application_id} отклонена", chat_id=callback_query.from_user.id)
            db.delete_withdraw(username=None, user_id=None, id=application_id)

        if callback_query.data == 'help':
            await callback_query.answer()
            await bot.edit_message_text(text="Здесь я могу ответить вам на часто-задаваемые вопросы. Вот их список, нажмите на определенную цифру, чтобы увидеть ответ:\n\n1.чето там\n2.asd\n3.asd\n4.asd\n\nТакже ты можешь обратиться в поддержку, но ответ сильно задержится.",message_id=callback_query.message.message_id,chat_id=callback_query.message.chat.id,reply_markup=kb.help_menu())

        if callback_query.data == 'answer_1':
            await callback_query.answer()
            await bot.edit_message_text(text='потому что', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,reply_markup=kb.back_to_help_menu())

        if callback_query.data == 'answer_2':
            await callback_query.answer()
            await bot.edit_message_text(text='потому что', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,reply_markup=kb.back_to_help_menu())

        if callback_query.data == 'ansnwer_3':
            await callback_query.answer()
            await bot.edit_message_text(text='потому что', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,reply_markup=kb.back_to_help_menu())

        if callback_query.data == 'answer_4':
            await callback_query.answer()
            await bot.edit_message_text(text='потому что', chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,reply_markup=kb.back_to_help_menu())

        if callback_query.data == 'to_helpers':
            await callback_query.answer()
            await bot.send_message(text="Напишите свой вопрос четко и понятно, чтобы поддержка смогла обработать его максимально быстро и качественно:", chat_id=callback_query.message.chat.id,reply_markup=kb.back_to_menu())
            await states.HelpQuestion.text.set()

        if callback_query.data.startswith('question_send_accept_'):
            await callback_query.answer()
            question_id = callback_query.data.split('_')[3]
            # db.set_valid_question(question_id)
            await bot.send_message(text="Ваша заявка отправлена! Ожидайте ответа администратора",chat_id=callback_query.from_user.id)

        if callback_query.data.startswith('question_send_reject_'):
            await callback_query.answer()
            question_id = callback_query.data.split('_')[3]
            db.delete_from_questions(callback_query.from_user.id,question_id)
            await bot.send_message(text="Ваша заявка удалена.",chat_id=callback_query.from_user.id)

        if callback_query.data == 'questions':
            await callback_query.answer()
            if db.check_questions():
                for i in db.check_questions():
                    await bot.send_message(text=f"ID Вопроса: {i[2]}\n\nТекст заявки: {i[1]}",chat_id=callback_query.from_user.id,reply_markup=kb.aproove_taken_question(i[2]))
            else:
                await bot.send_message(chat_id=callback_query.from_user.id,text='Упс... Похоже вопросов нет')
            await callback_query.answer()

        if callback_query.data.startswith('taken_question_reject_'):
            await callback_query.answer()
            question_id = callback_query.data.split('_')[3]
            db.delete_from_questions(user_id=None,id=question_id)
            await bot.send_message(text=f"Заявка с ID {question_id} отклонена",chat_id=callback_query.from_user.id)

        if callback_query.data.startswith('taken_question_answer_'):
            await callback_query.answer()
            question_id = callback_query.data.split('_')[3]
            await bot.send_message(text="Напишите ответ пользователю:",chat_id=callback_query.from_user.id)
            await states.AnswerQuestion.text.set()
            await state.update_data(id=question_id)

        if callback_query.data == 'change_exch_course':
            await callback_query.answer()
            await bot.send_message(text="Напишите новый курс в виде дроби(например: 0.5 или 0.4):",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
            await states.Change_Exch_Course.course.set()

        if callback_query.data == 'change_minimum_of_replenish':
            await callback_query.answer()
            await bot.send_message(text="Напишите новую минимальную сумму пополнения:",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
            await states.Change_Minimum_Of_Replenishment.number.set()

        if callback_query.data == 'change_minimum_of_withdraw':
            await callback_query.answer()
            await bot.send_message(text="Напишите новую минимальную сумму пополнения:",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
            await states.Change_Minimum_Of_Withdraw.number.set()

        if callback_query.data == 'info_about_settings':
            await callback_query.answer()
            await bot.send_message(text=f"Курс покупки золота - {db.select_from_settings()[0][0]}\n\nМинимальная сумма пополнения - {db.select_from_settings()[0][1]}\n\nМинимальная сумма вывода - {db.select_from_settings()[0][2]}",chat_id=callback_query.from_user.id)

        if callback_query.data == 'change_compulsory_subscribe':
            await callback_query.answer()
            await bot.send_message(text="Напишите ссылку на группу без https и @(например standoff_reviews):",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
            await states.Change_Compulsory_Subscribe.url.set()

        if callback_query.data == 'change_procent_for_referrer':
            await callback_query.answer()
            await bot.send_message(text="Напишите новый процент для пополнения процента оп покупки реферала(писать без %. Например - 20 или 10)",chat_id=callback_query.from_user.id, reply_markup=kb.back_to_menu())
            await states.ChangeProcentForReferrer.number.set()

        if callback_query.data == 'promo':
            await callback_query.answer()
            await bot.edit_message_text(text="Настройка промокодов",chat_id=callback_query.message.chat.id,message_id=callback_query.message.message_id,reply_markup=kb.promos())

        if callback_query.data == 'check_all_promos':
            await callback_query.answer()
            promos = db.select_from_promos(as_array=False)
            promos_as_text = ""
            if len(promos) != 0:
                for i in promos:
                    promos_as_text += f"{i[0]} | {i[1]} | {i[3]}\n"
                await bot.send_message(text=f"Доступные промокоды:\n\n{promos_as_text}",chat_id=callback_query.from_user.id)
            else:
                await bot.send_message(text="Промокодов нет",chat_id=callback_query.from_user.id)

        if callback_query.data == 'add_promo':
            await callback_query.answer()
            await bot.send_message(text="Напишите промокод, который вы хотите добавить:",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
            await states.AddPromo.promo.set()

        if callback_query.data == 'delete_promo':
            await callback_query.answer()
            promos = db.select_from_promos(as_array=False)
            promos_as_text = ""
            promos_as_array = []
            if len(promos) != 0:
                count = 1
                for i in promos:
                    print(i)
                    promos_as_text += f"{count}. {i[0]}\n"
                    promos_as_array.append(f"{count}. {i[0]}")
                    count += 1
                await bot.send_message(text=f"Доступные промокоды:\n\n{promos_as_text}",
                                       chat_id=callback_query.from_user.id)
                await states.DeletePromo.promos_array.set()
                await state.update_data(promos_array=promos_as_array)
                await state.get_data()
                await bot.send_message(text="Введите цифру промокода, который вы хотите удалить",chat_id=callback_query.from_user.id,reply_markup=kb.back_to_menu())
                await states.DeletePromo.next()
            else:
                await bot.send_message(text="Промокодов нет", chat_id=callback_query.from_user.id)

        if callback_query.data == 'delete_all_promos':
            await callback_query.answer()
            db.delete_all_promos()
            await bot.send_message(chat_id=callback_query.from_user.id,text="Все промокоды удалены")

        if callback_query.data == 'back_to_help_menu':
            await callback_query.answer()
            await bot.edit_message_text(message_id=callback_query.message.message_id, chat_id=callback_query.from_user.id, text="Здесь я могу ответить вам на часто-задаваемые вопросы. Вот их список, нажмите на определенную цифру, чтобы увидеть ответ:\n\n1.чето там\n2.asd\n3.asd\n4.asd\n\nТакже ты можешь обратиться в поддержку, но ответ сильно задержится.",reply_markup=kb.help_menu())

        if callback_query.data == 'ref_system':
            await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=f"Ваша реферальная ссылка: https://t.me/{cfg.BOT_NICNAME}?start={callback_query.from_user.id}\n\nОписание реферальной системы:\n\nЕсли пользователь зарегистрируется по вашей ссылке, то после каждого его пополнения, вам будет приходить процент. Рефералов может быть несколько.",reply_markup=kb.back_to_profile())

        if callback_query.data == 'back_to_profile':
            await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=callback_query.message.message_id, text=f"Информация по вашему профилю:\n\nЗолота: {0 if db.check_profile(callback_query.from_user.id)[0][2] is None else db.check_profile(callback_query.from_user.id)[0][2]}\n\nРефералы: {len(db.select_only_referrers(callback_query.from_user.id))}",reply_markup=kb.ref_system())

        if callback_query.data == 'throw_dice':
            await bot.send_message(chat_id=callback_query.from_user.id, text="Введите сумму ставки:",reply_markup=kb.cancel_dice())
            await states.SetDice.bet_sum.set()

    if callback_query.data == 'check_subscribe':
        await callback_query.answer()
        get_chat_member = await bot.get_chat_member(chat_id=f"@{db.select_from_settings()[0][3]}",user_id=callback_query.from_user.id)
        get_chat_member = get_chat_member['status']

        if get_chat_member == 'left':
            await bot.send_message(text="Вы все еще не подписаны на канал!",chat_id=callback_query.from_user.id)
        else:
            await bot.send_message(text="Подписка на канал оформлена, вы можете продолжать пользоваться ботом",reply_markup=kb.back_to_menu(),chat_id=callback_query.from_user.id)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)