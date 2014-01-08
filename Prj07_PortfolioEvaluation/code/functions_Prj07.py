# -*- coding: utf-8 -*-
"""
Created on Sat Oct 05 15:28:58 2013

@author: Olena
these functions can be modified/added based on in what format a portfolio data is given

"""
import os
import sys
import csv
import datetime
import pandas as pd
sys.path.append(os.path.normpath(os.path.join(sys.path[0],".."+os.sep+".."+os.sep+'common_py'+os.sep))) 
import UTILITIES
###################################################################################### 
#### auxiliary functions
######################################################################################  
def str2float(txt):
    try:
        return float(txt.strip())
    except:
        return None
        
        

    
###################################################################################### 
#####  dates functions
######################################################################################  
def set_trading_dates(TrdDates,DF):
    t = [d for d in DF["Open"].index]
    for date in t:
        try:
            date = date.date()
        except:
            date = date
        if date not in TrdDates:
            TrdDates.append(date)
    TrdDates.sort()
    return TrdDates
    
def define_portfolio_dates(TradingDays,Holdings):
    vec = []
    for day in TradingDays:
        for hold in Holdings:
            if day in hold["holding_days"] and day not in vec:
                vec.append(day)
    vec.sort()
    return vec
            
            
def parse_US_date(date,default=None):
    """I suggest to pass .now().date() into default"""
    if date == "" or date == None:
        return default
    elem = date.split("/")
    date = datetime.datetime(int(elem[-1]),int(elem[0]),int(elem[1])).date()
    return date

def parse_normal_date(date,default=None):
    """I suggest to pass .now().date() into default"""
    if date == "" or date == None:
        return default
    elem = date.split("/")
    year = int(elem[-1])
    if year < 2000:
        year += 2000
    date = datetime.datetime(year,int(elem[1]),int(elem[0])).date()
    return date    
    
###################################################################################### 
#####  read data
###################################################################################### 
    
def read_portfolio_holdings_v1_USdate(fn):
    """one of the first functions written. it assumes US date format and therefore must rearrange it"""
    """ data is given with the following column names in a csv file: Security	PositionType	Quantity OpenDate	CloseDate"""
    
    print "reading porfolio holdings from",fn
    if not os.access(fn,os.R_OK):
        print "!!! could not read",fn
        return None
    Holdings = []
    rows = csv.DictReader(open(fn,'rb'))
    for row in rows:
        stk = row["Security"].strip()
        if stk != "":
            holding = {}
            holding["ticker_name"] = stk
            holding["position_type"] = row["PositionType"]
            holding["quantity"] = int(row["Quantity"])
            s_date = row["OpenDate"]
            e_date = row["CloseDate"]
            holding["start_date"] = parse_US_date(s_date)
            holding["end_date"] = parse_US_date(e_date,default=datetime.datetime(2013,9,28).date()) #default=datetime.datetime.now().date()
            holding["holding_days"] = []
            holding["daily_Open"]=[]
            holding["daily_Close"]=[]
            Holdings.append(holding)
    
    print "num in Holdings", len(Holdings)
    for pos in ["S","L"]:    
        print "num",pos,"in Holdings:", sum([1 for hold in Holdings if hold["position_type"]==pos])        
            
    return Holdings

#def initialize_additional_attributes_of_holding(Holdings):
#    """this function could have been combined with a function where the first attributes are set"""
#    for holding in Holdings:
#        holding["holding_days"] = []
#        holding["daily_Open"]=[]
#        holding["daily_Close"]=[]
#
#    print "num in Holdings", len(Holdings)
#    for pos in ["S","L"]:    
#        print "num",pos,"in Holdings:", sum([1 for hold in Holdings if hold["position_type"]==pos])        
#    return Holdings  
    
def clean_US_tickerNames(Holdings,fn):
    """sometimes US ticker names just have US in them, they should be substituted corrected with UN, UW etc. in order to get the prices correctly"""
    """to accomplish that, open the ticker names file and do the cleaning"""
    if not os.access(fn,os.R_OK):
        print "!!! could not read",fn
    US_ticker_names = []
    for line in open(fn,'r').readlines():
        if line.split(",")[0] != "":
            US_ticker_names.append(line.split(",")[0])
    
    for hold in Holdings:
        if hold["ticker_name"].upper().find(" US EQUITY")> 0:
            tick = hold["ticker_name"].split(" ")[0]
            for ticker in US_ticker_names:
                if tick == ticker.split(" ")[0]:
                    hold["ticker_name"] = ticker
                    #print "sub occurred", tick, hold["ticker_name"]
    return Holdings
    

###################################################################################### 
##### establishing special DFs
######################################################################################   
    
def sortout_special_prices(fn):
    print "reading",fn
    headers = open(fn,'r').readline().split(",")[1:]
    dates = []
    for head in headers:
        t =  parse_normal_date(head.strip())
        if t != None:
            dates.append(t)
    #print dates,len(dates)
    
    series = {}
    tickers = []
    for line in open(fn,'r').readlines():
        ticker = line.split(",")[0].strip()
        if ticker != "":
            tickers.append(ticker)
            prices = [str2float(elem) for elem in line.split(",")[1:] if elem.strip() != ""]
            #print ticker, len(prices)
            prices = dict(zip(dates,prices))
            #print prices
            series[ticker] =pd.Series(prices,index=dates)

    df = pd.DataFrame(series,index=dates,columns = tickers)
    #UTILITIES.dump_data(df,stock_name="",t_fn="t_dump.csv")
    return df
    
    

    
