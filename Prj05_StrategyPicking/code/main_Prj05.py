# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 15:33:39 2013

@author: olenag
"""

import os
import sys
import datetime
import pandas as pd

import DATA_structures
import functions_Prj05

sys.path.append(os.path.normpath(os.path.join(sys.path[0],'..\..\common_py\\'))) 
import UTILITIES
import PLOT
import STRATEGIES

#DATA_DIR = "/Users/olena/Work_and_Research/PHRA/Projects/Prj05_StrategyPicking/data/" 
#OUT_DIR = "/Users/olena/Work_and_Research/PHRA/Projects/Prj05_StrategyPicking/outputs" 
DATA_DIR = "..\data\\"
OUT_DIR = "..\outputs"
    
def sortout_dates(start_date,time_period_inYears,end_date = None):
    print start_date  
    TimePeriods = UTILITIES.form_date_segments(start_date,time_period_inYears,end_date = end_date)   
    return TimePeriods

def pick_F2based_Strategy(investment,invs,strategy_name=None):
    print "EVER here"
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    if strategy_name == None:
        strategy_name = "BestF2based"
    investment.strategy_name = strategy_name
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name
    
    trial_days = 60
    for i in range(trial_days+1,len(investment.df["position"].index)-1,trial_days):#need range(1,x) becasue used index i-1 
        print i,
        strategy_to_apply = "B&H" #some default 
        score2apply = None
        max_RelRet = -1000
        for inv in invs:
            inv_return =  inv.df['position_return'][i-trial_days-1:i-1].sum()
            print "earnings:",inv.strategy_name,inv_return,
            if inv_return > max_RelRet:
                max_RelRet = inv_return
                strategy_to_apply = inv.strategy_name
                score2apply = inv.fscore2apply
        print "BEST:",strategy_to_apply
                
        p_inv = DATA_structures.INVESTMENT(investment.stock_name,investment.df[i:i+trial_days])
        p_inv.df = p_inv.df.drop(["position","trade_profit"],axis=1)

        if strategy_to_apply == "B&H":
            #print "applying", strategy_to_apply,
            STRATEGIES.strategy_BUY_n_HOLD(p_inv)
        elif strategy_to_apply == "Short&Hold":
            #print "applying", strategy_to_apply,
            STRATEGIES.strategy_SHORT_n_HOLD(p_inv)
        elif strategy_to_apply == "BASE+3_3HD":
#            print "applying", strategy_to_apply,
            MHD = 3
            STRATEGIES.strategy_BASE_MHD(p_inv,strategy_name = "BASE+3_"+str(MHD)+"HD",score=score2apply,longIn=-3,shortIn=3,MHD=MHD)
        elif strategy_to_apply == "BASE+3_2HD":
#            print "applying", strategy_to_apply,
            MHD = 2
            STRATEGIES.strategy_BASE_MHD(p_inv,strategy_name = "BASE+3_"+str(MHD)+"HD",score=score2apply,longIn=-3,shortIn=3,MHD=MHD)   
        elif strategy_to_apply == "TITO":
#            print "applying", strategy_to_apply,
            STRATEGIES.strategy_TITO(p_inv,score=score2apply,shortIn=3,shortOut=-3,longIn=-3,longOut=3)
        elif strategy_to_apply == "BASEio+3_3HD":
#            print "applying", strategy_to_apply,
            MHD = 3
            STRATEGIES.strategy_BASEio_MHD(p_inv,strategy_name = "BASEio+3_"+str(MHD)+"HD",score=score2apply,longIn=-3,shortIn=3,MHD =MHD)
        else:
            print "\n!!! CAUTION: no strategy specified"
        #print p_inv.df["position"][0:-1],"len = ",len(p_inv.df["position"][0:])
        investment.df["position"][i:i+trial_days] = p_inv.df["position"][0:]
        
        
            
    STRATEGIES.calculate_investment_return(investment)
    STRATEGIES.determine_individual_trades(investment) 
    print investment.strategy_name
    return strategy_name
 
if __name__=="__main__":
    print "using data directory:", DATA_DIR
    
    ################# INPUTS  ####################
    StockNames = ["A UN"]#'BDX UN']#,'ABC UN','BRCM UW','CAG UN','CL UN','DGX UN','ESRX UW','EMR UN','FLR UN','HSY UN','KR UN','LUV UN','MRO UN','MS UN','PPL UN','RHI UN','SIAL UW','SPLS UW','TGT UN','ZMH UN','JPM UN','WFC UN']

#    StockNames = [] #LEAVE EMPTY if all from DATA_DIR should be used
#    if StockNames == []: StockNames = UTILITIES.get_stock_names_inIndex_from_aFile_v1(DATA_DIR+"ticker_names_SP500.csv")
    print StockNames
    
    F2scores = ["F2(8,20)"] #,"F2(16,40)" "F2(8,20)"

    """Recommendation: in order to allow for a warm up, do not use anything before 1/1/2001"""    
    starting_date = datetime.datetime(2002,1,1).date()
    time_period_inYears = 1.0025 #1.01 # can be 1.33 if you like; use 0.0 for the one period
    end_date = datetime.datetime(2014,1,1).date()
    
    TimePeriods = sortout_dates(starting_date,time_period_inYears,end_date)
    """you can choose to overwrite TimePeriods as follows:"""
    #TimePeriods = [datetime.datetime(2005,1,1),datetime.datetime(2014,1,1).date()]

    print TimePeriods
    date1 = TimePeriods[0]
    date2 = TimePeriods[-1]
    s_dates = date1.strftime('%Y%m%d')+"-"+date2.strftime('%Y%m%d')
    
    out_dir = UTILITIES.make_output_dir(OUT_DIR)

    INV = []
        
    """MAIN FUNCTIONS"""
    t_snames = []
    for stock_name in StockNames:
        df = UTILITIES.read_stock_data_from_standard1_file(stock_name,DATA_DIR)
        if not df.empty:
            """Transform data as necessary before breaking it up in time periods. """                
            df = functions_Prj05.transform_DF(df,F2scores,stock_name)
            t_snames.append(stock_name)

            #the next allows to plot F2score series together with RelRet and other vars; some vars might need to be scaled in order to accomplish this
#            for score in F2scores:
#                PLOT.mutliple_TimeSeries_on_ONEplot(df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
#                                                ["ooRelRet","ooRelRet(2D avg)",score+"_Scaled"], #,"ooRelRet(8D avg)"
#                                                stock_name=stock_name,Yaxis='',
#                                                suptitle =stock_name +": behaviour of "+score+" and ooRelRet",
#                                                fig_fn=out_dir+stock_name+"_"+score+"_vs_ooRelRet_"+s_dates+".jpg",
#                                                date1=date1,date2=date2)

            ######   STRATEGIES ##############
#            for score in F2scores:
#                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
#                                               start_date=date1,end_date=date2)
#                STRATEGIES.strategy_TITO(inv,score=score,longIn=-3,longOut=3,shortIn=3,shortOut=-3,
#                                         date1=date1,date2=date2,out_dir=out_dir)
#                INV.append(inv)
#                #functions_Prj02.plot_strategies_per_time_period(TimePeriods,inv,out_dir,score,includeSignals=False,includeTradesEarnings=True,includeTrades=False)

            for score in F2scores:
                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
                                               start_date=date1,end_date=date2)
                MHD = 3                            
                strtg_name = STRATEGIES.strategy_BASE_MHD(inv,strategy_name = "BASE+3_"+str(MHD)+"HD",score=score,
                                                          longIn=-3,shortIn=3,MHD =MHD,date1=date1,date2=date2,out_dir=out_dir)
                INV.append(inv)
#                PLOT.mutliple_TimeSeries_on_ONEplot(inv.df,["%Cumulative RelRet Long","%Cumulative RelRet Short"],
#                                                    stock_name=stock_name,Yaxis='%CumRelRet',
#                                                    suptitle =stock_name +": %Cumulative RelRet of "+strtg_name+" for L & S" ,
#                                                    fig_fn=out_dir+stock_name+"_RelRet_"+strtg_name+"_"+s_dates+".jpg",
#                                                    date1=date1,date2=date2)

            for score in F2scores:
                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
                                               start_date=date1,end_date=date2)
                MHD = 3                            
                strtg_name = STRATEGIES.strategy_BASE_MHD(inv,strategy_name = "revBASE+3_"+str(MHD)+"HD",score=score,
                                                          longIn=3,shortIn=-3,MHD =MHD,date1=date1,date2=date2,out_dir=out_dir)
                INV.append(inv)

                
#            for score in F2scores:
#                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
#                                               start_date=date1,end_date=date2)
#                MHD = 3                            
#                strtg_name = STRATEGIES.strategy_BASEio_MHD(inv,strategy_name = "BASEio+3_"+str(MHD)+"HD",score=score,
#                                                          longIn=-3,shortIn=3,MHD =MHD,date1=date1,date2=date2,out_dir=out_dir)
#                INV.append(inv)

                
            for i in range(1):  #loop needed to make inv a local variable to this loop 
                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
                                               start_date=date1,end_date=date2)
                STRATEGIES.strategy_BUY_n_HOLD(inv,date1=date1,date2=date2,out_dir=out_dir)
                INV.append(inv)

#            for i in range(1):  #loop needed to make inv a local variable to this loop 
#                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
#                                               start_date=date1,end_date=date2)
#                STRATEGIES.strategy_SHORT_n_HOLD(inv,date1=date1,date2=date2,out_dir=out_dir)
#                INV.append(inv)
#    
            invs = [] #make a local var that allows to compare strategies just for one stock
            for inv in INV:
                if inv.stock_name == stock_name:
                    invs.append(inv)
                    
#            for i in range(1):
#                inv = DATA_structures.INVESTMENT(stock_name,df[date1.strftime('%d/%m/%Y'):date2.strftime('%d/%m/%Y')],
#                                               start_date=date1,end_date=date2)
#                pick_F2based_Strategy(inv,invs)
#                INV.append(inv)
#                invs.append(inv)
                

            
            plot_title = stock_name +": Strategy Comparison L+S"
            PLOT.compare_strategies(invs,var="%Cumulative RelRet", suptitle = plot_title,
                                    fig_fn= out_dir+stock_name+"_RelRet_L+S_strt_comp_"+s_dates+".jpg", 
                                    date1=date1, date2=date2,position_type='L+S')   
            plot_title = stock_name +": Strategy Comparison Short"
            PLOT.compare_strategies(invs,var="%Cumulative RelRet Short", suptitle = plot_title,
                                    fig_fn= out_dir+stock_name+"_RelRet_Short_strt_comp_"+s_dates+".jpg", 
                                    date1=date1, date2=date2,position_type = "Short")   
            plot_title = stock_name +": Strategy Comparison Long"
            PLOT.compare_strategies(invs,var="%Cumulative RelRet Long", suptitle = plot_title,
                                    fig_fn= out_dir+stock_name+"_RelRet_Long_strt_comp_"+s_dates+".jpg", 
                                    date1=date1, date2=date2,position_type='Long')                                       
            #PLOT.compare_strategies(invs,var="%Cumulative RawRet", suptitle = plot_title, fig_fn= out_dir+stock_name+"_RawRet_strt_comp_"+s_dates+".jpg",date1=date1, date2=date2)               
    StockNames = t_snames
    
    """Finishing touches"""
    print "\n Endings"
    for stock_name in StockNames: 
        for investment in INV:
            if investment.stock_name == stock_name:
                print investment.stock_name,investment.strategy_name,round(investment.TTLreturn,4),investment.start_date,investment.end_date,investment.fscore2apply
  
    time_stamp = datetime.datetime.now().strftime("%m%d-%H%M")    
    functions_Prj05.write_earnings_summary_2CSV(out_dir+"summary_"+s_dates+"_"+time_stamp+".csv",StockNames,INV)
    strategies = functions_Prj05.get_strategies(INV)      
    for strategy in strategies:
        functions_Prj05.generate_positions_file(StockNames,INV,strategy,out_dir=out_dir)


    