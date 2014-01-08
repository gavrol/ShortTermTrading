# -*- coding: utf-8 -*-
"""
Created on Mon Sep 09 15:56:36 2013

@author: olenag
"""


import os
import csv
import pandas as pd
import CLASSdef
import datetime
import math


DATA_DIR = "..\data\\"
    
    
def add_to_portfolio(portf,date,DATA,F2Scores,Decisions):
    portf.holdings[date] = {}
    for stk in DATA.keys():
        if Decisions[stk]["Decision"] in ["S","L"]:
            if stk == "TEL UN Equity":
                print stk,date,Decisions[stk]["Decision"]
            portf.holdings[date][stk] = {}
            portf.holdings[date][stk]["Decision"] =  Decisions[stk]["Decision"]
            portf.holdings[date][stk]["Scores"] = {} 
            portf.holdings[date][stk]["Decisions"] = {}
            for fscore in F2Scores:
                portf.holdings[date][stk]["Scores"][fscore] = DATA[stk][fscore]["Score"]
                portf.holdings[date][stk]["Decisions"][fscore] = Decisions[stk][fscore]     
                
                
def examine_portfolio_performance(portf,F2Scores,date_start,date_end):
  
    print "Examining portfolio with Strategy:",portf.strategy,"HD:", portf.HD,"from", date_start,"till",date_end

    #read open, close, beta, sector and poolIndicator from a DB dump, which is produced by another program    
    fn = "SP500.xls"
    DF = get_open_close_beta_sector_poolInd_fromDBdump(DATA_DIR+fn)
    portf = clean_portfolio(portf,DF)
    
    #get stock names based on the stock open/close extract from DB, probably the most reliable source of info    
    stock_names = []
    for elem in DF['Open'].columns:
        stock_names.append(elem) 
    #print stock_names
    
    phg_stock_sector = {}
    fn_stock_details = "Stock_details.csv"
    get_stock_sector_info(DATA_DIR+fn_stock_details,phg_stock_sector)
    
    evaluate_trades(portf,DF,F2Scores,phg_stock_sector)
    fn = "ComData_"+portf.strategy+"_MHD"+str(portf.HD)+"_"+date_start.strftime("%Y%m%d")+"_"+date_end.strftime("%Y%m%d")+".csv"  
    write2file_evaluated_trades(fn,portf)
    
    evaluate_dailyPortfolio(portf,DF)
    make_Portfolio_Summary(portf)
    fn = "PortfolioPerformance_"+portf.strategy+"_MHD"+str(portf.HD)+"_"+date_start.strftime("%Y%m%d")+"_"+date_end.strftime("%Y%m%d")+".csv"  
    write2file_portfolio_eval(fn,portf)
    
    #evaluate_investment_performance(portf,DF)
    
def evaluate_investment_performance(portf,DF):
    """this function is needed if I want to have a graphical representation. it's useful, but not sure it's worth the 
    time investment unless I make it generic enough so I can re-use it later."""
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)
    portf_dates.sort()
    
    df = pd.DataFrame()
    df["Daily P/L"] = pd.Series([0.0 for x in portf_dates],index=portf_dates) 
    df["Daily MKV"] = pd.Series([0.0 for x in portf_dates],index=portf_dates) 
    df["Daily Abs Ret"] = pd.Series([0.0 for x in portf_dates],index=portf_dates)
    df["Daily Rel Ret"] = pd.Series([0.0 for x in portf_dates],index=portf_dates)
    df["Daily Beta"] = pd.Series([0.0 for x in portf_dates],index=portf_dates)
    df["Daily Alpha"] = pd.Series([0.0 for x in portf_dates],index=portf_dates)

    DF_dates = get_DB_dates(DF)    
    for p_date in portf_dates:
        if p_date in DF_dates:
            date_indx = DF_dates.index(p_date) #must exist 
            for date in portf_dates:
                for stk in  portf.holdings[p_date].keys():
                    pass
               

    
