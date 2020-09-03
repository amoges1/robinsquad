import flask_vars
import robin_stocks as r
import pymongo
import pprint as pprint
import json
import ast

# import pymongo (needs dnspython)
# connect to MongoDB
client = pymongo.MongoClient(flask_vars.mongoDB)
db = client.robinsquad

def get_port_info(email): # my_acc, instrs_quantity
    '''Retrieve a list of stock objects from portfolio'''
    return db.users.find_one({"email": email})["portfolio"]

def login(email, password):
    '''Retrieve user account information e.g email, portfolio, equity, cash'''
    # log into Robinhood account
    r.authentication.login(email, password)

    # check user entry
    if(db.users.find_one({"email": email})):
        return True

    # new user: insert portfolio
    portfolio = r.account.build_holdings() # {'TSLA': {'x':'y', 'z':'a',...}, 'AAPL'..}
    uid = db.users.insert_one({"portfolio":portfolio}).inserted_id

    # new user: insert equity, cash and email
    profile = r.account.build_user_profile()
    db.users.find_one_and_update({"_id":uid}, { "$set" : {"equity": profile["equity"]} })
    db.users.find_one_and_update({"_id":uid}, {"$set": {"cash": profile["cash"]} })
    db.users.find_one_and_update({"_id":uid}, {"$set": {"email": email} })
    
    return True 

def get_acc_info(email):
    return db.users.find_one({"email": email}, {"_id": 0})

def logout(email):
    db.users.delete_one({"email": email})

def compare_ports(portfolio):
    '''Retrieve priorities for VTI, VXUS, and VCIT purchases by comparing current portfolio'''
    pprint.pprint('Determine index stock to purchase...')
    priority = {}

    for ticker in portfolio:
        tick_perct = float(portfolio[ticker]["percentage"])
        if ticker == "VTI" and tick_perct < 35:
            vti_diff = 35 - tick_perct
            priority.update({"VTI":vti_diff})

        elif ticker == "VXUS" and tick_perct < 35:
            vxus_diff = 35 - tick_perct
            priority.update({"VXUS":vxus_diff})

        elif ticker == "VCIT" and tick_perct < 10:
            vcit_diff = 10 - tick_perct
            priority.update({"VCIT":vcit_diff})
        
    # return symbols by highest priority in desc order
    return sorted(priority, key=priority.get, reverse=True)
    
def purchase_quantity(avail_cash, ask_price, max_amt):
    '''Based on available cash, find max purchase amount with current asking price'''
    quantity, total_cost = 0, 0 
    while avail_cash > total_cost:
        quantity = quantity + 1
        total_cost = quantity * ask_price
        if(quantity == max_amt + 1):
            break
    
    return (quantity - 1)

def single_order(sticker, quantity):
    r.order_buy_market(sticker, quantity)
    return True

def rebalance(email, password, max_amt):
    '''Rebalance portfolio by purchasing VIT, VXUS and/or VCIT'''

    # 1. Get portfolio
    portfolio = db.users.find_one({"email":email})["portfolio"]
    cash = float(db.users.find_one({"email":email})["cash"])
    
    # 2. Get priorities
    priorities = compare_ports(portfolio)

    # 3. Purchase stocks
    purchases = []
    
    # 4. Authenticate Robinhood
    r.authentication.login(email, password)

    for sticker in priorities:
        ask_price = float(r.get_stock_quote_by_symbol(sticker)["ask_price"])
        if  cash > ask_price:
            quantity = purchase_quantity(cash, ask_price, max_amt)
            # retrieve stock information
            stock_instrument = r.get_instruments_by_symbols(sticker)[0]

            # WARNING - UNCOMMENT BELOW TO EXECUTE ORDERS IMMEDIATELY!
            # r.orders.order_buy_market(sticker, quantity)

            bought = {}
            bought['name'] = stock_instrument['name'] 
            bought['quantity'] = quantity
            bought['price'] = ask_price
            bought['total_price'] = quantity * ask_price
            purchases.append(bought)
            
            #update cash after stock purchase(s) 
            cash = round(cash - (ask_price*quantity), 2)
    
    return purchases

   