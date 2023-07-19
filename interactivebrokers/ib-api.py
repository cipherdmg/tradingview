import datetime
from multiprocessing.resource_sharer import stop
from typing import Awaitable, Dict, Iterator, List, Optional, Union
import sys, copy
from ib_insync import *
import pandas as pd

ib = IB()

# use this instead for IB Gateway
#ih.connect('127.0.0.1',7497,clientId=1)
#ib.connect('127.0.0.1',7497,clientId=1)

#use this for TWS
ib.connect('127.0.0.1', 7497, clientId=1)

#https://ib-insync.readthedocs.io/recipes.html
#https://interactivebrokers.github.io/tws-api/historical_limitations.html
#https://github.com/PythonForForex/ib_insync-guide-interactive-brokers/blob/main/lean_hogs_strategy.py
#https://github.com/arabacibahadir/sup-res/blob/master/main_supres/main.py
#https://gitmemories.com/twopirllc/pandas-ta/issues/551

def bracket_order(direction, qty, price,sl=None, tp=None):
    bracket_order = ib.bracketOrder(
        direction,
        qty,
        limitPrice=price,
        takeProfitPrice=tp,
        stopLossPrice=sl,
    )

    return bracket_order

def limitOrder(contract, direction, qty, stockPrice, stopPrice, transmit):

    order = LimitOrder(action=direction,totalQuantity=qty, lmtPrice=stockPrice, transmit=transmit, orderId=ib.client.getReqId())
    #stopOrder = StopOrder(action="SELL", totalQuantity=qty,stopPrice=sl,orderId=self.client.getReqId(), transmit=True, parentId=order.orderId, **kwargs)
    stopOrder = StopOrder(action="SELL", totalQuantity=qty,stopPrice=stopPrice, transmit=transmit, parentId=order.orderId, orderId=ib.client.getReqId())

    tradeOrder = ib.placeOrder(contract,order)
    tradeStopOrder = ib.placeOrder(contract,stopOrder)

    tradeOrder.filledEvent += orderFilled
    tradeStopOrder.filledEvent += orderFilled

def optionsMarketOrderCall(stockContract, contract, direction, qty, priceCondition, stopPriceCondition, profitPriceCondition, transmit):

    order = MarketOrder(action=direction,totalQuantity=qty, transmit=transmit, orderId=ib.client.getReqId())
    if(priceCondition > 0):
        print("Setting priceCondition " + str(priceCondition))
        price_condition = PriceCondition(
            isMore=True,
            price=priceCondition,
            conId=stockContract.conId,
            exch=stockContract.exchange
        )
        order.conditions.append(price_condition)

    resultOrder = ib.placeOrder(contract,order)

    if(profitPriceCondition > 0):
        print("Setting profitPriceCondition " + str(profitPriceCondition))
        profitOrder = MarketOrder(action="SELL",totalQuantity=qty, transmit=transmit, parentId=order.orderId, orderId=ib.client.getReqId())
        profit_price_condition = PriceCondition(
            isMore=True,
            price=profitPriceCondition,
            conId=stockContract.conId,
            exch=stockContract.exchange
        )
        profitOrder.conditions.append(profit_price_condition)
        resultProfitOrder = ib.placeOrder(contract,profitOrder)

    stopOrder = MarketOrder(action="SELL",totalQuantity=qty, transmit=transmit, parentId=order.orderId, orderId=ib.client.getReqId())
    stop_price_condition = PriceCondition(
        isMore=False,
        price=stopPriceCondition,
        conId=stockContract.conId,
        exch=stockContract.exchange
    )

    stopOrder.conditions.append(stop_price_condition)
    resultStopOrder = ib.placeOrder(contract,stopOrder)

    #print(repr(resultOrder))


