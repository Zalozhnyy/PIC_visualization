import numpy as np
from mayavi import mlab

from extractor import read_particles_dump


def plot_3d(step: int):
    nx, ny, nz, res = [], [], [], []
    particles = read_particles_dump(step)

    for i, p in enumerate(particles):
        nx.append(p.rx)
        ny.append(p.ry)
        nz.append(p.rz)
        res.append(p.weight)

    mlab.points3d(nx, ny, nz, res)

    mlab.axes()
    mlab.show()


def main():
    plot_3d(200)


if __name__ == '__main__':
    main()