def make_Portfolio_Summary(portf):
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)
    portf_dates.sort()
    Summary = {}

    for att in ["No. Longs","No. Shorts","Long MKV","Long Beta","Short MKV","Short Beta","Beta","Net MKV"]:
        t = 0.0
        num = 0.0
        for p_date in portf_dates:
            if portf.holdings[p_date]["Eval"][att] != None:
                t += portf.holdings[p_date]["Eval"][att]
                num += 1.0
        if num != 0:
            Summary[att] = t/num
        else:
            Summary[att] = None
    for att in ["Long P/L","Short P/L","P/L","Long Alpha","Short Alpha"]:
        t = 0.0
        for p_date in portf_dates:
            if portf.holdings[p_date]["Eval"][att] != None:
                t += portf.holdings[p_date]["Eval"][att]
        Summary[att] = t 
    Summary["Long Alpha"]  = Summary["Long Alpha"]/portf.HD
    Summary["Short Alpha"]  = Summary["Short Alpha"]/portf.HD
    
    Summary["Long Ret"] = Summary["Long P/L"]/(Summary["Long MKV"]*portf.HD)
    Summary["Short Ret"] = Summary["Short P/L"]/(Summary["Short MKV"]*portf.HD) 
    Summary["Ret"] = Summary["P/L"]/(max(Summary["Short MKV"],Summary["Long MKV"])*portf.HD) 
    portf.summary = Summary
            
    
def write2file_portfolio_eval(ofn,portf):
    #Portfolio Picked @ Close	No. Longs	No. Shorts	P/L	MKV	Ret	Beta	Alpha	P/L	MKV	Ret	Beta	Alpha	P/L	NET MKV	Ret	Beta
    of = open(ofn,'w')
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)
    portf_dates.sort()
    
    headers ="Portfolio Picked @ Close,No. Longs,No. Shorts,Long P/L,Long MKV,Long Ret,Long Beta,Long Alpha,Short P/L,Short MKV,Short Ret,Short Beta,Short Alpha,P/L,Net MKV,Ret,Beta"
    of.write(headers+"\n")
    
    v_headers = headers.split(",")[1:]
    
    for p_date in portf_dates:
        ln = p_date.strftime("%d/%m/%Y")+","
        for heading in v_headers:
            ln+= str(portf.holdings[p_date]["Eval"][heading])+","
        of.write(ln+"\n")
    ln = "TOTAL,"
    for heading in v_headers:
        ln += str(portf.summary[heading])+","
    of.write(ln+"\n")
    of.close()
    
