# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:01:10 2013

@author: olenag
"""

import os
import functions
import datetime

import PORTFOLIO_functions
import CLASSdef



if __name__=="__main__":

    #DATA_DIR = "\\\\neptune\TradingRoom\RESEARCH\Allan\PerDay\withMoreStats\CorrectedDDnKRatio\\" 
    #DATA_DIR = "..\data\\"
    DATA_DIR = "\\\\neptune\TradingRoom\RESEARCH\OlenaG\PortfolioPicking\BandSize3\\"     
    BandSize = "Bs3"

    Long_TH = {"F2(8)":-2.5,"F2(12)":-3.0,"F2(16)":-3.0}
    Short_TH = {"F2(8)":3,"F2(12)":3,"F2(16)":3}
    
    key_HD = ["1HD","2HD","3HD","4HD","5HD"]    
    MHD1_Weights = {"1HD":1.0,"2HD":0.0,"3HD":0.0,"4HD":0.0,"5HD":0.0} #{"1HD":2,"2HD":1,"3HD":0,"4HD":0,"5HD":0}
    MHD2_Weights = {"1HD":0.0,"2HD":1.0,"3HD":0.0,"4HD":0.0,"5HD":0.0} #{"1HD":2,"2HD":3,"3HD":1,"4HD":0,"5HD":0}
    MHD3_Weights = {"1HD":0.0,"2HD":0.0,"3HD":1.0,"4HD":0.0,"5HD":0.0}
    
    key_Stat = ["Relative RPT (BPS)","Relative Signed Win Rate (%)","Number Trades","Stock Return (BPS)",
    "Max Drawdown (%)","Relative Sharpe","Relative KRatio"]

    key_Window = ["2 Year","1 Year","6 Month","3 Month","2 Month","1 Month"]

    #LBWindow_Weights = {"2 Year":0,"1 Year":0.0,"6 Month":1.0,"3 Month":2.0,"2 Month":0.0,"1 Month":2.5}
    LBWindow_Weights = {"2 Year":0,"1 Year":0.0,"6 Month":1.0,"3 Month":1.0,"2 Month":1.0,"1 Month":1.0} #this one is for weighing stats that are not number of trades
    NumTradesWeights = {"2 Year":0.0,"1 Year":0.0,"6 Month":1.0,"3 Month":1.1,"2 Month":1.3,"1 Month":1.5}    

    portf_value = 30000000
    capital_per_stock = 1000000
    investment_mode ="Fixed Cap/Stock"

    log = open("log.txt","w")
    F2Scores = ["F2(8)","F2(16)"]
    Strategies = ["Base"]#"byF2Ret"]#"byF2Ranks"]#"Base"]
    for strategy in Strategies:
        if strategy == "byRanks":
            LBWindow_Weights = {"2 Year":0,"1 Year":0.0,"6 Month":0.0,"3 Month":0.0,"2 Month":0.0,"1 Month":0.0} #NOT USED
            NumTradesWeights = {"2 Year":0,"1 Year":0.0,"6 Month":1.0,"3 Month":1.0,"2 Month":1.0,"1 Month":1.0}
        elif strategy == "byF2Ranks":
            LBWindow_Weights = {"2 Year":0,"1 Year":0.0,"6 Month":0.0,"3 Month":0.0,"2 Month":0.0,"1 Month":0.0} #NOT USED
            NumTradesWeights = {"2 Year":0,"1 Year":0.0,"6 Month":1.0,"3 Month":1.0,"2 Month":1.0,"1 Month":1.0}
        elif strategy == "byF2Ret":
            LBWindow_Weights = {"2 Year":0,"1 Year":0.0,"6 Month":0.0,"3 Month":0.0,"2 Month":0.0,"1 Month":0.0} #NOT USED
            NumTradesWeights = {"2 Year":0,"1 Year":0.0,"6 Month":1.0,"3 Month":1.0,"2 Month":1.0,"1 Month":1.0}
            
            
        HD_loop = {"MHD2":MHD2_Weights,} #"MHD3":MHD3_Weights
        for HD in HD_loop.keys():
            MHD = HD
            MHD_Weights = HD_loop[HD]
            print "\n",strategy, MHD
            decision_date = datetime.datetime(2012,8,29).date() #datetime.datetime(2012,8,29).date()
            date_start = decision_date
            date_end = datetime.datetime(2013,9,18).date() #datetime.datetime(2013,9,18).date()
        
            hd = int(MHD.replace("MHD",""))
            portf = CLASSdef.PORTFOLIO(strategy,hd, portf_value,capital_per_stock,investment_mode) #make sure hd is an integer
            while decision_date <= date_end :
                sDate = decision_date.strftime("%Y%m%d")
            
                DATA = {}
            
                data_for_date_not_found = False
                for fscore in F2Scores:
                    fn = DATA_DIR+"ExtraStats_"+fscore+"_Band_MultiHold_"+sDate+".csv"
                    if os.access(fn,os.R_OK):
                        functions.read_data(fn,DATA,fscore,key_HD,key_Stat,key_Window)
                    else:
                        data_for_date_not_found = True
               
                if not data_for_date_not_found:    
                    stock_names = sorted(DATA.keys())
                    #functions.debug_output(DATA,key_HD,key_Stat,key_Window,F2Scores,date=decision_date,fname=MHD)
                
                    CALC_Stats = {}
                                 
                    namesOfWeightedAvgs =functions.calculate_WeightedAvgs(DATA,LBWindow_Weights,MHD_Weights,F2Scores,key_HD,key_Stat,key_Window,CALC_Stats,NumTradesWeights)
                    Ranks = functions.rank_byAll_Stats(DATA,F2Scores,CALC_Stats,namesOfWeightedAvgs)
                    #functions.debug_output(DATA,key_HD,key_Stat,key_Window,F2Scores,CALC_Stats=CALC_Stats,namesOfWeightedAvgs=namesOfWeightedAvgs,Ranks=Ranks,date=decision_date,fname=MHD)    
                    
                    Decisions = {}
                    #initialize Decisions            
                    for stk in DATA.keys():
                        if stk not in Decisions.keys():
                            #if stk == "TEL UN Equity": print>> log,"Main:",stk,decision_date
                            Decisions[stk] = {}
                            Decisions[stk]["Decision"] = ""
                            for fscore in F2Scores:
                                Decisions[stk][fscore] = "" 
        
                    if strategy == "byRanks":
                        functions.choose_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions)
                        functions.choose_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions)
                    elif strategy == "byF2Ranks":
                        functions.choose_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions)
                        functions.choose_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions)
                    elif strategy == "byF2Ret":
                        functions.choose_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions)
                        functions.choose_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions)
                    elif strategy == "Base":
                        functions.choose_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions)
                        functions.choose_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions)
                        
                    
                    #functions.debug_output(DATA,key_HD,key_Stat,key_Window,F2Scores,CALC_Stats=CALC_Stats,namesOfWeightedAvgs=namesOfWeightedAvgs,Ranks=Ranks,Decisions=Decisions,date=decision_date,fname=strategy+"_"+MHD)   
                    print decision_date            
                    functions.make_final_LongDecisions(DATA,F2Scores,Decisions,num_THs_met = 1,logfn=log) 
                    functions.make_final_ShortDecisions(DATA,F2Scores,Decisions,num_THs_met = 1,logfn=log)
                    PORTFOLIO_functions.add_to_portfolio(portf,decision_date,DATA,F2Scores,Decisions)
                    fn = BandSize+"_"+strategy+"_"+MHD+"_"+ sDate+".csv"
                    functions.write_2file_finalDecisions(DATA,Decisions,fn,decision_date,F2Scores,logfn =log) 
                    print
                    
                decision_date += datetime.timedelta(days=1)
               
            functions.concatinate_files(BandSize+"_"+strategy+"_"+MHD,date_start,date_end)
            PORTFOLIO_functions.examine_portfolio_performance(portf,F2Scores,date_start,date_end)
            log.close()
                    