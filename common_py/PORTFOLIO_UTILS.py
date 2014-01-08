# -*- coding: utf-8 -*-
"""
Created on Sat Oct 05 17:25:32 2013

@author: Olena

Purpose: some utilities for portfolio evaluation
Datastructure: it's assumed that holding (hold) is the data structure this PORTFOLIO evaluator acts upon.
hold is a dictionary with some of the following keys:

"""
import os
import pandas as pd
import numpy
import math
import datetime

import sys
sys.path.append(os.path.normpath(os.path.join(sys.path[0],'..\..\common_py\\'))) 
import UTILITIES



###################################################################################### 
##### dataframe functions: reading prices/betas, cleaning them, etc.
######################################################################################

def make_dailyData_DataFrame(data_dir,fn_prefix,sheet_names):
    DF = {}
    for t_data in sheet_names:
        fn = data_dir+fn_prefix+t_data+".csv"
        if not os.access(fn,os.R_OK):
            print "!!! caution:",fn,"cannot be opened, or does not exist"
            df = pd.DataFrame() #is an empty dataframe 
        else:

            df = pd.DataFrame.from_csv(fn)
            t = [d.date() for d in df.index]
            df = df.reindex(index = t, columns = df.columns ) 
            stock_names = df.columns
            print "reading",fn_prefix+t_data
            print "num stocks:", len(stock_names)
            print "num days:",len(df.index)
        DF[t_data] = df
        
    return DF

def fill_Betas(DF,beta_names):
    for beta in beta_names:
        for stk in DF[beta].columns:
            DF[beta][stk] = DF[beta][stk].fillna(method='ffill')
            DF[beta][stk] = DF[beta][stk].fillna(method='bfill')
    return DF
    
def make_oneBeta(DF,mainBeta,secondaryBeta,proper_solution = True):
    """the reason for all those betas is to be able to have one. this one--the primary one--
    should take on the values of the primary beta, but where the primary doesn't exist then
    the values of the secondary should be taken.
    If the secondary doesn't exist either, then 1 should be used"""
    
    """NEEDS finishing DF['Beta'] to add"""
    for stk in DF[mainBeta].columns:
        if proper_solution:
            for d in range(len(DF[mainBeta][stk].index)):
                if type(DF[mainBeta][stk][d]) == numpy.float64  and math.isnan(DF[mainBeta][stk][d]): #may not work on every OS because of float64
                    if not math.isnan(DF[secondaryBeta][stk][d]):#
                        DF[mainBeta][stk][d] = DF[secondaryBeta][stk][d]
                    else:
                        DF[mainBeta][stk][d] = 1.0   
        else: #do only when need quick debuggind
            DF[mainBeta][stk] = DF[mainBeta][stk].fillna(1.00)
    DF["Beta"] = DF[mainBeta]                
    return DF
    
def fill_dailyData_with_defaults(Holdings,dailyData="Beta"):
    """function that fills missing betas with 1"""
    attribute = "daily_"+dailyData
    for hold in Holdings:
        if hold["holding_days"] != [] : 
            for d in range(len(hold["holding_days"])):
                if hold[attribute][d] == None:
                    hold[attribute][d] = 1
    return Holdings
    
#########################################################################
#####
########################################################################    
def make_Xrate_DF(fn):
    print "making Xrate DF from",fn
    currencies = {}
    dates = []
    c_curr = ""
    for line in open(fn,'r').readlines():
        date = UTILITIES.parse_normal_date(line.split(",")[0].strip())
        if date != None and date not in dates:
            dates.append(date)
        curr = line.split(",")[1].strip()
        if curr != c_curr:
            c_curr = curr
            currencies[c_curr] = {}
        rate = UTILITIES.str2float(line.split(",")[2].strip())
        
        if date != None and rate != None:
            currencies[c_curr][date] = rate

    #add all calendar dates since currency rate is applicable every day
    dates.sort()
    curr_date = dates[0]
    ldate = dates[-1]
    while curr_date < ldate:
        curr_date += datetime.timedelta(1)
        if curr_date not in dates:
            dates.append(curr_date)

    
    #now make the currencies DF
    Curr_DF = {}
    dates.sort()
    for curr in currencies.keys():
        Xrate = []
        for date in dates:
            if date in currencies[curr].keys():
                Xrate.append( currencies[curr][date])
            else:
                Xrate.append(None)
                #print "Xrate for",date,curr,"not A/V"
        prices = dict(zip(dates,Xrate))
        Curr_DF[curr] = pd.Series(prices,index=dates)
    df = pd.DataFrame(Curr_DF,index=dates)
    
    #UTILITIES.dump_data(df,stock_name="Currency",t_fn="t_CurrDF_dump.csv")
    return df  

