# -*- coding: utf-8 -*-
"""
Created on Tue Oct 01 17:11:05 2013

@author: olenag
"""
import os
import sys
import datetime
sys.path.append(os.path.normpath(os.path.join(sys.path[0],'..\..\Prj04_DailyProtfolioPickingExercise\code\\'))) 
import functions

if __name__=="__main__":

    #DATA_DIR = "\\\\neptune\TradingRoom\RESEARCH\Allan\PerDay\withMoreStats\CorrectedDDnKRatio\\" 
    #DATA_DIR = "..\data\\"
    DATA_DIR = "\\\\neptune\TradingRoom\RESEARCH\OlenaG\PortfolioPicking\BandSize3\\"     
    BandSize = "Bs3"
    
    key_HD = ["1HD","2HD","3HD","4HD","5HD"]        
    key_Stat = ["Relative RPT (BPS)","Relative Signed Win Rate (%)","Number Trades","Stock Return (BPS)",
    "Max Drawdown (%)","Relative Sharpe","Relative KRatio"]
    key_Window = ["2 Year","1 Year","6 Month","3 Month","2 Month","1 Month"]
    
    F2Scores = ["F2(8)","F2(16)"]
    decision_date = datetime.datetime(2012,8,29).date() #datetime.datetime(2012,8,29).date()
    date_start = decision_date
    date_end = datetime.datetime(2013,9,18).date() #datetime.datetime(2013,9,18).date()

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
        
  