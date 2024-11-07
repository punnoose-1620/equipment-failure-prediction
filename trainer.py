import pickle
import pandas as pd
from pre_processor import *
from graph_plotter import *
from model_creator import *
from sklearn.model_selection import train_test_split

def get_x_data(data, type='Training'):
    values = []
    for entry in tqdm(data, desc='\nGetting X Data for '+type):
        item = {}
        for key in entry.keys():
            if(key!='fail_stat'):
                try:
                    item[key] = float(str(entry[key]))
                except ValueError or TypeError:
                    print('Index Check : ', data.index(entry))
                    print("Exception Value : ", json.dumps(entry),'\n')
        values.append(item)
    print("\nX-vals for ",type," (",len(values),") : ",json.dumps(values, indent=4))
    return values

def get_y_data(data, type='Training'):
    values = []
    for entry in tqdm(data, desc='Getting Y Data for '+type):
        values.append(int(entry['fail_stat']))
    print("\nY-vals for ",type," (",len(values),") : ",values)
    return values

def save_model(fileName, model):
    with open('./saved_models/'+fileName+'.pkl', 'wb') as file:
        pickle.dump(model, file)
    print("fileName Model saved")

# Get Merged and Processed Data from datasets
processed_data = merge_datas()
# generate_all_graphs()

# Split data to training and testing data in 70-30 manner
train_data, test_data = train_test_split(processed_data, test_size=0.3, random_state=42)

# Split the training data into X_train and y_train
X_train = pd.DataFrame(get_x_data(train_data, 'Training'))
y_train = pd.DataFrame(get_y_data(train_data, 'Training'))
print('\n')

# Split the testing data into X_test and y_test
X_test = get_x_data(test_data, 'Testing')
y_test = get_y_data(test_data, 'Testing')

X_test_pd = pd.DataFrame(X_test)
y_test_pd = pd.DataFrame(y_test)

print("\nTrain count : (",len(X_train),' : ',len(y_train),')')
print("Test count : (",len(X_test),' : ',len(y_test),')')

train_logistic_regression(X_train, y_train)

# logistic_regression_model, lt_accuracy = logistic_regression(X_train, X_test_pd, y_train, y_test_pd)
# save_model('logistic_regression_model', logistic_regression_model)
# print("\nAccuracy of Logistic Model : ",lt_accuracy*1000,'\n')