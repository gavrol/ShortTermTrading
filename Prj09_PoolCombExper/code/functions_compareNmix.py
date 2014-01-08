# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 08:16:27 2013

@author: olenag
"""

import os
from pandas import *
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def format_legend(leg):
    try:
        for text in leg.get_texts():
            text.set_fontsize('small')
        for line in leg.get_lines():
            line.set_linewidth(0.7)
    except:
        pass

def format_legend_total(ax):
        # Shink current axis's height by 20% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.05,
                     box.width, box.height * 0.95])
    ax.set_xlabel('').set_visible(False)
    # Put a legend below current axis
    t_leg = ax.legend(loc='upper center', bbox_to_anchor=(.5, -0.1),
              fancybox=True, shadow=True, ncol=1)

    format_legend(t_leg)
    

def find_min(df):

        min_ = 100
        for i in range(5,len(df.index)):
            if abs(df.iloc[i]) < min_ and abs(df.iloc[i])> 0:
                min_ = abs(df.iloc[i])
        return min_
    
def compareSets(pools,indicator,side,methodCombination,filterCombination,resultDirectory):
    
    processedPools = 0
    globalUnion = ''
    globalIntersect = {}
    for currentPool in pools:
        processedPools+=1
        for nextPool in pools[processedPools:]:
            if nextPool == currentPool:
                continue
            print side+" "+currentPool+" "+nextPool
            union = indicator[currentPool]+indicator[nextPool]
            union = union.apply(np.sign)
            intersection = indicator[currentPool]*indicator[nextPool]

            if type(globalUnion) != DataFrame:
                globalUnion = union
                globalIntersect = intersection
            else:
                globalUnion += indicator[nextPool]
                globalIntersect *= indicator[nextPool]
            
    
    globalUnion = globalUnion.apply(np.sign)
    combinedPool = globalUnion
    globalUnionCount = globalUnion.sum(axis=1) 
    globalIntersectCount = globalIntersect.sum(axis=1)
    
    if side.lower() == "long":
        print "Max number:",globalUnionCount.max()
        print "Lowest number in combined portfolio:", find_min(globalUnionCount)
    else:
        print "Max number:",abs(globalUnionCount.min())
        print "Lowest number in combined portfolio:", find_min(globalUnionCount)        
    

    fig_Union,ax = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)
    globalUnionCount.plot(label=methodCombination, lw=1,alpha=.8,ax=ax)
    fig_Union.suptitle("Number of UNIQUE stocks in "+side,#+' '+methodCombination,
                       ha='center',va='top',fontsize=11,color='brown',fontweight='bold') 
    format_legend_total(ax)
    plt.savefig(resultDirectory+side+'_'+filterCombination +"_UNION.png")

    

    fig_Int,ax_Int = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)   
    globalIntersectCount.plot(label=methodCombination,lw=1,alpha=.8,ax=ax_Int) #label='ALL POOLS'
    fig_Int.suptitle("Number of COMMON stocks in "+side,
                     ha='center',va='top',fontsize=11,color='black',fontweight='bold')
    format_legend_total(ax_Int)
    plt.savefig(resultDirectory+side+'_'+filterCombination+"_INTERSECTION.png")
    
    #export to files
    globalUnion.to_csv(resultDirectory+side+'_'+filterCombination+"_UNION.csv")
    globalIntersect.to_csv(resultDirectory+side+'_'+filterCombination+"_INTERSECTION.csv")
    return combinedPool

def compare_2_holdings(fn1,fn2,resultDirectory,startDate,log = None):
    D_pools = {}
    pool1_n = fn1.split(os.sep)[-1].split(".")[0]
    pool2_n = fn2.split(os.sep)[-1].split(".")[0]
    D_pools[pool1_n] = fn1
    D_pools[pool2_n] = fn2
    poolNames = [pool1_n,pool2_n]
  
    longHolding = {}
    shortHolding = {}    
    for poolN in D_pools.keys():
        pool = DataFrame.from_csv(D_pools[poolN])[startDate:]
        
        longHoldingTmp = pool.copy()
        longHoldingTmp[longHoldingTmp<0] = 0
        longHoldingTmp[longHoldingTmp>0] = 1
        longHolding[poolN] = longHoldingTmp
        #longHolding[poolN].to_csv(poolN+" LONG.csv")
        shortHoldingTmp = pool.copy()
        shortHoldingTmp[shortHoldingTmp>0] = 0
        shortHoldingTmp[shortHoldingTmp<0] = -1
        shortHolding[poolN] = shortHoldingTmp
        #shortHolding[poolN].to_csv(poolN+" SHORT.csv")
        positionF_content = longHolding[poolN] + shortHolding[poolN]
        positionF_content.to_csv("positionF_"+poolN.replace("holdings_","")+".csv")
    
     

    methodCombination = "\n ".join(poolNames).replace("holdings_","").replace("_TISL_0_Position","")    
    filterCombination  = "__and__".join(poolNames).replace("holdings_","").replace("_TISL_0_Position","")   
    combLong = compareSets(poolNames,longHolding,"LONG",methodCombination,filterCombination,resultDirectory)
    combShort = compareSets(poolNames,shortHolding,"SHORT",methodCombination,filterCombination,resultDirectory)
    
    """now combining pools to show that after long and short net out we still have plenty of positions"""
#    combLong.to_csv("t_LONG.csv")
#    combShort.to_csv("t_SHORT.csv")
    combLongCount = combLong.sum(axis=1)
    combShortCount = combShort.sum(axis=1) 
    print "max num of pos in combined Long:", combLongCount.max()
    print "max num of pos in combined Short:", abs(combShortCount.min())
    TTLcomb = combLong + combShort
    TTLcomb.to_csv(resultDirectory+"positionF_"+filterCombination+".csv")


    TTLongCount =TTLcomb[TTLcomb>0].sum(axis=1)
    print "max number of Long in the final:",TTLongCount.max()
    print "avg Longs:", round(TTLongCount.mean(),0)
    print "Lowest number of LONGs in a combined portfolio:", find_min(TTLongCount)
    TTShortCount =TTLcomb[TTLcomb<0].sum(axis=1)
    print "max number of Short in the final:",abs(TTShortCount.min())   
    print "avg Short:", abs(round(TTShortCount.mean(),0))
    print "Lowest number of SHORTs in a combined portfolio:", find_min(TTShortCount)
    
    if log != None:
        log.write(filterCombination.replace("__and__",",")+","+str(TTLongCount.max())+","+str(find_min(TTLongCount))+","+str(round(TTLongCount.mean(),0))+","+str(abs(TTShortCount.min()))+"," +str(find_min(TTShortCount))+","+str(abs(round(TTShortCount.mean(),0)))+"\n"  )  