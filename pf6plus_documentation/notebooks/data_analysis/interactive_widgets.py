import ipywidgets as widgets


def create_year_slider():
    year_range_slider = widgets.IntRangeSlider(
        value=(2001, 2019),
        min=2001,
        max=2019,
        step=1,
        description="Range of Years",
        style={"description_width": "initial"},
    )
    return year_range_slider


def create_drug_options():
    pf6plus_drugs_options = widgets.SelectMultiple(
        options=[
            "Artemisinin",
            "Chloroquine",
            "DHA-PPQ",
            "Piperaquine",
            "Pyrimethamine",
            "S-P",
            "S-P-IPTp",
            "Sulfadoxine",
        ],
        value=["Artemisinin"],
        description="Drugs",
        style={"description_width": "initial"},
        disabled=False,
    )
    return pf6plus_drugs_options


def create_country_options(countries):
    country_options = widgets.Dropdown(
        options=countries,
        value=countries[0],
        description="Country",
        disabled=False,
    )
    return country_options


def create_population_options(populations):
    population_options = widgets.Dropdown(
        options=populations,
        value=None,
        description="Population",
        disabled=False,
    )
    return population_options


def create_threshold_options():
    threshold_options = widgets.IntSlider(
        min=0,
        max=100,
        step=1,
        value=25,
        description="Min Samples to include",
        style={"description_width": "initial"},
    )
    return threshold_options


def create_multi_country_options(countries):
    multi_country_options = widgets.SelectMultiple(
        options=countries,
        description="Country",
        style={"description_width": "initial"},
        disabled=False,
    )
    return multi_country_options


def create_multi_population_options(populations):
    multi_population_options = widgets.SelectMultiple(
        options=populations,
        rows=len(populations),
        value=[populations[0]],
        description="Population",
        style={"description_width": "initial"},
        disabled=False,
    )
    return multi_population_options


def create_num_haplotypes_slider():
    num_haplotypes_slider = widgets.IntSlider(
        min=0,
        max=10,
        step=1,
        value=5,
        description="Num Haplotypes to Plot",
        style={"description_width": "initial"},
    )
    return num_haplotypes_slider
