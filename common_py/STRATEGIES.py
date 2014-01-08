# -*- coding: utf-8 -*-
"""
Created on Thu Aug 08 14:46:13 2013

@author: olenag
"""

import pandas as pd
import UTILITIES


""" a place to keep most common strategies"""
#### auxiliary functions ###########################
def days_in_market(inv,pos_type = None):
    t = 0.0
#    for pos in inv.df['position']:
#        t+= abs(pos)
#    return t      
    for pos in inv.df["position"]:
        if pos_type == None: #same as L+S 
            t+= abs(pos)        
        elif pos_type.lower() == 'short' and pos == -1:
            t+= abs(pos)
        elif pos_type.lower() == 'long' and pos == 1:
            t+= abs(pos)

                
    return t            
    
def accumulated(indexes,df,var,position_type):
    t_sum = 0
    for i in reversed(indexes):
        #print i
        if df['position'].loc[i] == position_type: #hence the same position type 
            t_sum += df[var].loc[i] 
        else:
            break #breaks in the first time the position_type changes
    return t_sum


def count_days(indexes,df,position_type):
    t_sum = 0
    for i in reversed(indexes):
        #print i
        if df['position'].loc[i] == position_type: #hence the same position type 
            t_sum += abs(position_type)
        else:
            break #breaks in the first time the position_type changes
    return t_sum
    
def number_trades(inv,trade="short"):
    """assumes that determine_individual_trades() was already invoked"""
    t = 0.0
    if "end_position_mark" in inv.df.columns:
        for pos in inv.df["end_position_mark"]:
            if trade.lower() == 'short' and pos == -1:
                t+= abs(pos)
            elif trade.lower() == 'long' and pos == 1:
                t += pos
    return t        

def calculate_positionType_return(inv,pos_type =None):
    t = 0.0
    if pos_type == None: #both L+S
        for indx in inv.df['position'].index:
            if abs(inv.df['position'].loc[indx]) == 1:
                t += inv.df['position_return'].loc[indx]   
    elif pos_type.lower() == 'short':
        for indx in inv.df['position'].index:
            if inv.df['position'].loc[indx] == -1:
                t += inv.df['position_return'].loc[indx]
    elif pos_type.lower() == 'long':
        for indx in inv.df['position'].index:
            if inv.df['position'].loc[indx] == 1:
                t += inv.df['position_return'].loc[indx]  
    return t            
    
    
def calculate_investment_return(investment):
    investment.df['position_return'] = investment.df['position']*investment.df['ooRelRet(nextDay)']
    investment.df['position_return_long'] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    investment.df['position_return_short'] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    investment.df['position_return_long'][investment.df['position'] == 1] = investment.df['position_return']
    investment.df['position_return_short'][investment.df['position'] == -1] = investment.df['position_return']
 
    investment.df['position_Rawreturn'] = investment.df['position']*investment.df['ooRawRet(nextDay)']       
    investment.df['position_Rawreturn_long'] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    investment.df['position_Rawreturn_short'] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    investment.df['position_Rawreturn_long'][investment.df['position'] == 1] = investment.df['position_Rawreturn']
    investment.df['position_Rawreturn_short'][investment.df['position'] == -1] = investment.df['position_Rawreturn']
    
    investment.df['position_cum_return'] = investment.df['position_return'].cumsum()
    investment.df['position_cum_return_long'] = investment.df['position_return_long'].cumsum()
    investment.df['position_cum_return_short'] = investment.df['position_return_short'].cumsum()
    
    investment.df['position_cum_Rawreturn'] = investment.df['position_Rawreturn'].cumsum()
    investment.df['position_cum_Rawreturn_long'] = investment.df['position_Rawreturn_long'].cumsum()
    investment.df['position_cum_Rawreturn_short'] = investment.df['position_Rawreturn_short'].cumsum()
    
    investment.df['%Cumulative RelRet'] =  100*investment.df['position_cum_return']
    investment.df['%Cumulative RelRet Long'] =  100*investment.df['position_cum_return_long']
    investment.df['%Cumulative RelRet Short'] =  100*investment.df['position_cum_return_short']

    investment.df['%Cumulative RawRet'] =  100*investment.df['position_cum_Rawreturn']
    
    investment.TTLreturn = investment.df['position_return'].sum()
    investment.TTLrawReturn = investment.df['position_Rawreturn'].sum()
    