def fill_NANs_in_Xrate(DF):
    """make sense to do it since all days should have approx Xrate"""
    for xrate_ticker in DF.columns:
        DF[xrate_ticker] =  DF[xrate_ticker].fillna(method='ffill')
        DF[xrate_ticker] =  DF[xrate_ticker].fillna(method='bfill') 
    return DF    

def test_correct_crc_conversion(Holdings,Xrate_DF):
    """this is a function for dubugging purposes only. 
    It can be used only after each hold has been assigned currency 
    AND open/close prices have been read. Then I compare the logs to see if my currency conversion is correct."""
    for hold in Holdings:
        if hold["currency"].upper() != "USD":
            for d in range(len(hold["holding_days"])):
                day = hold["holding_days"][d]
                hold["daily_Open"][d] = hold["daily_Open"][d]*Xrate_DF[hold["currency"]][day]
                hold["daily_Close"][d] = hold["daily_Close"][d]*Xrate_DF[hold["currency"]][day]
                    
    return Holdings    

  
    
###################################################################################### 
##### benchmark 
######################################################################################  
def define_0_benchmark(TradingDays):
    """used for those porfolios where there are weird dates, eg. easter when all markets should be closed"""
    print "\n making a 0 benchmark"
    ser_cw_o2o = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_cw_c2c = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_cw_o2c = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_cw_c2o = pd.Series([0.0 for x in TradingDays],index= TradingDays)    

    ser_ew_o2o = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_ew_c2c = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_ew_o2c = pd.Series([0.0 for x in TradingDays],index= TradingDays)
    ser_ew_c2o = pd.Series([0.0 for x in TradingDays],index= TradingDays)  
    
    t_df = {"Close2Close": ser_cw_c2c, 
            "E.W. Close2Close": ser_ew_c2c,
            "Open2Open":ser_cw_o2o,
            "E.W. Open2Open": ser_ew_o2o,
            "Open2Close": ser_cw_o2c,
            "E.W. Open2Close": ser_ew_o2c,
            "Close2Open": ser_cw_c2o,
            "E.W. Close2Open": ser_ew_c2o}
    df = pd.DataFrame(t_df,index=TradingDays)
    
    print df.columns #,df.index
    print df["E.W. Open2Open"][0:10]
    return df
        
        
