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
#
# Retrieve a list of stock objects in relation to portfolio
#
def get_port_info(my_acc, instrs_quantity):
    port_stocks, port_equity = [], 0

    for instr, quantity in instrs_quantity.items():
        stock = my_acc.instrument(instr)
        symbol, name = stock['symbol'], stock['simple_name']
        # calculate stock's equity in dollars
        stock_equity = float(quantity) * float(my_acc.quote_data(symbol)['adjusted_previous_close'])
        stock_obj = Stock(symbol, name, int(float(quantity)), round(stock_equity,2))
        
        port_stocks.append(stock_obj)
        port_equity += int(float(quantity))
    
    # calculate stock's percentage
    for stock in port_stocks:
        stock.percentage = round( (stock.quantity / port_equity) , 4)

    return port_stocks 
#
# Retrieve user account information e.g equity, stocks, etc. and upload to json
#
def get_acc_info(email, password):
    # log into Robinhood account
    my_acc = Robinhood()
    try:
        my_acc.login(email,password)
    except:
        return False

    # from assets, retrieve instrument ids
    assets = [ asset for asset in my_acc.positions()['results']]
    instr_ids = [ instr['instrument'].split("/")[-2] for instr in assets ]
    quantity = [ asset['quantity'] for asset in my_acc.positions()['results']]
    
    # key, value => instr_id, quantity
    instrs_quantity = dict(zip(instr_ids, quantity))
    # remove any sold assets, quantity = 0.0000
    instrs_quantity = {k: v for k, v in instrs_quantity.items() if v != '0.0000'}
    
    # generate portfolio information - stocks, equity, credentials
    port_stocks = get_port_info(my_acc, instrs_quantity)
    avail_cash = float(my_acc.portfolios()['withdrawable_amount']) + float(my_acc.portfolios()['unwithdrawable_deposits'])
    print("avail: ", avail_cash)
    # create port dict 
    portfolio = {}
    portfolio['positions'] = []
    portfolio['email'] = email
    portfolio['password'] = password
    portfolio['equity'] = round(float(my_acc.portfolios()['equity']),2)
    portfolio['avail_cash'] = avail_cash
    
    for stock in port_stocks:
        # stock object must be serialized as json has limited type system
        portfolio['positions'].append(json.dumps(stock.__dict__))

    # upload port to acc.json         
    with open("acc.json", "w") as f:
        json.dump(portfolio, f)
    
    return True

#
# Retrieve priorities for VTI, VXUS, and VCIT purchases by comparing current portfolio
#
def compare_ports(positions):
    pprint.pprint('Determine index stock to purchase...')
    priority = {}

    for stock in positions:
        # Convert Str object to Python dict
        stockObj = ast.literal_eval(stock)
        if stockObj['symbol'] == 'VTI' and stockObj['percentage'] < .35:
            vti_diff = .35 - stockObj['percentage']
            priority.update({'VTI':vti_diff})

        elif stockObj['symbol'] == 'VXUS' and stockObj['percentage'] < .35:
            vxus_diff = .35 - stockObj['percentage']
            priority.update({'VXUS':vxus_diff})

        elif stockObj['symbol'] == 'VCIT' and stockObj['percentage'] < .10:
            vcit_diff = .10 - stockObj['percentage']
            priority.update({'VCIT':vcit_diff})
        
    # return symbols by highest priority in desc order
    return sorted(priority, key=priority.get, reverse=True)
    
#
# Based on available cash, find max purchase amount with current asking price
#
def purchase_quantity(avail_cash, ask_price):
    quantity, total_cost = 0, 0 
    while avail_cash > total_cost:
        quantity = quantity + 1
        total_cost = quantity * ask_price
    return (quantity - 1)

#
# Rebalance portfolio by purchasing VIT, VXUS and/or VCIT
#
def rebalance(file='acc.json'):
    # read from json file
    with open(file) as f:
        acc = json.load(f)
   
    avail_cash = acc['avail_cash']
    priorities = compare_ports(acc['positions'])
    my_acc = Robinhood()
    my_acc.login(acc['email'], acc['password'])

    purchases = []
    # purchase as many stock shares per priorities
    for sticker in priorities:
        ask_price = float(my_acc.quote_data(sticker)['ask_price'])
        if  avail_cash > ask_price:
            quantity = purchase_quantity(avail_cash, ask_price)
            # retrieve correct stock information
            stock_instrument = my_acc.instruments(sticker)[0]
            my_acc.place_buy_order(stock_instrument, quantity, ask_price)
            bought = {}
            bought['name'] = stock_instrument['simple_name'] 
            bought['quantity'] = quantity
            bought['price'] = ask_price
            purchases.append(bought)
            #update avail cash after stock purchase(s)
            avail_cash = round(avail_cash - (ask_price*quantity), 2)

    return purchases, acc['email']