def optionsMarketOrderPut(stockContract, contract, direction, qty, priceCondition, stopPriceCondition, profitPriceCondition, transmit):

    order = MarketOrder(action=direction,totalQuantity=qty, transmit=transmit, orderId=ib.client.getReqId())
    if(priceCondition > 0):
        print("Setting priceCondition " + str(priceCondition))
        price_condition = PriceCondition(
            isMore=False,
            price=priceCondition,
            conId=stockContract.conId,
            exch=stockContract.exchange
        )
        order.conditions.append(price_condition)

    resultOrder = ib.placeOrder(contract,order)

    if(profitPriceCondition > 0):
        print("Setting profitPriceCondition " + str(profitPriceCondition))
        profit_price_condition = PriceCondition(
            isMore=False,
            price=profitPriceCondition,
            conId=stockContract.conId,
            exch=stockContract.exchange
        )

        profitOrder = MarketOrder(action="SELL",totalQuantity=qty, transmit=transmit, parentId=order.orderId, orderId=ib.client.getReqId())
        profitOrder.conditions.append(profit_price_condition)
        resultProfitOrder = ib.placeOrder(contract,profitOrder)

    stopOrder = MarketOrder(action="SELL",totalQuantity=qty, transmit=transmit, parentId=order.orderId, orderId=ib.client.getReqId())
    stop_price_condition = PriceCondition(
        isMore=True,
        price=stopPriceCondition,
        conId=stockContract.conId,
        exch=stockContract.exchange
    )
    stopOrder.conditions.append(stop_price_condition)
    resultStopOrder = ib.placeOrder(contract,stopOrder)

    #print(repr(resultOrder))


#https://interactivebrokers.github.io/tws-api/historical_bars.html
#'1 secs', '5 secs', '10 secs' 15 secs', '30 secs', '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours', '3 hours', '4 hours', '8 hours', '1 day', '1 week', '1 month'.
def getHistoricalData(contract, timeframe, duration, preMarket=False):

    chartOptions=TagValue = []
    historical_data = ib.reqHistoricalData(
        contract=contract,
        endDateTime='',
        barSizeSetting=timeframe,
        durationStr=duration,
        whatToShow='MIDPOINT',
        useRTH=preMarket,
        chartOptions=chartOptions,
        timeout=60
    )

    #type(historical_data)
    df=util.df(historical_data)
    print(df)

    #df['backward_ewm'] = df['Close'].ewm(span=20,min_periods=0,adjust=False,ignore_na=False).mean()
    #df = df.sort_index()
    #df['ewm'] = df['close'].ewm(span=9,min_periods=0,adjust=False,ignore_na=False).mean()
    df['ewm9'] = df['close'].ewm(span=9,adjust=False).mean()
    # print(df[['ewm']].tail())
    print(df)


#https://interactivebrokers.github.io/tws-api/realtime_bars.html
def getRealtimeBar(contract):

    marketData = ib.reqMktData(contract=contract, genericTickList='', snapshot=True, regulatorySnapshot=False)

    #type(historical_data)
    ib.sleep(3)
    ib.cancelMktData(contract=contract)

    ask=marketData.ask
    bid=marketData.bid
    close=marketData.close
    last=marketData.last
    time=marketData.time.astimezone()

    #Note the Close is the previous days close
    print('time: ' + str(time) +  ' symbol: ' + str(contract.symbol) + ' ask: ' + str(ask) + ' bid: ' + str(bid) + ' close: ' + str(close) + ' last: ' + str(last) )
    #bars.updateEvent += onBarUpdate

#https://interactivebrokers.github.io/tws-api/realtime_bars.html
def getRealtimeBars(contract, barSize=5,  preMarket=False):

    bars = ib.reqRealTimeBars(contract=contract, barSize=barSize, whatToShow='MIDPOINT', useRTH=preMarket)

    #type(historical_data)
    ib.sleep(3)
    ib.cancelRealTimeBars(bars)

    df=util.df(bars)

    #Convert To EST
    list_timezones= []
    for row in df['time']:
        list_timezones.append(row.tz_convert('US/Eastern'))
        #list_timezones.append(pd.Timestamp(row, tz='UTC').tz_convert('US/Eastern'))
    df['time'] = list_timezones

    print(df)
    #bars.updateEvent += onBarUpdate

