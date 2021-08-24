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


def assign_variables_colours(data, variable):
    # dictionary storing the colours for each variable
    populations = np.unique(data[variable])
    colour_options = list(mcolors.TABLEAU_COLORS) + list(mcolors.XKCD_COLORS)
    variable_colours = {
        populations[i]: colour_options[i] for i in range(len(populations))
    }
    return variable_colours


def define_country_borders():
    resolution = "10m"
    category = "cultural"
    name = "admin_0_countries"
    shpfilename = shapereader.natural_earth(resolution, category, name)
    df = geopandas.read_file(shpfilename)
    return df


def add_colour_bar(samples_norm, ax, fig, cmap):
    dummy_scat = ax.scatter(
        [None] * len(samples_norm),
        [None] * len(samples_norm),
        c=samples_norm,
        cmap=cmap,
        vmin=0,
        vmax=2302,
        zorder=0,
    )
    fig.colorbar(
        mappable=dummy_scat,
        label="Number of samples",
        orientation="vertical",
        shrink=0.3,
    )


def format_map_background(stock_image, ax):
    if stock_image:
        ax.stock_img()
    elif not stock_image:
        ax.add_feature(cartopy.feature.LAND, color="lightgray")
        ax.add_feature(cartopy.feature.OCEAN)
        ax.add_feature(cartopy.feature.COASTLINE, edgecolor="grey")


def setup_map_plot(stock_image, label):
    # determine how many pixels (the resolution) of the plots
    plt.rcParams["figure.dpi"] = 200

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-80, 153, -26, 29], crs=ccrs.PlateCarree())

    country_borders = define_country_borders()

    # choose whether to have a stock image on the map
    format_map_background(stock_image, ax)

    return ax, fig, country_borders


### Create a map showing the sample distribution
def map_samples(data, label, stock_image=False, individual_sites=False, save_fig=False):

    """Plot a world map showcasing the countries where the  Pf6+ samples come from."""

    # temp supressing warning for slicing subsets (mapping with exact number on both dataframes)
    pd.options.mode.chained_assignment = None
    ax, fig, country_borders = setup_map_plot(stock_image, label)

    if individual_sites:
        # choose colourmap palette for country category scatterplot
        if individual_sites == "Country":
            country_colours = assign_variables_colours(data, "Country")
            data["Colour_code"] = data["Country"].map(country_colours)
        elif individual_sites == "Population":
            population_colours = assign_variables_colours(data, "Population")
            data["Colour_code"] = data["Population"].map(population_colours)
        else:
            raise ValueError("Individual sites must either be set to Country or Population")
            

        # admin sites by colour of country
        ax.scatter(
            data["Longitude_adm1"],
            data["Latitude_adm1"],
            c=data["Colour_code"],
            s=3.5,
            marker="o",
            linewidth=0.3,
        )

    if not individual_sites:
        # Find data
        samples = np.unique(data["Country"], return_counts=True)[1]
        # normalising using the (# of samples) corresponding to the country with the highest number of samples.
        samples_norm = samples / 2302
        countries = np.unique(data["Country"], return_counts=True)[0]
        
        # choose colourmap palette for map
        cmap = plt.cm.get_cmap("YlOrRd")
        add_colour_bar(samples_norm, ax, fig, cmap)

        for country, samp_norm in zip(countries, samples_norm):
            borders = country_borders.loc[
                country_borders["ADMIN"] == country, "geometry"
            ].values[0]
            ax.add_geometries(
                [borders],
                crs=ccrs.PlateCarree(),
                facecolor=cmap(samp_norm),
                edgecolor="none",
                zorder=1,
            )
    plt.title(label + " Sampled Countries", fontsize=6)
    plt.show()

    # save figure as .png with label & data as name
    if save_fig:
        fig.savefig(f'{label}_{strftime("%Y-%m-%d")}.png', bbox_inches="tight", dpi=200)


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


