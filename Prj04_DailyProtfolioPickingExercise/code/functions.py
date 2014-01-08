# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:04:40 2013

@author: olenag
"""

import csv
import datetime
import os
import sys
import shutil


def str2val(Str_stat,stat=None):
    str_stat = Str_stat.strip('"')
    if stat in ["Relative RPT (BPS)","Relative Signed Win Rate (%)","Number Trades","Stock Return (BPS)","Rank"]:
        try:
            return int(float(str_stat))
        except:
            return None
    else:
        try:
            return float(str_stat)
        except:
            return None  
            
def read_data(fn,DATA,fscore,key_HD,key_Stat,key_Window):
    #print "reading",fn
    if not os.access(fn,os.R_OK):
        print "!!! CAUTION: file",fn,"does not exist"
        return None

    for line in open(fn,'r').readlines():
        #sprint line
        stock_name = line.split(",")[0].strip('"')
        if stock_name.find("Equity") > 1 and stock_name.endswith("Equity"):# and len(line.split(","))>200: #and not stock_name.find("-W")>0
            line = line.replace('"','')
            line = line.strip('\n')
            if stock_name not in DATA.keys():
                DATA[stock_name] = {}
                DATA[stock_name]["Decision"] = None
            DATA[stock_name].setdefault(fscore, {})
            DATA[stock_name][fscore]["Rank"] = str2val(line.split(",")[1].strip('"'),"Rank")
            DATA[stock_name][fscore]["Score"] = str2val(line.split(",")[2].strip('"'),"Score")
            for HD in key_HD:
                 DATA[stock_name][fscore].setdefault(HD,{})
                 for stat in key_Stat:
                     DATA[stock_name][fscore][HD].setdefault(stat,{})
                     for window in key_Window:
                         try:
                             Str_stat = line.split(",")[3+ key_HD.index(HD)*(len(key_Stat) * len(key_Window)) + key_Stat.index(stat)*len(key_Window)+ key_Window.index(window)]                        #[3+len(key_HD)*key_HD.index(HD)+ len(key_Stat)*key_Stat.index(stat)+ key_Window.index(window)]                        
                             statistic = str2val(Str_stat,stat)    
                             DATA[stock_name][fscore][HD][stat][window] = statistic
                         except:
                             DATA[stock_name][fscore][HD][stat][window] = None
                         #if window == "1 Month" and stat == "Relative KRatio" and HD == "5HD":  print Str_stat, statistic                                               

#    for stk_key in DATA.keys():
#        print DATA[stk_key]
#        print 


def write_2file_finalDecisions(DATA,Decisions,fn,date,F2Scores,logfn=None):
    fn = open(fn,'wb')
    #header = "Stock,Date,Decision"
    #fn.write(header+"\n")
    s_date = date.strftime("%d/%m/%Y")
    for stk in DATA.keys():
        if Decisions[stk]["Decision"] in ["L","S"]:
            if (stk == 'BMC UW Equity' and date >= datetime.datetime(2013,9,5).date()) \
            or (stk == 'CVH UN Equity' and date >= datetime.datetime(2013,5,3).date()) \
            or (stk == 'HNZ UN Equity' and date >= datetime.datetime(2013,6,6).date()) \
            or (stk == 'PCS UN Equity' and date >= datetime.datetime(2013,4,26).date()) \
            or (stk == 'S UN Equity' and date >= datetime.datetime(2013,7,7).date()) \
            or (stk == 'WPI UN Equity' and date >= datetime.datetime(2013,1,18).date()) \
            or (stk == 'TIE UN Equity' and date >= datetime.datetime(2013,1,6).date()) \
            or (stk == 'KFT UW Equity' and date >= datetime.datetime(2012,9,27).date()) \
            or (stk == 'HNZ UN Equity' and date >= datetime.datetime(2013,6,4).date()) \
            or (stk == 'CBE UN Equity' and date >= datetime.datetime(2012,11,27).date()) \
            or (stk == 'ZTS-W UN Equity'):
                pass
            else:
                s = stk+","+s_date+"," +Decisions[stk]["Decision"] 
                #if logfn != None and stk == "TEL UN Equity": print>> logfn,"intoFile:",stk,Decisions[stk]["Decision"]
                for fscore in F2Scores:
                    s += ","+ str(DATA[stk][fscore]["Score"]) 
                fn.write(s+"\n")
    fn.close()

def concatinate_files(fn_pref,date_start,date_end):
    date1 = date_start.strftime("%Y%m%d")
    date2 = date_end.strftime("%Y%m%d")
    outfile = fn_pref+"_"+date1+"_"+date2+".csv"
    destination = open(outfile,'wb')
    
    decision_date = date_start
    while decision_date <= date_end:
        fn = fn_pref+"_"+decision_date.strftime("%Y%m%d")+".csv"
        if os.access(fn,os.R_OK):
            shutil.copyfileobj(open(fn,'rb'), destination)
            os.remove(fn)
        #else: print "! CAUTION",fn,"not found"
        decision_date += datetime.timedelta(days=1)            
    destination.close()   
        
            
def debug_output(DATA,key_HD,key_Stat,key_Window,F2Scores,CALC_Stats=None,namesOfWeightedAvgs=None,Ranks=None,Decisions=None,date=None,fname=""):   
    if date != None:
        s_date = date.strftime("%Y%m%d")
    else:
        s_date = ""
        
    stk_names = sorted(DATA.keys())
    for fscore in F2Scores:
        headers_s1 = ",,,"

        fn = open("t_"+fname+"_"+fscore+"_"+s_date+".csv",'wb')
        HDheaders = []
        for HD in key_HD:
            for i in range(len(key_Stat)*len(key_Window)):
                HDheaders.append(HD) # = key_HD*len(key_Stat)*len(key_Window)
        headers_s1 += ",".join(HDheaders) 
        if CALC_Stats != None and namesOfWeightedAvgs != None:
            more_head= []
            for HD in key_HD:
                for i in range(len(key_Stat)):
                    more_head.append(HD)
            headers_s1 += ",," + ",".join(more_head)             
        fn.write(headers_s1+"\n")

        stat_s = ",,,"
        statheaders = []
        for stat in key_Stat:
            for i in range(len(key_Window)):
                statheaders.append(stat)
        statheaders = statheaders*len(key_HD)
        stat_s += ",".join(statheaders)
        
        if CALC_Stats != None and namesOfWeightedAvgs != None:
            more_stat = namesOfWeightedAvgs*len(key_HD)
            stat_s += ",," + ",".join(more_stat)
            stat_s += ",,"+",".join(namesOfWeightedAvgs)
        if Ranks != None:
            stat_s += ",,"+",".join(Ranks)
        if Decisions !=None:
            stat_s += ",,Decision"
            
        fn.write(stat_s+"\n")

        wheaders = key_Window*len(key_HD)*len(key_Stat)
        fn.write("Stock,Rank,Score,"+",".join(wheaders)+"\n")

        for stk in stk_names:
            s = stk+","+str(DATA[stk][fscore]["Rank"])+"," +str(DATA[stk][fscore]["Score"])+","
            for HD in key_HD:
                 for stat in key_Stat:
                     for window in key_Window:
                         s += str(DATA[stk][fscore][HD][stat][window]) +","
            if CALC_Stats != None and namesOfWeightedAvgs != None:
                s += ","
                for HD in key_HD:
                    for stat in namesOfWeightedAvgs:
                        s += str(CALC_Stats[stk][fscore][HD][stat]) +","
                
                s += ","
                for stat in namesOfWeightedAvgs:
                    s += str(CALC_Stats[stk][fscore][stat]) +","
            if Ranks != None:
                s += ","
                for stat in Ranks:
                    s += str(CALC_Stats[stk][fscore][stat]) +","                
            if Decisions != None:
                s += ","+ Decisions[stk][fscore] +","                   
                    
            fn.write(s+"\n")
        fn.close()


    

#################################################################################
### stat calculations
#################################################################################
def manipulate_NumTrades(DATA,F2Scores,key_HD,key_Stat,key_Window):
    for fscore in F2Scores:    
        for stk in DATA.keys():
            for HD in key_HD:
                for w in range(len(key_Window)-1):
                    DATA[stk][fscore][HD]["Number Trades"][key_Window[w]] -= DATA[stk][fscore][HD]["Number Trades"][key_Window[w+1]] 
                
                    

def calculate_WeightedAvgs(DATA,LBW_Weights,MHD_Weights,F2Scores,key_HD,key_Stat,key_Window,CALC_Stats,NumTradesWeights):
    ##### Relative RPT (BPS)	Relative Signed Win Rate (%) Number Trades, Stock Return (BPS) 
    ###  Max Drawdown (%)	Relative Sharpe	Relative KRatio    
    
    for fscore in F2Scores:    
        for stk in DATA.keys():
            if stk not in CALC_Stats.keys():
                CALC_Stats[stk] = {}
            CALC_Stats[stk].setdefault(fscore, {})
            
            new_Stats = []
            for HD in key_HD:
                CALC_Stats[stk][fscore].setdefault(HD,{})
                for stat in key_Stat:
                    s_sum = 0
                    num = 0
                    if stat in ['Max Drawdown (%)',"Relative Sharpe",]: #assumes that this stat matters only for LBW of 6 months
                        window = "1 Year"
                        if DATA[stk][fscore][HD][stat][window] != None:
                            s_sum += DATA[stk][fscore][HD][stat][window]
                            num = 1
                    elif stat in ["Relative RPT (BPS)",'Relative Signed Win Rate (%)']: 
                        window = "6 Month"
                        if DATA[stk][fscore][HD][stat][window] != None:
                            s_sum += DATA[stk][fscore][HD][stat][window]
                            num = 1                            
                    elif stat in ["Relative KRatio"]: #assumes that this stat matters only for LBW of 1 year
                        window = "1 Year"
                        if DATA[stk][fscore][HD][stat][window] != None:
                            s_sum += DATA[stk][fscore][HD][stat][window]
                            num = 1     
                    elif stat in ["Stock Return (BPS)"]:
                        window = "1 Month" #assumes that this stat matters only for LBW of 1 month
                        if DATA[stk][fscore][HD][stat][window] != None:
                            s_sum += DATA[stk][fscore][HD][stat][window]
                            num = 1
                    elif stat in ["Number Trades"]:#different from other stats
                        for window in key_Window:
                            if DATA[stk][fscore][HD]["Number Trades"][window] != None:
                                s_sum += DATA[stk][fscore][HD][stat][window]*NumTradesWeights[window]
                                num += NumTradesWeights[window]   
                    else:
                        print "!!! CAUTION",stat,"not sorted"
                                 
#                    if stat not in ["Stock Return (BPS)","Number Trades"]:
#                        for window in key_Window:
#                            if DATA[stk][fscore][HD][stat][window] != None:
#                                s_sum += DATA[stk][fscore][HD][stat][window]*LBW_Weights[window]*DATA[stk][fscore][HD]["Number Trades"][window]
#                                num += LBW_Weights[window]*DATA[stk][fscore][HD]["Number Trades"][window]
              
#                    elif stat in ["Number Trades"]:
#                        for w in range(len(key_Window)):
#                            if w < len(key_Window)-1:
#                                DATA[stk][fscore][HD][stat][key_Window[w]] -= DATA[stk][fscore][HD][stat][key_Window[w+1]] 
#                                s_sum += DATA[stk][fscore][HD][stat][key_Window[w]]*NumTradesWeights2[key_Window[w]]
#                                num += NumTradesWeights2[key_Window[w]]
#                            else:
#                                s_sum += DATA[stk][fscore][HD][stat][key_Window[w]]*NumTradesWeights2[key_Window[w]]
#                                num += NumTradesWeights2[key_Window[w]]                                
#                            
                    newK_stat = "Wavg "+stat
                    if newK_stat not in new_Stats:
                        new_Stats.append(newK_stat)
                    if num != 0:
                        CALC_Stats[stk][fscore][HD][newK_stat] = s_sum/float(num)
                    elif num == 0 and s_sum != 0:#should never be here
                        print "!!! check if there is an error in calc",newK_stat,"for",stat,HD,stk,fscore
                        CALC_Stats[stk][fscore][HD][newK_stat] = None 
                    else:
                        CALC_Stats[stk][fscore][HD][newK_stat] = None                        


            for stat in new_Stats:
                s_sum = 0
                num = 0
                for HD in key_HD:
                    if CALC_Stats[stk][fscore][HD][stat] != None:
                        s_sum += CALC_Stats[stk][fscore][HD][stat]*MHD_Weights[HD]
                        num += MHD_Weights[HD]
                if num != 0:
                    CALC_Stats[stk][fscore][stat] = s_sum/float(num)
                else:
                    CALC_Stats[stk][fscore][stat] = None
    return new_Stats
    

def rank_byAll_Stats(DATA,F2Scores,CALC_Stats,namesOfWeightedAvgs):
    ranks = []    
    for stat in namesOfWeightedAvgs:
        rank_byStat(DATA,F2Scores,CALC_Stats,stat)
        ranks.append("Rank "+stat) #probably not the best way to do it, but ok for now
    return ranks
     
                      
def rank_byStat(DATA,F2Scores,CALC_Stats,stat): 
    for fscore in F2Scores:  
        v = []
        for stk in DATA.keys():
            if  CALC_Stats[stk][fscore][stat] != None:
                v.append(CALC_Stats[stk][fscore][stat])
        v.sort()
        
        for stk in DATA.keys():
            if  CALC_Stats[stk][fscore][stat] == None:
                 CALC_Stats[stk][fscore]["Rank "+stat] = None
            else:
                for i in range(len(v)):
                    if CALC_Stats[stk][fscore][stat] == v[i]:
                        CALC_Stats[stk][fscore]["Rank "+stat] = i
                        break

#################################################################################
### strategies
#################################################################################

####################################################################
"""
In this strategy I tried a lot. 
The original on BandSize3 was not promising: alpha-L 3.1 but with sharpe 0.11; Alpha-S -1.4. with the sharpe of -0.04. 
Ret -1.7%.
I tried using BandSize2.5 without much improvement. 