def define_benchmark_index(DF,market ="US",name="SP500"):
    print "\n making a standdard benchmark"
    """what will be used as the benchmark???  I recommend SP500 E.W. but there is a problem with"""
    #attr = market #name+" "+market
    if market == "US" and name == "SP500":    
        cw_stk = "SPY US Equity"
        ew_stk = "RSP US Equity"
    else:
        cw_stk = "SPY US Equity"
        ew_stk = "RSP US Equity"

    ser_cw_o2o = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_cw_c2c = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_cw_o2c = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_cw_c2o = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)    

    ser_ew_o2o = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_ew_c2c = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_ew_o2c = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)
    ser_ew_c2o = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index)  
    
    for d in range(1,len(DF["Open"].index)):
        ser_cw_o2o.iloc[d] = DF["Open"][cw_stk].iloc[d]/DF["Open"][cw_stk].iloc[d-1] - 1.0
        ser_ew_o2o.iloc[d] = DF["Open"][ew_stk].iloc[d]/DF["Open"][ew_stk].iloc[d-1] - 1.0
        ser_cw_c2c.iloc[d] = DF["Close"][cw_stk].iloc[d]/DF["Close"][cw_stk].iloc[d-1] - 1.0
        ser_ew_c2c.iloc[d] = DF["Close"][ew_stk].iloc[d]/DF["Close"][ew_stk].iloc[d-1] - 1.0
        ser_cw_o2c.iloc[d] = DF["Close"][cw_stk].iloc[d]/DF["Open"][cw_stk].iloc[d] - 1.0
        ser_ew_o2c.iloc[d] = DF["Close"][ew_stk].iloc[d]/DF["Open"][ew_stk].iloc[d] - 1.0
        ser_cw_c2o.iloc[d] = DF["Open"][cw_stk].iloc[d]/DF["Close"][cw_stk].iloc[d-1] - 1.0
        ser_ew_c2o.iloc[d] = DF["Open"][ew_stk].iloc[d]/DF["Close"][ew_stk].iloc[d-1] - 1.0 
    t_df = {"Close2Close": ser_cw_c2c, 
            "E.W. Close2Close": ser_ew_c2c,
            "Open2Open":ser_cw_o2o,
            "E.W. Open2Open": ser_ew_o2o,
            "Open2Close": ser_cw_o2c,
            "E.W. Open2Close": ser_ew_o2c,
            "Close2Open": ser_cw_c2o,
            "E.W. Close2Open": ser_ew_c2o}
    df = pd.DataFrame(t_df,index=DF["Open"].index)
    print df.columns,df.index
    print df["E.W. Open2Open"][0:10]
    return df
    

###################################################################################### 
##### reading more data and sorting it out  ######################################################
######################################################################################  
def read_market_tickers(fn):
    TickerSuffix_Currency = {}
    for line in open(fn,'r').readlines():
        ticker_suffix = line.split(',')[0].strip().upper()
        currency = line.split(',')[1].strip()
        TickerSuffix_Currency[ticker_suffix] = currency
    return TickerSuffix_Currency

def attach_currency_to_ticker(Holdings,TickerSuffix_Currency):
    for hold in Holdings:
        ticker_suffix = " ".join(hold["ticker_name"].split(" ")[1:]).upper()
        if ticker_suffix in TickerSuffix_Currency.keys():
            hold["currency"] = TickerSuffix_Currency[ticker_suffix]
        elif ticker_suffix in ["UN EQUITY", "UW EQUITY",]:
            hold["currency"] = "USD"
        else:
            if hold["ticker_name"].upper() in TickerSuffix_Currency.keys():
                hold["currency"] = TickerSuffix_Currency[hold["ticker_name"].upper()]
            else:
                hold["currency"] = "USD"
                print "!!! caution",hold["ticker_name"].upper(),"not found, will assume USD currency"
    return Holdings
 
  
def clean_ticker_names(Holdings,prices_DF):
    """when portfolio is given, the ticker names might not be the same as in our DB, 
    this function synchronizes the ticker names in the portfolio with what we have in the prices DF"""
    print "cleaning upper/lower case issues in ticker names"
    ticker_names_Upper = [ticker.upper() for ticker in prices_DF["Open"].columns]
    ticker_names = [ticker for ticker in prices_DF["Open"].columns]
    for hold in Holdings:
        if hold["ticker_name"] not in ticker_names:#in this case the name is most likely changed
            if hold["ticker_name"].upper() in ticker_names_Upper: #in this instance the case must be modified
                for ticker in ticker_names:
                    if hold["ticker_name"].upper() == ticker.upper():
                        #print hold["ticker_name"],'sub/ed by',ticker
                        hold["ticker_name"] = ticker
    return Holdings
            
            
