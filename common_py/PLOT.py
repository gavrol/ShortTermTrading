# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:06:40 2013

@author: olenag

PURPOSE: plotting functions
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
import pandas as pd


COLORS =["#8533D6","#5C5C8A","#a36e81","#7ba29a","#6600FF","#5C85D6","#006600","#1963D1","#0066FF","#5C5C8A","#6666FF",]
light_COLORS = ["#FFFF99","#66CCFF","#7f7f7f","#B8E65C","#52A3CC",]
Q_COLORS = ["#FFFF99","#1963D1","#0066FF","#B8E65C",]
short_color = "#FF3300"
long_color = "#009900"
STR_COLORS = ["#3300FF","#FF6600","#585858","#a36e81","#006600","#FF0000","#FF3399","#6600FF","#8533D6","#7ba29a","#5C5C8A",]

#############################################
## auxiliary functions
#############################################

def format_legend(leg):
    try:
        for text in leg.get_texts():
            text.set_fontsize('x-small')
        for line in leg.get_lines():
            line.set_linewidth(0.7)
    except:
        pass

def add_to_scatter_plots(ax,xlabel,title):
    ax.axhline(color='#000000')
    ax.axvline(color='#000000')
    ax.set_xlabel(xlabel,fontsize=9)
    ax.tick_params(labelsize=9)
    ax.set_title(title,fontsize=10,color='blue')
    ax.grid(True)
    t_leg = ax.legend(loc='best')
    format_legend(t_leg)

def form_suptitle(suptitle,date1=None, date2=None):
    if date1 != None:
        suptitle += " for "+date1.strftime("%d/%m/%Y")
    if date2 != None:
        suptitle += " thru "+ date2.strftime("%d/%m/%Y")
    return suptitle


def format_plot(ax,x_label,title=None,y_label = None,use_legends=True):
    ax.set_xlabel(x_label,fontsize=9)
    ax.axhline(color='#000000')
    if use_legends:
        t_leg = ax.legend(loc='best')
        format_legend(t_leg)
    ax.tick_params(labelsize=9)
    if title != None:
        ax.set_title(title,color='blue',fontsize=8)
    if y_label != None:
         ax.set_ylabel(y_label,fontsize=9)
        
#######################################################
### on DEMAND
#####################################################        
def add_range_lines(ax,df,var):
    ax.axhline(y=df[var].mean()+2*df[var].std(),color="#551076",linewidth=0.8,alpha=0.8)
    ax.axhline(y=df[var].mean()-2*df[var].std(),color="#551076",linewidth=0.8,alpha=0.8) 

def plotTrades(df,ax):
    for i in df["position"].index:
        if df["position"].loc[i] == 1:
            ax.axvline(x=i, color='#33CC33',alpha=0.4, linewidth=2.2)
        if df["position"].loc[i] == -1:
            ax.axvline(x=i, color='#FF3300',alpha=0.4, linewidth=2.2)

def plotSignals(df,signal,ax,shortIN=None,longIN=None,shortOUT=None,longOUT=None):
    if shortIN==None or longIN==None:
        for i in df[signal].index:
            if df[signal].loc[i] <= df[signal+"Qlower"].loc[i]:
                ax.axvline(x=i, color='g')
            if df[signal].loc[i] >= df[signal+"Qupper"].loc[i]:
                ax.axvline(x=i, color='r')    
    else:#for the case when shortIN/longIN are set a priori
        for i in df[signal].index:
            if df[signal].loc[i] <= longIN:
                ax.axvline(x=i, color='g')
            if df[signal].loc[i] >= shortIN:
                ax.axvline(x=i, color='r')    
        
def plot_TradesEarnings(df,ax,var="trade_profit"):
    """assumes trade_profit or something similar has been defined,
       the brighter the color the more money has been involved (lost or gained)"""
    for i in df["position"].index:
        if df["position"].loc[i] == 1 and df[var].loc[i] > 0:#gained money in LONG
            alpha = 0.3+min(30*df[var].loc[i],0.5)
            ax.axvline(x=i, color='#556b2f',alpha=alpha, linewidth=2.3)
        if df["position"].loc[i] == 1 and df[var].loc[i] < 0: #lost money in LONG
            alpha=0.3+min(-30*df[var].loc[i],0.5)
            ax.axvline(x=i, color='#00FF00',alpha=alpha, linewidth=2.3)
        if df["position"].loc[i] == -1 and  df[var].loc[i] > 0: #gained money in Short
            alpha=0.3+min(30*df[var].loc[i],0.5)
            ax.axvline(x=i, color='#FF6600',alpha=alpha, linewidth=2.3) #orange
        if df["position"].loc[i] == -1 and  df[var].loc[i] < 0: #lost money in SHORT
            alpha=0.3+min(-25*df[var].loc[i],05)
            ax.axvline(x=i, color='#FF66CC',alpha=alpha, linewidth=2.3) #bright pink           