Mostly I tried with abs(F2) > 2.5 (at time with abs(F2)>2). 

Played with limit on the Rank of RelSharpe. Wasn't very useful, and sometimes we are forced
 into limits based on the selection criteria, i.e., allowing strict bounds on all filters takes a while to converge to
 the limit of 30 choices, and relaxing them too much also takes long to converge. Hence adding filters necessitates 
 relaxing bounds on the filters that were there in the previous iteration.

NumTrds can be significant and important and may not. Why? With BandSize3, the band (-inf,-6) had very few numTrds, hence
relaxing numTrds was important. 

Adding Ranking of CumRelRet wasn't helping much.


So I changed to have RelSharpe (1Year) on Bandsize2, it improved a bit, but not enough.

The last attempt was to add CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] in order to improve perf, 
and that HELPED. I wonder if more could be done ..... How about tightening some and relaxing other filters?  
or even swapping filters in place?

Swapping did not help (I swapped RRPT and put it before RelSharpe). It's not performing well.  It's a bit of a mystery that combining F2 score and Sharpe 
is not helpful. Somehow it goes against my gut feel.

I experimented with MHD3 as well, and it did not do well either.
Experimented with F2>3.0 and RRPT and Sharpe of 6M on bandsize3, didn't like that either.

            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 70+relax:
                if abs(DATA[stk][fscore]["Score"]) > 2.5:
                    if CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] > 400 +relax:
                        if CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] > 400+relax:
