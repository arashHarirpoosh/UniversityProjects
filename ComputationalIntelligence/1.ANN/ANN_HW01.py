import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.transforms import BlendedGenericTransform

# reading csv file
data = pd.read_csv("dataset.csv")

df = pd.DataFrame(data, columns=['X1','X2', 'Label'])

# if label is 0 then the color is blue otherwise the color is red
#set the colors of data with label 0 as blue and label 1 as red
# colors = np.where(df.Label > 0, 'r', 'b')
# # a = plt.scatter(df.X1, df.X2, c=colors)
# # OR (with pandas 0.13 and up)
# #plot the scatter of the data
# scatter = df.plot(kind='scatter', x='X1', y='X2', c=colors)
# #show the plotted scatter
# plt.show()
# # plt.show(a)

# split data to train and test
x_train = df[['X1', 'X2']][0:150]
y_train = df[['Label']][0:150]
x_test = df[['X1', 'X2']][150:]
y_test = df[['Label']][150:]

def S(x):
    return 1/(1+np.exp(-x))

def fit(x_train, y_train, n_epoch, lr):
    train_data = list(zip(x_train['X1'], x_train['X2'], y_train['Label']))

    n = len(train_data)
    weights = np.random.normal(0, 1, size= 2)
    b = np.random.normal(0, 1, size=1)[0]

    print(weights, b)
    grad = [0, 0, 0]
    for epoch in range(n_epoch):
        cost = 0
        # grad[0] for bias
        for w in range(len(weights)):
            grad[w+1] = 0
            #grad[0] stands for bias grad
            grad[0] = 0
            for data in train_data:
                # compute y
                x1 = data[0]
                x2 = data[1]
                yt = data[2]
                x = np.array([x1, x2], dtype=float)
                W = np.array([weights[:]], dtype=float)
                inp_y = sum(i for i in np.multiply(x, W)[0])
                inp_y+= b
                y = S(inp_y)
                # compute cost
                cost += -(yt*np.log(y) + (1-yt)*np.log(1-y))
                # compute grad of the weights
                grad[w+1] += -data[w]*(yt - y)
                # compute grad[0] for biases
                grad[0] += -(yt - y)

        #update weights
        for w in range(len(weights)):
            weights[w] = weights[w] - (lr * grad[w+1]) / n
        #update bias
        b = b - (lr * grad[0])/n
    return b, weights

def test(x_test, y_test, weights, scatter = 0):
    test_data = pd.DataFrame({'X1':x_test['X1'], 'X2':x_test['X2'], 'Label':y_test['Label']})
    X1 = []
    X2 = []
    Label = []
    n = len(x_test)
    true_predicts = 0

    for row, data in test_data.iterrows():
        x1 = data['X1']
        x2 = data['X2']
        y = data['Label']
        yp = S(weights[0] + x1*weights[1][0] + x2*weights[1][1])
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
weights = fit(x_train, y_train, 1500, 0.5)

#test the model
acc = test(x_test, y_test, weights, 1)
acc_train = test(x_train, y_train, weights, 1)
print("Accuracy test of model is: ", acc)
print("Accuracy train of model is: ", acc_train)