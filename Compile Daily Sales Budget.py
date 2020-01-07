import pandas as pd
import os
import datetime as dt
from datetime import date
import holidays
from pandas.tseries.holiday import USFederalHolidayCalendar

os.chdir("C:/Users/mfrangos/Desktop/Annual Sales Budget")
Annual_Budget = pd.read_excel("Annual Sales Budget.xlsx")
Historical_Daily_Sales = pd.read_excel("Daily Sales from 2016 to 12-17-2019.xlsx")



#Holiday Calendar
year = 2020
month = 11
day = 26


def detect_holiday(year,month,day):
  us_holidays = holidays.UnitedStates()
  output = date(year,month,day) in us_holidays  # True
  return output

detect_holiday(year,month,day)

def compile_store_list(Annual_Budget):
  store_list = []
  for store in Annual_Budget["Store #"]:
      store_list.append(store)
  return store_list
budget_store_list = compile_store_list(Annual_Budget) #Note: this list is smaller than the number of stores we observe from 2016-2019, but it's all we got budgets for


#Create Holiday True/False Column
Holiday_Flag_Column = []
for DATE in Historical_Daily_Sales["DATE"]:
  print(DATE)
  DATE = str(DATE)
  #Remove zeroes from days like 20190101
  if DATE[-2] == "0":
    day = DATE[-1]
  else:
    day = DATE[-2:]
  #Remove zeroes from months like 20190101
  if DATE[-4] == "0":
    month = DATE[5]
  else:
    month = DATE[4:6]
    
  #print(DATE)
  Holiday_Flag_Column.append(detect_holiday(int(str(DATE)[:4]),int(month),int(day)))
#Append the new column
Historical_Daily_Sales["Holiday?"] = Holiday_Flag_Column



#Create a new column for the data: Find the proportions of each day to the entire year.
proportion_of_current_year = []
total_sales_for_current_2016 = Historical_Daily_Sales.loc[Historical_Daily_Sales["GL YR"] == 2016]["ADJ SALES"].sum()
total_sales_for_current_2017 = Historical_Daily_Sales.loc[Historical_Daily_Sales["GL YR"] == 2017]["ADJ SALES"].sum()
total_sales_for_current_2018 = Historical_Daily_Sales.loc[Historical_Daily_Sales["GL YR"] == 2018]["ADJ SALES"].sum()
total_sales_for_current_2019 = Historical_Daily_Sales.loc[Historical_Daily_Sales["GL YR"] == 2019]["ADJ SALES"].sum()
i = 0
for sales_amount,GL_YR in zip(Historical_Daily_Sales["ADJ SALES"],Historical_Daily_Sales["GL YR"]):
  print(i)
  if GL_YR == 2016:
    proportion_of_current_year.append(sales_amount/total_sales_for_current_2016)
  elif GL_YR == 2017:
    proportion_of_current_year.append(sales_amount/total_sales_for_current_2017)
  elif GL_YR == 2018:
    proportion_of_current_year.append(sales_amount/total_sales_for_current_2018)
  elif GL_YR == 2019:
    proportion_of_current_year.append(sales_amount/total_sales_for_current_2019)
  else:
    print("ERROR")
    proportion_of_current_year.append("ERROR")
  i=i+1
#Append the new column
Historical_Daily_Sales["proportion_of_current_year"] = proportion_of_current_year



test = Historical_Daily_Sales.pivot_table(index = ["GL YR"], columns = ['GL DAY'],values = ["ADJ SALES"], aggfunc = "sum")
test2 =  Historical_Daily_Sales.pivot_table(index = ["GL YR"], columns = ['GL DAY'],values = "Holiday?", aggfunc = "sum")
test = Historical_Daily_Sales.pivot_table(index = ["GL YR","Holiday?"], columns = ['GL DAY'],values = ['proportion_of_current_year'], aggfunc = "sum").to_excel("proportions.xlsx")

#Export training data
Historical_Daily_Sales.to_csv("training_data.csv")
