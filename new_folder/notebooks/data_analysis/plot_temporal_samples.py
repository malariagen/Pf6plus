# -*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import collections
import urllib.request
import math

# import plotting libraries
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy
import geopandas

# specifc imports to map and plot samples
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.offsetbox import AnchoredText
from collections import Counter
from cartopy.io import shapereader
from time import strftime

def temporal_samples(data, samples="Pf6+"):

    """Plot a stacked bar plot showcasing the temporal distribution of the samples in Pf6+."""
    # determine how many pixels (the resolution) of the plots
    plt.rcParams["figure.dpi"] = 200
    fig, ax = plt.subplots()

    if samples == "Pf6+":

        ax.bar(
            np.unique(data.loc[data["Process"] == "WGS"]["Year"]),
            np.unique(data.loc[(data["Process"] == "WGS"), "Year"], return_counts=True)[
                1
            ],
            label="Pf6",
        )
        ax.bar(
            np.unique(data.loc[data["Process"] != "WGS"]["Year"]),
            np.unique(data.loc[(data["Process"] != "WGS"), "Year"], return_counts=True)[
                1
            ],
            label="GenRe-Mekong",
        )
    elif samples == "Pf6":
                ax.bar(
            np.unique(data.loc[data["Process"] == "WGS"]["Year"]),
            np.unique(data.loc[(data["Process"] == "WGS"), "Year"], return_counts=True)[
                1
            ],
            label="Pf6",
        )
    elif samples == "GenRe":
        ax.bar(
            np.unique(data.loc[data["Process"] != "WGS"]["Year"]),
            np.unique(data.loc[(data["Process"] != "WGS"), "Year"], return_counts=True)[
                1
            ],
            label="GenRe-Mekong", color='tab:orange'
        )
    min_year = (data["Year"]).min()
    max_year = (data["Year"]).max()

    ax.set_xlim(min_year, max_year)

    ax.set_xlabel("Year")
    ax.set_ylabel("# of samples")
    ax.set_title("Year of Collection")
    ax.legend()
    plt.show()

