import numpy as np
from matplotlib import image
from matplotlib import pyplot as plt

WHITE_PIX = [255, 255, 255]


# Read The Image From Path
def read_image(path):
    img = image.imread(path)
    return img


# Create The Shadow Of Input Picture
def create_shadow(pic):
    dim = pic.shape
    new_dim = (int(1.25 * dim[0]), int(1.25 * dim[1]), dim[2])
    shadow_img = np.full(new_dim, WHITE_PIX)
    for r in range(len(pic)):
        for c in range(len(pic[r])):
            if not np.array_equal(pic[r][c], WHITE_PIX):
                gray_rgb = np.mean(pic[r][c])
                shadow_img[r][c] = [gray_rgb, gray_rgb, gray_rgb]

    return shadow_img


# Transfer The Shadow Image That Created In The Last Step With Shear Function
def shear_transformation(shadow_img, lamb=0.1):
    dim = shadow_img.shape
    transformed_img = np.full(shadow_img.shape, WHITE_PIX)
    transfer_func = np.array([[1, 0],
                              [lamb, 1]])
    for r in range(len(shadow_img)):
        for c in range(len(shadow_img[r])):
            if not np.array_equal(shadow_img[r][c], WHITE_PIX):
                pos = np.array([r, c])
                new_pos = np.matmul(transfer_func, pos).astype('int')
                new_r = np.min([new_pos[0], dim[0] - 1])
                new_c = np.min([new_pos[1], dim[1] - 1])
                transformed_img[new_r][new_c] = shadow_img[r][c]

    return transformed_img


# Combine The Original Image With The Transformed Image That Created In The Last Step
def combine_shadow(transformed_img, pic):
    for r in range(len(pic)):
        for c in range(len(pic[r])):
            pix = pic[r][c]
            if not np.mean(pix) > 235:
                transformed_img[r][c] = pix

    return transformed_img


# Use Above Functions To Add Shadow To The Image
def create_shadow_for_pic(pic):
    shadow_img = create_shadow(pic)
    print('Shadow Image Created...')
    plt.imshow(shadow_img)
    plt.title('Shadow Image')
    plt.show()
    shear_img = shear_transformation(shadow_img)
    print('Shear Transformation Is Done...')
    plt.imshow(shear_img)
    plt.title('Shear Transformed Image')
    plt.show()
    img_with_shadow = combine_shadow(shear_img, pic)
    print('Shadow Added To The Image...')
    image.imsave('ImageWithShadow.png', np.uint8(img_with_shadow))
    plt.imshow(img_with_shadow)
    plt.title('Image With Shadow')
    plt.show()


if __name__ == '__main__':
    addr = input('Image Path: ')
    img = read_image(addr)
    create_shadow_for_pic(img)