"""
####################################################################

def choose_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 5
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = 0
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=17:
        num_iter += 1
        relax +=5
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
    #print "TTL Shorts",ttl      
def tune_2Short_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] >50+relax:
                if abs(DATA[stk][fscore]["Score"]) > 3.0:
                    if CALC_Stats[stk][fscore]["Wavg Relative Signed Win Rate (%)"] < -55:
                        if CALC_Stats[stk][fscore]["Wavg Relative RPT (BPS)"] < -30: 
                            if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] < 450:
                            #if CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] < 200 -relax:
                                if final:
                                    Decisions[stk][fscore] = "S"
                                num += 1
        #print fscore,"num Shorts",num
        ttl += num
    print "TTL Shorts",ttl        
    return ttl
def choose_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 5
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = relax
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=17:
        num_iter += 1
        relax += 5
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)     
    #print "TTL Longs",ttl   
def tune_2Long_byF2Ranks(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 50+relax:
                if abs(DATA[stk][fscore]["Score"]) > 3.0:
                    if CALC_Stats[stk][fscore]["Wavg Relative Signed Win Rate (%)"] > 55:
                        if CALC_Stats[stk][fscore]["Wavg Relative RPT (BPS)"] > 30:
                            if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 50:
                            #if CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] > 300+relax:
                                if final:
                                    Decisions[stk][fscore] = "L"
                                num += 1
        #print fscore,"num Longs",num
        ttl += num
    print "TTL Longs",ttl        
    return ttl
    

#################################################################################
"""
by F2(rank) + CumRelRet

   if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 100 + relax:
       if DATA[stk][fscore]["Rank"] > 450+relax (<50-relax for short):
           if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 50  (<450 for Short):