def onBarUpdate(bars, hasNewBar):
    print(bars[-1])

def orderFilled(trade,fill):
    print("order has been filled")
    print(order)
    print(fill)


def buyStock(symbol, quantity, stockPrice, stopPrice, transmit):
    contract = Stock(symbol=symbol, exchange='SMART', currency='USD')
    ib.qualifyContracts(contract)

    # bars=ib.reqHistoricalData(contract,endDateTime='',durationStr="30 D", barSizeSetting='1 hour',whatToShow='MIDPOINT', useRTH=True)
    # df = util.df(bars)
    # print(df)

    limitOrder(contract=contract, direction='BUY', qty=quantity, stockPrice=stockPrice, stopPrice=stopPrice, transmit=transmit)
    return contract


def buyCallOptions(symbol,contractDate, strike, quantity, priceCondition, stopPriceCondition, profitPriceCondition, transmit):
    contract = Option(symbol=symbol, lastTradeDateOrContractMonth=contractDate ,strike=strike, right='C', exchange='SMART')
    stockContract = Stock(symbol=symbol, exchange='SMART', currency='USD')
    ib.qualifyContracts(contract)
    ib.qualifyContracts(stockContract)
    optionsMarketOrderCall(stockContract=stockContract, contract=contract, direction='BUY', qty=quantity, priceCondition=priceCondition, stopPriceCondition=stopPriceCondition, profitPriceCondition=profitPriceCondition, transmit=transmit)
    return contract

def buyPutOptions(symbol,contractDate, strike, quantity, priceCondition, stopPriceCondition, profitPriceCondition, transmit):
    contract = Option(symbol=symbol, lastTradeDateOrContractMonth=contractDate, strike=strike, right='P', exchange='SMART')
    stockContract = Stock(symbol=symbol, exchange='SMART', currency='USD')
    ib.qualifyContracts(contract)
    ib.qualifyContracts(stockContract)
    optionsMarketOrderPut(stockContract=stockContract, contract=contract, direction='BUY', qty=quantity, priceCondition=priceCondition, stopPriceCondition=stopPriceCondition, profitPriceCondition=profitPriceCondition, transmit=transmit)
    return contract

def printTrades():
    for trade in ib.trades():
        print("==this is one of my trades")
        print(trade)

#------------------------------------------------------------------------------
# Function takes an array and extracts CLI parameters and returns them in a dict object holding the values
#   Support arguments are -<key> | -<key> value
#------------------------------------------------------------------------------
def getArgs(argv):
    argProp = {}

    while len(argv) > 0:
        key = argv.pop(0) #.upper()
        #Check if they input a value EX: -node Node1 would have key as -NODE and value as Node1
        if len(argv) > 0 and argv[0][0] != '-':
            value = argv.pop(0)
        else:
            value = ''

        argProp[key.split('-')[1]]=value

    return argProp
# end of getArgs()


#buyStock(symbol='SPY', quantity=1, stockPrice=427.20, stopPrice=423, transmit=False)
#buyCallOptions(symbol='SPY', contractDate='20220817', strike=403, quantity=1, priceCondition=404, stopPriceCondition=403, transmit=True)
#buyPutOptions(symbol='SPY', contractDate='20220817', strike=403, quantity=1, priceCondition=403, stopPriceCondition=402, transmit=True)

#buyCallOptions(symbol='SPY', contractDate='20220817', strike=403, quantity=1, priceCondition=404, stopPriceCondition=403, transmit=False)
#buyPutOptions(symbol='SPY', contractDate='20220817', strike=403, quantity=1, priceCondition=403, stopPriceCondition=402, transmit=False)

#ib.sleep(3)

#printTrades()



#ib.run()

#------------------------------------------------------------------------------
# Debug notice
#------------------------------------------------------------------------------
def debug(msg):
    print("   DEBUG: " + msg)

# end of debug()

