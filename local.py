import os
import re
import struct

from dataclasses import dataclass
from typing import List

import numpy as np
from mayavi import mlab
import vtk

import matplotlib.pyplot as plt

from read_REMP import read_REMP

PROJECT_PATH = r'/home/nick/Work/test_projects/trap_conc_fixed_1'

VTP_FILE = '''<?xml version="1.0"?>
<VTKFile type="Collection" version="0.1"
         byte_order="LittleEndian"
         compressor="vtkZLibDataCompressor">
  <Collection>
    
    {files}

  </Collection>
</VTKFile>
'''

VPT_TEMPLATE = '''<DataSet timestep="{time_step}" group="" part="0"
file="{file_name}"/>
'''

@dataclass
class Particle:
    rx: float
    ry: float
    rz: float
    px: float
    py: float
    pz: float
    weight: float
    currentTime: float
    cellIdFlag: int
    particle_id: int
    process_rank: int


def get_part_distribution(data: np.ndarray, step: int):
    for f in os.listdir(PROJECT_PATH):
        if f.startswith(f'particles_dump_') and int(f.split('_')[-2]) == step:
            print(f)
            with open(os.path.join(PROJECT_PATH, f)) as file:
                for l in file.readlines():
                    xi, yi, zi, value = l.strip().split()

                    data[int(xi), int(yi), int(zi)] += float(value)

    return data


def read_binary_dump(fname: str, mpiRank: int):
    output = []
    with open(fname, 'rb') as f:
        magic_value = struct.unpack('i', f.read(4))[0]
        time_index = struct.unpack('i', f.read(4))[0]
        part_count = struct.unpack('l', f.read(8))[0]

        for _ in range(part_count):
            p = Particle(
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),

                *struct.unpack('f', f.read(4)),
                *struct.unpack('f', f.read(4)),
                *struct.unpack('i', f.read(4)),
                *struct.unpack('l', f.read(8)),
                mpiRank
            )

            output.append(p)

    return output


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


def read_particles_dump(step: int):
    particles: List[Particle] = []

    particles_savepoints = os.path.join(PROJECT_PATH, 'particles_savepoints')
    fil = re.compile(r"dump_(\d*)_(\d*).dat")
    for f in os.listdir(particles_savepoints):
        res = re.findall(fil, f)
        if len(res) > 0:
            time_index, mpi_rank = [int(i) for i in res[0]]
            if time_index == step:
                print('reading ', f)
                particles += read_binary_dump(os.path.join(particles_savepoints, f), mpi_rank)

    return particles


def create_vtk_dump(step: int):
    particles = read_particles_dump(step)

    if len(particles) > 0:
        pts = vtk.vtkPoints()
        pointDataRes = vtk.vtkDoubleArray()
        pointDataRes.SetName('weight')
        pointDataMpiRank = vtk.vtkIntArray()
        pointDataMpiRank.SetName('MpiRank')

        for p in particles:
            pts.InsertNextPoint(p.rx, p.ry, p.rz)
            pointDataRes.InsertNextValue(p.weight)
            pointDataMpiRank.InsertNextValue(p.process_rank)

        conn = vtk.vtkCellArray()
        for i in range(pts.GetNumberOfPoints()):
            conn.InsertNextCell(1, (i,))

        polyData = vtk.vtkPolyData()
        polyData.SetPoints(pts)
        polyData.SetVerts(conn)
        polyData.GetPointData().AddArray(pointDataRes)
        polyData.GetPointData().AddArray(pointDataMpiRank)

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetInputData(polyData)
        writer.SetFileName(f'particles_{step}.vtp')
        writer.Write()

    return f'particles_{step}.vtp'


def main():
    _, grid, _, _, _, _ = read_REMP(PROJECT_PATH)
    step = 9000
    # data = np.zeros((len(grid[0]['i05']), len(grid[1]['i05']), len(grid[2]['i05'])), dtype=float)
    #
    # data = get_part_distribution(data, step)
    # plot_3d(step)

    vtk_series = []

    for step in range(200, 14000 + 1, 200):
        vtk_series.append((create_vtk_dump(step), step))

    tmp = [VPT_TEMPLATE.format(time_step=time, file_name=vtk_file) for vtk_file, time in vtk_series]
    with open('particles.pvd', 'w', encoding='utf-8') as f:
        f.write(VTP_FILE.format(files='\n'.join(tmp)))

if __name__ == '__main__':
    main()