def determine_individual_trades(investment):
    #it fills a column that later allows us to have graphs that reflect the goodness of a trade
    investment.df["end_position_mark"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    indexes4rev = []
    ret = 0
    for i in range(len(investment.df["position"].index)):    
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        curr_pos = investment.df['position'].loc[indx]
        if i == len(investment.df["position"].index)-1:
            next_pos = 0
        else:
            next_pos = investment.df['position'].iloc[i+1]
        if curr_pos != 0 and curr_pos != next_pos:
            #this means a position has ended, now lets calculate what its profit is
            investment.df["end_position_mark"].loc[indx] = curr_pos #to calc num L and S later           
            accmRelRet = accumulated(indexes4rev,investment.df,'ooRelRet(nextDay)',curr_pos)
            numDaysOpened = count_days(indexes4rev,investment.df,curr_pos)
            accmAvgRelRet = accmRelRet/float(numDaysOpened)
            ret += accmAvgRelRet*curr_pos*numDaysOpened
            for j in range(i,0,-1):
                if investment.df['position'].iloc[j] == curr_pos:
                    investment.df['trade_profit'].iloc[j]= accmAvgRelRet*curr_pos
                    #print investment.df["trade_profit"].iloc[j],accmAvgRelRet
                else:
                    break
                #print j,accmAvgRelRet,accmRelRet,numDaysOpened


#################################################
# STRATEGIES
################################################                    

def strategy_LONG_TERM(investment,date1=None,date2=None,out_dir=""):
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    investment.df['position'].replace(0,1,inplace=True)
    investment.df['position'].replace(-1,1,inplace=True)

    investment.strategy_name = "BH"
    print "applying",investment.strategy_name,"to",investment.stock_name
    calculate_investment_return(investment) 
    determine_individual_trades(investment) 
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return investment.strategy_name

def strategy_BUY_n_HOLD(investment,date1=None,date2=None,out_dir=""):
    investment.df["position"] = pd.Series([1 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)

    investment.strategy_name = "B&H"
    print "applying",investment.strategy_name,"to",investment.stock_name
    calculate_investment_return(investment) 
    determine_individual_trades(investment) 
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return investment.strategy_name

def strategy_SHORT_n_HOLD(investment,date1=None,date2=None,out_dir=""):
    investment.df["position"] = pd.Series([-1 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)

    investment.strategy_name = "Short&Hold"
    print "applying",investment.strategy_name,"to",investment.stock_name
    calculate_investment_return(investment) 
    determine_individual_trades(investment) 
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return investment.strategy_name    

def strategy_BASE_MHD(investment,score=None,strategy_name=None,shortIn=3,longIn=-3,MHD=1,date1=None,date2=None,out_dir=""):
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    if strategy_name == None:
        strategy_name = "Base_"+str(MHD)+"HD"
    investment.strategy_name = strategy_name
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name,"with",investment.fscore2apply
    
    indexes4rev = []  

    for i in range(len(investment.df["position"].index)-1):    
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        if pos == 1:
            numDaysOpened = count_days(indexes4rev,investment.df,pos)
            investment.df['position'].iloc[i+1] = 1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if numDaysOpened >= MHD:
                investment.df['position'].iloc[i+1] = 0
                if investment.df[score].loc[indx] >= shortIn:
                    investment.df['position'].iloc[i+1] = -1
                        
        if pos == -1:
            numDaysOpened = count_days(indexes4rev,investment.df,pos)
            investment.df['position'].iloc[i+1] = -1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if numDaysOpened >= MHD:
                investment.df['position'].iloc[i+1] = 0
                if investment.df[score].loc[indx] <= longIn:
                    investment.df['position'].iloc[i+1] = 1

        if pos == 0: #if no position is held
            if investment.df[score].loc[indx] >= shortIn:
                investment.df['position'].iloc[i+1] = -1 #SHORT
            if investment.df[score].loc[indx] <= longIn:
                investment.df['position'].iloc[i+1] = 1  #LONG                   
                                               
    calculate_investment_return(investment)
    determine_individual_trades(investment)                                     
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return strategy_name


def strategy_BASEio_MHD(investment,score=None,strategy_name=None,shortIn=3,longIn=-3,MHD=1,date1=None,date2=None,out_dir=""):
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    if strategy_name == None:
        strategy_name = "BaseIO_"+str(MHD)+"HD"
    investment.strategy_name = strategy_name
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name,"with",investment.fscore2apply
    
    indexes4rev = []  

    for i in range(1,len(investment.df["position"].index)-1):#need range(1,x) becasue used index i-1 
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        if pos == 1:
            numDaysOpened = count_days(indexes4rev,investment.df,pos)
            investment.df['position'].iloc[i+1] = 1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if numDaysOpened >= MHD:
                investment.df['position'].iloc[i+1] = 0
                if investment.df[score].loc[indx] >= shortIn and investment.df[score].iloc[i-1] > shortIn :
                    investment.df['position'].iloc[i+1] = -1
                        
        if pos == -1:
            numDaysOpened = count_days(indexes4rev,investment.df,pos)
            investment.df['position'].iloc[i+1] = -1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if numDaysOpened >= MHD:
                investment.df['position'].iloc[i+1] = 0
                if investment.df[score].loc[indx] <= longIn and investment.df[score].iloc[i-1] < longIn:
                    investment.df['position'].iloc[i+1] = 1

        if pos == 0: #if no position is held
            if investment.df[score].loc[indx] >= shortIn and investment.df[score].iloc[i-1] > shortIn:
                investment.df['position'].iloc[i+1] = -1 #SHORT
            if investment.df[score].loc[indx] <= longIn and investment.df[score].iloc[i-1] < longIn:
                investment.df['position'].iloc[i+1] = 1  #LONG                   
                                               
    calculate_investment_return(investment)
    determine_individual_trades(investment)                                     
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return strategy_name
                        


                        
                        
def strategy_TITO(investment,score=None,shortIn=3,shortOut=-3,longIn=-3,longOut=3,
                  date1=None,date2=None,out_dir=""):
    """use scores to enter and to exit"""
    #preparations
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    investment.strategy_name = "TITO"
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name,"with",investment.fscore2apply

    for i in range(len(investment.df[score].index)-1):    
    #for i in investment.df[score].index:
        indx = investment.df[score].index[i]
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]
        #exiting conditions
        if pos == 1:
            investment.df['position'].iloc[i+1] = 1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if investment.df[score].loc[indx] >= longOut:
                investment.df['position'].iloc[i+1] = 0
            if investment.df[score].loc[indx] >= shortIn:
                investment.df['position'].iloc[i+1] = -1
                    
        if pos == -1:
            investment.df['position'].iloc[i+1] = -1 #by default assume we are holding the next day unless one of the below indicate otherwise 
            if investment.df[score].loc[indx] <= shortOut:
                investment.df['position'].iloc[i+1] = 0
            if investment.df[score].loc[indx] <= longIn:
                investment.df['position'].iloc[i+1] = 1

        if pos == 0: #if no position is held
            if investment.df[score].loc[indx] >= shortIn:
                investment.df['position'].iloc[i+1] = -1 #SHORT
            if investment.df[score].loc[indx] <= longIn:
                investment.df['position'].iloc[i+1] = 1  #LONG                   
                                               
    calculate_investment_return(investment)
    determine_individual_trades(investment)                                     
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return investment.strategy_name    

    
###################################################
## DONT BE GREEDY (aka DBG)
###################################################

    
    
def w_avg(vec):
    t = 0
    for i in range(len(vec)):
        if isinstance(vec[i],(int,float,long)):
            t+= vec[i]/float(i+1)
    return t/float(len(vec)+1)
    
    
def calculate_derivative(df,var,i1,i2):
    try:
        return (df[var].iloc[i2] - df[var].iloc[i1])/float(i2-i1)
    except: #when the history is not available
        return None

def get_slopes(df,var,i):
    time_periods = [1,3,5]
    derivs = []
    for t in time_periods:
        derivs.append(calculate_derivative(df,var,i,i-t))
    return derivs
    
def risky_short_signal(df,var,start_i):
    """Vars must be in the order of importance"""
    slopes = get_slopes(df,var,start_i)
    s = sum([1 for val in slopes if val > 0])
    if s == len(slopes):
        return True
    return False


def amiable_long_basedOn_derivatives(df,var,start_i):
    slopes = get_slopes(df,var,start_i)
    s = sum([1 for val in slopes if val > 0]) #check for positive derivatives
    if s == len(slopes):
        return True
    return False     

def amiable_short_basedOn_derivatives(df,var,start_i):
    slopes = get_slopes(df,var,start_i)
    s = sum([1 for val in slopes if val < 0]) #check for negative derivatives
    if s == len(slopes): #if all derivatives are negative,it's in decline so exit LONG
        return True
    return False     

def amiable_short_basedOn_MTPLderivatives(df,VARS,start_i):
    num_slopes = 0
    s = 0
    for var in VARS:
        slopes = get_slopes(df,var,start_i)
        num_slopes = len(slopes)
        #var_slopes.setdefault(var,get_slopes(df,var,start_i))
        s += sum([1 for val in slopes if val < 0])
    if s == len(VARS)*num_slopes:
        return True
    return False

def amiable_long_basedOn_MTPLderivatives(df,VARS,start_i):
    num_slopes = 0
    s = 0
    for var in VARS:
        slopes = get_slopes(df,var,start_i)
        num_slopes = len(slopes)
        #var_slopes.setdefault(var,get_slopes(df,var,start_i))
        s += sum([1 for val in slopes if val > 0])
    if s == len(VARS)*num_slopes:
        return True
    return False    



def strategy_DONT_BE_GREEDY(investment,score=None,date1=None,date2=None,out_dir=""):
    """use scores to enter, but use some 'reasonable' earning to exit"""
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    investment.strategy_name = "DBG"
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name,"with",investment.fscore2apply

    MHD = 100 # maximum holding days; I think MHD = 1 is stupid (and therefore should not be done)
    RHD = 3 # REASONABLE holding days; I don't think RHD should be anything other than 2 or 3
    #RHD <= MHD
    """at the end of each time period, eg, day, examine the stock 
    in order to make the decision what to do with that stock tomorrow morning;
    we assume that the close of the current period prices are already known 
    (but the open prices of the next day are not known)."""
    indexes4rev = []  

    for i in range(len(investment.df[score].index)-1):    
    #for i in investment.df[score].index:
        indx = investment.df[score].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        #exiting conditions
        if pos == 1 or pos == -1: #should one exist
            accmRelRet = accumulated(indexes4rev[:-1],investment.df,'ooRelRet(nextDay)',pos)
            accmRelRet += investment.df["ocRelRet"].loc[indx] #ocRelRet
            accmRawRet = accumulated(indexes4rev[:-1],investment.df,'ooRawRet(nextDay)',pos)
            accmRawRet += investment.df["ClosePrice"].loc[indx]/investment.df["OpenPrice"].loc[indx] - 1.0
            numDaysOpened = count_days(indexes4rev,investment.df,pos) #includes this day
            if pos == 1: #case: LONG position is held
#                print "in LONG on",indx
#                print "accmRelRet =",accmRelRet
#                print "accmRawRet = ",accmRawRet
#                print "numDaysOpened = ",numDaysOpened
                investment.df['position'].iloc[i+1] = 1 #by default assume we are holding the next day unless one of the below indicate otherwise 
                for days in [200,100]:#caseL1
                    if accmRelRet > 1.1*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]) + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                        investment.df['position'].iloc[i+1] = 0          
                        #print "pos closed in caseL1:", accmRelRet,">",1.1*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx])
                        break
                
                #a sign appears                
                if (investment.df[score].loc[indx] >= investment.df[score+"Qupper"].loc[indx] )\
                    and amiable_short_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i):
                    investment.df['position'].iloc[i+1] = -1    
                    #print "pos closed by SHORT"
                
                if numDaysOpened >= RHD and investment.df['position'].iloc[i+1] == 1:
                    for days in [40,100,200]: #DAYS:#caseL4
                        if accmRelRet > 1*investment.df["ooRelRet("+str(days)+"D std)"].loc[indx] + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                            investment.df['position'].iloc[i+1] = 0  
                            #print "pos closed in caseL4:",accmRelRet,">",investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]
                            break

                if numDaysOpened >= MHD/2.0 and investment.df['position'].iloc[i+1] == 1:
                    for days in [40,100,200]: #DAYS:#caseL4
                        if accmRelRet > 0.9*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]) + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                            investment.df['position'].iloc[i+1] = 0  
                            #print "pos closed in caseL5:",accmRelRet,">",investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]
                            break                    

                if investment.df['position'].iloc[i+1] == 1: #still in LONG
                    if numDaysOpened > MHD:
                        investment.df['position'].iloc[i+1] = 0                    
                        #provides guaranteed termination
                    if not amiable_long_basedOn_derivatives(investment.df,"ooRelRet(20D UWM)",i):
                        investment.df['position'].iloc[i+1] = 0   
                    if amiable_short_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i):
                        investment.df['position'].iloc[i+1] = -1 
                    
                    
            if pos == -1:#if SHORT is held
                investment.df['position'].iloc[i+1] = -1
                for days in [200,100]:#caseS1
                    if accmRelRet < -1.1*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]) + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                        investment.df['position'].iloc[i+1] = 0 
                        break
                    
                #a sign appears
                if (investment.df[score].loc[indx] <= investment.df[score+"Qlower"].loc[indx]) \
                    and amiable_long_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i): 
                    investment.df['position'].iloc[i+1] = 1
                
                if numDaysOpened >= RHD and investment.df['position'].iloc[i+1] == -1:                    
                    for days in [40,200,100]:#caseS4
                        if accmRelRet < -1*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]) + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                            investment.df['position'].iloc[i+1] = 0       
                            break
                        
                if numDaysOpened >= MHD/2.0 and investment.df['position'].iloc[i+1] == -1:
                    for days in [40,100,200]: #DAYS:#caseS5
                        if accmRelRet < -0.9*(investment.df["ooRelRet("+str(days)+"D std)"].loc[indx]) + investment.df["ooRelRet("+str(days)+"D avg)"].loc[indx]:
                            investment.df['position'].iloc[i+1] = 0                      
                            break

                if investment.df['position'].iloc[i+1] == -1: #guaranteed ways to exit
                    if numDaysOpened > MHD:
                        investment.df['position'].iloc[i+1] = 0    
                    if not amiable_short_basedOn_derivatives(investment.df,"ooRelRet(20D UWM)",i):
                        investment.df['position'].iloc[i+1] = 0                           
                    if amiable_long_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i): 
                        investment.df['position'].iloc[i+1] = 1
                        
        if pos == 0: #if no position is held
            if (investment.df[score].loc[indx] >= investment.df[score+"Qupper"].loc[indx])\
                and amiable_short_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i):
                investment.df['position'].iloc[i+1] = -1 #SHORT
            if (investment.df[score].loc[indx] <= investment.df[score+"Qlower"].loc[indx]) \
                and amiable_long_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i): 
                investment.df['position'].iloc[i+1] = 1  #LONG        
                
        if pos == 0: #new entry signal
            if amiable_long_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i): 
                investment.df['position'].iloc[i+1] = 1 
            if amiable_short_basedOn_MTPLderivatives(investment.df,["ooRelRet(10D UWM)","ooRelRet(20D UWM)"],i):
                investment.df['position'].iloc[i+1] = -1    
                                               
    calculate_investment_return(investment)
    determine_individual_trades(investment)                                     
    #UTILITIES.dump_data(investment.df,investment.stock_name,t_fn="t_"+investment.strategy_name+"_"+investment.stock_name+"_"+ date1.strftime('%d-%m-%y')+"_"+date2.strftime('%d-%m-%y')+".csv")       
    return investment.strategy_name