#########################################
### compare strategies
#########################################    

def compare_strategies(INV,var="%Cumulative RelRet",suptitle ='',fig_fn=None,date1=None,date2=None,position_type=None):
    fig,axes = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)    
    suptitle = form_suptitle(suptitle,date1,date2)
    if position_type == None:
        pos_color = 'black'
    elif position_type.lower() == 'short':
        pos_color = 'red'
    elif position_type.lower() == 'long':
        pos_color = 'green'
    else:
        pos_color = 'blue'
        
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color=pos_color) 
    
    for inv in INV:
        inv.df[var].plot(kind='line',color=STR_COLORS[INV.index(inv)],label=inv.strategy_name,ax=axes,alpha=0.9)

    format_plot(axes,"Date",y_label=var)        
            
    #plots finished
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()     
##############################################
### combination plots
##############################################
def add_OLSline(ax,alpha,beta,X,beta_pScore):
    ax.plot(X,beta*X+alpha,label="OLS fitted Line (p="+str(round(beta_pScore,2))+")",color='#0066FF',ls=':',alpha=(1-beta_pScore))
 
 
 
def combo_TimeSeries_Scatter(df,stock_name,score,yVar1=None,yVar2=None,longIN=None,longOUT=None,shortIN=None,shortOUT=None,
                         suptitle ='',fig_fn=None,date1=None,date2=None,mean_per= 1,ymin=None,ymax=None,stock=None,
                         includeTrades=False,includeTradesEarnings=False,includeSignals=False):
    """one ALWAYS needs a score here for the first plot"""
    if yVar1 != None and yVar2 != None:
        nrows = 2
    else:
        nrows = 1
    fig,axes = plt.subplots(nrows=nrows,ncols=1,sharex=False,sharey=False)
    fig.subplots_adjust(hspace=0.25)
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    if nrows == 2:
        ax = axes[0]
    else:
        ax = axes
    #the scatter plot    
    if yVar1 != None:
        title =  score+" vs. "+ yVar1 +" of "+stock_name
        if shortIN == None or longIN==None:
            strong_color = np.where(((df[score] < df[score+"Qlower"]) | (df[score] > df[score+"Qupper"])), 'b','y' )
        else:
            strong_color = np.where(((df[score] <= longIN) | (df[score] >= shortIN)), 'b','y' )
            
        ax.scatter(df[score],df[yVar1],marker='+',c=strong_color,label="")
    
        if stock != None and stock.OLS_Statistics_F2vsRelRet[score] != {}: # case when OLS for F2 has been done
            add_OLSline(ax,stock.OLS_Statistics_F2vsRelRet[score]['OLS_alpha'],
                            stock.OLS_Statistics_F2vsRelRet[score]['OLS_beta'],
                            df[score],stock.OLS_Statistics_F2vsRelRet[score]['beta-pScore'])
        add_to_scatter_plots(ax,score,title)
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)

    if nrows == 2:
        ax = axes[1]     

    #time series to plot   
    if yVar2 != None:
        t_title = yVar2 
        df[t_title].plot(kind='line',color=COLORS[0],label=t_title,ax=ax,alpha=0.9)
        pd.rolling_mean(df[t_title],mean_per).plot(color=COLORS[0],ax=ax,alpha=0.75,linewidth=3,label=str(mean_per)+"D rolling mean") #ls=':'
                
        if ("RelRet" in t_title) or ("RawRet" in t_title):
            add_range_lines(ax,df,t_title)

        if includeTradesEarnings:
            plot_TradesEarnings(df,ax)        

        if includeSignals:
            plotSignals(df,score,ax,shortIN=shortIN,longIN=longIN,shortOUT=shortOUT,longOUT=longOUT)

        if includeTrades:
            plotTrades(df,ax)

        format_plot(ax,"Date")        
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)

            
    #plots finished
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()     


