from hydrolib.core.io.mdu.models import FMModel
from hydrolib.core.io.xyz.models import XYZModel, XYZPoint
from hydrolib.core.io.inifield.models import (
    IniFieldModel,
    InitialField,
    InterpolationMethod,
    DataFileType,
)
from pathlib import Path
import os
import shutil
import subprocess

modelname = "model"

if Path(modelname).exists():
    shutil.rmtree(modelname)

os.mkdir(modelname)
os.chdir(modelname)

fm_model = FMModel()
fm_model.filepath = Path(f"{modelname}.mdu")

network = fm_model.geometry.netfile.network
network.mesh2d_create_rectilinear_within_extent(extent=(-5, -5, 5, 5), dx=1, dy=1)

xyz_model = XYZModel(points=[])
xyz_model.filepath = Path(f"{modelname}.xyz")
xyz_model.points = [
    XYZPoint(x=-5.1, y=-5.1, z=-50.0),
    XYZPoint(x=-5.1, y=5.1, z=-50.0),
    XYZPoint(x=5.1, y=-5.1, z=-20.0),
    XYZPoint(x=5.1, y=5.1, z=-20.0),
]

xyz_model.save()
bed_level = InitialField(
    quantity="bedlevel",
    datafile=xyz_model.filepath,
    datafiletype=DataFileType.sample,
    interpolationmethod=InterpolationMethod.triangulation,
)
fm_model.geometry.inifieldfile = IniFieldModel(initial=[bed_level])

fm_model.save(recurse=True)

shutil.copyfile("../network_patched.nc", "network.nc")

subprocess.run([r"..\..\x64_2021\dflowfm\scripts\run_dflowfm.bat", fm_model.filepath], check=True)