#-----------------------------------------------------------------
# Main
#-----------------------------------------------------------------
def main(args):

    #Check the arguments and if none are passed then just display info and return.  This could be used in a module or as an import
    if not args or len(args) == 0:
        #info("No Arguments were passed")
        return 1

    #Parse Arguments
    cloneArgs=copy.copy(args)
    argProps = getArgs(cloneArgs)
    debug("argProps: " + str(argProps))


    #buyCallOptions
    if((argProps.get('type') == 'CALL') and (argProps.get('symbol') != None) and (argProps.get('contractDate') != None) and (argProps.get('strike') != None) and (argProps.get('quantity') != None)
     and (argProps.get('priceCondition') != None) and (argProps.get('stopPriceCondition') != None) and (argProps.get('profitPriceCondition') != None) and (argProps.get('transmit') != None)):

        symbol=argProps.get('symbol')
        contractDate=argProps.get('contractDate')
        strike=float(argProps.get('strike'))
        quantity=float(argProps.get('quantity'))
        priceCondition=float(argProps.get('priceCondition'))
        stopPriceCondition=float(argProps.get('stopPriceCondition'))
        profitPriceCondition=float(argProps.get('profitPriceCondition'))
        transmit=True if argProps.get('transmit') == 'True' else False
        print('symbol: ' + str(symbol) + ' contractDate: ' + str(contractDate) + ' strike: ' + str(strike) + ' quantity: ' + str(quantity) + ' priceCondition: ' + str(priceCondition) + ' stopPriceCondition: ' + str(stopPriceCondition) + ' profitPriceCondition: ' + str(profitPriceCondition) + ' transmit: ' + str(transmit))

        #For Call Options the Stop should be less then the price and the take profit should be greater then the price
        if((stopPriceCondition >= priceCondition) and (priceCondition > 0)):
            print('Error: stopPriceCondition: ' + str(stopPriceCondition) + ' can not be larger then the priceCondition: ' + str(priceCondition))
            sys.exit()

        elif((profitPriceCondition <= priceCondition) and (priceCondition > 0)):
            print('Call Contract Error: profitPriceCondition: ' + str(profitPriceCondition) + ' can not be less then the priceCondition: ' + str(priceCondition))
            sys.exit()

        buyCallOptions(symbol=symbol, contractDate=contractDate, strike=strike, quantity=quantity, priceCondition=priceCondition, stopPriceCondition=stopPriceCondition, profitPriceCondition=profitPriceCondition, transmit=transmit)

    #buyPutOptions
    elif((argProps.get('type') == 'PUT') and (argProps.get('symbol') != None) and (argProps.get('contractDate') != None) and (argProps.get('strike') != None) and (argProps.get('quantity') != None)
     and (argProps.get('priceCondition') != None) and (argProps.get('stopPriceCondition') != None) and (argProps.get('profitPriceCondition') != None) and (argProps.get('transmit') != None)):

        symbol=argProps.get('symbol')
        contractDate=argProps.get('contractDate')
        strike=float(argProps.get('strike'))
        quantity=float(argProps.get('quantity'))
        priceCondition=float(argProps.get('priceCondition'))
        stopPriceCondition=float(argProps.get('stopPriceCondition'))
        profitPriceCondition=float(argProps.get('profitPriceCondition'))
        transmit=True if argProps.get('transmit') == 'True' else False
        print('symbol: ' + str(symbol) + ' contractDate: ' + str(contractDate) + ' strike: ' + str(strike) + ' quantity: ' + str(quantity) + ' priceCondition: ' + str(priceCondition) + ' stopPriceCondition: ' + str(stopPriceCondition) + ' profitPriceCondition: ' + str(profitPriceCondition) + ' transmit: ' + str(transmit))

        #For PUT Options the Stop should be greater then the price and the take profit should be kess then the price
        if((stopPriceCondition <= priceCondition) and (priceCondition > 0)):
            print('Error: stopPriceCondition: ' + str(stopPriceCondition) + ' can not be less then the priceCondition: ' + str(priceCondition))
            sys.exit()

        elif((profitPriceCondition >= priceCondition) and (priceCondition > 0)):
            print('Put Contract Error: profitPriceCondition: ' + str(profitPriceCondition) + ' can not be greater then the priceCondition: ' + str(priceCondition))
            sys.exit()

        buyPutOptions(symbol=symbol, contractDate=contractDate, strike=strike, quantity=quantity, priceCondition=priceCondition, stopPriceCondition=stopPriceCondition, profitPriceCondition=profitPriceCondition, transmit=transmit)

    #Get Historical Data
    # timeframe='1 secs', '5 secs', '10 secs' 15 secs', '30 secs', '1 min', '2 mins', '3 mins', '5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours', '3 hours', '4 hours', '8 hours', '1 day', '1 week', '1 month'
    # duration = '60 S', '30 D', '13 W', '6 M', '10 Y'.
    elif((argProps.get('marketData') == 'historical') and (argProps.get('type') == 'STOCK') and (argProps.get('symbol') != None) and (argProps.get('timeframe') != None) and (argProps.get('duration') != None)):
        symbol=argProps.get('symbol')
        contract = Stock(symbol=symbol, exchange='SMART', currency='USD')
        timeframe=argProps.get('timeframe')
        duration=argProps.get('duration')
        preMarket=False if argProps.get('preMarket') == 'True' else True
        getHistoricalData(contract=contract, timeframe=timeframe, duration=duration, preMarket=preMarket)

    #Get Realtime Data
    elif((argProps.get('marketData') == 'onetime') and (argProps.get('type') == 'STOCK') and (argProps.get('symbol') != None)):
        symbol=argProps.get('symbol')
        contract = Stock(symbol=symbol, exchange='SMART', currency='USD')
        getRealtimeBar(contract=contract)

    #Get Realtime Data
    elif((argProps.get('marketData') == 'realtime') and (argProps.get('type') == 'STOCK') and (argProps.get('symbol') != None)):
        symbol=argProps.get('symbol')
        contract = Stock(symbol=symbol, exchange='SMART', currency='USD')
        preMarket=False if argProps.get('preMarket') == 'True' else True
        getRealtimeBars(contract=contract, barSize=5, preMarket=preMarket)


    ib.sleep(3)
    #printTrades()

    sys.exit()