###################################################################################### 
##### filling in holding data  ######################################################
######################################################################################              
def populate_holdingDays_for_each_holding(Holdings,prices_DF,dfname=""):
    """this function fills the holding_days (days) list for each holding"""
    """MUST be envoked BEFORE getting prices and calculating DMV and PnL"""
    """MUST be envoked AFTER clean_ticker_names() to synchronize ticker_names"""
    
    for hold in Holdings:
        if hold["holding_days"] == []:
            if hold["ticker_name"] in prices_DF["Open"].columns:
                for d in prices_DF["Open"].index:
                    try:
                        d = d.date()
                    except:
                        pass
                    #print d 
                    if d >= hold["start_date"] and d <= hold["end_date"]:
                        hold["holding_days"].append(d) 
    return Holdings

def populate_dailyData_for_each_holding(Holdings,prices_DF,dailyData='Open',dfname=""):
    """MUST be envoked AFTER clean_ticker_names() to make sure ticker names are synchronized"""
    """This function can be used to read open, close, beta, etc."""
    """MUST be envoked AFTER populate_holdingDays_for_each_holding() has been done"""
    print "populating daily_"+dailyData,"from",dfname
    attribute = "daily_"+dailyData
    if attribute not in Holdings[0].keys():
        for hold in Holdings:
            hold[attribute] = []
            
    
    for hold in Holdings:
        if hold["holding_days"] != [] : #so holding days exist and open_prices is still unfilled
            if hold["ticker_name"] in prices_DF[dailyData].columns:
                if hold[attribute] == []:
                    for day in hold["holding_days"]:
                        try:
                            hold[attribute].append(prices_DF[dailyData][hold["ticker_name"]][day])
                        except:
                            hold[attribute].append(None)
                            #print "None was inserted for",hold["ticker_name"],day
                elif (None in hold[attribute]):
                    #print hold["ticker_name"],"has None in data",dailyData
                    for d in range(len(hold["holding_days"])):
                        if hold[attribute][d] == None:
                            try:
                                hold[attribute][d] = prices_DF[dailyData][hold["ticker_name"]][hold["holding_days"][d]]
                            except:
                                pass
                            
    return Holdings

def fill_missing_prices(Holdings,attr):
    print "executing fill_missing_prices on",attr
    """If this function causes an error then something must be wrong with the with the price on the first day"""
    for hold in Holdings:
        #print hold['ticker_name'],hold["holding_days"][0]
        for d in range(1,len(hold["holding_days"])): #as starting price in day d=0 cannot be unknown
            if type(hold[attr][d]) == numpy.float64 and math.isnan(hold[attr][d]): 
                #print hold["ticker_name"],"date", hold["holding_days"][d],"filled with", hold[attr][d-1]
                hold[attr][d] = hold[attr][d-1]
    return Holdings
    
    
###################################################################################### 
##### portfolio evalution functions
######################################################################################  
    
def calculate_portfolio_value_on_a_day(date,Holdings,attrib):
    val = 0
    for hold in Holdings:
        if date in hold["holding_days"]:
            d = hold["holding_days"].index(date)
            val += hold[attrib][d]
    return val
        
def calculate_holdings_daily_weight_in_portfolio(Portf_Close_daily_MKV_inUSD,hold,TradingDays):
    """assumes everything has been converted to one currency"""
    hold["weight"] = [1 for elem in hold["holding_days"]]
    if len(hold["holding_days"]) == 1:
        date = hold["holding_days"][0]
        if date not in TradingDays:
            print "!!!! ERROR ERROR cannot be here"
            hold["weight"][0] = 1
        else:
            if hold["Close_daily_MKV_inUSD"][0] != None:
                hold["weight"][0] = hold["Close_daily_MKV_inUSD"][0]/Portf_Close_daily_MKV_inUSD[date]
            else:
                hold["weight"][0] = 1
    else:
        for d in range(len(hold["holding_days"])):
            date = hold["holding_days"][d]
            if date not in TradingDays:
                print "!!!! ERROR ERROR cannot be here"
                hold["weight"][d] = 1
            else:
                if hold["Close_daily_MKV_inUSD"][d] != None:
                    hold["weight"][d] = hold["Close_daily_MKV_inUSD"][0]/Portf_Close_daily_MKV_inUSD[date]
                else:
                    hold["weight"][d] = 1
        
    return hold
    
    
    
