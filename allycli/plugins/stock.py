import requests
from plugin import plugin
from colorama import Fore
from inspect import cleandoc
import re


@plugin('stock')
class Stock:
    """
    stock <stock_id>            : Get details of stock identified by <stock_id>(one id at a time)
    stock getid                 : Search stock id
    stock profile <stock_id>    : Get company profile
    stock fstatement <stock_id> : Get latest ANNUAL finincial statement of the company
    stock gainers               : Most gainers in NYSE
    stock losers                : Most losers in NYSE
    stock help                  : Prints help
    *** AVAILABLE ONLY FOR US EQUITIES ***

    Data provided for free by IEX (https://iextrading.com/developer). View IEX’s Terms of Use (https://iextrading.com/api-exhibit-a/).
    """

    def handle_getid(self, ally, parts):
        parts.pop(0)
        name = ' '.join(parts) if parts else ally.input("Enter the name of the stock: ")
        self.get_stock_id(ally, name)

    def handle_profile_or_fstatement(self, ally, parts, command):
        if len(parts) != 2:
            ally.say("You forgot to mention the symbol", Fore.RED)
        else:
            symbol = parts[1]
            if command == 'profile':
                self.get_profile(ally, symbol)
            else:
                self.get_financial_stmt(ally, symbol)

    def __call__(self, ally, s):
        if not s or 'help' in s:
            ally.say(cleandoc(self.__doc__), Fore.GREEN)
            return

        parts = s.split()
        command = parts[0]

        if command == 'getid':
            self.handle_getid(ally, parts)
        elif command in ['profile', 'fstatement']:
            self.handle_profile_or_fstatement(ally, parts, command)
        elif command == 'gainers':
            self.get_gainers(ally)
        elif command == 'losers':
            self.get_losers(ally)
        else:
            self.get_stock_data(ally, s)
    def get_stock_data(self, ally, quote):
        ''' Given a stock symbol, get the real time price of the stock '''
        url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/' + quote
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            if('symbol' in data.keys()):
                ally.say("Symbol: " + str(data['symbol']), Fore.GREEN)
                ally.say("Price: " + str(data['price']), Fore.GREEN)
                ally.say("IEX Real-Time Price (https://iextrading.com/developer)")
            elif('Error' in data.keys()):
                ally.say("Invalid stock symbol name", Fore.RED)
            else:
                ally.say("Error. Please retry")
        else:
            ally.say("Cannot find the name. Try again later\n", Fore.RED)

    def get_stock_id(self, ally, name):
        ''' Get the list of stock IDs given a company name or part of the company name '''
        url = 'https://financialmodelingprep.com/api/v3/company/stock/list'
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            found = False

            # Add try block. Somtimes the endpoint does not work or has unexcepted behaviour
            try:
                for stock in data['symbolsList']:
                    if(re.match(name.lower(), stock['name'].lower())):
                        found = True
                        ally.say(stock['symbol'] + "\t\t" + stock['name'], Fore.GREEN)

                if not found:
                    ally.say("The given name could not be found\n", Fore.RED)
            except KeyError:
                ally.say("The endpoint is not working at the moment. Try again later", Fore.RED)
        else:
            ally.say("Cannot find the name at this time. Try again later\n", Fore.RED)

    def get_profile(self, ally, symbol):
        ''' Given a stock symbol get the company profile '''
        url = 'https://financialmodelingprep.com/api/v3/company/profile/' + symbol
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            if(not data):
                ally.say("Cannot find details for " + symbol, Fore.RED)
            else:
                ally.say(" Symbol      : " + data['symbol'], Fore.GREEN)
                ally.say(" Company     : " + data['profile']['companyName'], Fore.GREEN)
                ally.say(" Industry    : " + data['profile']['industry'], Fore.GREEN)
                ally.say(" Sector      : " + data['profile']['sector'], Fore.GREEN)
                ally.say(" Website     : " + data['profile']['website'], Fore.GREEN)
                ally.say(" Exchange    : " + data['profile']['exchange'], Fore.GREEN)
                ally.say(" Description : " + data['profile']['description'], Fore.GREEN)

        else:
            ally.say("Cannot find details for " + symbol, Fore.RED)

    def get_financial_stmt(self, ally, symbol):
        ''' Get the last annual financial statement of a company given it's stock symbol '''
        url = 'https://financialmodelingprep.com/api/v3/financials/income-statement/' + symbol
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            if(not data):
                ally.say("Cannot find details for: " + symbol, Fore.RED)
            else:
                for key in data['financials'][0].keys():
                    ally.say(key + " => " + data['financials'][0][key], Fore.GREEN)
        else:
            ally.say("Cannot find details for " + symbol, Fore.RED)

    def get_gainers(self, ally):
        ''' Get the most gainers of the day '''
        url = 'https://financialmodelingprep.com/api/v3/stock/gainers'
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            if(not data):
                ally.say("Cannot find details at this moment.", Fore.RED)
            else:
                for gainer in data['mostGainerStock']:
                    ally.say(gainer['ticker'] + " | " + gainer['companyName'], Fore.GREEN)
                    ally.say("Price: " + str(gainer['price']) + " | Change: " + str(gainer['changes']), Fore.GREEN)
                    ally.say("Percent gained: " + str(gainer['changesPercentage'])[1:-1] + "\n\n", Fore.GREEN)
        else:
            ally.say("Cannot get gainers list at the moment")

    def get_losers(self, ally):
        ''' Get the most losers of the day '''
        url = 'https://financialmodelingprep.com/api/v3/stock/losers'
        resp = requests.get(url)

        if(resp.status_code == 200):
            data = resp.json()
            if(not data):
                ally.say("Cannot find details at the moment.", Fore.RED)
            else:
                for loser in data['mostLoserStock']:
                    ally.say(loser['ticker'] + " | " + loser['companyName'], Fore.GREEN)
                    ally.say("Price: " + str(loser['price']) + " | Change: " + str(loser['changes']), Fore.GREEN)
                    ally.say("Percent lost: " + str(loser['changesPercentage'])[1:-1] + "\n\n", Fore.GREEN)
        else:
            ally.say("Cannot get losers list at the moment")
