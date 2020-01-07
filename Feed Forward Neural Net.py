import os
code_directory = "C:/Users/mfrangos/Desktop/Annual Sales Budget"
os.chdir(code_directory)
import pandas as pd
import datetime as dt

    
#SET FEATURE VARIABLES HERE. Which data will we use to predict bad accounts
#UNUSED: "FA_Offered", "FA_Paid",,"TotalPayments", "PercentPaid", "FA_Accepted","Balance"
predictiveVars = ["STORE","GL DAY","Holiday?","GL PD","SHORT GL DAY","DATE",'calendar day',
       'calendar month', 'calendar year',"proportion_of_current_year"] #, #,"GL YR" #'Daily Store Proportion of Year' #


CurrentDate = dt.datetime.now()
CurrentMonth = CurrentDate.month
CurrentDay = CurrentDate.day


#def main():
#training data
trainingData = pd.read_csv("training_data.csv", encoding = "ISO-8859-1")


#MAKE 1-HOT COLUMNS 
trainingData["Holiday?"] = trainingData["Holiday?"].replace(True,1).replace(False,0)



#BUILD THE NEURAL NETWORK


##BALANCE THE DATA
#Section not used. Although predictions were accurate, the model was flagging more accounts than necessary.

#Problem = pd.DataFrame(trainingData[trainingData[:]["ActionRequired"] == 1])
#NoProblem = pd.DataFrame(trainingData[trainingData[:]["ActionRequired"] == 0])
#smallestSizedDf = min(len(Problem),len(NoProblem))
#Problem = Problem[:smallestSizedDf]
#NoProblem = NoProblem[:smallestSizedDf]
##Recombine the data. It is now balanced with 50% problem items and 50% good items.
#trainingData = pd.concat([Problem, NoProblem], axis = 0)

#standardizing the input features/target
from sklearn.preprocessing import StandardScaler
X = trainingData[:][predictiveVars]
#X.set_index("STORE", inplace = True) #Remove??

#Target Variable 
y = pd.DataFrame(trainingData[:]) 
#y.set_index("STORE", inplace = True)
sc_y = StandardScaler()
y = y['ADJ SALES']




sc = StandardScaler()
X = pd.DataFrame(sc.fit_transform(X))
X

#Replace na's with 0
X.fillna(value=0, inplace= True)


#We now split the input features and target variables into 
#training dataset and test dataset. out test dataset will be 30% of our entire dataset.
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

from keras import Sequential
from keras.layers import Dense, Dropout
from tensorflow.keras import layers

NN_model = Sequential()
#First Hidden Layer
NN_model.add(Dense(8, activation='relu', input_dim=len(predictiveVars), kernel_initializer='random_uniform')) 
#NN_model.add(Dropout(0.2))
NN_model.add(Dense(128, activation='relu'))
#NN_model.add(Dropout(0.2))
NN_model.add(Dense(256, activation='relu'))
#NN_model.add(Dropout(0.2))
NN_model.add(Dense(512, activation='relu'))
#NN_model.add(Dropout(0.2))
NN_model.add(Dense(512, activation='relu'))
#NN_model.add(Dropout(0.2))

#Linear output. Lex's suggestion
NN_model.add(Dense(1))
#Worked well
#NN_model.add(Dense(1, activation = "relu")) #try tanh, leakyrelu, or linear, softplus (0+ outputs only), or relu (0+ values only)

#Compiling the neural network
from keras.optimizers import Adam
from keras.optimizers import SGD
epochs = 50
opt = Adam(lr=0.001  , decay=1e-4 / 200) #lr = 1e-4 #Best model was this one I think
#opt = Adam(lr=0.01) #lr = 1e-4
#opt = SGD(lr=0.01, decay=1e-6 / epochs, momentum=0.9, nesterov=True) 


NN_model.compile(optimizer =opt,loss='MSE') #'adam' 'MSE' for loss #Metrics = accuracy is only for classification #MAE #mean_absolute_percentage_error