def side_eval(Holdings,TradingDays,side="L",shift=-1,attr="daily_Ret"):
    ser_S = pd.Series([0.0 for x in TradingDays],index=TradingDays)
    print "side evaluation:",side #, ser_S, ser_S.index
    
    for d in range(len(TradingDays)):
        L_sum = 0
        date = TradingDays[d]
        for hold in Holdings:
            if hold["position_type"].upper() == side.upper():
                if len(hold["holding_days"]) == 1 and date in hold["holding_days"]:
                    L_sum += hold[attr][0]*hold["weight"][0]
                elif date in hold["holding_days"][1:]:
                    ind = hold["holding_days"].index(date)
                    if shift != 0 and ind > 0:
                        try:
                            L_sum += hold[attr][ind + shift]*hold["weight"][ind]
                        except:
                            print hold["ticker_name"],'ind=',ind,'len(HoldDays)',len(hold["holding_days"]),'date=',date
                            
                    elif shift == 0:
                        L_sum += hold[attr][ind]*hold["weight"][0]
                            
        ser_S[d] = L_sum
    return ser_S
      
def DailyStats_eval_return(Holdings,TradingDays,attr="daily_Ret"):
    ser_L = side_eval(Holdings,TradingDays,side="L",shift=-1,attr=attr)
    ser_S = side_eval(Holdings,TradingDays,side="S",shift=-1,attr=attr)                
    df = {"Long": ser_L,"Short":ser_S}
    df = pd.DataFrame(df,index = TradingDays)                
    return df


def make_CumStats(df): 
    df["Cum Long"] = df["Long"].cumsum()
    df["Cum Short"] = df["Short"].cumsum()
    df["Cum L+S"] = df["Cum Long"] + df["Cum Short"]
    df["Cum Long %"] = 100*df["Long"].cumsum()
    df["Cum Short %"] = 100*df["Short"].cumsum()
    df["Cum L+S %"] = 100*(df["Cum Long"] + df["Cum Short"])
        
###################################################################################### 
##### trade evaluation  functions
######################################################################################  
    
def calculate_RelRet(hold,BenchMarkDF,beta="Beta"):
    hold["daily_Alpha"] = [0 for elem in hold["daily_Ret"]]
    hold["daily_RelRet"] = [0 for elem in hold["daily_Ret"]]
    beta = "daily_"+beta
    multiplier = 1
    if hold["position_type"].upper() == "S":
        multiplier = -1
    
    benchMarkName = "US"
    
    
    if len(hold["holding_days"]) == 1:
        day = hold["holding_days"][0]
        if day in BenchMarkDF["US"].index:
            benchMarkName = "US"
        elif day in BenchMarkDF["WORLD"].index:
            benchMarkName = "WORLD"
        else:
            print day,"not found in any index, 0 will be used for benchmarking"
            benchMarkName = "0"
        #if benchMarkName in ["WOLD","0"]: print day,"benchmark",benchMarkName,"is used"
        if hold["daily_Ret"][0] != None and hold[beta][0] != None and benchMarkName not in ["WORLD","0"]:
            hold["daily_Alpha"][0] = hold["daily_Ret"][0]-multiplier*hold[beta][0]*BenchMarkDF[benchMarkName]["Open2Close"][day]
            hold["daily_RelRet"][0] = hold["daily_Ret"][0]-multiplier*BenchMarkDF[benchMarkName]["Open2Close"][day]

    else:
        for d in range(len(hold["daily_Ret"])-1):
            day = hold["holding_days"][d+1]
            if day in BenchMarkDF["US"].index:
                benchMarkName = "US"
            elif day in BenchMarkDF["WORLD"].index:
                benchMarkName = "WORLD"
            else:
                print day,"not found in any index"
                benchMarkName = "0"
            if benchMarkName in ["WOLD","0"]: print day,"benchmark",benchMarkName,"is used"
            if hold["daily_Ret"][d] != None and hold[beta][d] != None and benchMarkName not in ["WORLD","0"]:    
                hold["daily_Alpha"][d] = hold["daily_Ret"][d]-multiplier*hold[beta][d]*BenchMarkDF[benchMarkName]["Close2Close"][day]
                hold["daily_RelRet"][d] = hold["daily_Ret"][d]-multiplier*BenchMarkDF[benchMarkName]["Close2Close"][day]
            
        
        d = len(hold["daily_Ret"])-1
        day = hold["holding_days"][d+1]
        if day in BenchMarkDF["US"].index:
            benchMarkName = "US"
        elif day in BenchMarkDF["WORLD"].index:
            benchMarkName = "WORLD"
        else:
            print day,"not found in any index" 
            benchMarkName = "0"
        if benchMarkName in ["WOLD","0"]: print day,"benchmark",benchMarkName,"is used"
        if hold["daily_Ret"][d] != None and hold[beta][d] != None and benchMarkName not in ["WORLD","0"]:     
            hold["daily_Alpha"][d] = hold["daily_Ret"][d]-multiplier*hold[beta][d]*BenchMarkDF[benchMarkName]["Close2Open"][day]
            hold["daily_RelRet"][d] = hold["daily_Ret"][d]-multiplier*BenchMarkDF[benchMarkName]["Close2Open"][day]
        
    return hold
               

