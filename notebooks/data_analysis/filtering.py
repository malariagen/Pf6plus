import numpy as np
import pandas as pd


def define_year_bins(years):
    years = np.array(years)
    year_range = []
    if len(years.shape) == 1:
        year_range.extend(list(range(years[0], years[1] + 1)))
    else:
        for bin_i in range(years.shape[0]):
            year_range.extend(list(range(years[bin_i][0], years[bin_i][1] + 1)))
    return year_range


def filter_years(data, years, bin=False):
    if years:
        if bin:
            years = define_year_bins(years)
        data = data.loc[(data["Year"].isin(years))]
    return data


def filter_data_by_country_and_population(
    data, threshold, country=None, population=None
):
    # Only keep data with country and population matching
    locus_year_group = pd.DataFrame(
        data.loc[(data["Country"] == country) & (data["Population"] == population)]
    )
    # Only keep data with country and population matching
    pf_country = filter_countries_and_years_below_threshold(locus_year_group, threshold)
    return pf_country


def filter_data_by_population(data, threshold, country=None, population=None):
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
    # Only include dates and country combinations that have over threshold of data points
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


def filter_WGS_data(data):
    return data.loc[data["Process"] == "WGS"].copy()


def filter_non_WGS_data(data):
    return data.loc[data["Process"] != "WGS"].copy()


def find_studies_at_coord(data, lat, long):
    studies = np.unique(
        data.loc[data["Latitude_adm1"] == lat].loc[data["Longitude_adm1"] == long].Study
    )
    return studies


def find_samples_per_location(data):
    samples_per_location = (
        data.groupby(["Longitude_adm1", "Latitude_adm1"])
        .size()
        .reset_index()
        .rename(columns={0: "Samples"})
    )
    return samples_per_location
