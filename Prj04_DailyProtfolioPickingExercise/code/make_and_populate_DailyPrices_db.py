import os
import sys
import csv 
import sqlite3
import pandas as pd





def create_tbl(dbname,tblname) :
    print "\n Creating table %s in DB %s" %(tblname,dbname)
    db = sqlite3.connect(dbname)
    c = db.cursor()

    c.execute("drop table if exists %s" %tblname)
    c.execute('create table %s (Ticker Text(50) Primary Key, Open Real,Close Real,PoolIndicator Numeric, Sector Text(200),  Date TEXT(10))' %tblname)
 
    db.commit()
    db.close()    

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
    
def populate_ASX_ListedCompanies_tbl(company_info,dbname,tblname,date):
    print '\nPopulating table %s in DB %s' %(tblname,dbname)
    db = sqlite3.connect(dbname)
    c = db.cursor()    
    
    for name,ticker,sector in company_info:                      
        sql = """insert into %s (CompanyName,Ticker, Sector, DateLastTraded) values("%s",'%s','%s','%s') """ %(tblname,name,ticker.upper(),sector,date)
        c.execute(sql)  
    
    db.commit()
    c.execute("select count(*) from %s" %tblname)
    print "Number of elements inserted:",c.fetchall()
    db.close()   



if __name__=="__main__":
    dbname = "../data/SP500_DailyData"

    fn = "../data/SP500_DailyData.xls"
    
    tbls = ["SP500_Open","SP500_Close","SP500_Beta","SP500_SectorInfo"]
    for tbl in tbls:
        create_tbl(dbname,tblname) 
    populate_ASX_ListedCompanies_tbl(company_info,dbname,tblname,date)

 
