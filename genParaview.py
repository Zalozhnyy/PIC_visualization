import os
import asyncio

import vtk

from extractor import SAVE_PREFIX, read_particles_dump

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


async def create_vtk_dump(step: int):
    await asyncio.sleep(1)
    particles = await read_particles_dump(step)

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
        writer.SetFileName(os.path.join(SAVE_PREFIX, f'particles_{step}.vtp'))
        writer.Write()

    return f'particles_{step}.vtp'


async def read_time_series():
    vtk_series = []

    r = await asyncio.gather(*[create_vtk_dump(step) for step in range(500, 9001, 500)])
    print(r)

    # for step in range(500, 9000 + 1, 500):
    #     vtk_series.append((create_vtk_dump(step), step))
    #
    tmp = [VPT_TEMPLATE.format(time_step=time, file_name=vtk_file) for vtk_file, time in vtk_series]

    with open(os.path.join(SAVE_PREFIX, 'particles.pvd'), 'w', encoding='utf-8') as f:
        f.write(VTP_FILE.format(files='\n'.join(tmp)))


def read_single_file(step: int):
    create_vtk_dump(step)


if __name__ == '__main__':
    asyncio.run(read_time_series())
    # read_single_file(200)