def tabulate_drug_resistant(
    data, drug, country=None, population=None, year=None, bin=False
):

    """Tabulate the frequency of drug resistant samples per country/year

    Parameters:
      - drug: Any of the drugs in the Pf6+ dataframe ['Artemisinin', 'Chloroquine', 'DHA-PPQ', 'Piperaquine', 'Pyrimethamine', 'S-P', 'S-P-IPTp', 'Sulfadoxine']
      - country: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon', 'Colombia', 'Congo DR', 'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia', 'Ivory Coast', 'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru', 'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Viet Nam']
      - population: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - year: An array with the year(s) in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.

    Returns:
      A dataframe showing the number of Resistant, Sensitive & Undetermined
      samples using the drug/country/year (or) drug/country/year combination provided. . The total number
      of samples and drug resistant frequency is also provided.
    """

    if all([country, year]):

        if bin:
            samples = data.loc[
                (data.Country.isin([country]))
                & (data.Year.isin([b for b in range(min(year), max(year))]))
            ]
            print(
                drug
                + " resistant samples "
                + "in "
                + str(country)
                + " from "
                + str(min(year))
                + " to "
                + str(max(year))
            )
        else:
            samples = data.loc[(data.Country.isin([country])) & (data.Year.isin(year))]
            print(drug + " resistant samples in " + str(country) + " on " + str(year))

        phenotypes = (
            samples.groupby([drug])
            .size()
            .fillna(0)
            .astype(int)
            .to_frame("Samples")
            .transpose()
        )

    elif all([population, year]):

        if bin:

            samples = data.loc[
                (data.Population.isin([population]))
                & (data.Year.isin([b for b in range(min(year), max(year))]))
            ]
            print(
                drug
                + " resistant samples "
                + "in "
                + str(population)
                + " from "
                + str(min(year))
                + " to "
                + str(max(year))
            )
        else:
            samples = data.loc[
                (data.Population.isin([population])) & (data.Year.isin(year))
            ]
            print(
                drug + " resistant samples in " + str(population) + " on " + str(year)
            )

        phenotypes = (
            samples.groupby([drug])
            .size()
            .fillna(0)
            .astype(int)
            .to_frame("Samples")
            .transpose()
        )

    # if no year is specified, return all years
    elif country:
        samples = data.loc[data.Country.isin([country])]
        phenotypes = (
            samples.groupby(["Year", drug]).size().unstack().fillna(0).astype(int)
        )
        print(drug + " resistant samples in " + str(country))

    # if no country is specified, return all years
    else:
        if bin:
            samples = data.loc[data.Year.isin([b for b in range(min(year), max(year))])]
            print(
                drug
                + " resistant samples in all countries from "
                + str(min(year))
                + " to "
                + str(max(year))
            )

        elif population:
            samples = data.loc[(data.Population.isin([population]))]
            phenotypes = (
                samples.groupby(["Population", drug])
                .size()
                .unstack()
                .fillna(0)
                .astype(int)
            )
            print(drug + " resistant samples on all years")

        else:
            print(drug + " resistant samples on all years")
            phenotypes = (
                data.groupby(["Country", drug]).size().unstack().fillna(0).astype(int)
            )

    phenotypes = phenotypes.assign(Total=phenotypes.sum(1))

    # calculating the frequency using all samples, no matter how many they are! (note that some combinations will have a small number of samples, so the frequency will not be an adequeate estimate))
    phenotypes["Resistant Frequency"] = [
        round(row[0] / (row[0] + row[1]), 2)
        for row in phenotypes[["Resistant", "Sensitive"]].to_numpy()
    ]

    # fully troubleshoot numbers (TO DO)
    # add exception for multiple countries & multiple years (TO DO)
    # add exception for repeated countries/years (TO DO)
    # try:
    #   return phenotypes['Resistant']
    # except KeyError:
    #   raise KeyError('The specified Country/Year combination is not in the dataset')

    return phenotypes


