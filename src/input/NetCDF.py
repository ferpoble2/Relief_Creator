"""
File that contains the functions to read files in NetCDF4 format.
"""
import logging as log
import numpy as np
from netCDF4 import Dataset


def read_info(file_name: str):
    """
    Extract the information of X, Y and Z from a NetCDF4 file.

    Args:
        file_name (str): Filename to analize.

    Returns:
        np.array, np.array, np.array: Values of the variables X, Y
                                      and Z in the file.
    """
    root_grp = Dataset(file_name, "r", format="NETCDF4")

    x = np.array(root_grp.variables["x"])
    y = np.array(root_grp.variables["y"])
    z = np.array(root_grp.variables["z"])

    return x, y, z


if __name__ == "__main__":
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.DEBUG)

    filename = "test_inputs/IF_60Ma_AHS_ET.nc"

    rootgrp = Dataset(filename, "r", format="NETCDF4")

    log.debug("Dimensiones del archivo:")
    log.debug(rootgrp.dimensions)

    log.debug("Grupos del archivo:")
    log.debug(rootgrp.groups)

    log.debug("Variables del archivo:")
    log.debug(rootgrp.variables)

    X, Y, Z = read_info(filename)

    log.info("X values")
    log.info(X)

    log.info("Y values")
    log.info(Y)

    log.info("Z values.")
    log.info(Z)
