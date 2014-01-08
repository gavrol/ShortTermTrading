# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:44:57 2013

@author: jaroslawb
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
    

def compareSets(pools,indicator,side,methodCombination,filterCombination,directory,resultDirectory):
    
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
            unionCount = union.sum(axis=1)
            intersection = indicator[currentPool]*indicator[nextPool]
            intersectionCount = intersection.sum(axis=1)


            if type(globalUnion) != DataFrame:
                globalUnion = union
                globalIntersect = intersection
            else:
                globalUnion += indicator[nextPool]
                globalIntersect *= indicator[nextPool]
            
    
    globalUnion = globalUnion.apply(np.sign)
    globalUnionCount = globalUnion.sum(axis=1) 
    globalIntersectCount = globalIntersect.sum(axis=1)
    

#    fig_Union,ax = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)
#    globalUnionCount.plot(label=methodCombination, lw=1,alpha=.8,ax=ax)
#    fig_Union.suptitle("Number of UNIQUE stocks in "+side,#+' '+methodCombination,
#                       ha='center',va='top',fontsize=11,color='brown',fontweight='bold') 
#    format_legend_total(ax)
#    plt.savefig(resultDirectory+side+'_'+filterCombination +"_UNION.png")

    

    fig_Int,ax_Int = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)   
    globalIntersectCount.plot(label=methodCombination,lw=1,alpha=.8,ax=ax_Int) #label='ALL POOLS'
    fig_Int.suptitle("Number of COMMON stocks in "+side,
                     ha='center',va='top',fontsize=11,color='black',fontweight='bold')
    format_legend_total(ax_Int)
    plt.savefig(resultDirectory+side+'_'+filterCombination+"_INTERSECTION.png")
    
    #export to files
#    globalUnion.to_csv(resultDirectory+side+'_'+filterCombination+"_UNION.csv")
    globalIntersect.to_csv(resultDirectory+side+'_'+filterCombination+"_INTERSECTION.csv")
    

if __name__=="__main__":

    directory = ".."+os.sep+'data'+os.sep
    
    resultDirectory = directory+'outputs'+os.sep
    if not os.path.exists(resultDirectory):
        os.makedirs(resultDirectory)
    

    methods = ["SP500","RIEF700_LM_RIEF_Bottom600"]#"PHG_US","RIEF700_LM_RIEF_Top200"]#"RIEF700_LM_RIEF_Top100"]#,,]
    filters = methods
                       
    #print "Directories to scan", methods
    print "A/V filters:",filters
    
    PoolIndicator = {} #dict of DataFrames

    longHolding = {}
    shortHolding = {}    
    
    for method in methods:
        fn = method+".csv"
        PoolIndicator[method] = DataFrame.from_csv(directory+fn)[datetime(2005,2,1):]
           
    for f1 in range(len(filters)-1):
        for f2 in range(f1+1,len(filters)):
            filterCombination = filters[f1]+'_AND_'+filters[f2]
            methodCombination = filters[f1]+'\n'+ filters[f2]
            combFilters = [filters[f1],filters[f2]]
            print "combination of filters:",combFilters
            compareSets(combFilters,PoolIndicator,"Pool",methodCombination,
                        filterCombination,directory,resultDirectory)

