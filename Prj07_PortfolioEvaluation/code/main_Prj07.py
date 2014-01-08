# -*- coding: utf-8 -*-
"""
Created on Sat Oct 05 11:51:54 2013

@author: Olena
PURPOSE: This program was created as a shell to be able to evaluate portfolios. 
        (Mainly based on the porfolio picking exercise which made me want to understand how porfolios get evaluated and assessed.)
        
The shell of the main must be modified depending on the type of data that is given. 
But later on the functions. 

a HOLDING is a class which I express in terms of a dictionary 
    (b/c it's easier to find the attributes and it becomes more versitile)

class HOLDING:
        self.start_date
        self.end_date 
        self.ticker_name 
        self.position_type 'L' or 'S' 
        self.holding_days = [] #holding days, based on the market where the stock comes from

"""
import os
import sys

import functions_Prj07


sys.path.append(os.path.normpath(os.path.join(sys.path[0],".."+os.sep+".."+os.sep+'common_py'+os.sep))) 
import PORTFOLIO_UTILS
import UTILITIES
import PLOT

DATA_DIR = ".."+os.sep+"data"+os.sep
OUT_DIR = ".."+os.sep+"outputs"


if __name__ == "__main__":
    print "portfolio evaluation program"
    out_dir = UTILITIES.make_output_dir(OUT_DIR)
    fn = DATA_DIR+ "Portfolio.csv"    
    Holdings = functions_Prj07.read_portfolio_holdings_v1_USdate(fn)
    #Holdings = functions_Prj07.initialize_additional_attributes_of_holding(Holdings)
    Holdings = functions_Prj07.clean_US_tickerNames(Holdings,DATA_DIR+"ticker_names_SP500.csv")
    
    Xrate_DF = PORTFOLIO_UTILS.make_Xrate_DF(DATA_DIR+"Xrate.csv")
    Xrate_DF = PORTFOLIO_UTILS.fill_NANs_in_Xrate(Xrate_DF)
    TickerSuffix_Currency = PORTFOLIO_UTILS.read_market_tickers(DATA_DIR+ "MarketCurrencies.csv")
    Holdings = PORTFOLIO_UTILS.attach_currency_to_ticker(Holdings,TickerSuffix_Currency)
        
    #have daily prices and other stuff DataFrame
    sheet_names = ["Open","Close","SectorInfo","BarraBeta","SMA6MBeta"]
    WORLD600_DF = PORTFOLIO_UTILS.make_dailyData_DataFrame(DATA_DIR,"WORLD600_woXrate_",sheet_names)
    SP500_DF = PORTFOLIO_UTILS.make_dailyData_DataFrame(DATA_DIR,"SP500_",sheet_names)    
    WORLD600_DF = PORTFOLIO_UTILS.fill_Betas(WORLD600_DF,["BarraBeta","SMA6MBeta"])
    SP500_DF = PORTFOLIO_UTILS.fill_Betas(SP500_DF,["BarraBeta","SMA6MBeta"])
    
    
    WORLDa_DF={}
    WORLDa_DF["Close"] = functions_Prj07.sortout_special_prices(DATA_DIR+"SET01_Close.csv")
    WORLDa_DF["Open"] = functions_Prj07.sortout_special_prices(DATA_DIR+"SET01_Open.csv")
    WORLDa_DF["BarraBeta"] = functions_Prj07.sortout_special_prices(DATA_DIR+"SET01_BarraBeta.csv")
    WORLDa_DF = PORTFOLIO_UTILS.fill_Betas(WORLDa_DF,["BarraBeta"])
    
    #make one Beta and then you can refer to it as "Beta"
    SP500_DF = PORTFOLIO_UTILS.make_oneBeta(SP500_DF,"BarraBeta","SMA6MBeta",proper_solution = True)
    WORLD600_DF = PORTFOLIO_UTILS.make_oneBeta(WORLD600_DF,"BarraBeta","SMA6MBeta",proper_solution = True)
    WORLDa_DF = PORTFOLIO_UTILS.make_oneBeta(WORLDa_DF,"BarraBeta","BarraBeta",proper_solution = True)

    #now fill in important attributes of each holding
    Holdings = PORTFOLIO_UTILS.clean_ticker_names(Holdings,SP500_DF)    
    Holdings = PORTFOLIO_UTILS.clean_ticker_names(Holdings,WORLD600_DF)
    Holdings = PORTFOLIO_UTILS.clean_ticker_names(Holdings,WORLDa_DF)


    Holdings = PORTFOLIO_UTILS.populate_holdingDays_for_each_holding(Holdings,SP500_DF,dfname="SP500_DF")
    Holdings = PORTFOLIO_UTILS.populate_holdingDays_for_each_holding(Holdings,WORLD600_DF,dfname="WORLD600_DF")
    Holdings = PORTFOLIO_UTILS.populate_holdingDays_for_each_holding(Holdings,WORLDa_DF,dfname="WORLDa_DF")

    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,SP500_DF,dailyData='Open',dfname="SP500_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLD600_DF,dailyData='Open',dfname="WORLD600_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLDa_DF,dailyData='Open',dfname="WORLDa_DF")
    Holdings = PORTFOLIO_UTILS.fill_missing_prices(Holdings,"daily_Open")
    
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,SP500_DF,dailyData='Close',dfname="SP500_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLD600_DF,dailyData='Close',dfname="WORLD600_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLDa_DF,dailyData='Close',dfname="WORLDa_DF")
    Holdings = PORTFOLIO_UTILS.fill_missing_prices(Holdings,"daily_Close")
    
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,SP500_DF,dailyData='Beta',dfname="SP500_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLD600_DF,dailyData='Beta',dfname="WORLD600_DF")
    Holdings = PORTFOLIO_UTILS.populate_dailyData_for_each_holding(Holdings,WORLDa_DF,dailyData='Beta',dfname="WORLDa_DF")

    
    #determining Trading Days based on the porfolio holdings
    TradingDays = []
    TradingDays = functions_Prj07.set_trading_dates(TradingDays,WORLD600_DF)
    TradingDays = functions_Prj07.set_trading_dates(TradingDays,WORLDa_DF)
    TradingDays = functions_Prj07.define_portfolio_dates(TradingDays,Holdings)
    print 'number of dates', len(TradingDays) , TradingDays[0:4],TradingDays[-1] 

    #  make benchmark
    BenchMarkIndex = {}
    BenchMarkIndex["US"] = PORTFOLIO_UTILS.define_benchmark_index(SP500_DF,market="US",name="SP500")
    #t_WORLD600_DF is made only for the BenchMark of the world; it's important that it's already converted to one currency
    t_WORLD600_DF = PORTFOLIO_UTILS.make_dailyData_DataFrame(DATA_DIR,"WORLD600_",["Open","Close"])
    BenchMarkIndex["WORLD"] = functions_Prj07.define_WORLDbenchmark_index(t_WORLD600_DF,Xrate_DF,TickerSuffix_Currency,market="WORLD",name="PHG_WORLD600",needs_Xrate_conversion=False)
    BenchMarkIndex["0"] = PORTFOLIO_UTILS.define_0_benchmark(TradingDays) #must have TradingDays correct before this function call
    
    for hold in Holdings:
        hold = PORTFOLIO_UTILS.evaluate_holding(hold,BenchMarkIndex)
    for hold in Holdings: 
        #if currency conversion is necessary it must be done after PnL has been calculated
        hold = PORTFOLIO_UTILS.currency_conversion(hold,Xrate_DF)

    functions_Prj07.write2file_4debugging(Holdings,BenchMarkIndex)#for debugging only
     
    Portf_Close_daily_MKV_inUSD = {}
    for date in TradingDays:
        Portf_Close_daily_MKV_inUSD[date] = PORTFOLIO_UTILS.calculate_portfolio_value_on_a_day(date,Holdings,"Close_daily_MKV_inUSD")
            
    for hold in Holdings:
        hold = PORTFOLIO_UTILS.calculate_holdings_daily_weight_in_portfolio(Portf_Close_daily_MKV_inUSD,hold,TradingDays)


    DailyStats = {}
    DailyStats["Absolute Return"] = PORTFOLIO_UTILS.DailyStats_eval_return(Holdings,TradingDays,attr="daily_Ret")
    PORTFOLIO_UTILS.make_CumStats(DailyStats["Absolute Return"])
    UTILITIES.dump_data(DailyStats["Absolute Return"],stock_name="AbsRet",t_fn="t_AbsRet.csv")
    PLOT.mutliple_TimeSeries_on_ONEplot(DailyStats["Absolute Return"],
                                    ["Cum Long %","Cum Short %","Cum L+S %"],
                                    stock_name="Portfolio",Yaxis='',
                                    suptitle ="Portfolio Return",
                                    fig_fn= out_dir+"Portfolio_Abs_Ret.jpg",
                                    date1=TradingDays[0], date2=TradingDays[-1])
                                    
    DailyStats["Relative Return"] = PORTFOLIO_UTILS.DailyStats_eval_return(Holdings,TradingDays,attr="daily_RelRet")
    PORTFOLIO_UTILS.make_CumStats(DailyStats["Relative Return"])
    UTILITIES.dump_data(DailyStats["Relative Return"],stock_name="RelRet",t_fn="t_RelRet.csv")
    PLOT.mutliple_TimeSeries_on_ONEplot(DailyStats["Relative Return"],
                                    ["Cum Long %","Cum Short %","Cum L+S %"],
                                    stock_name="Portfolio",Yaxis='',
                                    suptitle ="Portfolio RelRet",
                                    fig_fn= out_dir+"Portfolio_RelRet.jpg",
                                    date1=TradingDays[0], date2=TradingDays[-1])
                                    
    DailyStats["Alpha"] = PORTFOLIO_UTILS.DailyStats_eval_return(Holdings,TradingDays,attr="daily_Alpha")
    PORTFOLIO_UTILS.make_CumStats(DailyStats["Alpha"])
    UTILITIES.dump_data(DailyStats["Alpha"],stock_name="RelRet",t_fn="t_Alpha.csv") 
    PLOT.mutliple_TimeSeries_on_ONEplot(DailyStats["Alpha"],
                                    ["Cum Long %","Cum Short %","Cum L+S %"],
                                    stock_name="Portfolio",Yaxis='',
                                    suptitle ="Portfolio Alpha",
                                    fig_fn= out_dir+"Portfolio_Alpha.jpg",
                                    date1=TradingDays[0], date2=TradingDays[-1])
    
    
    #to do
    """
   
    1) each stock should have currency/market it's from, or for different dates, there should be different banchMarks, depending on which market is opened


    4) make a general Beta
    
    """
