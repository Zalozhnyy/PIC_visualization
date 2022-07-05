import os
import re
import asyncio

from typing import List
import struct
from dataclasses import dataclass

PROJECT_PATH = r'C:\Work\test_projects\trap_conc_fixed'
SAVE_PREFIX = r'C:\Work\test_projects\trap_conc_fixed\vtk_particles'


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

@dataclass
class ParticleSmall:
    rx: float
    ry: float
    rz: float
    weight: float
    process_rank: int


def read_binary_dump(fname: str, mpiRank: int):
    output = []
    with open(fname, 'rb') as f:

        magic_value = struct.unpack('i', f.read(4))[0]
        time_index = struct.unpack('i', f.read(4))[0]
        part_count = struct.unpack('Q', f.read(8))[0]

        if part_count > 0:
            print('[INFO] reading ', f, f" part_count={part_count}")

        for _ in range(part_count):
            # p = Particle(
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #
            #     *struct.unpack('f', f.read(4)),
            #     *struct.unpack('f', f.read(4)),
            #     *struct.unpack('i', f.read(4)),
            #     *struct.unpack('q', f.read(8)),
            #     mpiRank
            # )

            p = ParticleSmall(
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('f', f.read(4)),
                mpiRank
            )


            output.append(p)

    return output


def read_binary_dump_generator(fname: str, mpiRank: int):
    with open(fname, 'rb') as f:
        magic_value = struct.unpack('i', f.read(4))[0]
        time_index = struct.unpack('i', f.read(4))[0]
        part_count = struct.unpack('Q', f.read(8))[0]

        for _ in range(part_count):
            # p = Particle(
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #     *struct.unpack('d', f.read(8)),
            #
            #     *struct.unpack('f', f.read(4)),
            #     *struct.unpack('f', f.read(4)),
            #     *struct.unpack('i', f.read(4)),
            #     *struct.unpack('q', f.read(8)),
            #     mpiRank
            # )

            p = ParticleSmall(
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('d', f.read(8)),
                *struct.unpack('f', f.read(4)),
                mpiRank
            )

            yield p


async def read_particles_dump(step: int):
    particles: List[Particle] = []

    particles_savepoints = os.path.join(PROJECT_PATH, 'particles_savepoints')
    fil = re.compile(r"dump_(\d*)_(\d*)")
    for f in os.listdir(particles_savepoints):
        res = re.findall(fil, f)
        if len(res) > 0:
            time_index, mpi_rank = [int(i) for i in res[0]]
            if time_index == step:
                particles += read_binary_dump(os.path.join(particles_savepoints, f), mpi_rank)

    return particles


def read_particles_dump_generator(step: int):
    particles_savepoints = os.path.join(PROJECT_PATH, 'particles_savepoints')
    fil = re.compile(r"dump_(\d*)_(\d*).dat")

    for f in os.listdir(particles_savepoints):
        res = re.findall(fil, f)
        if len(res) > 0:
            time_index, mpi_rank = [int(i) for i in res[0]]
            if time_index == step:
                gen = read_binary_dump_generator(os.path.join(particles_savepoints, f), mpi_rank)

                while True:
                    try:
                        yield next(gen)

                    except StopIteration:
                        break