if __name__ == "__main__":

    #python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'CALL' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '404' -stopPriceCondition '403' -profitPriceCondition '406' -transmit 'True'
    #python /dev-cli/cli/modules/tradingview/ib/ib-options.py -type 'PUT' -symbol 'SPY' -contractDate '20220829' -strike '403' -quantity '1' -priceCondition '403' -stopPriceCondition '402' -profitPriceCondition '400' -transmit 'True'

    #argv=["-symbol", 'SPY', "-contractDate", '20220829', "-strike", '403', "-quantity", '1', "-priceCondition" ,'404' , "-stopPriceCondition", '403', "-profitPriceCondition", "406", "-transmit", 'True']

    #argv=["-marketData", "historical" ,"-type", "STOCK", "-symbol", 'SPY', "-timeframe", "5 mins" , "-duration", "1 D", "-preMarket", "True"]
    #argv=["-marketData", "historical" ,"-type", "STOCK", "-symbol", 'SPY', "-timeframe", "5 mins" , "-duration", "7200 S", "-preMarket", "True"]
    #argv=["-marketData", "realtime" ,"-type", "STOCK", "-symbol", 'SPY', "-preMarket", "True"]

    #argv=["-marketData", "onetime" ,"-type", "STOCK", "-symbol", 'SPY']

    #argv=["-symbol", 'SPY', "-type", "CALL", "-contractDate", '20220928', "-strike", '361', "-quantity", '1', "-priceCondition" ,'361' , "-stopPriceCondition", '360', "-profitPriceCondition", "368", "-transmit", 'False']

    main_results=main(sys.argv)
    #main_results=main(argv)

    # if(main_results == 1):
    #     help()