def evaluate_dailyPortfolio(portf,DF):
    print "\n evaluating portfolios"
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)  
    portf_dates.sort()

    DF_dates = get_DB_dates(DF)
    
    for p_date in portf_dates:
        date_indx = DF_dates.index(p_date)
        portf_eval = {}
        numLongs = 0
        numShorts = 0
        L_PnL = 0
        S_PnL = 0
        L_MKV = 0
        S_MKV = 0
        L_Beta = 0
        S_Beta = 0
        S_Alpha = 0
        L_Alpha = 0
        if date_indx >= len(DF_dates)-1: #very little evaluation can be done in this case as there is no data about the next day after the portfolio was picked
            for stk in  portf.holdings[p_date].keys():            
                if portf.holdings[p_date][stk]["Decision"] == "S":
                    numShorts += 1
                elif portf.holdings[p_date][stk]["Decision"] == "L":
                    numLongs += 1                
                else:
                    print "!!! caution: should not be here"
            portf_eval["No. Longs"] = numLongs
            portf_eval["No. Shorts"] = numShorts
            portf_eval["Long P/L"] = None           
            portf_eval["Short P/L"] = None
            portf_eval["Long MKV"] = None
            portf_eval["Short MKV"] = None
            portf_eval["Long Ret"] = None
            portf_eval["Short Ret"] = None
            portf_eval["Long Beta"] = None
            portf_eval["Short Beta"] = None
            portf_eval["Long Alpha"] = None
            portf_eval["Short Alpha"] = None
            portf_eval["P/L"] = None
            portf_eval["Net MKV"] = None
            portf_eval["Ret"] = None
            portf_eval["Beta"] = None
          
        else:
            for stk in  portf.holdings[p_date].keys():            
                if portf.holdings[p_date][stk]["Decision"] == "S" and portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                    numShorts += 1
                    S_PnL += portf.holdings[p_date][stk]["Eval"]["Total P/L"]
                    S_MKV += portf.holdings[p_date][stk]["Eval"]["D1 MKV"]
                    if portf.holdings[p_date][stk]["Eval"]["S W Beta"] != None:
                        S_Beta += portf.holdings[p_date][stk]["Eval"]["S W Beta"]
                    if portf.holdings[p_date][stk]["Eval"]["W Alpha"] != None:
                        S_Alpha += portf.holdings[p_date][stk]["Eval"]["W Alpha"]  
                        
                elif portf.holdings[p_date][stk]["Decision"] == "L" and portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                    numLongs += 1
                    L_PnL += portf.holdings[p_date][stk]["Eval"]["Total P/L"]
                    L_MKV += portf.holdings[p_date][stk]["Eval"]["D1 MKV"]
                    if portf.holdings[p_date][stk]["Eval"]["L W Beta"] != None:
                        L_Beta += portf.holdings[p_date][stk]["Eval"]["L W Beta"]  
                    if portf.holdings[p_date][stk]["Eval"]["W Alpha"] != None:
                        L_Alpha += portf.holdings[p_date][stk]["Eval"]["W Alpha"] 
                        
            portf_eval["No. Longs"] = numLongs
            portf_eval["No. Shorts"] = numShorts
            portf_eval["Long P/L"] = L_PnL           
            portf_eval["Short P/L"] = S_PnL
            portf_eval["Long MKV"] = L_MKV
            portf_eval["Short MKV"] = S_MKV
            portf_eval["Long Ret"] = L_PnL/L_MKV
            portf_eval["Short Ret"] = S_PnL/S_MKV
            portf_eval["Long Beta"] = L_Beta
            portf_eval["Short Beta"] = S_Beta
            portf_eval["Long Alpha"] = L_Alpha
            portf_eval["Short Alpha"] = S_Alpha
            portf_eval["P/L"] = portf_eval["Long P/L"] + portf_eval["Short P/L"]
            portf_eval["Net MKV"] = portf_eval["Long MKV"] - portf_eval["Short MKV"]
            portf_eval["Ret"] = portf_eval["P/L"]/max(portf_eval["Long MKV"], portf_eval["Short MKV"])
            portf_eval["Beta"] = (portf_eval["Long MKV"]*portf_eval["Long Beta"]+portf_eval["Short MKV"]*portf_eval["Short Beta"])/max(portf_eval["Long MKV"], portf_eval["Short MKV"])
            
        portf.holdings[p_date]["Eval"] = portf_eval
        
        
def clean_portfolio(portf,DF):
    """in real life this function is not necessary as we know which stocks will be suspended from trading due to corporate actions,
    and we will not chooses such stocks to trade. 
    However this function is necessary for this exercise. """
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)
    portf_dates.sort()
        
    DF_dates = get_DB_dates(DF)    
    
    for p_date in portf_dates:
        if p_date not in DF_dates:
            print "Portfolio date", p_date.strftime("%d/%m/%Y"),"not in DFdates, so portfolio won't be evaluated"
            del portf.holdings[p_date]
        else: 
            date_indx = DF_dates.index(p_date) #must exist 
            for stk in  portf.holdings[p_date].keys():
                if math.isnan(DF["Close"][stk].loc[p_date]) or math.isnan(DF["Beta"][stk].loc[p_date]): #closing prices is not there or Beta is missing
                    print "deleting",stk,"for",p_date,"b/c either Close or Beta are missing"
                    del portf.holdings[p_date][stk]
                else:
                    for i in range(1,portf.HD+2):
                        if date_indx + i <= len(DF_dates)-1: 
                            if math.isnan(DF["Open"][stk].iloc[date_indx+i]):#the opening prices for all the following days must be there as well, else the stock should not be considered for the portfolio
                                print "deliting", stk,"for",p_date,"b/c open",i,"days later is missing"                            
                                del portf.holdings[p_date][stk]
                                break
 
    return portf
    
