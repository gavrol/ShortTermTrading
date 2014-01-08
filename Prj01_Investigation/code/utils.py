# -*- coding: utf-8 -*-
"""
Created on Tue Jul 09 10:10:43 2013

@author: olenag
"""

import pandas as pd
from class_definitions import *
import os
import sys
import datetime
import math


    
def form_date_segments(starting_date,time_period_inYears):
    incr_days= time_period_inYears*math.floor(365)
    Dates = []
    curr_date = starting_date
    while curr_date <= datetime.datetime.now().date():
        Dates.append(curr_date)
        curr_date += datetime.timedelta(days = incr_days)
        
    print "Dates = ",Dates
    return Dates
    

def make_output_dir(out_dir):
    if not os.path.exists(out_dir):
        print 'does not exist'
        os.makedirs(out_dir)
    else:
        print out_dir, "exists"
    out_dir += "\\"    
    return out_dir

def dump_data_csv(df,stock_name,t_fn=None):
    if t_fn == None:    
        t_fn = "t_"+stock_name+"_Dump.csv"

    try:    
        df.to_csv(t_fn,sep=',')
        #df[df["F2(8,20)"] < - 5 ].to_csv(t_fn,sep=',')
    except:
        print "CAUTION: could not WRITE to",t_fn," (opened somewhere?)"
        
        
def dump_data_xls(DF,Stocks,t_fn=None):
    
    if t_fn == None:
        t_fn = "t_dumps.xls"
    writer = pd.ExcelWriter(t_fn)
    for s in range(len(Stocks)):
        DF[s].to_excel(writer,Stocks[s].name)
    writer.save()

    #t_fn = "x_"+stock.name+"_Dump.xls"
    #df.to_excel(t_fn)        

def explore_shifts(df,stock):
    #t_fn = "t_noshift_"+stock.name+".csv"
    #df['Close Price'].to_csv(t_fn,sep= ",")
    t_fn = "t_shifts2_"+stock.name+".csv"
    df['Close Price'].shift(2).to_csv(t_fn,sep=",")
    
    
def simple_operations_on_DataFrame(df,stock):
    """This function allows to figure out what column headers the data file has"""
    
    print df.describe()
    print "df.columns=",df.columns
    print "df.index=",df.index[0:10]

    
    print [ att for att in df.keys()]
    print "df.values=",df.values[0:5]
    for col_name in df.columns:
        print col_name
        print df[col_name][0:3]    
 
 ##### stuff to learn from ########################
 #    KEEP as it can be useful to learn from
 
def subset_by_condition(df,QUANTILES):
    conditions = []
    for f2score in F2scores:
        conditions.append(df[f2score] < df[f2score].quantile(QUANTILES[0]))
        conditions.append(df[f2score] > df[f2score].quantile(QUANTILES[1]))

    signif_df = df[conditions[0] | conditions[1] | conditions[2] | conditions[3]]
    #utils.dump_data_csv(signif_df,stock)
    """ alternatively the above can  be done like this: """
    s_Q = STAT_functions.get_stationary_quantiles1(df,F2scores,QUANTILES) 
    #don't need this as determining quantiles can be done on a fly             
    #F2Quants.append(s_Q)

""" 
    print "\nmore spiffy prints" 

    print "print DataFrame only with dates before Jan 1, 2010"
    print df[df["Date"] < datetime.datetime(2010,1,10)]

    print "Close PRICE only for the dates before Jan 1, 2010"
    print df["IBM Close Price"][df["Date"] < datetime.datetime(2010,1,10)] 

    row = 2
    print "\nprinting by row index",row
    print df.ix[0:row]
    print "\nonly selected columns for row indexed",row
    print df.ix[0:row,["IBM Ret","Pool Ret"]]
    print "\n new"
    print df.ix[0:row*100, ['IBM Beta','IBM F2','IBM Ret']] #[not math.isnan(df['IBM Beta'])]
    #print "DF only the not NaN entries for the date before Jan 30, 2010"
    #print not math.isnan(df['IBM Beta'][df["Date"] < datetime.datetime(2010,1,30)] )
    """