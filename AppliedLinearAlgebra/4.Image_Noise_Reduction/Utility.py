from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import math


# Construct Matrix R
def construct_r_matrix(s, size, k):
    R = np.zeros(size)
    x, y = size[0], size[1]
    for i in range(x):
        for j in range(y):
            if i == j:
                if i <= k:
                    R[i][i] = s[i]
                else:
                    R[i][i] = 0
    return R


# Construct CLean Matrix
def construct_clean_matrix(u, r, v):
    u_r = u.dot(r)
    clear = u_r.dot(v)
    return clear


# Reduce The Noise Of 2D Matrix
def noise_reduction(mat, k):
    length = mat.shape[:2]
    U, S, V = np.linalg.svd(mat)
    R = construct_r_matrix(S, length, k)
    cleaned_matrix = construct_clean_matrix(U, R, V)
    return cleaned_matrix


def get_main_function():
    x = np.linspace(0, math.pi * 3 / 2, 30)
    y = np.linspace(0, math.pi * 3 / 2, 30)
    X, Y = np.meshgrid(x, y)
    return np.sin(X * Y)


def make_function_noisy(z):
    max_noise = 0.1
    t = 2 * np.random.rand(30 * 30) * max_noise - max_noise
    t = t.reshape(30, 30)
    return np.add(z, t)


def get_function():
    return make_function_noisy(get_main_function())


def show_my_matrix(Z):
    x = np.linspace(0, math.pi * 3 / 2, 30)
    y = np.linspace(0, math.pi * 3 / 2, 30)
    X, Y = np.meshgrid(x, y)
    ax = plt.axes(projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                    cmap='viridis', edgecolor='black')
    ax.set_title('surface');
    ax.view_init(60, 35)
    plt.show()


def show_main():
    Z = get_main_function()
    show_my_matrix(Z)


def show_noisy():
    Z = get_function()
    show_my_matrix(Z)


if __name__ == '__main__':
    show_main()
    show_noisy()
    z = get_function()
    clean_matrix = noise_reduction(z, 7)
    show_my_matrix(clean_matrix)
