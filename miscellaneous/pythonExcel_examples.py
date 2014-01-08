# -*- coding: utf-8 -*-
"""
Created on Tue Oct 01 16:29:42 2013

@author: olenag
"""

### parts of old main
    for stock_name in StockNames: 
        ttl_profit = 0
        elem = 0
        for investment in Investments:
            if investment.stock_name == stock_name:
                print investment.stock_name,investment.strategy_name,round(investment.TTLreturn,4),investment.start_date,investment.end_date,investment.fscore2apply
                ttl_profit += investment.TTLreturn
                elem += 1    
    if Investments != []:    
        functions_Prj02.write_earnings_summary_2XLS_byTimePeriod(out_dir+"summary"+time_stamp+".xls",StockNames,TimePeriods,Investments)

def write_earnings_summary_2XLS_byTimePeriod(fn,StockNames,TimePeriods,Investments):
    import xlwt
    wkbk = xlwt.Workbook()
    sh1 = wkbk.add_sheet("Percentage RelRet")
    sh2 = wkbk.add_sheet("RelRet in Bpts per DayInMarket")    
    strategies = get_strategies(Investments)
    
    headers = ["start_date","end_date"]
    
    for stock_name in StockNames:
        for strategy in strategies:
            headers.append(stock_name+" "+ strategy)
    

    sh1_content = []
    sh2_content = []
    
    for d in range(len(TimePeriods)-1):
        line_sh1 = []
        line_sh2 = []
        line_sh1.extend([TimePeriods[d].strftime("%d/%m/%Y"),TimePeriods[d+1].strftime("%d/%m/%Y")]) 
        line_sh2.extend([TimePeriods[d].strftime("%d/%m/%Y"),TimePeriods[d+1].strftime("%d/%m/%Y")])
        
        for stock_name in StockNames:
            for strategy in strategies:
                for inv in Investments:
                    if inv.stock_name == stock_name and inv.start_date == TimePeriods[d] and inv.end_date ==TimePeriods[d+1] \
                    and inv.strategy_name == strategy:
                        line_sh1.append(str(round(inv.TTLreturn*100,2)))
                        line_sh2.append(str(round(10000.0*inv.TTLreturn/float(STRATEGIES.days_in_market(inv)),1)))
        sh1_content.append(line_sh1)
        sh2_content.append(line_sh2)

    line_sh1 = []
    line_sh2 = [] 
    line1_sh1 = []       
    line1_sh1.extend(["Total % Return (over all time periods)",""])
    line_sh1.extend(["Average Return",""])
    line_sh2.extend(["Average Return",""])
    for stock_name in StockNames:
        for strategy in strategies:
            ttl_profit = 0
            bps_per_trade = 0
            elem = 0.0
            for inv in Investments:
                for d in range(len(TimePeriods)-1):
                    if inv.stock_name == stock_name and inv.strategy_name == strategy\
                    and inv.start_date == TimePeriods[d] and inv.end_date ==TimePeriods[d+1]:
                        ttl_profit += inv.TTLreturn
                        bps_per_trade += 10000.0*inv.TTLreturn/float(STRATEGIES.days_in_market(inv))
                        elem += 1.0
            line1_sh1.append(str(round(ttl_profit*100.0,2)))
            line_sh1.append(str(round(ttl_profit*100.0/elem,2)))
            line_sh2.append(str(round(bps_per_trade/elem,1)))
    sh1_content.append(line_sh1)
    sh2_content.append(line_sh2)
    sh1_content.append(line1_sh1)   
    
    for h in range(len(headers)):
        sh1.write(0,h,headers[h])                 
        sh2.write(0,h,headers[h])
        for r in range(len(sh1_content)):
            sh1.write(r+1,h,sh1_content[r][h])
        for r in range(len(sh2_content)):
            sh2.write(r+1,h,sh2_content[r][h])
    wkbk.save(fn)