What I have tried for byF2Ret:
1a) running it with ["Rank Wavg Number Trades"] > 100+relax  and DATA[stk][fscore]["Rank"] > 450+relax (<50-relax for short)
 did not do well  on Alpha-long, but not bad on Alpha-short, though Alpha-short is not very consistent;
 
1b) running it with ["Rank Wavg Number Trades"] > 100+relax  and DATA[stk][fscore]["Rank"] > 450+relax (<50-relax for short)
    ["Rank Wavg Stock Return (BPS)"] > 50 (<450 for Short) improved Alpha-long but , but degraded Alpha-short.
 
2) running it with ["Rank Wavg Number Trades"] > 10+relax  and DATA[stk][fscore]["Rank"] > 450+relax (<50-relax for short)
  ["Rank Wavg Stock Return (BPS)"] > 50 (<450 for Short), improved Alpha-long, but improved little on Alpha-short.
  
3) running with ["Rank Wavg Number Trades"] > +relax  and DATA[stk][fscore]["Rank"] > 450+relax (<50-relax for short)  
  ["Rank Wavg Stock Return (BPS)"] > 50 (<450 for Short), improved upon 2), i.e., significantly improved Alpha-long.
  
The best performance is for March-Sept 2013 is
for Short: ["Rank Wavg Number Trades"] > 100+relax  and DATA[stk][fscore]["Rank"] < 50+relax

