"""This code takes an Image as input, and based on that creates a color palette."""

import sys
import requests
import numpy as np
from os.path import expanduser
from PIL import Image
from sklearn.cluster import KMeans

# Set user directory for saving Images from web.
HOME = expanduser("~")


def load_image(picture, fname):
    """
    Load an image either from the web or from a path.
    Filename optional.
    """
    # Set filename. Used for downloading an Image off the web.
    if not fname:
        file = 'default.jpg'
    else:
        file = fname + '.jpg'
    # If http in input use requests to get the Image. If path provided open directly.
    if 'http' in picture:
        with open(file, 'wb') as f:
            f.write(requests.get(picture).content)
        image = HOME + "\{}".format(file)
        image = Image.open(image)
        return image
    else:
        image = Image.open('{}'.format(picture))
        return image


def make_clusters(image, clusters):
    """
    Makes color clusters using K-Means clustering.
    """
    # Convert the Image input in a contiguous array (ndim >= 1) in memory (C order).
    array = np.ascontiguousarray(image)
    # Make a new view of array with the numpy void datatype.
    array_n = array.view(np.dtype((np.void, array.dtype.itemsize * array.shape[-1])))
    # Find the unique elements of an array and return a contiguous flattened array using ravel().
    array_n = np.unique(array_n.ravel())
    # Convert from datatype V3 back to uint8 and reshape back to original shape.
    array_n = array_n.view(array.dtype).reshape(-1, array.shape[-1])
    # We use K-Means for clustering. Ref. https://scikit-learn.org/stable/modules/clustering.html#k-means
    km = KMeans(clusters).fit(array_n)
    # Convert clusters back to int from float.
    cluster_points = km.cluster_centers_.astype(int)
    # Order cluster points from light to dark.
    cluster_points = cluster_points[np.lexsort((cluster_points[:,0], -cluster_points[:,1]))]
    
    return cluster_points


def make_palette(clusters, image):
    """
    Make a palette from clusters and return Image.
    Palette scales width based on original Image width.
    """
    # Set width and height.
    width, height = image.width, int(image.height * .25)
    # Use split in iteration to make the color blocks.
    split = int(width/len(clusters))
    # Make array from image dimensions. Deafult color black.
    data = np.zeros((height, width, 3), dtype=np.uint8)
    # Use split and skip to move blocks in array per iteration.
    skip = 0
    for n, r in enumerate(clusters):
        data[0:height, skip:(n+1)*split] = [r[0], r[1], r[2]]
        skip += split
    # Generate image from array.    
    palette_image = Image.fromarray(data, 'RGB')
    
    return palette_image


def make_backround(image):
    """
    Make a black backround Image based on original image size.
    10% bigger.
    """
    # Set width and height, scaled by 10 percent.
    width, height = int(image.width * 1.1), int(image.height * 1.1 + (int(image.height) * .4))
    # Make array from image dimensions. Deafult color black.
    data = np.zeros((height, width, 3), dtype=np.uint8)
    # Generate image from array.
    backround = Image.fromarray(data, 'RGB')
    
    return backround


def final_output(image, backround, palette):
    """
    Makes the final output Image based  on image, backround, palette
    """
    # Create an offset and paste original Image within.
    offset = ((backround.width - image.width) // 2, (backround.height - image.height) // 8)
    backround.paste(image, offset)
    # Create an offset and paste palette below original Image.
    offset = ((backround.width - palette.width) // 2, ((backround.height - palette.height) // 8) + image.height)
    backround.paste(palette, offset)
    
    return backround


def palette_from_image(picture, clusters=10, fname=False):
    """
    Main function that calls all required functions.
    """
    image = load_image(picture, fname)
    img = image.convert('RGB')
    
    cluster_points = make_clusters(img, clusters)
    palette = make_palette(cluster_points, img)
    backround = make_backround(img)
    
    final_image = final_output(img, backround, palette)
    
    return final_image, palette
