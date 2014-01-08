# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 09:23:59 2013

@author: olenag

PURPOSE: a set of utilities, e.g., writing to files, etc. that might be needed accross projects
"""
import os
import sys
import pandas as pd
import math
import datetime

#####  READING data #################################################
def read_stock_data_from_standard1_file(stock_name,data_dir):
    print "\nreading",stock_name,"from", data_dir
    df = pd.DataFrame()
    for fn in os.listdir(data_dir):
        t_name = fn.split('.')[0].replace(' Equity','')
        if t_name.upper() ==  stock_name.upper():     
            fn = data_dir+fn
            if os.path.isfile(fn): 
                #print "reading:",fn  
                df = pd.DataFrame()        
                if  fn.endswith("xls") or fn.endswith("xlsx"):
                    sheets = pd.ExcelFile(fn).sheet_names
                    print sheets
                    df = pd.ExcelFile(fn).parse(sheets[0],index_col=0,parse_dates=True)
                elif fn.endswith("csv"):#not recommended as the dates don't get parsed correctly
                    df = pd.read_csv(fn,index_col=0,parse_dates=True)
    if df.empty:
        print "\n!!! COULD NOT FIND DATA FOR",stock_name,"\n empty dataframe will be returned\n"
    return df
                    
def get_stock_names_from_data_dir_based_on_filenames(data_dir):
    t = []
    for fn in os.listdir(data_dir):
        stock_name = fn.split('.')[0].replace(' Equity','')      
        if os.path.isfile(data_dir+fn):
            if fn.endswith("xls"):
                t.append(stock_name)
    return t        

def get_stock_names_inIndex_from_aFile_v1(fn):
    """expects file with one column where they are ticker names, bloomberg names"""
    list = []
    for line in open(fn,'r').readlines():
        if line.strip() != "":
            ticker = line.split(',')[0].strip()
            ticker = ticker.replace(" Equity","").strip('')
            list.append(ticker)
    print "number of stocks read",len(list)
    #print list
    return list
            
############################################################
## DATAFRAME utilities
############################################################            
            
def re_index(df):
    """used to make sure that index of a DataFrame is a date"""
    t = [d.date() for d in df.index]
    df.reindex(index = t, columns = df.columns )
    return df
    
##### dumping DataFrame content #####################################
def dump_data(df,stock_name="",t_fn=None):
    if t_fn == None:    
        t_fn = "t_"+stock_name+"_dump.csv"

    try:    
        df.to_csv(t_fn,sep=',')
        #df[df["F2(8,20)"] < - 5 ].to_csv(t_fn,sep=',')
    except:
        print "CAUTION: could not WRITE to",t_fn," (opened somewhere?)"
        
        
def dump_MLTPLdfs(DF,stock_names=[],t_fn=None):
    
    if t_fn == None:
        t_fn = "t_dumps.xls"
    writer = pd.ExcelWriter(t_fn)
    for s in range(len(stock_names)):
        DF[s].to_excel(writer,stock_names[s])
    writer.save()

    #t_fn = "x_"+stock.name+"_Dump.xls"
    #df.to_excel(t_fn)   

### output-related stuff    ###########################################
def make_output_dir(out_dir):
    if not os.path.exists(out_dir):
        print 'does not exist'
        os.makedirs(out_dir)
    else:
        print out_dir, "exists"
    if "windows" in sys.platform.lower():
        out_dir += "\\"    
    else:
        out_dir +="/" #for linux and OS X
    return out_dir

##########   transforming numbers     ##################################################
def str2float(txt):
    try:
        return float(txt.strip())
    except:
        return None

############# dates   #################################################
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
    
def form_date_segments(start_date,time_period_inYears,end_date=None):
    """divides the TIME from the starting_date into time periods based on the specified time_period_inYears value"""
    incr_days= time_period_inYears*math.floor(365)
    Dates = []
    curr_date = start_date
    if end_date == None:
        end_date = datetime.datetime.now().date()
    if start_date > end_date:
        print "\n!!! CAUTION: starting date after end date",start_date.strftime("%d/%m/%Y"),"\n"
        Dates = [datetime.datetime(2000,1,1)]
    elif  time_period_inYears == 0:
        Dates = [start_date]
    else:
        while curr_date < end_date:
            Dates.append(curr_date)
            curr_date += datetime.timedelta(days = incr_days)
    if end_date == None:
        Dates.append(datetime.datetime.now().date())
    else:
        Dates.append(end_date)
    if len(Dates) == 1:
        print "\n!!! CAUTION: Time periods is empty in ", sys._getframe().f_code.co_name,"\n"
    #print Dates
    return Dates

def eliminate_short_time_periods(TP,min_num_days=10):
    """if we desire all time periods under min_num_days to be disregarded in our analysis"""
    """this function is INCORRECT as it never adds the last date,
        but I don't think I need it anyways since PHG want to see the entire horizon"""
    if min_num_days < 1:
        return TP
    
    t = []
    for d in range(len(TP)-1):
        t.append(TP[d])
        if TP[d+1] < TP[d] +  datetime.timedelta(days = min_num_days):
            break
    #print t
    return t