def evaluate_holding(hold,BenchMarkDF):
    """evaluating a holding"""
    
    hold = calculate_daily_MKV(hold,attribute="Open")
    hold = calculate_daily_MKV(hold,attribute="Close")
    hold = calculate_daily_PnL_v1(hold)
    hold = calculate_daily_Ret_v1(hold)
    hold = calculate_RelRet(hold,BenchMarkDF,beta="Beta")
    """the following should be done after the weights have been calculated, 
    which means, sometimes, currency conversion. However as long as weights are taken into account for graphs 
    and the daily stats (which they are in the side_evaluation) then it's all ok."""
    hold = calculate_totals(hold,attribute="Ret")
    hold = calculate_totals(hold,attribute="PnL")
    #hold = calculate_totals(hold,attribute="RelRet")
    #hold = calculate_totals(hold,attribute="Alpha")
    

def calculate_totals(hold,attribute="Ret"):
    """actually these are useless till the weights are put in place. and if we are dealing with different currencies,
    then we first have to do conversion"""
    Tattr = "Total "+attribute
    attribute = "daily_"+attribute
    hold[Tattr] = 0
    if len(hold[attribute]) == 1:
        hold[Tattr] += hold[attribute][0] 
    else:
        for d in range(len(hold[attribute])):
            if hold[attribute][d] != None:
                hold[Tattr] += hold[attribute][d]    
    #print hold["ticker_name"],Tattr,"=",hold[Tattr]
    return hold
    
def calculate_daily_Ret_v1(hold):
    hold["daily_Ret"] =[]
    if len(hold["holding_days"]) == 1:
        if hold["daily_PnL"][0] != None and hold["Open_daily_MKV"][0] != None:
            hold["daily_Ret"].append(hold["daily_PnL"][0]/hold["Open_daily_MKV"][0])
        else:
            hold["daily_Ret"].append(None)
    else:
        for d in range(0,len(hold["daily_PnL"])-1):
            if hold["Close_daily_MKV"][d] != None and hold["daily_PnL"][d] != None:
                hold["daily_Ret"].append(hold["daily_PnL"][d]/hold["Close_daily_MKV"][d])
            else:
                hold["daily_Ret"].append(None)
        d = len(hold["daily_PnL"])-1
        if hold["Open_daily_MKV"][-1] != None and hold["daily_PnL"][-1] != None:
            hold["daily_Ret"].append(hold["daily_PnL"][-1]/hold["Open_daily_MKV"][-1])
        else:
            hold["daily_Ret"].append(None)
    return hold                
                

