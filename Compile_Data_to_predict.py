import pandas as pd
import os
import datetime as dt
from datetime import date
import holidays
from pandas.tseries.holiday import USFederalHolidayCalendar


os.chdir("C:/Users/mfrangos/Desktop/Annual Sales Budget")
Data_to_predict_on = pd.read_csv("Data_to_predict_on.csv")
Store_list = pd.read_excel("Store_List.xlsx")

def detect_holiday(year,month,day):
  us_holidays = holidays.UnitedStates()
  output = date(year,month,day) in us_holidays  # True
  return output

store_list = list(set(Store_list.iloc[:,0]))

#Create Holiday True/False Column
Holiday_Flag_Column = []
for DATE in Data_to_predict_on["DATE"]:
  #print(DATE)
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
Data_to_predict_on["Holiday?"] = Holiday_Flag_Column

aggregate = pd.DataFrame()
for store in store_list:
  #print(store)
  temp = Data_to_predict_on.iloc[:,1:]
  temp["STORE"] = store
  aggregate = aggregate.append(temp)


#Budget = pd.read_excel("Annual Sales Budget.xlsx")
#aggregate = pd.merge(aggregate,Budget,how = "outer",on = "STORE")

#"Bring in some new columns"
Fiscal_Calendar = pd.read_excel("C:/Users/mfrangos/Desktop/Fiscal Calendars/GeneralLedger Calendar.xlsx")
Fiscal_Calendar.columns = [x.replace("DCODE","DATE") for x in Fiscal_Calendar.columns] #Fix column names
aggregate = pd.merge(aggregate,Fiscal_Calendar[["DATE","calendar day","calendar month","calendar year"]],how = "inner",on = "DATE") #,


proportion_column = pd.read_csv("training_data.csv")
group = proportion_column[["STORE","calendar day","calendar month",'proportion_of_current_year',"calendar year"]]
group = group.groupby(["STORE","calendar day","calendar month","calendar year"])
average_weights = pd.DataFrame(group.mean()).reset_index()
average_weights = average_weights.loc[average_weights["calendar year"] == 2019]

aggregate = pd.merge(aggregate,average_weights,
         how="left",
         on = ["STORE","calendar day","calendar month"])

aggregate.columns = [x.replace("calendar year_x","calendar year") for x in aggregate.columns] #Fix column names
aggregate.drop("calendar year_y",inplace = True,axis = 1)

aggregate.to_csv("Data_to_predict_on_using_NN.csv")


#VERIFY INTEGRITY
#for store in set(aggregate["STORE"]):
#  #print(store)
#  print(len(aggregate[aggregate["STORE"] == int(f"{store}")]))

  
