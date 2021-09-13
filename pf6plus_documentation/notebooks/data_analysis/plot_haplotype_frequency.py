# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from data_analysis.plotting import Subplots
from data_analysis.filtering import (
    filter_years,
    filter_countries_and_years_below_threshold,
)


class FindTopHaplotypes:

    """Functions to find most frequent haplotypes for a gene"""

    def __init__(self, gene, data):
        self.gene = gene
        self.data = data

    def order_haps_by_freq(self):
        top_haps = list(
            self.data.groupby(self.gene).size().sort_values(ascending=False).index
        )
        return top_haps

    def filter_out_invalid_haps(self, haplotypes):
        # TODO add in some exception if there isn't any data
        haplotypes = [hap for hap in haplotypes if "-" not in hap]
        haplotypes = [hap for hap in haplotypes if "," not in hap]
        return haplotypes

    def count_hap_freq_per_year(self, haplotypes):
        hap_freq_per_year = (
            self.data.groupby(["Year", self.gene])
            .size()
            .unstack()
            .fillna(0)
            .astype(int)[haplotypes]
        )
        return hap_freq_per_year

    def normalise_haplotype_frequency(self, haplotype_frequencies):
        return haplotype_frequencies.loc[:].div(
            haplotype_frequencies.sum(axis=1), axis=0
        )

    def truncate_haps_into_other_column(self, haplotype_frequencies, haplotypes):
        haplotype_frequencies_truncated = haplotype_frequencies[haplotypes].copy()
        haplotype_frequencies_truncated[
            "Other"
        ] = 1 - haplotype_frequencies_truncated.round(6).sum(axis=1)
        return haplotype_frequencies_truncated

    def normalised_count_top_n_haplotypes_per_year(self, n):
        top_haps = self.order_haps_by_freq()
        top_haps = self.filter_out_invalid_haps(top_haps)
        hap_freq_per_year = self.count_hap_freq_per_year(top_haps)
        normalised_hap_frequencies = self.normalise_haplotype_frequency(
            hap_freq_per_year
        )
        frequencies_of_top_n_haps = self.truncate_haps_into_other_column(
            normalised_hap_frequencies, top_haps[:n]
        )
        return frequencies_of_top_n_haps


def check_list(l):
    if not isinstance(l, list):
        raise ValueError("{} must be in a list. e.g. ['{}']".format(l, l))


def define_filters(country, population):
    if country:
        #         check_list(country)
        loc = "Country"
        filters = country
        if population:
            print(
                "WARNING: both population and country specified, will only filter by country."
            )
    elif population:
        #         check_list(population)
        loc = "Population"
        filters = population

    try:
        filters
    except:
        raise ValueError("No country or population provided")
    return loc, filters


def plot_haplotype_frequency(
    data,
    gene,
    num_top_haplotypes=5,
    threshold=25,
    countries=None,
    populations=None,
    years=None,
    bin=False,
):
    """Tabulate the frequency of top n haplotypes on a specific gene per country (or) population per year

    Parameters:
      - gene: Any of the genes in the Pf6+ dataframe ['PfCRT', 'Kelch', 'PfDHFR', 'PfEXO', 'PGB', 'Plasmepsin2/3', 'PfDHPS', 'PfMDR1']
      - num_top_haplotypes: The (n) most common haplotypes, default is 5. These excludes missing haplotypes.
      - countries: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon', 'Colombia', 'Congo DR', 'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia', 'Ivory Coast', 'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru', 'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Viet Nam']
      - populations: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - years: Any/list of the years in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.
      - threshold: To increase confidence on disperse data, only use country (or) population/year combinations with n_samples>threshold (default=25, must be greater than 0)
    Returns:
      A dataframe showing the number of Resistant, Sensitive & Undetermined
      samples using the drug/country/year (or) drug/country/year combination provided. The total number
      of samples and drug resistant frequency is also provided.
    """
    loc, filters = define_filters(countries, populations)
    nfilters = len(filters)

    # Only include dates specified
    data = filter_years(data, years, bin)

    figure = Subplots(colours=True)
    for i in range(nfilters):
        # Filter data
        locus_year_group = pd.DataFrame(data.loc[(data[loc] == filters[i])])
        samples_subset = filter_countries_and_years_below_threshold(
            locus_year_group, threshold
        )

        # Count n haplotypes per year and normalise
        haplotype_finder = FindTopHaplotypes(gene, samples_subset)
        normalised_phenotypes = (
            haplotype_finder.normalised_count_top_n_haplotypes_per_year(
                num_top_haplotypes
            )
        )
        # Plot
        title = "{} Predominant Variants in {}".format(gene, filters[i])
        colour_code_haps = figure.plot_subplot(i, normalised_phenotypes, title)
    figure.plot_figure_grid()
    return figure