def exit_short_basedOn_derivatives(df,VARS,start_i):
    #VARS should have two vars, FIRST for the short term, second more long-term
    if spike_occurred(df,start_i,days=6) != 0: 
        return amiable_long_basedOn_derivatives(df,VARS[0],start_i)
    else:
        return amiable_long_basedOn_derivatives(df,VARS[1],start_i)

def exit_long_basedOn_derivatives(df,VARS,start_i):
    #VARS should have two vars, FIRST for the short term, second more long-term
    if spike_occurred(df,start_i,days=6) != 0: 
        return amiable_short_basedOn_derivatives(df,VARS[0],start_i)       
    else:
        return amiable_short_basedOn_derivatives(df,VARS[1],start_i)  
        
def enter_short_basedOn_MTPLderivatives(df,VARS,start_i):
    #VARS should have 3 vars, FIRST for the short term, second more midlength-term, last for the longer-term
    if spike_occurred(df,start_i,days=6) != 0: 
        Vars = [VARS[0], VARS[1]]
        return amiable_short_basedOn_MTPLderivatives(df,Vars,start_i)
    else:
        Vars = [VARS[1],VARS[2]]
        return amiable_short_basedOn_MTPLderivatives(df,Vars,start_i)       

def enter_long_basedOn_MTPLderivatives(df,VARS,start_i):
    #VARS should have 3 vars, FIRST for the short term, second more midlength-term, last for the longer-term
    if spike_occurred(df,start_i,days=6) != 0: 
        Vars = [VARS[0], VARS[1]]
        return amiable_long_basedOn_MTPLderivatives(df,Vars,start_i)
    else:
        Vars = [VARS[1],VARS[2]]
        return amiable_long_basedOn_MTPLderivatives(df,Vars,start_i)       

    
