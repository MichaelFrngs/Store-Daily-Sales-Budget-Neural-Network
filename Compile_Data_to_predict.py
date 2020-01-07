import pandas as pd
import os
import datetime as dt
from datetime import date
import holidays
from pandas.tseries.holiday import USFederalHolidayCalendar


os.chdir("C:/Users/mfrangos/Desktop/Annual Sales Budget")
Data_to_predict_on = pd.read_csv("Data_to_predict_on.csv")


def detect_holiday(year,month,day):
  us_holidays = holidays.UnitedStates()
  output = date(year,month,day) in us_holidays  # True
  return output

#Exclude 101 cuz it's in already
store_list = list(set([101,147,163, 166, 171, 178, 180, 209, 221, 237, 239, 322, 323, 375, 379, 120, 150, 152, 154, 160, 161, 260, 261, 263, 292, 320, 330, 369, 382, 402, 103, 129, 133, 134, 155, 159, 164, 188, 195, 233, 236, 248, 255, 329, 358, 115, 126, 131, 141, 167, 215, 235, 238, 243, 253, 349, 360, 365, 107, 157, 158, 169, 172, 173, 176, 181, 191, 194, 212, 244, 256, 364, 130, 231, 246, 258, 262, 279, 287, 289, 295, 314, 386, 393, 447, 211, 228, 249, 252, 267, 282, 291, 304, 312, 316, 321, 411, 419, 128, 234, 245, 266, 272, 273, 274, 275, 281, 298, 310, 408, 414, 420, 434, 132, 177, 182, 216, 217, 220, 222, 227, 229, 242, 247, 254, 264, 265, 331, 340, 344, 372, 278, 300, 303, 313, 318, 324, 327, 337, 343, 367, 371, 394, 398, 201, 203, 241, 271, 280, 288, 290, 293, 294, 317, 333, 428, 108, 112, 113, 118, 125, 135, 142, 170, 184, 187, 350, 401, 102, 109, 117, 121, 123, 124, 136, 138, 144, 174, 179, 186, 192, 207, 232, 114, 143, 148, 175, 205, 210, 214, 336, 353, 355, 362, 363, 366, 104, 127, 139, 145, 149, 151, 153, 183, 206, 213, 224, 225, 309, 354, 110, 119, 156, 162, 165, 193, 208, 223, 230, 250, 268, 270,307,378]
))

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

#
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
#aggregate['proportion_of_current_year'] = 
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
#  
  