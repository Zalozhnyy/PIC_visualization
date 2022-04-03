import os
import struct
import concurrent.futures
import time

import vtk

from extractor import SAVE_PREFIX, Particle, read_particles_dump_generator
from genParaview import VPT_TEMPLATE, VTP_FILE


def create_vtk_dump(step: int):
    start_time = time.time()

    pts = vtk.vtkPoints()
    pointDataRes = vtk.vtkDoubleArray()
    pointDataRes.SetName('weight')
    pointDataMpiRank = vtk.vtkIntArray()
    pointDataMpiRank.SetName('MpiRank')

    gen = read_particles_dump_generator(step)

    while True:
        try:
            p = next(gen)
            pts.InsertNextPoint(p.rx, p.ry, p.rz)
            pointDataRes.InsertNextValue(p.weight)
            pointDataMpiRank.InsertNextValue(p.process_rank)

        except StopIteration:
            break

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
    writer.SetFileName(os.path.join(SAVE_PREFIX, f'particles_{step}.vtp'))
    writer.Write()

    return f'[INFO] particles_{step}.vtp done in {time.time() - start_time}', (f'particles_{step}.vtp', step)


def read_time_series():
    q = [800, 600, 400, 200] + list(range(1000, 20000 + 1, 200))
    vtk_series = []

    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        results = executor.map(create_vtk_dump, q)

        for info, filename in results:
            vtk_series.append(filename)
            print(info)

    tmp = [VPT_TEMPLATE.format(time_step=time, file_name=vtk_file) for vtk_file, time in vtk_series]

    with open(os.path.join(SAVE_PREFIX, 'particles.pvd'), 'w', encoding='utf-8') as f:
        f.write(VTP_FILE.format(files='\n'.join(tmp)))


if __name__ == '__main__':
    read_time_series()
