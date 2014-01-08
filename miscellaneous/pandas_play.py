# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 17:31:59 2013

@author: Olena
"""
df["ooRelRet(CumSum)"] = df["ooRelRet"].cumsum()
STD = df["ooRelRet"].std()
MEAN = df["ooRelRet"].mean()

df[f2score+"Qlower"] = df[f2score].quantile(Quantiles[0])
df[f2score+"Qupper"] = df[f2score].quantile(Quantiles[1])
        #these have to come AFTER we have examined what is already opened            
        if pos == 0 and investment.df[score].loc[i] <= investment.df[score+"Qlower"].loc[i]:
            pos = 1 #long it
        elif pos == 0 and investment.df[score].loc[i] >= investment.df[score+"Qupper"].loc[i]:
            pos = -1 #short it
                    
os.getcwd()  

#### dataframe functions ######################
      
import datetime
import pandas as pd
import math

days = 7
d1 = datetime.datetime(2001,1,1).date()
def date_range(d1,days):
    dates = []
    #dates.append(d1)
    for d in range(days):
        dates.append(d1+datetime.timedelta(days=d))
    return dates
    
df = pd.DataFrame(10*randn(7,4),index=date_range(d1,days),columns=["A","B","C","D"])


for col_name in df.columns:
    print col_name
    for row_ind in df.index:
        print row_ind
        print  df.loc[row_ind,col_name]
        df.loc[row_ind,col_name] = round(df.loc[row_ind,col_name],1)

df['A'][d1]
d1 = datetime.datetime(2001,1,1).date()
df['A'][d1.strftime('%Y-%m-%d')] #doesn't work

df['E'] = pd.Series([0.0 for x in df.index], index=df.index)
df['E'][df['D'] >0] = df['D']

df['F'] = pd.Series([0.0 for x in df.index], index=df.index)
df['F'][df['D'] <=0] = df['D']

df['E'][0:2] = df['A'][0:2] 
df['E'][2:4] = [-1.11,2.222]

df = df.drop(['F'],axis =1)
for i in range(len(df.A.index)):
    print i
    print df.A.iloc[i]
    i_ind = df.A.index[i]
    print i_ind
    print df.A.loc[i_ind]        
    

#### Panel Dataframe functions #########################    
fn = "..\data\SP500.xls"

print "\nreading",fn
DF = {}
sheets = pd.ExcelFile(fn).sheet_names
print sheets

for sheet in sheets:
    df = pd.DataFrame()
    df = pd.ExcelFile(fn).parse(sheet,index_col=0,parse_dates=True)
    df = re_index(df)
    DF[sheet] = df

#for key in DF.keys(): print key print DF[key].columns

#for debugging
for key in DF.keys(): 
    print key, 
    index_Dates = []
    for elem in DF[key].index:
        index_Dates.append(elem)
    columns = DF[key].columns
    ticker = columns[1]
    print ticker,
    #print DF[key][ticker].values[0:10]
    date = datetime.datetime(2013,5,2)
    print date.strftime("%d/%m/%Y"), DF[key][ticker].loc[date],
    indx_date = index_Dates.index(date)
    print "=",DF[key][ticker].iloc[indx_date],"next days'",DF[key][ticker].iloc[indx_date+1]

print DF['Open']['CVH UN Equity'].values[0:10]
print DF['Open']['CVH UN Equity'].loc[datetime.datetime(2013,5,7)]
if math.isnan(DF['Open']['CVH UN Equity'].loc[datetime.datetime(2013,5,7)]):
    print 'nan'


def convert_to_date(text):
    text = text.split("/")
    if len(text) != 3:
        print "!!! COULD not convert",text,"to date"
        return None
    try:
        date = datetime.datetime(int(text[2]),int(text[1]),int(text[0])).date()
        return date
    except:
        return None        
        
def re_index(df):
    t = []
    for date in  df.index:
        t.append(date.date())
    df.reindex(index = t, columns = df.columns )
    return df
        
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


fn = "../data/SP500.xls"
DF = get_open_close_beta_sector_poolInd_fromDBdump(fn)

        