def filter_country_data(data, threshold, country=None, population=None):
    # Only keep data with country and population matching
    locus_year_group = pd.DataFrame(
        data.loc[(data["Country"] == country) & (data["Population"] == population)]
    )
    # Only keep data with country and population matching
    pf_country = filter_countries_and_years_below_threshold(locus_year_group, threshold)
    return pf_country


def filter_population_data(data, threshold, country=None, population=None):
    # Only keep data from set population
    locus_year_group = pd.DataFrame(data.loc[(data["Population"] == population)])

    samples_subset = filter_countries_and_years_below_threshold(
        locus_year_group, threshold
    )

    # Keep all countries apart from one selected
    pf = samples_subset.loc[
        (samples_subset["Country"] != country)
        & (samples_subset["Population"] == population)
    ]
    return pf


def filter_countries_and_years_below_threshold(data, threshold):
    # Only keep data with country and population matching
    country_sample_size = pd.DataFrame(data.groupby(["Year", "Country"]).size())
    country_sample_size = country_sample_size.reset_index()
    # Only include dates that have over threshold of data points
    filtered_data = data.loc[
        (
            data["Year"].isin(
                country_sample_size[country_sample_size[0] > threshold]["Year"]
            )
        )
        & (
            data["Country"].isin(
                country_sample_size[country_sample_size[0] > threshold]["Country"]
            )
        )
    ]
    return filtered_data


def count_phenotypes(data, drug):
    phenotypes = data.groupby(["Year", drug]).size().unstack().fillna(0).astype(int)
    phenotypes = phenotypes.assign(Total=phenotypes.sum(1))
    return phenotypes


def calculate_prevalence(data, drug):
    if ("Resistant" in data) & ("Sensitive" in data):
        data["Prevalence " + drug] = [
            round(row[0] / (row[0] + row[1]), 2)
            for row in data[["Resistant", "Sensitive"]].to_numpy()
        ]

    elif "Resistant" in data:
        data["Prevalence " + drug] = [
            round(row[0] / (row[0]), 2) for row in data[["Resistant"]].to_numpy()
        ]

    elif "Sensitive" in data:
        data["Prevalence " + drug] = [
            round(row[0] / (row[0]), 2) for row in data[["Sensitive"]].to_numpy()
        ]
        
    return data


def generate_subplots(k):
    # Choose subplot dimensions
    ncol = 2
    nrow = math.ceil(k / ncol)
    # set up figure
    figure, axes = plt.subplots(nrow, ncol, figsize=(5 * ncol, 3 * nrow))
    axes = axes.flatten()
    return figure, axes


def remove_unused_axes(figure, axes, n_plotable, n_plotted):
    if (n_plotable % 2) != 0:
        n_plotable += 1
    for k in range(n_plotted, n_plotable):
        figure.delaxes(axes.flatten()[k])
    return figure, axes


def setup_subplot(axes, plot_i):
    ax = axes.flatten()[plot_i]
    ax.set_ylim(0, 1)
    ax.set_xlim(2001, 2019)
    ax.set_xlabel("Year")
    ax.set_ylabel("Prevalence")
    return ax


def add_subplot(
    axes, plot_i, phenotypes_country, phenotypes_population, drug, country, population
):
    ax = setup_subplot(axes, plot_i)
    ax.plot(phenotypes_country.iloc[:, -1], "o-", label="Prevalence " + country)
    ax.plot(phenotypes_population.iloc[:, -1], "o-", label="Prevalence " + population)
    ax.set_title(
        drug
        + " resistance prevalence in "
        + country
        + " from "
        + str(min(phenotypes_population.index))
        + " to "
        + str(max(phenotypes_population.index)),
        size=10,
    )
    ax.legend()

def check_population(population,data, country):
    
    if not population: 
        populations = list(np.unique(data.loc[(data["Country"] == country)].Population))
        if len(populations)!=1:
            error = "{} is part of more than one population. Please set one of the following options as the population argument:  {}".format(country,populations)
            raise ValueError(error)
        else:
            population = populations[0]  
    return population
            
    