def spike_occurred(df,start_i,days = 7):
    """returns TRUE if there has been a spike in RelRet in the last 7 days.
        Note, it finds the most recent spike, whether positive or negative.
        Hence if there were a couple of spikes, we only pick up the most recent one
        and hence can underestimate their influence because there could be 
        two spikes of the same kind, or of the opposite kind and hence they 'cancel' 
        each others influence out.
        """
    """Why are spikes important??? To decide how many days of everage to use for
        entering and exiting signal."""
    """how to define a spike? larger than 1.5 std of the RelRet in the last 200 days"""
    time_periods = [day for day in range(1,days+1)]
    for t in time_periods:
        try: #try provides a graceful exit in case of accessing values outside of a list
            RR = df["ooRelRet"].iloc[start_i-t] 
            if abs(RR) > 1.4*df["ooRelRet(200D std)"].iloc[start_i-t]:
                if RR > 0:
                    return 1
                if RR < 0:
                    return -1
        except:
            return 0 
            
############## Simple ############################
def strategy_SIMPLE(investment,score=None,date1=None,date2=None,out_dir=""):
    """use scores to enter, but use some 'reasonable' earning to exit"""
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    investment.strategy_name = "SIMPLE"
    investment.fscore2apply = score
    print "applying",investment.strategy_name,"to",investment.stock_name          
    MHD = 2
    
    """at the end of each time period, eg, day, examine the stock 
    in order to make the decision what to do with that stock tomorrow morning;
    we assume that the close of the current period prices are already known 
    (but the open prices of the next day are not known)."""
    indexes4rev = []  

    for i in range(len(investment.df["position"].index)-1):    
    #for i in investment.df[score].index:
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        #exiting conditions
        if pos == 1 or pos == -1: #should one exist
            accmRelRet = accumulated(indexes4rev[:-1],investment.df,'ooRelRet(nextDay)',pos)
            accmRelRet += investment.df["ocRelRet"].loc[indx] #ocRelRet
            accmRawRet = accumulated(indexes4rev[:-1],investment.df,'ooRawRet(nextDay)',pos)
            accmRawRet += investment.df["ClosePrice"].loc[indx]/investment.df["OpenPrice"].loc[indx] - 1.0
            numDaysOpened = count_days(indexes4rev,investment.df,pos) #includes this day
            if pos == 1: 
                if investment.df["ccRelRet"].loc[indx] < -1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = -1
