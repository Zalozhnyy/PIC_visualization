import matplotlib.pyplot as plt
import numpy as np

from extractor import read_particles_dump


def plot_2d(data, grid):
    win = 20
    for iz in range(len(grid[2]['i05']) // 2 - win, len(grid[2]['i05']) // 2 + win, 2):
        plt.contourf([i for i in range(len(grid[0]['i05']) // 2 - win, len(grid[2]['i05']) // 2 + win, 1)],
                     [i for i in range(len(grid[1]['i05']) // 2 - win, len(grid[2]['i05']) // 2 + win, 1)],
                     data[
                     data.shape[0] // 2 - win:data.shape[0] // 2 + win,
                     data.shape[1] // 2 - win:data.shape[1] // 2 + win,
                     iz])
        plt.show()





if __name__ == '__main__':
    pass