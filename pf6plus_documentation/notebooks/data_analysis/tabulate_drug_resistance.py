# -*- coding: utf-8 -*-
import pandas as pd
from data_analysis.filtering import filter_years
from data_analysis.plot_dr_prevalence import DrugResistancePrevalence, set_population


def tabulate_drug_resistant(
    data, drug, country=None, population=None, years=None, bin=False
):

    """Tabulate the frequency of drug resistant samples per country/year

    Parameters:
      - drug: Any of the drugs in the Pf6+ dataframe ['Artemisinin', 'Chloroquine', 'DHA-PPQ', 'Piperaquine', 'Pyrimethamine', 'S-P', 'S-P-IPTp', 'Sulfadoxine']
      - country: Any of the countries in the Pf6+ dataframe (if specified, population value is not used) ['Bangladesh', 'Benin', 'Burkina Faso', 'Cambodia', 'Cameroon',
       'Colombia', "Côte d'Ivoire", 'Democratic Republic of the Congo',
       'Ethiopia', 'Gambia', 'Ghana', 'Guinea', 'India', 'Indonesia',
       'Kenya', 'Laos', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
       'Mozambique', 'Myanmar', 'Nigeria', 'Papua New Guinea', 'Peru',
       'Senegal', 'Tanzania', 'Thailand', 'Uganda', 'Vietnam']
      - population: Any of the populations in the Pf6+ dataframe ['CAF', 'EAF', 'ESEA', 'OCE', 'SAM', 'SAS', 'WAF', 'WSEA']
      - years: An array with the year(s) in the Pf6+ dataframe [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
      - bin: If True, all the years between the specified values will be used. If False, individual years are used.

    Returns:
      A dataframe showing the number of Resistant, Sensitive & Undetermined
      samples using the drug/country/year (or) drug/country/year combination provided. . The total number
      of samples and drug resistant frequency is also provided.
    """
    # filter years, keeping all if none set
    data_filtered_by_year = filter_years(data, years, bin)
    dr_prev = DrugResistancePrevalence(drug)

    if country:
        population = set_population(population, country, data)
        data_filtered_by_year = pd.DataFrame(
            data_filtered_by_year.loc[
                (data_filtered_by_year["Country"] == country)
                & (data_filtered_by_year["Population"] == population)
            ]
        )
        # TODO: if no data

        phenotypes = dr_prev.count_phenotypes_per_year(data_filtered_by_year)
    elif population:
        data_filtered_by_year = pd.DataFrame(
            data_filtered_by_year.loc[
                (data_filtered_by_year["Population"] == population)
            ]
        )
        phenotypes = dr_prev.count_phenotypes_per_year(data_filtered_by_year)
    else:
        phenotypes = (
            data_filtered_by_year.groupby(["Country", drug])
            .size()
            .unstack()
            .fillna(0)
            .astype(int)
        )
    phenotypes["Total"] = phenotypes.sum(axis=1)

    # calculating the frequency using all samples, no matter how many they are! (note that some combinations will have a small number of samples, so the frequency will not be an adequeate estimate))
    phenotypes["Resistant Frequency"] = (
        phenotypes["Resistant"] / (phenotypes["Resistant"] + phenotypes["Sensitive"])
    ).round(2)

    return phenotypes
