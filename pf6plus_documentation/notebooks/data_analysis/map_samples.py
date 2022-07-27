# -*- coding: utf-8 -*-
import numpy as np

# import plotting libraries
import folium
from folium.plugins import MarkerCluster

from data_analysis.plotting import assign_variables_colours
from data_analysis.filtering import (
    filter_WGS_data,
    filter_non_WGS_data,
    find_studies_at_coord,
    find_samples_per_location,
)


def filter_data_for_mapping(data, data_subset):
    label = data_subset
    if not data_subset or data_subset == "Pf6+":
        label = "Pf6+"
    elif data_subset == "Pf6":
        data = filter_WGS_data(data)
    elif data_subset == "GenRe":
        data = filter_non_WGS_data(data)
    return data, label


def set_colours_for_individual_sites(data, individual_sites):
    # choose colourmap palette for country category scatterplot
    if individual_sites == "Country":
        country_colours = assign_variables_colours(np.unique(data["Country"]))
        data["Colour_code"] = data["Country"].map(country_colours)
    elif individual_sites == "Population":
        population_colours = assign_variables_colours(np.unique(data["Population"]))
        data["Colour_code"] = data["Population"].map(population_colours)
    else:
        raise ValueError(
            "Individual sites must either be set to 'Country', 'Population', or False"
        )
    return data


class GeoPlotMap:

    """Functions to plot map"""

    def __init__(self, zoom_to_start=2, location_to_start=[13.1339, 16.1039]):
        self.zoom_to_start = zoom_to_start
        self.location_to_start = location_to_start
        self.my_map = folium.Map(
            location=self.location_to_start,
            zoom_start=self.zoom_to_start,
            tiles="cartodb positron",
        )
        url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
        self.country_shapes = ("{}/world-countries.json").format(url)

    def fill_in_countries(self, samples_per_country):
        folium.Choropleth(
            geo_data=self.country_shapes,
            name="choropleth",
            data=samples_per_country,
            columns=["Country", "Samples"],
            key_on="feature.properties.name",
            fill_color="YlOrRd",
            nan_fill_color="#FFFFFF00",
            fill_opacity=0.4,
            line_opacity=0.2,
            legend_name="Number of Samples",
            threshold_scale=[0, 500, 1000, 1500, 2000, 2500],
        ).add_to(self.my_map)
        return self.my_map

    def add_marker_to_cluster(self, cluster, lat, long, country, n_samples, studies):
        folium.Marker(
            location=[lat, long],
            popup=folium.map.Popup(
                (
                    (
                        "Country: {} <br>" "Samples: {} <br>" "Studies: <br> {} <br>"
                    ).format(country, n_samples, "<br>".join(studies))
                ),
                max_width=450,
            ),
            tooltip=country,
        ).add_to(cluster)

    def add_cluster_to_map(self):
        cluster = MarkerCluster().add_to(self.my_map)
        return cluster


def map_samples(data, data_subset=None, zoom_to_start=2, location=[13.1339, 16.1039]):
    data, label = filter_data_for_mapping(data, data_subset)
    # Count samples per country
    samples_per_country = (
        data.groupby(["Country"]).size().reset_index().rename(columns={0: "Samples"})
    )
    mapper = GeoPlotMap(zoom_to_start=zoom_to_start, location_to_start=location)
    my_map = mapper.fill_in_countries(samples_per_country)

    # for each country create a cluster
    for country in np.unique(data.Country):
        # add marker cluster
        country_cluster = mapper.add_cluster_to_map()
        country_data = data.loc[data.Country == country]
        # samples per location
        samples_per_location = find_samples_per_location(country_data)
        for _, location in samples_per_location.iterrows():
            # skip unknown coordinates
            if (location["LatitudeAdmDiv1"] == '-'):
                continue
            else:
                latitude = location["LatitudeAdmDiv1"]
                longitude = location["LongitudeAdmDiv1"]
                
            # Studies for site
            studies = find_studies_at_coord(
                country_data, latitude, longitude
            )
            # Add marker to country cluster
            mapper.add_marker_to_cluster(
                country_cluster,
                latitude,
                longitude,
                country,
                int(location.Samples),
                studies,
            )
    return my_map
