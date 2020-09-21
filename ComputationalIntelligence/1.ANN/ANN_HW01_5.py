import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.transforms import BlendedGenericTransform

# reading csv file
data = pd.read_csv("dataset.csv")

df = pd.DataFrame(data, columns=['X1','X2', 'Label'])

# split data to train and test
x_train = df[['X1', 'X2']][0:150]
y_train = df[['Label']][0:150]
x_test = df[['X1', 'X2']][150:]
y_test = df[['Label']][150:]

def S(x):
    return 1/(1+np.exp(-x))

def fit(x_train, y_train, n_epoch, lr):
    train_data = list(zip(x_train['X1'], x_train['X2'], y_train['Label']))

    weights = np.random.normal(0, 1, size= 6)
    bias = np.random.normal(0, 1, size=3)
    z = [0, 0]
    grad = np.zeros(9)

    for epoch in range(n_epoch):
        for data in train_data:
            # compute y
            yt = data[2]
            z[0] = S(data[0]*weights[0] + data[1]*weights[1] + bias[0])
            z[1] = S(data[0]*weights[2] + data[1]*weights[3] + bias[1])
            y = S(z[0]*weights[4] + z[1]*weights[5] + bias[2])
            loss = y - yt
            dis_y = y*(1-y)
            dis_z0 = z[0]*(1-z[0])
            dis_z1 = z[1]*(1-z[1])
            #dcost/db0
            grad[0] = 2*weights[4]*loss*dis_y*dis_z0
            #dcost/db1
            grad[1] = 2*weights[5]*loss*dis_y*dis_z1
            #dcost/db2
            grad[2] = 2*loss*dis_y
            #dcost/dW
            grad[3] = data[0]*grad[0]
            grad[4] = data[1]*grad[0]
            #dcost/dV
            grad[5] = data[0]*grad[1]
            grad[6] = data[1]*grad[1]
            #dcost/dU
            grad[7] = z[0]*grad[2]
            grad[8] = z[1]*grad[2]
            #update weights
            num_of_weight_group = int(len(weights)/2)
            num_of_w_in_group = int(len(weights)/num_of_weight_group)
            for w in range(num_of_weight_group):
                for i in range(num_of_w_in_group):
                    weights[2*w+i] = weights[2*w+i] - (lr * grad[3+2*w+i])
            #update bias
            for b in range(len(bias)):
                bias[b] = bias[b] - (lr * grad[b])
    return bias, weights

def test(x_test, y_test, params, scatter = 0):
    test_data = pd.DataFrame({'X1':x_test['X1'], 'X2':x_test['X2'], 'Label':y_test['Label']})
    bias = params[0]
    weights = params[1]
    z = [0, 0]

    X1 = []
    X2 = []
    Label = []
    n = len(x_test)
    true_predicts = 0

    for row, data in test_data.iterrows():
        x1 = data['X1']
        x2 = data['X2']
        y = data['Label']
        z[0] = S(x1 * weights[0] + x2 * weights[1] + bias[0])
        z[1] = S(x1 * weights[2] + x2 * weights[3] + bias[1])
        yp = S(z[0] * weights[4] + z[1]*weights[5] + bias[2])
        if yp > 0.5:
            yp = 1
        else:
            yp = 0
        if y == yp:
            true_predicts += 1
        X1.append(x1)
        X2.append(x2)
        Label.append(yp)
    acc = true_predicts/n
    if scatter:
        # set the colors of data with label 0 as blue and label 1 as red
        colors = np.where(test_data.Label > 0, 'r', 'b')
        # plot the scatter of the data
        inp_scatter = test_data.plot(title= 'Test Dataset', kind='scatter', x='X1', y='X2', c=colors)
        # show the plotted scatter
        plt.show()

        res_data = pd.DataFrame({'X1': X1, 'X2': X2, 'Label': Label})
        # set the colors of data with label 0 as blue and label 1 as red
        colors = np.where(res_data.Label > 0, 'r', 'b')
        #plot the scatter of the data
        predicted_scatter = res_data.plot(title= 'Predicted Test Dataset', kind='scatter', x='X1', y='X2', c=colors)
        #show the plotted scatter
        plt.show()
    return acc

#train the model
weights = fit(x_train, y_train, 2000, 0.7)

#test the model
acc = test(x_test, y_test, weights, 0)
acc_train = test(x_train, y_train, weights, 0)
print("Accuracy test of model is: ", acc)
print("Accuracy train of model is: ", acc_train)