def calculate_daily_PnL_v1(hold):
    multiplier = 1
    if hold["position_type"].upper() == "S":
        multiplier = -1    
    hold["daily_PnL"]=[]
    if len(hold["holding_days"]) == 1:
        if hold["Close_daily_MKV"][0] != None and hold["Open_daily_MKV"][0] != None:
            hold["daily_PnL"].append((hold["Close_daily_MKV"][0] - hold["Open_daily_MKV"][0])*multiplier)
        else:
            hold["daily_PnL"].append(None)
    else:
        for d in range(1,len(hold["holding_days"])-1):
            if hold["Close_daily_MKV"][d] != None and hold["Close_daily_MKV"][d-1] != None:
                hold["daily_PnL"].append((hold["Close_daily_MKV"][d] - hold["Close_daily_MKV"][d-1])*multiplier)
            else:
                hold["daily_PnL"].append(None)
        d = len(hold["holding_days"])- 1
        if hold["Open_daily_MKV"][d] != None and hold["Close_daily_MKV"][d-1] != None:
            hold["daily_PnL"].append((hold["Open_daily_MKV"][d] - hold["Close_daily_MKV"][d-1])*multiplier) 
        else:
            hold["daily_PnL"].append(None)
    return hold

    
def calculate_daily_MKV(hold,attribute="Open"):
    attr = attribute+"_daily_MKV"
    price = "daily_"+attribute
    hold[attr] = []
    
    for d in range(len(hold["holding_days"])):
        try:
            hold[attr].append(hold[price][d]*hold['quantity'])
        except:
            hold[attr].append(None)
    return hold

def currency_conversion_of_daily_PnL_v1(hold,Xrate_DF,attrib):
    usd_attrib = attrib+"_inUSD"
    if usd_attrib not in hold.keys():
        hold[usd_attrib] = []
    if hold["currency"].upper() != "USD":
        if len(hold["holding_days"]) == 1:
            day = hold["holding_days"][0]
            if hold[attrib] != None:
                hold[usd_attrib].append(hold[attrib][0]*Xrate_DF[hold["currency"]][day])
            else:
                hold[usd_attrib].append(None)
        else:
            for d in range(1,len(hold["holding_days"])):
                day = hold["holding_days"][d]
                if hold[attrib] != None:
                    hold[usd_attrib].append(hold[attrib][d-1]*Xrate_DF[hold["currency"]][day])
                else:
                    hold[usd_attrib].append(None)      
    else:
        hold[usd_attrib] = [ elem for elem in hold[attrib]]
    return hold
        

def currency_conversion_of_daily_attrib(hold,Xrate_DF,attrib):
    """this is a function for dubugging purposes only. 
    It can be used only AFTER each holding has been assigned currency the original attribute has been set."""
    
    usd_attrib = attrib+"_inUSD"
    if usd_attrib not in hold.keys():
        hold[usd_attrib] = []
    if hold["currency"].upper() != "USD":
        for d in range(len(hold["holding_days"])):
            day = hold["holding_days"][d]
            if hold[attrib][d] != None:
                hold[usd_attrib].append(hold[attrib][d]*Xrate_DF[hold["currency"]][day])
            else:
                hold[usd_attrib].append(None)
    else:
        hold[usd_attrib] = [ elem for elem in hold[attrib]]
    return hold   

def currency_conversion(hold,Xrate_DF):
    hold = currency_conversion_of_daily_attrib(hold,Xrate_DF,"Open_daily_MKV")
    hold = currency_conversion_of_daily_attrib(hold,Xrate_DF,"Close_daily_MKV")
    hold = currency_conversion_of_daily_PnL_v1(hold,Xrate_DF,"daily_PnL")
    return hold
    
    
###################################################################################### 
##### temporary functions. should not be used if one can help it  ####################
######################################################################################           
