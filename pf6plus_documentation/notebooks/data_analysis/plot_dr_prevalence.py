# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from data_analysis.plotting import Subplots
from data_analysis.filtering import (
    filter_years,
    filter_data_by_country_and_population,
    filter_data_by_population,
)


class DrugResistancePrevalence:

    """Functions to calculate the prevalence of drug resistance per year"""

    def __init__(self, drug):
        self.drug = drug

    def count_phenotypes_for_drug(self, data):
        try:
            resistant = len(data.loc[data[self.drug] == "Resistant"])
            sensitive = len(data.loc[data[self.drug] == "Sensitive"])
            undetermined = len(data.loc[data[self.drug] == "Undetermined"])
        except:
            return 0, 0, 0
        return resistant, sensitive, undetermined

    def count_phenotypes_per_year(self, data):
        phenotypes = (
            data.groupby(["Year", self.drug]).size().unstack().fillna(0).astype(int)
        )
        phenotypes = phenotypes.assign(Total=phenotypes.sum(1))
        return phenotypes

    def calculate_prevalence(self, data):
        data["Prevalence"] = [
            round(row[0] / (row[0] + row[1]), 2)
            for row in data[["Resistant", "Sensitive"]].to_numpy()
        ]
        return data


# separate class
def set_population(population, country, data):
    if not population:
        populations = list(np.unique(data.loc[(data["Country"] == country)].Population))
        if len(populations) != 1:
            error = "{} is part of more than one population. Please set one of the following options as the population argument:  {}".format(
                country, populations
            )
            raise ValueError(error)
        else:
            population = populations[0]
    else:
        check_population_country_combo(population, country, data)
    return population


def check_population_country_combo(population, country, data):
    countries = (
        data.loc[(data["Population"] == population)]["Country"].unique().tolist()
    )
    if country not in countries:
        raise ValueError(
            "No data available for the country-population combination specified. {} has data for the following countries: {}".format(
                population, countries
            )
        )


# Put in separate
def plot_dr_prevalence(
    data, drugs, country=None, population=None, years=None, bin=False, threshold=25
):

    """Plot the prevalence of resistant samples per country/year

    Parameters:
      - drug: Any/list of the drugs in the Pf6+ dataframe ['Artemisinin', 'Chloroquine', 'DHA-PPQ', 'Piperaquine', 'Pyrimethamine', 'S-P', 'S-P-IPTp', 'Sulfadoxine']
      - country: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon',
       'Colombia', "Côte d'Ivoire", 'Democratic Republic of the Congo',
       'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia',
       'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
       'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru',
       'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Vietnam']
      - population: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - year: Any/list of the years in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.
      - threshold: To increase confidence on disperse data, only use country (or) population/year combinations with n_samples>threshold (default=25)

    Returns:
      A series of plots (one per drug) showing the prevalence of resistant variants the drug/country/year (or) drug/country/year combination provided.
    """
    #     if not isinstance(drugs, list):
    #         raise ValueError('Drugs parameter must be a list.')
    population = set_population(population, country, data)

    data = filter_years(data, years, bin)
    pf_country = filter_data_by_country_and_population(
        data, threshold, country, population
    )
    pf_population = filter_data_by_population(data, threshold, country, population)

    figure = Subplots(colours=True)
    plot_i = 0
    for drug in drugs:
        dr_prev = DrugResistancePrevalence(drug)
        # Count phenotypes
        phenotypes_country = dr_prev.count_phenotypes_per_year(pf_country)
        phenotypes_population = dr_prev.count_phenotypes_per_year(pf_population)

        # CHECK DATA
        # calculate prevalence
        try:
            phenotypes_country = dr_prev.calculate_prevalence(phenotypes_country)
        except:
            # add diff exceptions messages (dependending on resistant, sensitive, undetermined)
            print(
                "WARNING: Not enough data on {} resistant variants in {} dataset. No plot will be produced.".format(
                    drug, country
                )
            )
            continue

        try:
            phenotypes_population = dr_prev.calculate_prevalence(phenotypes_population)
        except:
            # still plot country, but don't plot population data
            phenotypes_population = pd.DataFrame(
                columns=phenotypes_country.columns, index=phenotypes_country.index
            )
            print(
                "WARNING: Not enough data on {} resistant variants in {} dataset. Only plotting country data.".format(
                    drug, population
                )
            )
        prevalences = pd.merge(
            phenotypes_country["Prevalence"],
            phenotypes_population["Prevalence"],
            on=["Year"],
            how="outer",
            suffixes=[
                " {}".format(country),
                " {} excluding {}".format(population, country),
            ],
        ).sort_index()

        # Add subplot
        title = "{} resistance prevalence in {}".format(
            drug,
            country,
        )
        sub_title = "({}-{})".format(
            str(min(prevalences.index)),
            str(max(prevalences.index)),
        )
        figure.plot_subplot(
            plot_i,
            prevalences,
            title,
            sub_title,
        )
        plot_i += 1
    figure.plot_figure_grid()


def count_phenotypes_for_list_of_drugs(drugs, data):
    resistant = []
    sensitive = []
    undetermined = []
    for drug in drugs:
        d = DrugResistancePrevalence(drug)
        res, sens, undet = d.count_phenotypes_for_drug(data)
        resistant.append(res)
        sensitive.append(sens)
        undetermined.append(undet)
    return resistant, sensitive, undetermined


def plot_phenotype_bar_chart_compared_to_pf6plus(dataset, pf6plus):
    figure = Subplots(colours=True)

    # For results from grc
    drugs = [
        "Artemisinin",
        "Chloroquine",
        "DHA-PPQ",
        "Piperaquine",
        "Pyrimethamine",
        "SP",
        "SP-IPTp",
        "Sulfadoxine",
    ]
    pf6plus_drugs = [
        "Artemisinin",
        "Chloroquine",
        "DHA-PPQ",
        "Piperaquine",
        "Pyrimethamine",
        "S-P",
        "S-P-IPTp",
        "Sulfadoxine",
    ]

    resistant, sensitive, undetermined = count_phenotypes_for_list_of_drugs(
        drugs, dataset
    )
    figure.add_bar_plot(0, drugs, resistant, sensitive, undetermined, "GRC Phenotypes")
    resistant, sensitive, undetermined = count_phenotypes_for_list_of_drugs(
        pf6plus_drugs, pf6plus
    )
    figure.add_bar_plot(
        1, pf6plus_drugs, resistant, sensitive, undetermined, "Pf6+ Phenotypes"
    )
    figure.plot_figure_grid()