def define_WORLDbenchmark_index(DF,Xrate_DF,TickerSuffix_Currency,market="WORLD", name="PHG_WORLD600",needs_Xrate_conversion=True):
    """in order to ignore conversion rate, everything has be already in USD. then just do E.W. average"""
    """needs a lot more work if this average is to be build on my own"""

    print "\n making WORLD benchmark"
    DF['Open'][name] = DF['Open'].sum(axis=1)
    DF['Close'][name] = DF['Close'].sum(axis=1)  
    ew_stk = name
    cw_stk = name
        
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
##### writing to files  for debugging  ####################
######################################################################################            
def format_writing1(hold,line,attr):
    key = "Total "+attr
    if key in hold.keys():
        s = line+","+str(hold[key])+","+attr+","
    else:    
        s = line +",,"+attr+","
    return s
def write2file_4debugging(Holdings,BenchMarkIndex):
    #do a check to make sure prices have been found
    logf = open("log.csv",'w')
    for hold in Holdings:
        names = hold["ticker_name"]+","+hold["position_type"]+","+hold["start_date"].strftime("%Y-%m-%d")+","+hold["end_date"].strftime("%Y-%m-%d")+","
        quant_s = names+",,Quantity,"+str(hold["quantity"])+","        
        dates_s = names+",,Dates,"       
        prices_s = names+",,Open,"
        pricesC_s = names+",,Close,"
        beta_s = names+",,Beta,"
        oMKV_s = names+",,Open_MKV,"
        cMKV_s = names+",,Close_MKV,"
        PnL_s = format_writing1(hold,names,"PnL")
        Ret_s = format_writing1(hold,names,"Ret")
        RelRet_s = format_writing1(hold,names,"RelRet")
        Alpha_s = format_writing1(hold,names,"Alpha")
       
        if hold["holding_days"] == []:
            print hold["ticker_name"],"doesn't have price data for",hold["start_date"],hold["end_date"]
        else:
            for d in range(len(hold["holding_days"])):
                dates_s += str(hold["holding_days"][d])+","                
                prices_s += str(hold["daily_Open"][d])+","
                pricesC_s += str(hold["daily_Close"][d])+","
                cMKV_s += str(hold["Close_daily_MKV"][d])+","
                oMKV_s += str(hold["Open_daily_MKV"][d])+","
                beta_s += str(hold["daily_Beta"][d]) +","
                if d <= len(hold["daily_PnL"])-1:               
                    PnL_s += str(hold["daily_PnL"][d])+","
                    Ret_s += str(hold["daily_Ret"][d])+","
                    RelRet_s += str(hold["daily_RelRet"][d])+","
                    Alpha_s += str(hold["daily_Alpha"][d])+","
#                    Ret_s += str(hold["daily_Ret"][d]*hold['weight'][d])+","
#                    RelRet_s += str(hold["daily_RelRet"][d]*hold['weight'][d])+","
#                    Alpha_s += str(hold["daily_Alpha"][d]*hold['weight'][d])+","
                    
        logf.write(dates_s+"\n"+prices_s+"\n"+pricesC_s +"\n"+cMKV_s+"\n"+oMKV_s +"\n"+PnL_s+"\n"+Ret_s+"\n"+RelRet_s+"\n"+Alpha_s+"\n"+beta_s+"\n"+quant_s+"\n")
    s = ""
    for d in BenchMarkIndex["US"].index:
        try: d.date()
        except: pass
        s += d.strftime("%Y-%m-%d")+","
    logf.write(s)
    logf.close()
        
def write2file_holdings_summary(Holdings):
    """Run this to write a summary but only AFTER Totals for Ret and PnL have been """
    logf = open("holdings_summary.csv","w")
    s = "Equity,PositionType,StartDate,EndDate,Quantity,TTL PnL,TTL Ret, TTL RelRet, TTL Alpha"
    logf.write(s+"\n")
    for hold in Holdings:
        line = hold["ticker_name"]+","+hold["position_type"]+","+hold["start_date"].strftime("%Y-%m-%d")+","+hold["end_date"].strftime("%Y-%m-%d")+"," 
        line += str(hold["quantity"]) +","
        if "Total PnL" in hold.keys():
            line += str(hold["Total PnL"]) +","
        else:
            line += ","
        if "Total Ret" in hold.keys():
            line += str(hold["Total Ret"]) +","
        else:
            line += ","
        if "Total RelRet" in hold.keys():
            line += str(hold["Total RelRet"]) +","
        else:
            line += ","
        if "Total Alpha" in hold.keys():
            line += str(hold["Total Alpha"]) +","
        else:
            line += ","            
        logf.write(line+"\n")    
    logf.close()
    
    
    
                
                
