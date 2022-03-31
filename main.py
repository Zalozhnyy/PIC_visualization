import paramiko
import numpy as np
import matplotlib.pyplot as plt
import os
import math
import numpy as np
from mayavi import mlab



from collections import defaultdict

HOST = 'XXX'
USER = 'XXX'
PASSWORD = 'XXXX'

PROJECT_PATH = r'/nethome/nicz97/PARTICLES_ROMAN/concentration/trap_conc_fixed_1'
np_ = 32


def open_connection():
    transport = paramiko.Transport((HOST, 22))
    transport.connect(None, USER, PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport


def get_part_count():
    sftp, transport = open_connection()
    tmp = []

    for f in sftp.listdir(PROJECT_PATH):
        if f.startswith('partCountFile'):

            with sftp.open(PROJECT_PATH + f"/{f}", 'r') as file:
                for l in file.readlines():
                    try:
                        indx, time, count = l.strip().split()
                        tmp.append([int(indx), float(time), int(count)])

                    except ValueError:
                        print(l.strip(), "error")

    if sftp: sftp.close()
    if transport: transport.close()

    data = np.array(tmp)
    return data


def get_part_distribution(step: int):
    sftp, transport = open_connection()

    data = np.zeros((800, 800, 800), dtype=float)
    for f in sftp.listdir(PROJECT_PATH):
        if f.startswith(f'particles_dump_{step}'):
            print(f)
            with sftp.open(PROJECT_PATH + f"/{f}") as file:
                for l in file.readlines():
                    xi, yi, zi, value = l.strip().split()
                    data[int(xi), int(yi), int(zi)] += float(value)

    print(data)

def process(tmp_data, skip=1):
    data = []

    for i in range(0, len(tmp_data), skip):
        x, y, z = list(map(float, tmp_data[i].split()[:3]))

        if math.isnan(x) or math.isnan(y) or math.isnan(z):
            print('nan found')
            break

        data.append([x, y, z])

    return data


def plot3d(data):
    x, y, z = data[:, 0], data[:, 1], data[:, 2]
    # v = np.full_like(x, 1)
    v = np.arange(0, x.shape[0], 1)

    l = mlab.plot3d(x, y, z, v, tube_radius=200, colormap='Spectral')
    return l


# def main():
#     data_path = r'data/output_50'
#     n = 5
#
#     data = np.array(process(read(data_path), n))
#     plot3d(data)
#
#     mlab.show()


def gen_cell():

    c = 0
    n = 100 * 100 * 100
    step = n // 100
    for i in range(1, n + 1, step):
        print(0)
        print(step - 1)
        print(1)
        print(1)

        c += step
    print(c)

if __name__ == '__main__':

    data = get_part_count()
    print(data)

    plt.plot(data[:, 1], data[:, 2])
    plt.grid()
    plt.show()