def evaluate_trades(portf,DF,F2Scores,phg_stock_sector):
    print "\n evaluating trades"
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)

    DF_dates = get_DB_dates(DF)
    
    for p_date in portf_dates:
        if p_date not in DF_dates:
            print "Portfolio date", p_date.strftime("%d/%m/%Y"),"not in DFdates, so it won't be evaluated"
            pass
        else: #Quantity	Sector	Beta	Last	Open 1	Open 2	D1 Ret	D2 Ret	D3 Ret	D4 Ret	D5 Ret
            for stk in  portf.holdings[p_date].keys():
                #print stk,
                stk_eval = {}
                try:
                    stk_eval["Last"] = DF["Close"][stk].loc[p_date]
                    #print "Last", stk_eval["Last"],
                    if portf.investment_mode == "Fixed Cap/Stock":
                        stk_eval["Quantity"] = round(portf.capital_per_stock/stk_eval["Last"],0)
                        #print "Quantity", stk_eval["Quantity"]
                except:
                    stk_eval["Last"] = None
                    stk_eval["Quantity"] = None
                    print "could not find Last and/or Quantity for",stk,p_date
                    
                try:
                    stk_eval["Beta"] = DF["Beta"][stk].loc[p_date]
                except:
                    print "could not find Beta for",stk,p_date
                    stk_eval["Beta"] = None
                    
                if stk in phg_stock_sector.keys() and phg_stock_sector[stk].sector != "":
                    stk_eval["Sector"] = phg_stock_sector[stk].sector
                else:
                    try:
                        stk_eval["Sector"] = DF["SectorInfo"][stk].loc[p_date]
                    except:
                        stk_eval["Sector"] = None
                        
                date_indx = DF_dates.index(p_date) 
                for hd in range(portf.HD+1):
                    try:
                        stk_eval["Open "+str(hd+1)] = DF["Open"][stk].iloc[date_indx+hd+1]
                    except:
                        stk_eval["Open "+str(hd+1)] = None

                
                for hd in range(1,portf.HD+1):
                    if stk_eval["Open "+str(hd)] != None and stk_eval["Quantity"] != None:
                        stk_eval["D"+str(hd) +" MKV"] = stk_eval["Open "+str(hd)]*stk_eval["Quantity"]
                    else:
                        stk_eval["D"+str(hd) +" MKV"] = None
                        
                        
                stk_eval["Total P/L"] = 0        
                for hd in range(1,portf.HD+1):
                    if stk_eval["Open "+str(hd+1)] != None and stk_eval["Open "+str(hd)] != None and stk_eval["Quantity"] != None:
                        stk_eval["D"+str(hd) +" P/L"] = (stk_eval["Open "+str(hd+1)]- stk_eval["Open "+str(hd)])*stk_eval["Quantity"]
                        if portf.holdings[p_date][stk]["Decision"] == "S":
                            stk_eval["D"+str(hd) +" P/L"] = -stk_eval["D"+str(hd) +" P/L"]
                        stk_eval["Total P/L"] +=  stk_eval["D"+str(hd) +" P/L"]
                    else:
                        stk_eval["D"+str(hd) +" P/L"] = None
                
                stk_eval["Total return"] = 0
                for hd in range(1,portf.HD+1):
                    if stk_eval["D"+str(hd) +" P/L"] != None and stk_eval["D"+str(hd) +" MKV"] != None:
                        stk_eval["D"+str(hd) +" Ret"] = stk_eval["D"+str(hd) +" P/L"]/stk_eval["D"+str(hd) +" MKV"]
                        stk_eval["Total return"] += stk_eval["D"+str(hd) +" Ret"]
                    else:
                        stk_eval["D"+str(hd) +" Ret"] = None
                if stk_eval["Open 1"] != None and stk_eval["Quantity"] != None:
                    stk_eval["Total return (com)"] = stk_eval["Total P/L"]/(stk_eval["Open 1"]*stk_eval["Quantity"])
                else:
                     stk_eval["Total return (com)"] =0
                     
                #ALPHA
                stk_eval["Alpha"] = None
                SP500ewcum = 0
                for hd in range(portf.HD):
                    try:
                        SP500ewcum += DF["SP500 E.W."].iloc[date_indx+hd+2]
                    except:
                        SP500ewcum += 0 #= None
                    
                if stk_eval["Beta"] != None and SP500ewcum != None:
                    if portf.holdings[p_date][stk]["Decision"] == "S":
                        stk_eval["Alpha"] = stk_eval["Total return"] + stk_eval["Beta"]*SP500ewcum
                    elif portf.holdings[p_date][stk]["Decision"] == "L":
                        stk_eval["Alpha"] = stk_eval["Total return"] - stk_eval["Beta"]*SP500ewcum
                    else:
                        print "!!! CAUTION: should not be here:",stk,"is neither L nor S",p_date
                        
                stk_eval["L Weight"] = None
                stk_eval["S Weight"] = None
                
                portf.holdings[p_date][stk]["Eval"] = stk_eval
            
            #finished the first round thru all the stocks: see what's in each portfolio up to now
            L_D1_MKV = 0
            S_D1_MKV = 0
            for stk in  portf.holdings[p_date].keys():
                if portf.holdings[p_date][stk]["Decision"] == "S":
                    if portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                        S_D1_MKV += portf.holdings[p_date][stk]["Eval"]["D1 MKV"]
                elif portf.holdings[p_date][stk]["Decision"] == "L":
                    if portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                        L_D1_MKV += portf.holdings[p_date][stk]["Eval"]["D1 MKV"]
                else:
                    print "CAUTION!!! should not be here as it indicates that something in the portfolio is neither S nor L"
            
            #evaluated Weighted Beta and Alpha (based on Short and Long); done only after the first run 
            for stk in  portf.holdings[p_date].keys():
                if portf.holdings[p_date][stk]["Decision"] == "S" and portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                    portf.holdings[p_date][stk]["Eval"]["S Weight"] = -portf.holdings[p_date][stk]["Eval"]["D1 MKV"]/S_D1_MKV
                    portf.holdings[p_date][stk]["Eval"]["S W Beta"] = portf.holdings[p_date][stk]["Eval"]["S Weight"]*portf.holdings[p_date][stk]["Eval"]["Beta"] 
                    if portf.holdings[p_date][stk]["Eval"]["Alpha"] != None:
                        portf.holdings[p_date][stk]["Eval"]["W Alpha"] = -portf.holdings[p_date][stk]["Eval"]["S Weight"]*portf.holdings[p_date][stk]["Eval"]["Alpha"] 
                    else:
                        portf.holdings[p_date][stk]["Eval"]["W Alpha"] = None
                    portf.holdings[p_date][stk]["Eval"]["L Weight"] = ""
                    portf.holdings[p_date][stk]["Eval"]["L W Beta"] = ""
                elif portf.holdings[p_date][stk]["Decision"] == "L" and portf.holdings[p_date][stk]["Eval"]["D1 MKV"] != None:
                    portf.holdings[p_date][stk]["Eval"]["L Weight"] = portf.holdings[p_date][stk]["Eval"]["D1 MKV"]/L_D1_MKV
                    portf.holdings[p_date][stk]["Eval"]["L W Beta"] = portf.holdings[p_date][stk]["Eval"]["L Weight"]*portf.holdings[p_date][stk]["Eval"]["Beta"] 
                    
                    if portf.holdings[p_date][stk]["Eval"]["Alpha"] != None:
                        portf.holdings[p_date][stk]["Eval"]["W Alpha"] = portf.holdings[p_date][stk]["Eval"]["L Weight"]*portf.holdings[p_date][stk]["Eval"]["Alpha"] 
                    else:
                        portf.holdings[p_date][stk]["Eval"]["W Alpha"] = None                    
                    
                    portf.holdings[p_date][stk]["Eval"]["S Weight"] =""
                    portf.holdings[p_date][stk]["Eval"]["S W Beta"] = ""

                else:
                    portf.holdings[p_date][stk]["Eval"]["L Weight"] = None
                    portf.holdings[p_date][stk]["Eval"]["L W Beta"] = None
                    portf.holdings[p_date][stk]["Eval"]["W Alpha"] = None
                    portf.holdings[p_date][stk]["Eval"]["S Weight"] = None
                    portf.holdings[p_date][stk]["Eval"]["S W Beta"] = None
                    

                        
                        
                    