#                if investment.df['position'].iloc[i+1] == 1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                    
            if pos == -1: 
                investment.df['position'].iloc[i+1] = -1 
                if investment.df["ccRelRet"].loc[indx] > 1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = 1
#                if investment.df['position'].iloc[i+1] == -1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                 
                
        if pos == 0:
            RR =  investment.df["ccRelRet"].loc[indx] 
            if RR > 1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                investment.df['position'].iloc[i+1] = -1
            if RR < -1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                investment.df['position'].iloc[i+1] = 1
    calculate_investment_return(investment)
    determine_individual_trades(investment)        


### First Momentum strategies ###########################                             

def strategy_MOMENTUM1(investment,date1=None,date2=None,out_dir=""):
    """use scores to enter, but use some 'reasonable' earning to exit"""
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    investment.strategy_name = "MOMENTUM1"
    investment.fscore2apply = None
    print "applying",investment.strategy_name,"to",investment.stock_name          

    for days in [50,200] :
        for var in ['ccRelRet']:
            df[var+"("+str(days)+"D std)"] = pd.rolling_std(df[var],days)    


    for var in ['ccRelRet',]:  
        for days in [10,20,]:       
            df[var+"("+str(days)+"D SMA)"] = pd.rolling_mean(df[var],days)
            df[var+"("+str(days)+"D WM)"] =pd.rolling_mean(df[var+"("+str(days)+"D SMA)"],10)
 
            
            
    """at the end of each time period, eg, day, examine the stock 
    in order to make the decision what to do with that stock tomorrow morning;
    we assume that the close of the current period prices are already known 
    (but the open prices of the next day are not known)."""
    indexes4rev = []  

    for i in range(len(investment.df["position"].index)-1):    
    #for i in investment.df[score].index:
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        #exiting conditions
        if pos == 1 or pos == -1: #should one exist
            accmRelRet = accumulated(indexes4rev[:-1],investment.df,'ooRelRet(nextDay)',pos)
            accmRelRet += investment.df["ocRelRet"].loc[indx] #ocRelRet
            accmRawRet = accumulated(indexes4rev[:-1],investment.df,'ooRawRet(nextDay)',pos)
            accmRawRet += investment.df["ClosePrice"].loc[indx]/investment.df["OpenPrice"].loc[indx] - 1.0
            numDaysOpened = count_days(indexes4rev,investment.df,pos) #includes this day
            if pos == 1: 
                if accmRelRet > 0 and investment.df["ClosePrice"].loc[indx]:
                if investment.df["ccRelRet"].loc[indx] < -1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = -1
