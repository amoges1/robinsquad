from Robinhood import Robinhood
import pprint as pprint
import json
import ast

class Stock:
    """Stock holds basic information"""
    def __init__(self, symbol, name, quantity, value) :
        self.symbol = symbol
        self.name = name
        self.quantity = quantity
        self.total_value = value
        self.percentage = 0.0

# Retrieve stock objects of holdings by converting instr to sym, name, etc.
def get_stock_info(my_account, instr_quantity):
    holdings = []
    total_quantity = 0.0
    balance = 0.0
    # print("Now loading", end="", flush=True)
    for key, quantity in instr_quantity.items():
        stock = my_account.instrument(key)
        symbol = stock['symbol']
        # print("...{}".format(symbol))
        name = stock['simple_name']
        total_value = float(quantity) * float(my_account.quote_data(symbol)['adjusted_previous_close'])
        stock_obj = Stock(symbol, name, round(float(quantity)), round(total_value,2))
        holdings.append(stock_obj)

        balance += total_value
        total_quantity += float(quantity)
    
    for stock in holdings:
        stock.percentage = round( (float(stock.quantity) / float(total_quantity)) , 4)

    return holdings, balance

def get_user_info(email, password):
    # log into Robinhood account
    my_account = Robinhood()
    
    try:
        my_account.login(email,password)
    except:
        return False

    # Gather stocks instruments and their symbols, names, quantities, total values
    instruments = [ item['url'][45:-1] for item in my_account.positions()['results']]
    quantity = [ item['quantity'] for item in my_account.positions()['results']]
    
    instr_quantity = dict(zip(instruments, quantity))
    instr_quantity = {k: v for k, v in instr_quantity.items() if v != '0.0000'}
    
    my_holdings, total_balance = get_stock_info(my_account, instr_quantity)
    cash = float(my_account.portfolios()['withdrawable_amount']) + float(my_account.portfolios()['unwithdrawable_deposits'])
    
    portfolio = {}
    portfolio.setdefault('positions', [])
    portfolio['email'] = email
    portfolio['password'] = password
    portfolio['balance'] = round(total_balance, 2)
    portfolio['cash'] = cash
    
    for stock in my_holdings:
        # Serialize Stock Object
        portfolio['positions'].append(json.dumps(stock.__dict__))

    # print(portfolio)
    
    # upload to acc.json         
    with open("acc.json", "w") as f:
        json.dump(portfolio, f)
    
    my_account.logout()

    return True

# Retrieve priorities for VTI, VXUS, and VCIT
def compare_ports(account):
    pprint.pprint("Determine index stock to purchase...")
    priority = dict()

    for stock in account["positions"]:
        # Convert Str object to Python dict
        stockObj = ast.literal_eval(stock)
        if stockObj["symbol"] == "VTI" and stockObj["percentage"] < .35:
            vti_diff = .35 - int(stockObj["percentage"])
            priority.update({'VTI':vti_diff})
            # print("VTI is off by {} ".format(vti_diff))
        elif stockObj["symbol"] == "VXUS" and stockObj["percentage"] < .35:
            vxus_diff = .35 - stockObj["percentage"]
            priority.update({'VXUS':vxus_diff})
            # print("VXUS is off by {} ".format(vxus_diff))
        elif stockObj["symbol"] == "VCIT" and stockObj["percentage"] < .10:
            vcit_diff = .10 - stockObj["percentage"]
            priority.update({'VCIT':vcit_diff})
            # print("VCIT is off by {} ".format(vcit_diff))
        else:
            continue
        
    # print("This is priority: ", priority)
    # just return symbols
    return sorted(priority, key=priority.get, reverse=True)
    

def purchase_quantity(purchase_amt, ask_price):
    quantity = 0
    total = 0
    while purchase_amt > total:
        quantity = quantity + 1
        total = quantity * ask_price
    return (quantity - 1)

def rebalance(file="acc.json"):
    # Read from JSON file
    with open(file) as f:
        account = json.load(f)
   
    # print("Let's see what to purchase...")
    purchase_amt = account['cash']
    priorities = compare_ports(account)
    my_trader = Robinhood()
    my_trader.login(account["email"], account["password"])

    purchases = []
    for stock in priorities:
        ask_price = float(my_trader.quote_data(stock)['ask_price'])
        if ask_price < purchase_amt:
            quantity = purchase_quantity(purchase_amt, ask_price)
            curr_bid = float(my_trader.quote_data(stock)['bid_price'])
            stock_instrument = my_trader.instruments(stock)[0]
            my_trader.place_buy_order(stock_instrument, quantity, curr_bid)
            bought = {}
            bought['name'] = stock_instrument['name'] #showed up as ${stock} adjust here!
            bought['quantity'] = quantity
            bought['price'] = curr_bid
            purchases.append(bought)
    
    my_trader.logout()

    return purchases, account["email"]