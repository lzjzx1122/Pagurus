from scipy.io import loadmat
import numpy as np
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from sklearn import metrics
#from sklearn.externals 
import joblib
import time

def main(param):
    start_time = time.time()

    #dataset = loadmat('EEG_X.mat')
    #labelset = loadmat('EEG_Y.mat')
    
    dataset = loadmat('/proxy/exec/EEG_X.mat')
    labelset = loadmat('/proxy/exec/EEG_Y.mat')
    data_X = dataset['X'][0]
    label_Y = labelset['Y'][0]
    train_x = []
    train_y = []
    test_x = []
    test_y = []
    #get train_x[0]
    train_x.append(data_X[1])
    train_y.append(label_Y[1])
    for i in range(2,15):
            train_x[0] = np.vstack((train_x[0],data_X[i]))
            train_y[0] = np.vstack((train_y[0],label_Y[i]))
    test_x.append(data_X[0])
    test_y.append(label_Y[0])
    #get train_x[1-14]
    for i in range(1,15):
        train_x.append(data_X[0])
        train_y.append(label_Y[0])
        for j in range(1,15):
            if i != j:
                train_x[i] = np.vstack((train_x[i],data_X[j]))
                train_y[i] = np.vstack((train_y[i],label_Y[j]))
        test_x.append(data_X[i])
        test_y.append(label_Y[i])
    for i in range(0,15):
        train_x[i] = preprocessing.scale(train_x[i])
        test_x[i] = preprocessing.scale(test_x[i])

    #for i in range(0,15):
    svm_0 = SVC(gamma = 0.001,C = 100)
    svm_0.fit(train_x[0],train_y[0].ravel())
    svm_0_result = svm_0.predict(test_x[0])
        #train accuracy
    print('train_accuracy : ',svm_0.score(train_x[0], train_y[0].ravel()))
        # test accuracy
    m = 0
    for n in range(0,len(test_y[0])):
        if svm_0_result[n] == test_y[0][n]:
            m = m+1
    test_accuracy = m/len(test_y[0])
    print('test_accuracy : ',test_accuracy)
    
    return {"latency": time.time() - start_time}

#main({})