#Callbacks
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
NAME = f"Model"
tensorboard = TensorBoard(log_dir = f"C:/Users/mfrangos/Desktop/Annual Sales Budget/logs/{NAME}") #Dynamically created names for our logs. Goes by the model name we defined above
#More tensorboard settings
filepath = "CallBack Model-{epoch:02d}-{val_acc:.3f}"
#checkpoint = ModelCheckpoint("models/{}.model".format(
#        #filepath,monitor = "val_acc",
#        verbose = 1,                  
#        save_best_only = True,
#        mode = "max"))

##########################################
#Fitting the data to the training dataset
##########################################
NN_model.fit(X_train,y_train, batch_size=1000, epochs=epochs, shuffle=True, validation_data=(X_test,y_test), callbacks = [tensorboard])
#3 epochs looked good

#Save the model
try:
  NN_model.save(f"C:/Users/mfrangos/Desktop/Annual Sales Budget/Saved Models/Model {str(dt.datetime.now()).replace(':','.')[:-10]}")
  NN_model.save(f"C:/Users/mfrangos/Desktop/Annual Sales Budget/Saved Models/Latest Model")
except Exception as e:
  print("Could not save model.",e)
#You can then use keras.models.load_model(filepath) to reinstantiate your model.  


#Evaluate the fitted model
#eval_model=NN_model.evaluate(X_train, y_train)
#print("Loss = ", eval_model)

#We now predict the output for our test dataset. 
#y_pred=NN_model.predict(X_test)



#
#
#
#print("True Positive (no problems)", cm[0][0], "False Positive", cm[0][1],"\n",
#      "False Negative", cm[1][0], "True Negative (Problems Detected)", cm[1][1])
#
#print("Negative Accuracy = ", cm[1][1]/(cm[1][1]+cm[1][0]))
#print("Positive Accuracy = ", cm[0][0]/(cm[0][0]+cm[0][1]))
#print("Total Accuracy = ", (cm[0][0]+cm[1][1])/(cm[0][0]+cm[0][1]+cm[1][0]+cm[1][1]))








###LETS MAKE PREDICTIONS ON AN UNSEEN DATASET
#Load Data
SecondValidationSet = pd.read_csv("Data_to_predict_on_using_NN.csv")

#MAKE 1-HOT COLUMNS 
SecondValidationSet["Holiday?"] = SecondValidationSet["Holiday?"].replace(True,1).replace(False,0)

#SecondValidationSet = trainingData ##FOR DEBUG

X2= SecondValidationSet[:][predictiveVars]

#standardizing the input feature
from sklearn.preprocessing import StandardScaler
X2 = pd.DataFrame(sc.transform(X2))   

#Replace na's with 0
X2.fillna(value=0, inplace= True)

#X2["STORE"] = SecondValidationSet["STORE"]
#X2.set_index("STORE", inplace = True)

Xnew = X2
#Make predictions using the NN_model model
ynew = NN_model.predict(Xnew)

#assign the predictions
SecondValidationSet["Prediction"] = ynew




#
##Dumb Conversions
#Total_Budget = 346056737.23
#SecondValidationSet["a"] = SecondValidationSet["Prediction"]
#SecondValidationSet["b"] = (SecondValidationSet["a"] - SecondValidationSet["a"].min())/(SecondValidationSet["a"].max()-SecondValidationSet["a"].min())
#
#SecondValidationSet["Weight"] = SecondValidationSet["b"]*0.000152 #Scaled weights
#SecondValidationSet["Total Yearly Budget"] = pd.read_excel("budget_column.xlsx")
#SecondValidationSet["Allocation"] = SecondValidationSet["Total Yearly Budget"]*SecondValidationSet["Weight"]
#SecondValidationSet["Allocation"] = SecondValidationSet["Allocation"]* Total_Budget/SecondValidationSet["Allocation"].sum()

SecondValidationSet.pivot_table(index = 'Holiday?',columns = ["GL DAY"], values = "Prediction", aggfunc = "sum",margins=True).to_excel(f"{code_directory}/Excel outputs/AI Pivot {str(dt.datetime.now()).replace(':','.')[:-10]}.xlsx")
SecondValidationSet.to_csv(f"{code_directory}/Excel outputs/AI Predictions {str(dt.datetime.now()).replace(':','.')[:-10]}.csv")


#if __name__ == "__main__":
#    main()