def  write2file_evaluated_trades(ofn,portf):
    of = open(ofn,'w')
    portf_dates = []
    for elem in portf.holdings.keys():
        portf_dates.append(elem)
    portf_dates.sort()
    #print "Portfolio Dates:",portf_dates
    
    headers ="Ticker,Portfolio Date,Quantity,Sector,Beta,Last,"
    for hd in range(portf.HD+1):
        headers += "Open "+str(hd+1)+","
    for hd in range(portf.HD):
        headers += "D"+str(hd+1)+" MKV,"
    for hd in range(portf.HD):
        headers += "D"+str(hd+1)+" P/L,"
    for hd in range(portf.HD):
        headers += "D"+str(hd+1)+" Ret,"    

    headers += "Total P/L,Total return,Total return (com),L Weight,S Weight,Alpha,L W Beta,S W Beta,W Alpha"
    of.write(headers+"\n")
    
    v_headers = headers.split(",")[2:]
    
    for p_date in portf_dates:
        for stk in  portf.holdings[p_date].keys():  
            ln = stk+","+p_date.strftime("%d/%m/%Y")+","
            for heading in v_headers:
                ln+= str(portf.holdings[p_date][stk]["Eval"][heading])+","
            of.write(ln+"\n")

    of.close()
    
    

def get_open_close_beta_sector_poolInd_fromDBdump(fn):   
    print "\nreading",fn
    DF = {}
    sheets = pd.ExcelFile(fn).sheet_names
    #print sheets
    
    for sheet in sheets:
        df = pd.DataFrame()
        df = pd.ExcelFile(fn).parse(sheet,index_col=0,parse_dates=True)
        df = re_index(df)
        DF[sheet] = df
    
    for key in DF.keys():
        for stk in DF['Beta'].columns:
            DF['Beta'][stk] = DF['Beta'][stk].fillna(method='ffill')
            DF['Beta'][stk] = DF['Beta'][stk].fillna(method='bfill')
            #print stk, DF['Beta'][stk].values[0:10]    
   
    DF["SP500"] = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index) #["SPY US Equity"].index
    DF["SP500 E.W."] = pd.Series([0.0 for x in DF["Open"].index],index= DF["Open"].index) #["RSP US Equity"]
    
    for d in range(1,len(DF["Open"].index)):
        DF["SP500"].iloc[d] = DF["Open"]["SPY US Equity"].iloc[d]/DF["Open"]["SPY US Equity"].iloc[d-1] - 1.0
        DF["SP500 E.W."].iloc[d] = DF["Open"]["RSP US Equity"].iloc[d]/DF["Open"]["RSP US Equity"].iloc[d-1] - 1.0
        
        
    print "SP500", DF["SP500"].values[0:10]
    print "SP500 E.W.", DF["SP500 E.W."].values[0:10]
    
    return DF
    
    
