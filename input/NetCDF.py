"""
File that contains the functions to read files in NetCDF4 format.
"""
import logging as log
from netCDF4 import Dataset
import numpy as np


def read_info(filename: str):
    """
    Extract the information of X, Y and Z from a NetCDF4 file.

    Args:
        filename (str): Filename to analize.

    Returns:
        np.array, np.array, np.array: Values of the variables X, Y
                                      and Z in the file.
    """
    rootgrp = Dataset(filename, "r", format="NETCDF4")

    X = np.array(rootgrp.variables["x"])
    Y = np.array(rootgrp.variables["y"])
    Z = np.array(rootgrp.variables["z"])

    return X, Y, Z


if __name__ == "__main__":
    log.basicConfig(format="%(asctime)s - %(message)s", level=log.INFO)

    filename = "./test_inputs/IF_60Ma_AHS_ET.nc"

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
