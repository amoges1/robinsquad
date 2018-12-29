# Robinsquad

Robinsquad is a Python web application utilizing Flask and React JavaScript, along with an unofficial Robinhood API, to automate stock purchases to rebalance your portfolio.

1. A Login page is provided to sign into your Robinhood Brokerage account, automatically populating acc.json file with your:

    - Email and Password
    - Positions: An array containing all your holdings, each with their respective name, symbol, quantity, total dollar value and percentage of your portfolio
    - Balance: The total value of your portfolio, including uninvested money
    - Cash: Uninvested money available for spending

2. After logging on, you'll be redirected to the home page, displaying all aforementioned information.

3. *Important* Based on my personal research in finance and investing, I decided the ideal portfolio *for me* is:

    - 35% Vanguard Total Stock Market ETF, VTI
    - 35% Vanguard Total International Stock ETF, VXUS
    - 10% Vanguard Intermediate-Term Corporate Bond ETF, VCIT

Therefore, when opting to automate your purchases by clicking "Invest" on the home page, your current portfolio will be compared to this ideal portfolio. Based on your cash, purchases of VTI, VXUS and/or VCIT will occur *instantly.*

For optimization, sit back, deposit cash biweekly, and let Robinsquad handle everything...

*Disclaimer: I'm an amateur investor. You can get rich...or broke. I take no responsibility because it's the computer's fault" 