#                if investment.df['position'].iloc[i+1] == 1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                    
            if pos == -1: 
                investment.df['position'].iloc[i+1] = -1 
                if investment.df["ccRelRet"].loc[indx] > 1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = 1
#                if investment.df['position'].iloc[i+1] == -1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                 
                
        if pos == 0:
            RR =  investment.df["ooRelRet(10D WM)"].loc[indx] 
            boundary = investment.df["ooRelRet(100D std)"].loc[indx]
            if RR > 0.8*boundary: # and ???:
                investment.df['position'].iloc[i+1] = 1
            if RR < -0.8*boundary:
                investment.df['position'].iloc[i+1] = -1
    calculate_investment_return(investment)
    determine_individual_trades(investment)        


def strategy_TURTLE1(investment,date1=None,date2=None,out_dir=""):
    """This is NOT the original turle for many reasons, e.g., turtles usually traded when a breakout 
    occurred not waiting for the open of the next day, they were monitoring intra-day prices, etc."""
    investment.df["position"] = pd.Series([0 for x in investment.df.index],index= investment.df.index)
    investment.df["trade_profit"] = pd.Series([0.00 for x in investment.df.index],index= investment.df.index)
    
    investment.strategy_name = "TURTLE1"
    investment.fscore2apply = None
    print "applying",investment.strategy_name,"to",investment.stock_name          

    for var in ['ClosePrice',]:  
        for days in [20,]:       
            df[var+"("+str(days)+"D SMA)"] = pd.rolling_mean(df[var],days)
            df[var+"("+str(days)+"D WM)"] =pd.rolling_mean(df[var+"("+str(days)+"D SMA)"],10)    
    """at the end of each time period, eg, day, examine the stock 
    in order to make the decision what to do with that stock tomorrow morning;
    we assume that the close of the current period prices are already known 
    (but the open prices of the next day are not known)."""
    indexes4rev = []  

    for i in range(len(investment.df["position"].index)-1):    
    #for i in investment.df[score].index:
        indx = investment.df["position"].index[i]
        indexes4rev.append(indx)
        pos = investment.df['position'].loc[indx] #same as  investment.df['position'].iloc[i]

        #exiting conditions
        if pos == 1 or pos == -1: #should one exist
            accmRelRet = accumulated(indexes4rev[:-1],investment.df,'ooRelRet(nextDay)',pos)
            accmRelRet += investment.df["ocRelRet"].loc[indx] #ocRelRet
            accmRawRet = accumulated(indexes4rev[:-1],investment.df,'ooRawRet(nextDay)',pos)
            accmRawRet += investment.df["ClosePrice"].loc[indx]/investment.df["OpenPrice"].loc[indx] - 1.0
            numDaysOpened = count_days(indexes4rev,investment.df,pos) #includes this day
            if pos == 1: 
                if accmRelRet > 0 and ???:
                if investment.df["ccRelRet"].loc[indx] < -1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = -1
#                if investment.df['position'].iloc[i+1] == 1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                    
            if pos == -1: 
                investment.df['position'].iloc[i+1] = -1 
                if investment.df["ccRelRet"].loc[indx] > 1.8*investment.df["ooRelRet(200D std)"].loc[indx]:
                    investment.df['position'].iloc[i+1] = 1
#                if investment.df['position'].iloc[i+1] == -1: #still in LONG
#                    if numDaysOpened > MHD:
#                        investment.df['position'].iloc[i+1] = 0                 
                
        if pos == 0:
            RR =  investment.df["ooRelRet(10D UWM)"].loc[indx] 
            boundary = investment.df["ooRelRet(100D std)"].loc[indx]
            if RR > 0.8*boundary and ???:
                investment.df['position'].iloc[i+1] = 1
            if RR < -0.8*boundary:
                investment.df['position'].iloc[i+1] = -1
    calculate_investment_return(investment)
    determine_individual_trades(investment)   