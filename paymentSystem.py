import payok
import config as cfg

def create_pay(amount, payment, desc,method):
    return payok.createPay(secret=cfg.secret_token_of_your_shop, amount=amount, payment=payment, shop=cfg.shop_id_of_your_shop,desc=desc, method=method)

def get_transaction(payment_id):
    return payok.getTransaction(API_ID=cfg.API_ID, API_KEY=cfg.API_KEY,payment=payment_id,shop=cfg.shop_id_of_your_shop)

# print(create_pay(10,"1003",'asd',method=True))
# print(payok.getTransaction(API_ID=cfg.API_ID,API_KEY=cfg.API_KEY,payment='1003',shop=cfg.shop_id_of_your_shop)['1']['transaction_status'])
