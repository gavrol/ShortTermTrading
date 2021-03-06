'''
Created on 07/07/2013

@author: olena
'''
import os
import sys
import numpy as np
import pandas as pd
from class_definitions import *
import utils
import Plotting
import STAT_functions
from dateutil import parser
import datetime



def transform_df_ASneeded(df,F2scores,shift,stock_name):
    #df.replace(df['F2(8,20)'][df['F2(8,20)']<-5],-5)
    """transform curr_df here if you want running means, etc"""

    yVar = "ooRelRet(3days rolling mean)" 
    df[yVar] =pd.rolling_mean(df["ooRelRet"],3)
    shift  = -4
    df[yVar] = df[yVar].shift(shift)    
    
    df["ooRelRet(nextDay)"] = df["ooRelRet"].shift(-1)
      
    if 'barraBeta' in df.columns:
        df['barraBeta'] = df['barraBeta'].fillna(method='ffill')
        df['barraBeta'] = df['barraBeta'].fillna(method='bfill')
    else:
        print 'barraBeta not available in this set'
        
    df['corr_Prices20'] = pd.rolling_corr(df["ClosePrice"],df["EWPoolClose"],20)
    df['corr_Prices8'] = pd.rolling_corr(df["ClosePrice"],df["EWPoolClose"],8)
    df['corr_Ret'] = pd.rolling_corr(df['ooRawRet'],df['ooPoolRet'],40)

    
    newF2scores = []
    for f2score in F2scores:
        df[f2score][df[f2score] <-15] = -15
        df[f2score][df[f2score] > 15] = 15    
        
        name = f2score+'Exp'
        newF2scores.append(name)
        df[name] = df[f2score]*df['corr_Ret']
    
    xVar ='F2'    
    newF2scores = F2scores 
    print newF2scores

    #based on how you transformed df
    utils.dump_data_csv(df,stock_name,t_fn="t_"+stock_name+"_transformedDF_"+xVar+"_vs_"+yVar+".csv")
    return df,shift,xVar,yVar,newF2scores
    

def functions_to_perform_onDF(df,stock,F2scores,shift,QUANTILES,date1,date2,out_dir='',xVar="???",yVar="RelRet"):
    print "\n Performing functions on a DF subset with number of observations = ", len(df)
    print stock.name
    print yVar, "is being explored"
    print  date1.strftime('%d-%m-%y'),  date2.strftime('%d-%m-%y')
    
    STAT_functions.ols_F2vsYvar(df,stock,F2scores,yVar,QUANTILES)  
    
    """prep stuff for plotting"""
    s_dates = date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')

    fig_fn =  out_dir+ stock.name+"_"+xVar+"_vs_"+yVar + "_" +s_dates #+ "_shift("+str(abs(shift))+")"
    suptitle = xVar+" vs "+yVar #+" (with Shift_Days="+str(abs(shift))+")" #the super-title above all subplots; can be omitted
    #Plotting.ScatterSubplots_F2vsYvar(df,stock,F2scores,QUANTILES,fig_fn+".jpg",date1,date2,suptitle,yVar,ymin=-0.04,ymax=0.04)

    fig_fn = out_dir+ stock_name+"_"+yVar+"_behaviour_"+s_dates+".jpg"
    #Plotting.stacked_TimeSeries(df,stock_name,[yVar],yVar+" behaviour of "+stock_name,fig_fn,date1,date2,mean_per=8,ymin=-0.04,ymax=0.04)

    F2scores = [F2scores[0]]
    for fscore in F2scores:#F2scores if all are needed
        if fscore.find('8')> -1:
            roll_mean = 8
        else:
            roll_mean = 15
        depVar = "ooRelRet(nextDay)" #yVar
        fig_fn = out_dir+ stock.name+"_behaviour_"+fscore+"_"+depVar+"_"+yVar + "_" +s_dates+".jpg"
        suptitle = stock.name+": behaviour of "+fscore
        Plotting.overlays_TimeSeries(df,stock_name,fscore,yVar1=yVar,yVar2=depVar,suptitle=suptitle,
                                     fig_fn=fig_fn,stock = stock,date1=date1,date2=date2,Quantiles=QUANTILES,
                                     mean_per=roll_mean,ymin=-0.04,ymax=0.04,)
                           
    
    fig_fn = out_dir+ stock_name+"_"+yVar+"_Hist_"+s_dates+".jpg"
    #Plotting.stacked_histograms(df,stock_name,[yVar],stock_name,fig_fn,date1,date2)

def to_feed_anOld_habbit(DF,df,Stocks,stock_name):
    """there is a function or two written for comparison of different stocks, hence
       DF and Stocks are used there. Hence this function is filling the datastructures
       DF and Stocks just in case there is a need to use them."""
    DF.append(df)
    stock = STOCK(stock_name)
    stock.df = df
    Stocks.append(stock)

def write2file_OLSstats4F2(ofn,F2scores,Dates,Date_Stock):
        ofn = open(o_fn,'w')
        stats = ["Rsquared","OLS_alpha","alpha-pScore","OLS_beta","beta-pScore","number_of_observations","AIC","BIC"]
        ofn.write("period_start_date,period_end_date,f2score,"+",".join(stats)+"\n")
        for f2score in F2scores:
            for d in range(len(Dates)):
                date1 = Dates[d]
                if d != len(Dates)-1:
                    date2 = Dates[d+1]
                else:
                    date2 = datetime.datetime.now().date()
                s = ""
                s += date1.strftime('%d/%m/%Y')+","+date2.strftime('%d/%m/%Y')+",\""+f2score+"\","
                if date1 in Date_Stock.keys():
                    stock = Date_Stock[date1] 
                    for stat in stats:
                        s += str(stock.OLS_Statistics_F2vsRelRet[f2score][stat])+","
                    ofn.write(s+"\n")
            ofn.write("\n")
        ofn.close()    
