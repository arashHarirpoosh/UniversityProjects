import numpy as np
import matplotlib.pyplot as plt


# Read The IMG File
def read_data(addr):
    img = plt.imread(addr)
    return img


# Construct Matrix R
def construct_r_matrix(s, size, t):
    R = np.zeros(size)
    x, y = size[0], size[1]
    for i in range(x):
        for j in range(y):
            if i == j:
                if s[i] > t:
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
def noise_reduction(mat, t):
    length = mat.shape[:2]
    U, S, V = np.linalg.svd(mat)
    R = construct_r_matrix(S, length, t)
    cleaned_matrix = construct_clean_matrix(U, R, V)
    return cleaned_matrix


# Reduce The Noise Of 3D Matrix
def image_noise_reduction(nimg, t):
    r_img = nimg[:, :, 0]
    g_img = nimg[:, :, 1]
    b_img = nimg[:, :, 2]
    cleaned_matrix_r = noise_reduction(r_img, t).astype('uint8')
    cleaned_matrix_g = noise_reduction(g_img, t).astype('uint8')
    cleaned_matrix_b = noise_reduction(b_img, t).astype('uint8')
    cleaned_matrix = np.stack((cleaned_matrix_r, cleaned_matrix_g, cleaned_matrix_b), axis=2)
    plt.imshow(cleaned_matrix)
    plt.imsave('cleaned_matrix.png', cleaned_matrix)
    plt.show()


if __name__ == '__main__':
    img = read_data('noisy.jpg')
    image_noise_reduction(img, 1400)
