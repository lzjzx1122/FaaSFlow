from matplotlib import pyplot as plt
import rasterio
import sys

def plot(file_name):
    with rasterio.open(file_name, 'r') as src:
        arr = src.read(1, out_shape=(src.height//10, src.width//10))
        plt.subplots(1,1)
        plt.gca().set_title(file_name)
        plt.imshow(arr)
        plt.colorbar(shrink=0.5)

    plt.savefig('fig.png', format='png')

if __name__ == '__main__':
    file_name = sys.argv[1]
    plot(file_name)
    
