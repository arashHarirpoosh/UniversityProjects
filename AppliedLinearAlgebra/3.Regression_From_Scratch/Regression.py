import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Read The Data From CSV File
def read_data(file_name):
    df = pd.read_csv(file_name, usecols=["Open"])
    return df


# Split Data To Train And Test Samples
def split_data(df, test_size=10):
    train_data, test_data = df[:-test_size], df[-test_size:]
    xs_train, ys_train = train_data.index.values, train_data["Open"].values
    xs_test, ys_test = test_data.index.values, test_data["Open"].values
    return xs_train, ys_train, xs_test, ys_test


# Create Matrix A For Linear Regression
def construct_a2(b2):
    bc1 = np.ones(b2.shape[0], dtype='int32')
    a2 = np.stack((bc1, b2), axis=1)
    return a2


# Create Matrix A For Non Linear Regression
def construct_a3(b2):
    bc1 = np.ones(b2.shape[0], dtype='int32')
    bc3 = np.square(b2)
    a2 = np.stack((bc1, b2, bc3), axis=1)
    return a2


# Train Regression Model
def fit(a, yf_train):
    ata = a.T.dot(a)
    atb = a.T.dot(yf_train)
    res = np.linalg.solve(ata, atb)
    return res


# Test The Model With Test Data's
def test(c, a, yt_test):
    predicted_y = a.dot(c)
    dif = predicted_y - yt_test
    for i in range(len(dif)):
        print('Calculated Value:', predicted_y[i])
        print('Actual value', yt_test[i])
        print('error:', dif[i], '\n')


# Plot Regression Line And Input Data's
def plot_linear_regression(c, n, x, y_t):
    if n == 2:
        a = construct_a2(x)
        name = 'LinearRegression.png'
    else:
        a = construct_a3(x)
        name = 'NonLinearRegression.png'
    y_pred = a.dot(c)

    plt.plot(x, y_pred, '.', label='Predicted Line')
    plt.scatter(x, y_t, marker='*', color='orange', alpha=0.7, label='Real Data')
    plt.legend()
    plt.savefig(name)
    plt.show()


if __name__ == '__main__':
    data = read_data('GOOGL.csv')
    x_train, y_train, x_test, y_test = split_data(data)
    a_train2 = construct_a2(x_train)
    a_test2 = construct_a2(x_test)
    coef = fit(a_train2, y_train)
    plot_linear_regression(coef, 2, x_train, y_train)
    print('Linear Regression Test Results:\n')
    test(coef, a_test2, y_test)

    a_train3 = construct_a3(x_train)
    a_test3 = construct_a3(x_test)
    coef = fit(a_train3, y_train)
    plot_linear_regression(coef, 3, x_train, y_train)
    print('\nNonLinear Regression Test Results:\n')
    test(coef, a_test3, y_test)