def define_year_bins(years):
            years = np.array(years)
            year_range = []
            if len(years.shape) == 1: 
                year_range.extend(list(range(years[0],years[1]+1)))
            else:
                for bin_i in range(years.shape[0]):
                    year_range.extend(list(range(years[bin_i][0],years[bin_i][1]+1)))
            return year_range
        
            
def plot_dr_prevalence(
    data, drugs, country=None, population=None, years=None, bin=False, threshold=25
):

    """Plot the prevalence of resistant samples per country/year

    Parameters:
      - drug: Any/list of the drugs in the Pf6+ dataframe ['Artemisinin', 'Chloroquine', 'DHA-PPQ', 'Piperaquine', 'Pyrimethamine', 'S-P', 'S-P-IPTp', 'Sulfadoxine']
      - country: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon', 'Colombia', 'Congo DR', 'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia', 'Ivory Coast', 'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru', 'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Viet Nam']
      - population: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - year: Any/list of the years in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.
      - threshold: To increase confidence on disperse data, only use country (or) population/year combinations with n_samples>threshold (default=25)

    Returns:
      A series of plots (one per drug) showing the prevalence of resistant variants the drug/country/year (or) drug/country/year combination provided.
    """
    population = check_population(population,data,country)  
            
    # determine how many pixels (the resolution) of the plots
    plt.rcParams["figure.dpi"] = 200

    #Only include dates specified 
    if years: 
        if bin: 
            years = define_year_bins(years)
        data = data.loc[(data['Year'].isin(years))]
        
    # Filter out country specific data
    pf_country = filter_country_data(data, threshold, country, population)
    # Filer out population specific data for everything other than the country defined by the user
    pf_population = filter_population_data(data, threshold, country, population)

    # Set up df for prevelence for each drug
    years = data["Year"].unique()
    ndrugs = len(drugs)

    fig, axes = generate_subplots(ndrugs)
    plot_i = 0
    for drug in drugs:

        # Count phenotypes
        phenotypes_country = count_phenotypes(pf_country, drug)
        phenotypes_population = count_phenotypes(pf_population, drug)
        # check if it is in the data before giving the size
        try:
            phenotypes_country["Resistant"]
            phenotypes_country["Sensitive"]
        except:
            # add diff exceptions messages (dependending on resistant, sensitive, undetermined)
            print("Not enough data on {} resistant variants in {} dataset".format(drug,country))
            continue
            

        # add exceptions for spellings and countries not matching the population provided (allow but throw a warning)
        # Calculate prevalence
        phenotypes_population = calculate_prevalence(phenotypes_population, drug)
        phenotypes_country = calculate_prevalence(phenotypes_country, drug)
        # Add subplot
        add_subplot(
            axes,
            plot_i,
            phenotypes_country,
            phenotypes_population,
            drug,
            country,
            population,
        )
        plot_i += 1
    fig.tight_layout()
    remove_unused_axes(fig, axes, ndrugs, plot_i)


def find_top_haplotypes(data, gene):
    top_haps = list(data.groupby(gene).size().sort_values(ascending=False).index)
    # exclude missing values for all haplotypes
    # TODO add in some exception if there isn't any data
    top_haps = [hap for hap in top_haps if "-" not in hap]
    top_haps = [hap for hap in top_haps if "," not in hap]
    return top_haps