for Long:  ["Rank Wavg Number Trades"] > + relax and DATA[stk][fscore]["Rank"] > 450+relax and 
                    ["Rank Wavg Stock Return (BPS)"] > 50:
  
however, I belive it's overfited, and the best is to do this:
["Rank Wavg Number Trades"] > +relax  and DATA[stk][fscore]["Rank"] > 460+relax  
  ["Rank Wavg Stock Return (BPS)"] > 60 
  
["Rank Wavg Number Trades"] > 50 +relax  and DATA[stk][fscore]["Rank"] < 50-relax   
  ["Rank Wavg Stock Return (BPS)"] < 440 

use F(8) and F(16)  
""" 
#################################################################################
def choose_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 4
    num_chosen = 33 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = relax
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=13:
        num_iter += 1
        relax += 3
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
    #print "TTL Longs",ttl   

def tune_2Long_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > + relax:
                if DATA[stk][fscore]["Rank"] > 460+relax:
                    if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 60:
                        if final:
                            Decisions[stk][fscore] = "L"
                        num += 1
        #print fscore,"num Longs",num
        ttl += num
    print "TTL Longs",ttl        
    return ttl

    
def choose_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 4
    num_chosen = 33 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = 0
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=13:
        num_iter += 1
        relax +=3
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
    #print "TTL Shorts",ttl        

def tune_2Short_byF2Ret(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 50 +relax: #if minimal ranking on NumTrade, +relax
                if DATA[stk][fscore]["Rank"] < 50-relax:
                    if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] < 440:
                        if final:
                            Decisions[stk][fscore] = "S"
                        num += 1
        #print fscore,"num Shorts",num
        ttl += num
    print "TTL Shorts",ttl        
    return ttl
            
##############################################################################
### BASE
##############################################################################    
def choose_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 2
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = relax
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=13:
        num_iter += 1
        relax +=1
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
    #print "TTL Longs",ttl   

def tune_2Long_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if DATA[stk][fscore]["Rank"] > 469+relax:
                #if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 50:
                    if final:
                        Decisions[stk][fscore] = "L"
                    num += 1
        #print fscore,"num Longs",num
        ttl += num
    print "TTL Longs",ttl        
    return ttl

def choose_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 2
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = 0
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=13:
        num_iter += 1
        relax +=1
        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
    #print "TTL Shorts",ttl        

def tune_2Short_Base(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):
    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if DATA[stk][fscore]["Rank"] < 31-relax:
                #if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] < 450:
                    if final:
                        Decisions[stk][fscore] = "S"
                    num += 1
        #print fscore,"num Shorts",num
        ttl += num
    print "TTL Shorts",ttl        
    return ttl                
####################################################################
"""
If  Rel Sharpe(6M) is used, then one must use NumTrades filter. And for BandSize 2.5, NumTrades should be at least 80.
The performance of this strategy is not helped by SignedWin in the case of BandSize3 -inf,-6,-3,0.

