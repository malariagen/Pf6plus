# -*- coding: utf-8 -*-

def tabulate_drug_resistant(
    data, drug, country=None, population=None, year=None, bin=False
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
