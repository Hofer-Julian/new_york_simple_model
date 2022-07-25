from hydrolib.core.io.mdu.models import FMModel
from hydrolib.core.io.xyz.models import XYZModel, XYZPoint
from hydrolib.core.io.inifield.models import (
    IniFieldModel,
    InitialField,
    InterpolationMethod,
    DataFileType,
)
from hydrolib.core.io.ext.models import ExtModel, Boundary
from pathlib import Path
import os
import shutil
from distutils.dir_util import copy_tree
from bmi.wrapper import BMIWrapper
import matplotlib.pyplot as plt

modelname = "model"

if Path(modelname).exists():
    shutil.rmtree(modelname)

os.mkdir(modelname)
copy_tree("initial_files", modelname)  # TODO: remove this
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


boundary = Boundary(
    quantity="waterlevelbnd", locationfile="Boundary01.pli", forcingfile="WaterLevel.bc"
)
external_forcing = ExtModel(boundary=[boundary])
fm_model.external_forcing.extforcefilenew = external_forcing

fm_model.save(recurse=True)

os.chdir("..")
os.environ["PATH"] = (
    str(Path().cwd() / "dflowfm_dll") + os.pathsep + os.environ["PATH"]
)

with BMIWrapper(
    engine="dflowfm", configfile=os.path.abspath(f"{modelname}/{modelname}.mdu")
) as model:
    index = 0
    while model.get_current_time() < model.get_end_time():
        model.update()
        if index == 10:
            x = model.get_var("xz")
            y = model.get_var("yz")
            water_depth = model.get_var("hs")
            fig, ax  = plt.subplots()
            sc = ax.scatter(x, y, c=water_depth)
            fig.colorbar(sc)
            plt.show()

        index += 1
