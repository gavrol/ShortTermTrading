# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 08:15:26 2013

@author: olenag

PURPOSE: 

"""

import os
import csv
import pandas as pd
import math

#strategy,PoolSize,Relative Max DD (%),Relative KRatio,Relative Sharpe,
#Relative RPTD WithCost mean,# Trades,Relative Mean Win / Loss,Relative Win Rate %,Relative Signed Win Rate %,
#HD mean,Long Relative Max DD (%),Long Relative KRatio,Long Relative Sharpe,
#Long Relative RPTD WithCost mean,Long # Trades,Long Relative Mean Win / Loss,Long Relative Win Rate %,
#Long Relative Signed Win Rate %,Long HD mean,Short Relative Max DD (%),Short Relative KRatio,Short Relative Sharpe,
#Short Relative RPTD WithCost mean,Short # Trades,Short Relative Mean Win / Loss,Short Relative Win Rate %,
#Short Relative Signed Win Rate %,Short HD mean,Absolute RPT WithCost mean,Absolute Mean Win / Loss,_ReturnType,
#Absolute Win Rate %,Absolute Return p.a.,Absolute Signed Win Rate %,
#Relative RPT WithCost mean,Absolute Max DD (%),Portfolio Name,HD max,Absolute RPTD WithCost mean,
#Long Relative RPT WithCost mean,Long HD max,Long Relative Return p.a.,
#Short Relative RPT WithCost mean,Short Relative Return p.a.,
#Short HD max,_RT Cost bps,Absolute KRatio,Relative Return p.a.,Absolute Sharpe

def split_params(params):
    HD = None
    cost = None
    numpos = None
    PS = None
    F2 = "F2"
    strategy = None
    
    params = params.split(" ")
    for param in params:
        if param.startswith("HD"):
            HD = int(param.split(":")[-1])
        elif param.startswith("pos"):
            numpos = int(param.split(":")[-1])
        elif param.startswith("cost"):
            cost = int(float(param.split(":")[-1]))
        elif param.startswith("poolsize"):
            PS = int(float(param.split(":")[-1]))
        elif param.startswith("F2"):
            F2 += "("+str(param.split(":")[-1])+")"    
        elif param.startswith("Filter"):
            strategy =param.split(":")[-1]               
    return HD,numpos,cost,PS,F2,strategy
            
def get_stats(fn,STATS,f2,HDs,PSs,costs,NumPos,strategy):
    print "reading", fn
    rows = csv.DictReader(open(fn,'rb'))

    for row in rows:
        #name = row["strategy"].strip()
        params = row["Portfolio Name"]
        HD,numpos,cost,PS,F2,name = split_params(params)

        if name != "" and f2 == F2 and name.lower() == strategy.lower() :
            if PS not in PSs:
                PSs.append(PS)
            if HD not in HDs:
                HDs.append(HD)
            if numpos not in NumPos:
                NumPos.append(numpos)
            if cost not in costs:
                costs.append(cost)

                
            key =  name +":"+str(PS)+":"+str(HD)+":"+str(numpos)+":"+str(cost)
            stats = {'total':{},'Short':{},"Long":{}}
            if key not in stats.keys():
                STATS[key] = {}
            else:
                print "!!! ERROR: key",key,"already in dict"
            stats["Strategy"] = name
            stats["PS"] = PS
            stats["HD"] = HD
            stats["Positions"] = numpos
            stats["CostPerTrd(BP)"] = cost
    
            stats['total']["Sharpe"] = float(row["Absolute Sharpe"])
            stats['total']["K Ratio"] = float(row["Absolute KRatio"])
            stats['total']["Ann return [%]"] = float(row["Absolute Return p.a."])
            stats['total']["MaxDD[%]"] = float(row["Absolute Max DD (%)"])
            stats['total']["Max HD"] =  math.ceil(float(row["HD max"]))
            stats['total']["Avg HD"] = math.ceil(float(row["HD mean"]))
    
            stats['Long']["Sharpe"] = float(row["Long Relative Sharpe"])
            stats['Long']["K Ratio"] = float(row["Long Relative KRatio"])
            stats['Long']["Ann return [%]"] = float(row["Long Relative Return p.a."])
            stats['Long']["MaxDD[%]"] = float(row["Long Relative Max DD (%)"])
            stats['Long']["Max HD"] =  math.ceil(float(row["Long HD max"]))
            stats['Long']["Avg HD"] =  math.ceil(float(row["Long HD mean"]))
    
            stats['Short']["Sharpe"] = float(row["Short Relative Sharpe"])
            stats['Short']["K Ratio"] = float(row["Short Relative KRatio"])
            stats['Short']["Ann return [%]"] = float(row["Short Relative Return p.a."])
            stats['Short']["MaxDD[%]"] = float(row["Short Relative Max DD (%)"])
            stats['Short']["Max HD"] =  math.ceil(float(row["Short HD max"]))
            stats['Short']["Avg HD"] =  math.ceil(float(row["Short HD mean"]))
            
            STATS[key] = stats
        

    

def dump_2file(fn,STATS,strategies,PSs,NumPos,HDs,cost):
    fn = open(fn,'w')
    headers = ["Strategy","Ann return [%]","Sharpe","MaxDD[%]","Calmar","Max HD","Avg HD","K Ratio","Positions","NumPositions","PoolSize","CostPerTrd(BP)"]
    
    fn.write(",".join(headers)+"\n")
 
    tPS = []
    for side in ['total','Long','Short']:
        fn.write(side +"\n")
        for filt in strategies:
            if filt.upper() == "NOFILTER":
                tPS = [PSs[0]]
            else:
                tPS = PSs
            for HD in HDs:
                for numpos in NumPos:
                    for ps in tPS:
                        for key in STATS.keys():
                            tmp = key.split(':')
                            filt_ =tmp[0]
                            ps_= int(tmp[1])
                            hd_ =int(tmp[2])
                            numpos_=int(tmp[3])
                            cost_ =int(tmp[4])
                            #print filt_,ps_,hd_,numpos_,cost_
                            if filt_ == filt and ps == ps_ and numpos == numpos_ and hd_== HD and cost==cost_:
                                s = ""
                                for header in headers:     
                                    stats = STATS[key][side]
                                    if header == "Strategy":
                                        s += " ".join(STATS[key]["Strategy"].replace("MarketUpDown","MUD").replace("F2Sensitivity","F2S").split("_")) 
                                        #if s in ["F2S AvgSimpleRank","IR AvgSimpleRank", "MUD AvgSimpleRank"]: s = s.replace(" AvgSimpleRank","")
                                        s += ' ('+f2+' PoolSize'+str(STATS[key]["PS"])+')'+","
                                    elif header == "Calmar":
                                        s += str(stats["Ann return [%]"]/stats["MaxDD[%]"]) +","
                                    elif header == "Positions":
                                        s += str(STATS[key][header]) +"L:"+str(STATS[key][header]) +"S" +","
                                    elif header == "CostPerTrd(BP)":
                                        s += str(STATS[key][header]) +","
                                    elif header == "PoolSize":
                                        s += str(STATS[key]["PS"]) +","
                                    elif header == "NumPositions":
                                        s += str(STATS[key]["Positions"]) +","
                                    else:
                                        s += str(stats[header]) +","
                                fn.write(s+"\n")
        fn.write("\n")
    fn.close()
        
if __name__=="__main__":
    
    DATA_DIR = ".."+os.sep+"data"+os.sep+"strategy_stats_dumps"+os.sep
    F2 = ["F2(8)","F2(6)"]
    for f2 in F2:
        for year in ["2010"]:
            STATS = {}
            strategies = []
            PSs = []
            HDs = []
            costs = []
            NumPos = []            
            
            for fn in os.listdir(DATA_DIR):
                if fn.endswith("csv") and fn.split("_")[-2].split(".")[0] == "from"+year:
                    #print fn
                    strategy = "_".join(fn.split("_")[:-2])
                    if strategy not in strategies:
                        strategies.append(strategy)
                    #else: print "!!! CAUTION: strategy",strategy,"has already been seen. possibly a second part file"
                    fn = DATA_DIR+fn
                    get_stats(fn,STATS,f2,HDs,PSs,costs,NumPos,strategy)
    
            print strategies
        
            #for HD in HDs:
            for cost in costs:
                fn = DATA_DIR+ "oSTATS_from"+str(year)+"_cost"+str(cost)+"_"+f2+".csv"
                dump_2file(fn,STATS,strategies,PSs,NumPos,HDs,cost)