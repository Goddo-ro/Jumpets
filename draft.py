from PIL import Image
import os


def load_image(*name):
    fullname = os.path.join('data', 'images', *name)
    image = Image.open(fullname)
    return image


for o in range(1, 9):
    image = load_image("dog", "jumping", "Jump {}.png".format(str(o)))
    pixels = image.load()
    x, y = image.size


    for i in range(x):
        for j in range(y):
            if pixels[i, j] == (0, 0, 0, 255):
                pixels[i, j] = (1, 1, 1, 255)
    image.save("data/images/dog/jumping/Jump {}.png".format(str(o)))