def plot_haplotype_frequency(
    data,
    gene,
    num_top_haplotypes=5,
    threshold=25,
    country=None,
    population=None,
    year=None,
    bin=False,
):
    """Tabulate the frequency of top n haplotypes on a specific gene per country (or) population per year

    Parameters:
      - gene: Any of the genes in the Pf6+ dataframe ['PfCRT', 'Kelch', 'PfDHFR', 'PfEXO', 'PGB', 'Plasmepsin2/3', 'PfDHPS', 'PfMDR1']
      - num_top_haplotypes: The (n) most common haplotypes, default is 5. These excludes missing haplotypes.
      - country: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon', 'Colombia', 'Congo DR', 'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia', 'Ivory Coast', 'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru', 'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Viet Nam']
      - population: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - year: Any/list of the years in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.
      - threshold: To increase confidence on disperse data, only use country (or) population/year combinations with n_samples>threshold (default=25, must be greater than 0)
    Returns:
      A dataframe showing the number of Resistant, Sensitive & Undetermined
      samples using the drug/country/year (or) drug/country/year combination provided. The total number
      of samples and drug resistant frequency is also provided.
    """
    # determine how many pixels (the resolution) of the plots
    plt.rcParams["figure.dpi"] = 200

    if country:
        loc = "Country"
        filters = country
        if population:
            print(
                "WARNING: both population and country specified, will only filter by country."
            )
    elif population:
        loc = "Population"
        filters = population
    else:
        print("No country or population provided")

    nfilters = len(filters)
    fig, axes = generate_subplots(nfilters)

    # Set haplotypes colours
    colour_options = list(mcolors.TABLEAU_COLORS) + list(mcolors.XKCD_COLORS)
    colour_code_haps = {}
    colour_n = 0
    for i in range(nfilters):
        # get samples size for country or population selected
        locus_year_group = pd.DataFrame(data.loc[(data[loc] == filters[i])])
        # Only keep data with country and population matching
        samples_subset = filter_countries_and_years_below_threshold(
            locus_year_group, threshold
        )
        # Count n haplotypes per year and normalise
        normalised_phenotypes = count_top_n_haplotypes_per_year(
            samples_subset, gene, num_top_haplotypes
        )

        # Plot
        colour_code_haps, colour_n = plot_hap(
            axes,
            i,
            normalised_phenotypes,
            colour_code_haps,
            colour_options,
            colour_n,
            gene,
            filters[i],
        )
    fig.tight_layout()
    remove_unused_axes(fig, axes, nfilters, nfilters)


def count_top_n_haplotypes_per_year(samples_subset, gene, n):
    # Count haplotypes per year
    phenotypes = (
        samples_subset.groupby(["Year", gene]).size().unstack().fillna(0).astype(int)
    )
    # Find most frequent haplotypes
    top_haps = find_top_haplotypes(samples_subset, gene)
    phenotypes = phenotypes[top_haps]
    # normalise data
    normalised_phenotypes = phenotypes.loc[:].div(phenotypes.sum(axis=1), axis=0)
    # keep top n haplotypes
    normalised_phenotypes = normalised_phenotypes[top_haps[:n]]
    # Calculate sum of all haplotypes not included
    normalised_phenotypes["Other"] = 1 - normalised_phenotypes.round(6).sum(axis=1)
    return normalised_phenotypes


def add_colour(hap, colour_code_haps, colour_options, colour_n):
    # Set haplotypes colours
    if hap not in colour_code_haps:
        colour_code_haps[hap] = colour_options[colour_n]
        colour_n += 1
        if colour_n == (len(colour_options) - 1):
            colour_n = 0
    return colour_code_haps, colour_n


def plot_hap(
    axes, plot_i, dataframe, colour_code_haps, colour_options, colour_n, gene, filter
):
    ax = setup_subplot(axes, plot_i)
    for hap in dataframe.columns:
        # Set haplotypes colours
        colour_code_haps, colour_n = add_colour(
            hap, colour_code_haps, colour_options, colour_n
        )
        ax.plot(
            dataframe[hap],
            label=hap,
            linestyle="--",
            marker="o",
            color=colour_code_haps[hap],
        )
    ax.axvline(2012, color="grey", linestyle="--", linewidth=1)
    ax.set_title(gene + " Predominant Variants in " + filter)
    ax.legend()
    return colour_code_haps, colour_n
