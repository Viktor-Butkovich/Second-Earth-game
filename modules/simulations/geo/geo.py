import matplotlib.pyplot as plt
import rasterio
import numpy as np
from scmrepo.git import Git
from pathlib import Path

PACKAGE_ROOT = Git(root_dir=".").root_dir

out_dir = f"{PACKAGE_ROOT}/modules/simulations/geo/geo_out"
Path(out_dir).mkdir(parents=True, exist_ok=True)


def main():
    print("Running geo.py")