#############################################################################
###  MAIN body ##############################################################
#############################################################################

if __name__ == '__main__':
    #hard-coded-in INPUTS    

    QUANTILES = [.1,.9]

    starting_date = "1/1/2001"
    time_period_inYears = 1.0 # can be 1.33 if you like

    shift = -1 #if filled transform_df_ASneeded
    in_dir = "\\\\neptune\olenag\Projects\Prj01_Investigation\data\\"#  "C:\\temp\\olenas_tmps\\" #olenas_tmps \\temp\\olenas_dumps\\ \\temp\\olenas_tmps\\
    out_dir = utils.make_output_dir("\\\\neptune\olenag\Projects\Prj01_Investigation\outputs")    
    
    #main data structures    
    STOCKS ={} #keys are stocknames; it contains dict-like Date_Stock
    Stock_Names = []
    DF = [] #historical; not sure I need it now
    Stocks = [] #historical, because there are functions that are written for DF and Stocks    
    
    #functions on the inputs to conform them to what they should be    
    starting_date = parser.parse(starting_date).date()
    print starting_date
    Dates = utils.form_date_segments(starting_date,time_period_inYears)
    
    """if decide to look at the entrie file, set Dates = []"""
    #Dates = []
    
    xVar, yVar = '',''
    #now get the data from datbase dumps and do what your main puporse is    
    for fn in os.listdir(in_dir):
        if os.path.isfile(in_dir+fn) and fn[0].isalpha(): 
            print "\nreading:",fn
            F2scores = ["F2(8,20)"]#,"F2(15,40)"]              
            sheets = pd.ExcelFile(in_dir+fn).sheet_names
            #print sheets
            df = pd.ExcelFile(in_dir+fn).parse(sheets[0],index_col=0,parse_dates=True)
            print "number of observations retrieved:",len(df)
            
            stock_name = fn.split(" ")[0]
            Stock_Names.append(stock_name)
            print stock_name
            to_feed_anOld_habbit(DF,df,Stocks,stock_name)
            Date_Stock = {} #keys are dates, values are stocks

            df,shift,xVar,yVar,F2scores = transform_df_ASneeded(df,F2scores,shift,stock_name)
            
            fig_fn = out_dir+ stock_name+"_behaviour.jpg"
            #Plotting.stacked_TimeSeries(df,stock_name,["ClosePrice","EWPoolClose","ccRelRet","barraBeta"],"Behaviour of "+stock_name,fig_fn)
            
            #g_xVar = 'barraBeta'            
            #fig_fn = out_dir+ stock_name+"_Prices_vs_"+g_xVar+".jpg"            
            #Plotting.stacked_ScatterPlots(df,stock_name,["ccRawRet","ccPoolRet"],g_xVar,stock_name,fig_fn)
            
            #now go thru the segments of dates
            if Dates != []:
                for d in range(len(Dates)):
                    date1 = Dates[d]
                    if d != len(Dates)-1:
                        date2 = Dates[d+1]
                    else:
                        date2 = datetime.datetime.now().date()
                    #print date1, date2
                    curr_df = df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')]
                    stock = STOCK(stock_name)
                    stock.df = curr_df
                    #utils.simple_operations_on_DataFrame(curr_df,stock)

                    """all the manipulation must be done before the stocks are put into the dict"""  
                    if len(curr_df) > 7:
                        functions_to_perform_onDF(curr_df,stock,F2scores,shift,QUANTILES,date1,date2,out_dir,xVar,yVar)
                        """now append the stock"""
                        Date_Stock.setdefault(date1,stock)
                    else:
                        print "CAUTION: there is insufficient data between",date1.strftime('%d/%m/%Y'),"and",date2.strftime('%d/%m/%Y'),"to produce any reasonable analysis"
            else: #if Date = [] --we were not splitting the time horizon in any periods
                #print df.index[0], type(df.index[0])
                date1 = df.index[0]
                Dates.append(date1)
                date2 = df.index[-1]
                stock = STOCK(stock_name)                                
                curr_df = df
                #utils.simple_operations_on_DataFrame(curr_df,stock)
                if len(curr_df) > 7:
                    functions_to_perform_onDF(curr_df,stock,F2scores,shift,QUANTILES,date1,date2,out_dir,xVar,yVar)
                    """now append the stock"""
                    Date_Stock.setdefault(date1,stock)
            STOCKS.setdefault(stock_name,Date_Stock)
    
    #now write tables of the results

    for stock_name in Stock_Names:
        Date_Stock = STOCKS[stock_name]
        o_fn = out_dir+stock_name+"_OLSstats_"+xVar+"_vs_"+yVar+"_Segm"+str(len(Dates))+".csv" #+f2score
        if stock.OLS_Statistics_F2vsRelRet != {}:
            write2file_OLSstats4F2(o_fn,F2scores,Dates,Date_Stock)
            
        
    """if comparision across all stocks are needed, use the following (but only when there are few stocks"""
    fig_fn = out_dir+ "F2_compare" #"_shift("+str(abs(shift))+").jpg"
    suptitle = xVar+" vs "+yVar# +" (with Shift_Days="+str(abs(shift))+")"          
    #Plotting.ScatterSubplots_F2vsRelRet_multipleStocks(DF,Stocks,F2scores,shift,QUANTILES,fig_fn+'.jpg',suptitle,yVar)
    #utils.dump_data_xls(DF,Stocks)
  