The strategy seems to have weak alpha-Short and not such a great alpha-long. It performs ok, even for BandSize2,
but not great.

using Sharpe(1Y)
putting RRPT before RelSharpe is not a good idea. Here is what I've tried and 
 CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] >100+relax:
     CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] > 450 +relax:
         CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] > 400+relax:         
            CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 50:
and it did not produce good results

and neither has this one:
 if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 250+relax:
                if CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] > 410 +relax:
                    if CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] > 400+relax: 

I acknowledge there there are many more things to try. Maybe one of many possible combinations would help. 
I think the bandsize is significant too. The original RelSharpe(6M) with numTrades(I dont remember) on BandSize3 
seem to have had the best Short-alpha.

It seems that using short-term stats (say 6M) improved short-alpha but deteriorates long-alpha, and using long-term stats   
does the opposite.

And I am no sure if numTrades is important. It might be but only for certain BandSize.

I think I will stop with this strategy for now.

            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 200+relax:
                if CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] > 420 +relax:
                    if CALC_Stats[stk][fscore]["Rank Wavg Relative Sharpe"] > 420+relax: 
"""
####################################################################
def choose_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 3
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = relax
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=15:
        num_iter += 1
        relax += 3

        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
         
    print "TTL Longs",ttl   

def tune_2Long_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):

    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] > 100+relax:
                if CALC_Stats[stk][fscore]["Wavg Relative Signed Win Rate (%)"] > 60:
                    if CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] > 400 + relax: 
                        if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] > 50:
                            if final:
                                Decisions[stk][fscore] = "L"
                            num += 1
        #print fscore,"num Longs",num
        ttl += num
    print "TTL Longs",ttl        
    return ttl

def choose_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions):
    margin_on_number_of_stk = 3
    num_chosen = 30 #should be bigger than 30 if more than 1 Fscore is used
    relax = 0
    ttl = tune_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
    num_iter = 0
    last_relax = 0
    while abs(ttl -num_chosen) > margin_on_number_of_stk and num_iter <=15:
        num_iter += 1
        relax +=3

        if ttl < num_chosen - margin_on_number_of_stk:
            ttl = tune_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=-relax)
            last_relax = -relax
        elif ttl > num_chosen + margin_on_number_of_stk:
            ttl = tune_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=relax)
            last_relax = relax
    ttl = tune_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=last_relax,final=True)
         
    print "TTL Shorts",ttl      

def tune_2Short_byRanks(DATA,F2Scores,CALC_Stats,Decisions,relax=0,final=False ):

    ttl = 0
    for fscore in F2Scores:
        num = 0
        for stk in DATA.keys():
            if CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] != None \
            and CALC_Stats[stk][fscore]["Rank Wavg Number Trades"] >100+relax:
                if CALC_Stats[stk][fscore]["Wavg Relative Signed Win Rate (%)"] < -60:
                    if CALC_Stats[stk][fscore]["Rank Wavg Relative RPT (BPS)"] < 100 - relax: 
                        if CALC_Stats[stk][fscore]["Rank Wavg Stock Return (BPS)"] < 450:
                            if final:
                                Decisions[stk][fscore] = "S"
                            num += 1
        #print fscore,"num Shorts",num
        ttl += num
    print "TTL Shorts",ttl        
    return ttl

####################################################################
def make_final_LongDecisions(DATA,F2Scores,Decisions,num_THs_met = 1,logfn = None):
    longs = 0
    for stk in DATA.keys():
        num = 0
        for fscore in F2Scores:
            if Decisions[stk][fscore] == "L":
                num += 1
        if num >= num_THs_met:
            Decisions[stk]["Decision"] = "L"   
            #if stk == "TEL UN Equity": print>> logfn,"Final:",stk,"L"
            longs += 1
    print "TTL Longs",longs

def make_final_ShortDecisions(DATA,F2Scores,Decisions,num_THs_met = 1,logfn = None):
    shorts = 0
    for stk in DATA.keys():
        num = 0
        for fscore in F2Scores:
            if Decisions[stk][fscore] == "S":
                num += 1
        if num >= num_THs_met:
            Decisions[stk]["Decision"] = "S"
            #if stk == "TEL UN Equity": print>> logfn,"Final:",stk,"S"
            shorts += 1
    print "TTL Shorts",shorts    


####################################################################





#################################################################                          
####  under construction       ###################################
#################################################################                                             

                
            
            
            
    

        