# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 17:02:52 2013

@author: olenag
"""

import os
import sys
import math
import pandas as pd
import datetime

sys.path.append(os.path.normpath(os.path.join(sys.path[0],'..\..\common_py\\'))) 
import STRATEGIES
import UTILITIES


DAYS = [20]#10,20,40,100,200]
############################################################
## DATA READING functions
############################################################




############################################################
### transformation ----- one of the most important functions, as it precalculates what can be used later for strategies
############################################################    
def transform_DF(df,F2scores,stock_name="",Quantiles=None):
    
    #MUST HAVE 
    df["ooRelRet(nextDay)"] = df["ooRelRet"].shift(-1) #for return calculation
    df["ooRawRet(nextDay)"] = df["ooRawRet"].shift(-1)   

    if 'barraBeta' in df.columns:
        df['barraBeta'] = df['barraBeta'].fillna(method='ffill')
        df['barraBeta'] = df['barraBeta'].fillna(method='bfill')
    else:
        print 'barraBeta not available in this set'  

    for f2score in F2scores:
        df[f2score][df[f2score] <-15] = -15
        df[f2score][df[f2score] > 15] = 15 
        df[f2score+"_Scaled"] = df[f2score]*0.01 #for graphing purposes only to combine it on the same graph with RelRet
        
        #I tried rolling quantiles of 220Days, but they were ending up with F2 of 2.2 as a shorting signal. 
        #I think 2years at least should be used.
        df[f2score+"Qlower"] = pd.rolling_quantile(df[f2score],window=400,quantile=0.095)
        df[f2score+"Qupper"] = pd.rolling_quantile(df[f2score],window=400,quantile=0.905)
        df[f2score+"Qlower"] = df[f2score+"Qlower"].fillna(method='bfill')
        df[f2score+"Qupper"] = df[f2score+"Qupper"].fillna(method='bfill')
 
    """some stats that are necessary for graphing and stat analysis"""
    
    for var in ['ooRelRet','ccRelRet',]:  #'ooRawRet'
        df[var+"(Cum)"] = df[var].cumsum()
        for days in [1,2,3,5,8,10,20]:       
            df[var+"("+str(days)+"D avg)"] = pd.rolling_mean(df[var],days)
            df[var+"(next"+str(days)+"D avg)"] = pd.rolling_mean(df[var],days).shift(-(days+1))#negative shift allows to look into the future, used for graphs, but not for trading.           
            df[var+"("+str(days)+"D sum)"] = pd.rolling_sum(df[var],days)

    for days in [3,10]:  #this vector must be a subset of the vector above
        var = "ooRelRet"
        df[var+"("+str(days)+"D UWM)"] = pd.rolling_mean(df["ooRelRet("+str(days)+"D avg)"],10)

    for var in ['ccRelRet','ooPoolRet','ccPoolRet']: #'ooRawRet' 
        for days in [5,8,10,15,20]:       
            df["avg"] = pd.rolling_mean(df[var],days)
            df["std"] = pd.rolling_std(df[var],days)
            df[var+"_E("+str(days)+"D)"] = df['avg']/df['std']
    df = df.drop(["avg","std"],axis = 1)
    
    #UTILITIES.dump_data(df,stock_name,t_fn="t_"+stock_name+"_transformed.csv")    
            
    return df    



##############################################################
## prep data for graph drawing
##############################################################



#########################################
# Position files related stuff
##########################################

def replace_headers(fn,old_string,new_string):   
    with open(fn,'r') as f:
        newlines = []
        for line in f.readlines():
            newlines.append(line.replace(old_string,new_string))
            
    with open(fn, 'w') as f:
        for line in newlines:
            f.write(line)
    
def make_positions_file4stock(fn,stock_name,Investments,strategy):
    for inv in Investments:
        if inv.strategy_name == strategy and stock_name == inv.stock_name:
            inv.df['position'].to_csv(fn,sep=',',header=True)    

    replace_headers(fn,"t()","")    
    replace_headers(fn,"position",stock_name+ " Equity")  

def generate_positions_file(StockNames,INV,strategy=None,out_dir=""):
    """generate files to be read by PHG report creator"""    
    time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M") 
    if strategy != None:       
        fn = out_dir+strategy+"_"+time_stamp+".csv"
        make_positions_file(fn,StockNames,INV,strategy)
        for stock_name in StockNames:
            fn = out_dir+strategy+"_"+stock_name+".csv"
            #make_positions_file4stock(fn,stock_name,INV,strategy)        

def make_positions_file(fn,StockNames,Investments,strategy):
    of = open(fn,'w')
    s = ","
    for stockN in StockNames:
        s+= stockN + " Equity" +","
    of.write(s+"\n")
    
    for indx in Investments[0].df.index:
        s = indx.strftime("%d/%m/%Y") +","
        for stock_name in StockNames:
            for inv in Investments:
                if inv.strategy_name == strategy and stock_name == inv.stock_name:
                    s += str(inv.df['position'].loc[indx]) +","
        of.write(s+"\n")
    of.close()
                    
#########################################
# summary files, data output
##########################################
def get_strategies(Investments):
    strategies = []
    for inv in Investments:
        if inv.strategy_name not in strategies:
            strategies.append(inv.strategy_name)
    return strategies
        
    
def write_earnings_summary_2CSV(fn,StockNames,Investments):
    of = open(fn,"w")
    strategies = get_strategies(Investments)
    
    for stock_name in StockNames:
        s =stock_name+","
        for strategy in strategies:
            s+= strategy+","
        of.write(s+"\n")        
        lRR = "Long % RelRet,"
        sRR = "Short % RelRet,"
        RR = "L+S % RelRet,"
        lbps = "Long bps/day,"
        sbps = "Short bps/day,"
        s1 = "L+S bps/day,"
        s2 = "Days in market,"
        s3 = "Long Trades,"
        s4 = "Short Trades,"
        for strategy in strategies:
            for inv in Investments:
                if inv.stock_name == stock_name and inv.strategy_name == strategy:  
                    RR += str(round(inv.df['position_return'].sum()*100,2))+","
                    lRR += str(round(inv.df['position_return_long'].sum()*100,2))+","
                    sRR += str(round(inv.df['position_return_short'].sum()*100,2))+","
                    lbps += str(round(10000*inv.df['position_return_long'].sum()/float(max(STRATEGIES.days_in_market(inv,'long'),1)),1)) + ","
                    sbps += str(round(10000*inv.df['position_return_short'].sum()/float(max(STRATEGIES.days_in_market(inv,'short'),1)),1)) + ","                    
                    
#                    RR += str(round(inv.TTLreturn*100,2))+","
#                    lRR += str(round(STRATEGIES.calculate_positionType_return(inv,"long")*100,2))+","
#                    sRR += str(round(STRATEGIES.calculate_positionType_return(inv,"short")*100,2))+","
#                    lbps += str(round(10000*STRATEGIES.calculate_positionType_return(inv,"long")/float(max(STRATEGIES.days_in_market(inv,'long'),1)),1)) + ","
#                    sbps += str(round(10000*STRATEGIES.calculate_positionType_return(inv,"short")/float(max(STRATEGIES.days_in_market(inv,'short'),1)),1)) + ","                    
                    s1 += str(round(10000*inv.df['position_return'].sum()/float(max(STRATEGIES.days_in_market(inv),1)),1)) + ","
                    s2 += str(STRATEGIES.days_in_market(inv)) +","
                    s3 += str(STRATEGIES.number_trades(inv,trade="long")) +","
                    s4 += str(STRATEGIES.number_trades(inv,trade="short")) +","
        of.write(RR+"\n"+lRR+"\n" +sRR+"\n"+lbps+"\n"+sbps+"\n"+s1+"\n"+s2+"\n"+s3+"\n"+s4+"\n")

    s ="Portfolio,"
    for strategy in strategies:
        s+= strategy+","
    of.write(s+"\n")        
    sRR = "L+S % RelRet,"
    s3 = "Long Trades,"
    s4 = "Short Trades,"
    for strategy in strategies:
        ttl_RelRet = 0
        ttl_bps = 0
        ttl_short_trades = 0
        ttl_long_trades = 0
        elem = 0
        ttl_days_in_market = 0
        for inv in Investments:
            if inv.strategy_name == strategy:
                ttl_RelRet += inv.TTLreturn*100
                ttl_bps += 10000.0*inv.TTLreturn
                elem += 1
                ttl_short_trades += STRATEGIES.number_trades(inv,trade="short")
                ttl_long_trades += STRATEGIES.number_trades(inv,trade="long")
                ttl_days_in_market += STRATEGIES.days_in_market(inv)
                
        sRR += str(round(ttl_RelRet,2))+","
        s3 += str(ttl_long_trades) +","
        s4 += str(ttl_short_trades) +","
    of.write(sRR+"\n" +s3+"\n"+s4+"\n")

    of.close()
    
#########################################
# temporary functions, no longer in use but kept for right now just in case
##########################################         
