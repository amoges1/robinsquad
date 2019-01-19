"""Robinhood.py: a collection of utilities for working with Robinhood's Private API """

#Standard libraries
import logging
import warnings

from enum import Enum

#External dependencies
from six.moves.urllib.parse import unquote  # pylint: disable=E0401
from six.moves.urllib.request import getproxies  # pylint: disable=E0401
from six.moves import input

import getpass
import requests
import six
import dateutil

#Application-specific imports
from . import exceptions as RH_exception

class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint """

    REGULAR = 'regular'
    EXTENDED = 'extended'


class Transaction(Enum):
    """Enum for buy/sell orders """

    BUY = 'buy'
    SELL = 'sell'


class Robinhood:
    """Wrapper class for fetching/parsing Robinhood endpoints """

    endpoints = {
        #"login": "https://api.robinhood.com/api-token-auth/",
        "login": "https://api.robinhood.com/oauth2/token/",
        "logout": "https://api.robinhood.com/api-token-logout/",
        "investment_profile": "https://api.robinhood.com/user/investment_profile/",
        "accounts": "https://api.robinhood.com/accounts/",
        "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
        "ach_relationships": "https://api.robinhood.com/ach/relationships/",
        "ach_transfers": "https://api.robinhood.com/ach/transfers/",
        "applications": "https://api.robinhood.com/applications/",
        "dividends": "https://api.robinhood.com/dividends/",
        "edocuments": "https://api.robinhood.com/documents/",
        "instruments": "https://api.robinhood.com/instruments/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/",
        "fundamentals": "https://api.robinhood.com/fundamentals/",
        "tags": "https://api.robinhood.com/midlands/tags/tag/"
    }

    session = None
    username = None
    password = None
    headers = None
    auth_token = None

    logger = logging.getLogger('Robinhood')
    logger.addHandler(logging.NullHandler())


    ###########################################################################
    #                       Logging in and initializing
    ###########################################################################

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }

        self.session.headers = self.headers


    def login_prompt(self): #pragma: no cover
        """Prompts user for username and password and calls login() """

        username = input("Username: ")
        password = getpass.getpass()

        return self.login(username=username, password=password)


    def login(self,
              username,
              password,
              mfa_code=None):
        """Save and test login info for Robinhood accounts

        Args:
            username (str): username
            password (str): password

        Returns:
            (bool): received valid auth token

        """

        self.username = username
        self.password = password
        payload = {
            'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
            'expires_in': 600,
            'grant_type': 'password',
            'password': self.password,
            'scope': 'internal',
            'username': self.username
        }

        if mfa_code:
            payload['mfa_code'] = mfa_code

        try:
            res = self.session.post(self.endpoints['login'], data=payload, timeout=15)
            res.raise_for_status()
            data = res.json()
            print(data)
        except requests.exceptions.HTTPError:
            raise RH_exception.LoginFailed()

        if 'mfa_required' in data.keys():           # pragma: no cover
            raise RH_exception.TwoFactorRequired()  # requires a second call to enable 2FA

        if 'access_token' in data.keys():
            self.oauth_token = data['access_token']
            self.headers['Authorization'] = 'Bearer ' + self.oauth_token
            return True

        return False


    def logout(self):
        """Logout from Robinhood

        Returns:
            (:obj:`requests.request`) result from logout endpoint

        """

        try:
            req = self.session.post(self.endpoints['logout'], timeout=15)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None

        return req


    ###########################################################################
    #                               GET DATA
    ###########################################################################

    def investment_profile(self):
        """Fetch investment_profile """

        res = self.session.get(self.endpoints['investment_profile'], timeout=15)
        res.raise_for_status()  #will throw without auth
        data = res.json()

        return data


    def instruments(self, stock):
        """Fetch instruments endpoint

            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`): JSON contents from `instruments` endpoint
        """

        res = self.session.get(self.endpoints['instruments'], params={'query': stock.upper()}, timeout=15)
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        if (stock == ""):
            return res

        return res['results']


    def instrument(self, id):
        """Fetch instrument info

            Args:
                id (str): instrument id

            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(self.endpoints['instruments']) + str(id) + "/"

        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidInstrumentId()

        return data


    def quote_data(self, stock=''):
        """Fetch stock quote

            Args:
                stock (str): stock ticker, prompt if blank

            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """

        url = None

        if stock.find(',') == -1:
            url = str(self.endpoints['quotes']) + str(stock) + "/"
        else:
            url = str(self.endpoints['quotes']) + "?symbols=" + str(stock)

        #Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data

    # We will keep for compatibility until next major release
    def quotes_data(self, stocks):
        """Fetch quote for multiple stocks, in one single Robinhood API call

            Args:
                stocks (list<str>): stock tickers

            Returns:
                (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
                    same order of input args. If any ticker is invalid, a None will occur at that position.
        """

        url = str(self.endpoints['quotes']) + "?symbols=" + ",".join(stocks)

        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data["results"]


    def get_quote_list(self,
                       stock='',
                       key=''):
        """Returns multiple stock info and keys from quote_data (prompt if blank)

            Args:
                stock (str): stock ticker (or tickers separated by a comma)
                , prompt if blank
                key (str): key attributes that the function should return

            Returns:
                (:obj:`list`): Returns values from each stock or empty list
                               if none of the stocks were valid

        """

        #Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            keys = key.split(',')
            myStr = ''
            for item in keys:
                myStr += stock[item] + ","

            return (myStr.split(','))


        #Prompt for stock if not entered
        if not stock:   #pragma: no cover
            stock = input("Symbol: ")

        data = self.quote_data(stock)
        res = []

        # Handles the case of multple tickers
        if stock.find(',') != -1:
            for stock in data['results']:
                if stock is None:
                    continue
                res.append(append_stock(stock))

        else:
            res.append(append_stock(data))

        return res


    def get_quote(self, stock=''):
        """Wrapper for quote_data """

        data = self.quote_data(stock)
        return data["symbol"]

    def get_historical_quotes(self, stock, interval, span, bounds=Bounds.REGULAR):
        """Fetch historical data for stock

            Note: valid interval/span configs
                interval = 5minute | 10minute + span = day, week
                interval = day + span = year
                interval = week
                TODO: NEEDS TESTS

            Args:
                stock (str): stock ticker
                interval (str): resolution of data
                span (str): length of data
                bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint
        """
        if type(stock) is str:
            stock = [stock]

        if isinstance(bounds, str):  # recast to Enum
            bounds = Bounds(bounds)

        params = {
            'symbols': ','.join(stock).upper(),
            'interval': interval,
            'span': span,
            'bounds': bounds.name.lower()
        }

        res = self.session.get(self.endpoints['historicals'], params=params, timeout=15)
        return res.json()


    def get_news(self, stock):
        """Fetch news endpoint
            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`) values returned from `news` endpoint
        """

        return self.session.get(self.endpoints['news'] + stock.upper() + "/", timeout=15).json()


    def print_quote(self, stock=''):    #pragma: no cover
        """Print quote information
            Args:
                stock (str): ticker to fetch

            Returns:
                None
        """

        data = self.get_quote_list(stock, 'symbol,last_trade_price')
        for item in data:
            quote_str = item[0] + ": $" + item[1]
            print(quote_str)
            self.logger.info(quote_str)


    def print_quotes(self, stocks): #pragma: no cover
        """Print a collection of stocks

            Args:
                stocks (:obj:`list`): list of stocks to pirnt

            Returns:
                None
        """

        if stocks is None:
            return

        for stock in stocks:
            self.print_quote(stock)


    def ask_price(self, stock=''):
        """Get asking price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): ask price
        """

        return self.get_quote_list(stock, 'ask_price')


    def ask_size(self, stock=''):
        """Get ask size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): ask size
        """

        return self.get_quote_list(stock, 'ask_size')


    def bid_price(self, stock=''):
        """Get bid price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): bid price
        """

        return self.get_quote_list(stock, 'bid_price')


    def bid_size(self, stock=''):
        """Get bid size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): bid size
        """

        return self.get_quote_list(stock, 'bid_size')


    def last_trade_price(self, stock=''):
        """Get last trade price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): last trade price
        """

        return self.get_quote_list(stock, 'last_trade_price')


    def previous_close(self, stock=''):
        """Get previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): previous closing price
        """

        return self.get_quote_list(stock, 'previous_close')


    def previous_close_date(self, stock=''):
        """Get previous closing date for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): previous close date
        """

        return self.get_quote_list(stock, 'previous_close_date')


    def adjusted_previous_close(self, stock=''):
        """Get adjusted previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): adjusted previous closing price
        """

        return self.get_quote_list(stock, 'adjusted_previous_close')


    def symbol(self, stock=''):
        """Get symbol for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): stock symbol
        """

        return self.get_quote_list(stock, 'symbol')


    def last_updated_at(self, stock=''):
        """Get last update datetime

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): last update datetime
        """

        return self.get_quote_list(stock, 'last_updated_at')


    def last_updated_at_datetime(self, stock=''):
        """Get last updated datetime

            Note:
                queries `quote` endpoint, dict wrapper
                `self.last_updated_at` returns time as `str` in format: 'YYYY-MM-ddTHH:mm:ss:000Z'

            Args:
                stock (str): stock ticker

            Returns:
                (datetime): last update datetime

        """

        #Will be in format: 'YYYY-MM-ddTHH:mm:ss:000Z'
        datetime_string = self.last_updated_at(stock)
        result = dateutil.parser.parse(datetime_string)

        return result


    def get_account(self):
        """Fetch account information

            Returns:
                (:obj:`dict`): `accounts` endpoint payload
        """

        res = self.session.get(self.endpoints['accounts'], timeout=15)
        res.raise_for_status()  #auth required
        res = res.json()

        return res['results'][0]


    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """

        return self.session.get(url, timeout=15).json()

    def get_popularity(self, stock=''):
        """Get the number of robinhood users who own the given stock

            Args:
                stock (str): stock ticker

            Returns:
                (int): number of users who own the stock
        """
        stock_instrument = self.get_url(self.quote_data(stock)["instrument"])["id"]
        return self.get_url("{base}{instrument}/popularity/".format(base=self.endpoints['instruments'], instrument=stock_instrument))["num_open_positions"]

    def get_tickers_by_tag(self, tag=None):
        """Get a list of instruments belonging to a tag

            Args: tag - a string that equals one of the following:
                * top-movers
                * etf
                * 100-most-popular
                * mutual-fund
                * finance
                * cap-weighted
                * investment-trust-or-fund

            Returns:
                (List): a list of Ticker strings
        """
        instrument_list = self.get_url("{base}{_tag}/".format(base=self.endpoints['tags'], _tag=tag))["instruments"]
        return [self.get_url(instrument)["symbol"] for instrument in instrument_list]


    ###########################################################################
    #                           GET FUNDAMENTALS
    ###########################################################################

    def get_fundamentals(self, stock=''):
        """Find stock fundamentals data

            Args:
                (str): stock ticker

            Returns:
                (:obj:`dict`): contents of `fundamentals` endpoint
        """

        #Prompt for stock if not entered
        if not stock:   #pragma: no cover
            stock = input("Symbol: ")

        url = str(self.endpoints['fundamentals']) + str(stock.upper()) + "/"

        #Check for validity of symbol
        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data


    def fundamentals(self, stock=''):
        """Wrapper for get_fundamentlals function """

        return self.get_fundamentals(stock)


    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolios(self):
        """Returns the user's portfolio data """

        req = self.session.get(self.endpoints['portfolios'], timeout=15)
        req.raise_for_status()

        return req.json()['results'][0]


    def adjusted_equity_previous_close(self):
        """Wrapper for portfolios

            Returns:
                (float): `adjusted_equity_previous_close` value

        """

        return float(self.portfolios()['adjusted_equity_previous_close'])


    def equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `equity` value
        """

        return float(self.portfolios()['equity'])


    def equity_previous_close(self):
        """Wrapper for portfolios

            Returns:
                (float): `equity_previous_close` value
        """

        return float(self.portfolios()['equity_previous_close'])


    def excess_margin(self):
        """Wrapper for portfolios

            Returns:
                (float): `excess_margin` value
        """

        return float(self.portfolios()['excess_margin'])


    def extended_hours_equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `extended_hours_equity` value
        """

        try:
            return float(self.portfolios()['extended_hours_equity'])
        except TypeError:
            return None


    def extended_hours_market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `extended_hours_market_value` value
        """

        try:
            return float(self.portfolios()['extended_hours_market_value'])
        except TypeError:
            return None


    def last_core_equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `last_core_equity` value
        """

        return float(self.portfolios()['last_core_equity'])


    def last_core_market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `last_core_market_value` value
        """

        return float(self.portfolios()['last_core_market_value'])


    def market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `market_value` value
        """

        return float(self.portfolios()['market_value'])


    def order_history(self):
        """Wrapper for portfolios

            Returns:
                (:obj:`dict`): JSON dict from getting orders
        """

        return self.session.get(self.endpoints['orders'], timeout=15).json()


    def dividends(self):
        """Wrapper for portfolios

            Returns:
                (:obj: `dict`): JSON dict from getting dividends
        """

        return self.session.get(self.endpoints['dividends'], timeout=15).json()


    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data

            Returns:
                (:object: `dict`): JSON dict from getting positions
        """

        return self.session.get(self.endpoints['positions'], timeout=15).json()


    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in

            Returns:
                (:object: `dict`): Non-zero positions
        """

        return self.session.get(self.endpoints['positions']+'?nonzero=true', timeout=15).json()


    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################

    def place_order(self,
                    instrument,
                    quantity=1,
                    bid_price=0.0,
                    transaction=None,
                    trigger='immediate',
                    order='market',
                    time_in_force = 'gfd'):
        """Place an order with Robinhood

            Notes:
                OMFG TEST THIS PLEASE!

                Just realized this won't work since if type is LIMIT you need to use "price" and if
                a STOP you need to use "stop_price".  Oops.
                Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order
                transaction (:enum:`Transaction`): BUY or SELL enum
                trigger (:enum:`Trigger`): IMMEDIATE or STOP enum
                order (:enum:`Order`): MARKET or LIMIT
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or until cancelled)

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        if isinstance(transaction, str):
            transaction = Transaction(transaction)

        if not bid_price:
            bid_price = self.quote_data(instrument['symbol'])['bid_price']

        payload = {
            'account': self.get_account()['url'],
            'instrument': unquote(instrument['url']),
            'price': float(bid_price),
            'quantity': quantity,
            'side': transaction.name.lower(),
            'symbol': instrument['symbol'],
            'time_in_force': time_in_force.lower(),
            'trigger': trigger,
            'type': order.lower()
        }

        #data = 'account=%s&instrument=%s&price=%f&quantity=%d&side=%s&symbol=%s#&time_in_force=gfd&trigger=immediate&type=market' % (
        #    self.get_account()['url'],
        #    urllib.parse.unquote(instrument['url']),
        #    float(bid_price),
        #    quantity,
        #    transaction,
        #    instrument['symbol']
        #)

        res = self.session.post(self.endpoints['orders'], data=payload, timeout=15)
        res.raise_for_status()

        return res


    def place_buy_order(self,
                        instrument,
                        quantity,
                        bid_price=0.0):
        """Wrapper for placing buy orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order

            Returns:
                (:obj:`requests.request`): result from `orders` put command

        """

        transaction = Transaction.BUY

        return self.place_order(instrument, quantity, bid_price, transaction)


    def place_sell_order(self,
                         instrument,
                         quantity,
                         bid_price=0.0):
        """Wrapper for placing sell orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        transaction = Transaction.SELL

        return self.place_order(instrument, quantity, bid_price, transaction)

    # Methods below here are a complete rewrite for buying and selling
    # These are new. Use at your own risk!

    def place_market_buy_order(self,
                               instrument_URL = None,
                               symbol = None,
                               time_in_force = None,
                               quantity = None):
        """Wrapper for placing market buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'immediate',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 quantity = quantity))

    def place_limit_buy_order(self,
                              instrument_URL = None,
                              symbol = None,
                              time_in_force = None,
                              price = None,
                              quantity = None):
        """Wrapper for placing limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'immediate',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 price = price,
                                 quantity = quantity))

    def place_stop_loss_buy_order(self,
                                  instrument_URL = None,
                                  symbol = None,
                                  time_in_force = None,
                                  stop_price = None,
                                  quantity = None):
        """Wrapper for placing stop loss buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'stop',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 quantity = quantity))

    def place_stop_limit_buy_order(self,
                                   instrument_URL = None,
                                   symbol = None,
                                   time_in_force = None,
                                   stop_price = None,
                                   price = None,
                                   quantity = None):
        """Wrapper for placing stop limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'stop',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 price = price,
                                 quantity = quantity))

    def place_market_sell_order(self,
                                instrument_URL = None,
                                symbol = None,
                                time_in_force = None,
                                quantity = None):
        """Wrapper for placing market sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'immediate',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 quantity= quantity))

    def place_limit_sell_order(self,
                               instrument_URL = None,
                               symbol = None,
                               time_in_force = None,
                               price = None,
                               quantity = None):
        """Wrapper for placing limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The minimum price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'immediate',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 price = price,
                                 quantity = quantity))

    def place_stop_loss_sell_order(self,
                                   instrument_URL = None,
                                   symbol = None,
                                   time_in_force = None,
                                   stop_price = None,
                                   quantity = None):
        """Wrapper for placing stop loss sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'stop',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 quantity = quantity))

    def place_stop_limit_sell_order(self,
                                    instrument_URL = None,
                                    symbol = None,
                                    time_in_force = None,
                                    price = None,
                                    stop_price = None,
                                    quantity = None):
        """Wrapper for placing stop limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'stop',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 price = price,
                                 quantity = quantity))

    def submit_order(self,
                     instrument_URL = None,
                     symbol = None,
                     order_type = None,
                     time_in_force = None,
                     trigger = None,
                     price = None,
                     stop_price = None,
                     quantity = None,
                     side = None):
        """Submits order to Robinhood

            Notes:
                This is normally not called directly.  Most programs should use
                one of the following instead:

                    place_market_buy_order()
                    place_limit_buy_order()
                    place_stop_loss_buy_order()
                    place_stop_limit_buy_order()
                    place_market_sell_order()
                    place_limit_sell_order()
                    place_stop_loss_sell_order()
                    place_stop_limit_sell_order()

            Args:
                instrument_URL (str): the RH URL for the instrument
                symbol (str): the ticker symbol for the instrument
                order_type (str): 'MARKET' or 'LIMIT'
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or
                                                       until cancelled)
                trigger (str): IMMEDIATE or STOP enum
                price (float): The share price you'll accept
                stop_price (float): The price at which the order becomes a
                                    market or limit order
                quantity (int): The number of shares to buy/sell
                side (str): BUY or sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(ValueError('Neither instrument_URL nor symbol were passed to submit_order'))
            instrument_URL = self.instruments(symbol)[0]['url']

        if(symbol is None):
            symbol = self.session.get(instrument_URL, timeout=15).json()['symbol']

        if(side is None):
            raise(ValueError('Order is neither buy nor sell in call to submit_order'))

        if(order_type == None):
            if(price == None):
                if(stop_price == None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(ValueError('Invalid order_type in call to submit_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(ValueError('Limit order has no price in call to submit_order'))
            if(price <= 0):
                raise(ValueError('Price must be positive number in call to submit_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(ValueError('Stop order has no stop_price in call to submit_order'))
            if(price <= 0):
                raise(ValueError('Stop_price must be positive number in call to submit_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(ValueError('Stop price set for non-stop order in call to submit_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(ValueError('Limit order has no price in call to submit_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(ValueError('Market order has price limit in call to submit_order'))

        price = float(price)

        if(quantity is None):
            raise(ValueError('No quantity specified in call to submit_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(ValueError('Quantity must be positive number in call to submit_order'))

        payload = {}

        for field,value in [('account',self.get_account()['url']),
                            ('instrument',instrument_URL),
                            ('symbol',symbol),
                            ('type',order_type),
                            ('time_in_force', time_in_force),
                            ('trigger',trigger),
                            ('price',price),
                            ('stop_price',stop_price),
                            ('quantity',quantity),
                            ('side',side)]:
            if(value is not None):
                payload[field] = value

        res = self.session.post(self.endpoints['orders'], data=payload, timeout=15)
        res.raise_for_status()

        return res
