# Robinsquad

Robinsquad is a Python web application utilizing Flask and React JavaScript, along with an unofficial Robinhood API, to automate stock purchases to rebalance your portfolio.

Getting Started:
    1.	Pip install: pymongo dnspython robin_stocks flask_cors 
    2.	Add MongoDB instance robin_flask.py to hold your account information

1. A Login page is provided to sign into your Robinhood Brokerage account, automatically populating into a MongoDB database with your:

    - Email
    - Portfolio: An array containing all your holdings, each with their respective name, symbol, quantity, total dollar value and percentage of your portfolio
    - Equity: The total value of your portfolio
    - Cash: Uninvested money available for spending

![image](https://user-images.githubusercontent.com/17581500/92060400-aa1f2580-ed61-11ea-90b0-3fee0f482158.png)

2. After logging on, you'll be redirected to the home page, displaying all aforementioned information.

![image](https://user-images.githubusercontent.com/17581500/92060393-a4294480-ed61-11ea-855a-01efd7549d0a.png)

3. *Important* Based on my personal research in finance and investing, I decided the ideal portfolio *for me* is:

    - 35% Vanguard Total Stock Market ETF, VTI
    - 35% Vanguard Total International Stock ETF, VXUS
    - 10% Vanguard Intermediate-Term Corporate Bond ETF, VCIT

Therefore, when opting to automate your purchases by clicking "Invest" on the home page, your current portfolio will be compared to this ideal portfolio. Based on your cash, purchases of VTI, VXUS and/or VCIT will occur *instantly.* For caution, line 105 of robinsquad.py of rebalance function is disabled to prevent accidental purchase -- uncomment at your risk. 

For optimization, sit back, deposit cash biweekly, and let Robinsquad handle everything...

*Disclaimer: I'm an amateur investor. You can become rich...or broke. I take no responsibility because it's the computer's fault* 