###############################################
####### for time series #######################
###############################################
def mutliple_TimeSeries_on_ONEplot(df,VARS,stock_name='',Yaxis='',suptitle ='',colors = None,fig_fn=None,date1=None,date2=None):
    """very useful to plot short and long on a same graph, 
    but can be used for other purposes as well"""
    fig,axes = plt.subplots(nrows=1,ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)    
    suptitle = form_suptitle(suptitle,date1,date2)

    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color='black') 
    for v in range(len(VARS)):  
        var = VARS[v]
        if (var.lower().find("long")>=0):
            color = 'green'
        elif (var.lower().find('short')>= 0):
            color = 'red'
        else:
            color = COLORS[v]
        df[var].plot(kind='line',color=color,label=var,ax=axes)
    
        if var.lower().find("relret")>=0:
            axes.axes.set_ylim(-0.05,0.05)

    format_plot(axes,"Date",y_label=Yaxis)        


            
    #plots finished
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()  


def TimeSeries(df,stock_name,VARS,signal=None,longIN=None,longOUT=None,shortIN=None,shortOUT=None,
                         suptitle ='',fig_fn=None,date1=None,date2=None,mean_per=1,ymin=None,ymax=None,
                         includeTrades=False,includeTradesEarnings=False,includeSignals=False):
                             #for most stacked graphs enforce ymin=ymax=None as different scales apply
                    
    """Multiple Windows, shared X-axis. perfect for time series.
    
    This function allows to graphs as many variables (in vector VARS) on the shared X-axis
    but in separate windows, hence allowing to juxtaposition different varibles which cannot be
    compared well on the same Y-axis.

    the graphs have rolling mean plotted on top of each statistic.    
    """
    fig,axes = plt.subplots(nrows=len(VARS),ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)
    #fig.set_size_inches(25.5,20.5)
    
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    for f in range(len(VARS)):  
        if len(VARS) == 1:
            ax = axes
        else:
            ax = axes[f]
        t_title = VARS[f] 

        df[t_title].plot(kind='line',color=COLORS[f],ax=ax,alpha=0.9,label=t_title)

        if mean_per > 1 and t_title.find("Close") < 0:
            pd.rolling_mean(df[t_title],mean_per).plot(ax=ax,color=COLORS[f],linewidth=2,label=str(mean_per)+"D rolling mean") #color="#52A3CC",alpha=0.70,linewidth=1.9,style="k--"
        
        if ("RelRet" in t_title) or ("RawRet" in t_title):
            add_range_lines(ax,df,t_title)        

        if includeTradesEarnings:
            plot_TradesEarnings(df,ax)        

        if includeSignals and signal!=None:
            plotSignals(df,signal,ax,shortIN=shortIN,longIN=longIN,shortOUT=shortOUT,longOUT=longOUT)

        if includeTrades:
            plotTrades(df,ax)


        if f == len(VARS)-1:
            format_plot(ax,"Date",title=t_title,use_legends=False)        
        else:
            format_plot(ax,"",title=t_title,use_legends=False) 
        if ymin != None:
            ax.axes.set_ylim(ymin,ymax)    
        if t_title.lower() in ["oorelret","ccrelret"]:
            ax.axes.set_ylim(-0.06,0.06)
        if t_title.lower() in ["oorelret(3d avg)","ccrelret(3d avg)"]:
            ax.axes.set_ylim(-0.03,0.03)
                  
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()         


#########################################
### histograms
#########################################    

def format_histogram(ax,title=None,xlab="",ylab="",index=0):
    if title != None:
        ax.set_title(title,color=COLORS[index],fontsize=9,fontweight='bold')
    ax.set_xlabel(xlab,fontsize=9)
    ax.set_ylabel(ylab,fontsize=9)
    ax.tick_params(labelsize=9)                 
    
    
def result_comparison_histograms(df,VARS,numBins=100,
                         suptitle ='',fig_fn=None,date1=None,date2=None,median=False):
                             
    fig,axes = plt.subplots(nrows=len(VARS),ncols=1,sharex=True,sharey=False)
    fig.subplots_adjust(hspace=0.15)    
    suptitle = form_suptitle(suptitle,date1,date2)
    fig.suptitle(suptitle,ha='center', va='center',fontsize=10,color="#FF3300") 
    
    for f in range(len(VARS)):  
        if len(VARS) == 1:
            ax = axes
        else:
            ax = axes[f]
        var = VARS[f]
        df[var].hist(bins=numBins,color=COLORS[f],ax=ax) #label=t_title,
        if median:    
            ax.axvline(x=df[var].quantile(0.5),linewidth=4, color='r')  
        format_histogram(ax,var,ylab=var,index=f)
        
    if fig_fn != None:
        plt.savefig(fig_fn)  
    else:
        plt.show()         
    