def get_stock_sector_info(fn,STOCKS):   
    """eventually needs to be reworked to get this from the DB of individual files for each stock"""    
    if os.access(fn,os.R_OK):
        for line in open(fn,'r').readlines(): 
            stk = line.split(",")[0].strip()
            if stk != "":
                stock = CLASSdef.STOCK(stk)
                if stk not in STOCKS.keys():                   
                    STOCKS[stk] = stock
                stock = STOCKS[stk]
                stock.GICS = line.split(",")[1].strip()
                stock.sector = line.split(",")[2].strip("\n").strip()
                    


#### Auxiliary #####################################################################################

    
def get_DB_dates(DF):
    DF_dates = []
    for date in DF["Close"].index:
        DF_dates.append(date.date())
    return DF_dates    

    
def str2float(txt):
    txt.strip() #'\"').strip("\'")
    try:
        return float(txt)
    except:
        return None                  

            
def re_index(df):
    t = []
    for date in  df.index:
        t.append(date.date())
    df.reindex(index = t, columns = df.columns )
    return df

#### temp #####################################################################################
#### temp #####################################################################################
#### temp #####################################################################################  

                


    
                    
#df["position"] = pd.Series([0 for x in df.index],index= df.index)
#df = pd.DataFrame(10*randn(7,4),index=date_range(d1,days),columns=["A","B","C","D"]) 

#################################################################################
### portfolio functions
#################################################################################


