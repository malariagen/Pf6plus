import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import panel as pn

# Bokeh Libraries
import numpy as np
import bokeh.plotting
import bokeh.models
import bokeh.layouts
import bokeh.io
import bokeh.palettes
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category10, Accent, Dark2, Turbo256
import itertools
from bokeh.transform import dodge
from math import pi


class Subplots:

    """Functions to find most frequent haplotypes for a gene"""

    def __init__(self, ncol=2, colours=False):
        self.figures = []
        self.ncol = ncol
        self.colours = colours
        if self.colours:
            self.colour_code_dict = {}
            self.colour_options = Category10[10] + Accent[8] + Dark2[8] + Turbo256

    def add_colour_to_dictionary(self, new_key):
        if new_key not in self.colour_code_dict:
            self.colour_code_dict[new_key] = self.colour_options[
                len(self.colour_code_dict)
            ]

    def plot_subplot(self, plot_i, dataframe, title):
        figure = bokeh.plotting.figure(
            title=title,
            x_range=(2001, 2019),
            y_range=(0, 1),
            plot_width=1500,
            plot_height=300,
            tools="pan,wheel_zoom,box_zoom,reset,tap",
            toolbar_location="above",
            active_scroll="wheel_zoom",
            active_drag="pan",
        )
        for column in dataframe.columns:
            if self.colours:
                self.add_colour_to_dictionary(column)
                colour = self.colour_code_dict[column]
            else:
                colour = None

            temp_df = dataframe[[column]].dropna().rename(columns={column: "Data"})
            source = ColumnDataSource(temp_df)
            lines = figure.line(
                x="Year",
                y="Data",
                source=source,
                legend_label=column,
                line_width=2,
                color=colour,
            )
            circles = figure.circle(
                x="Year", y="Data", source=source, size=10, color=colour, alpha=0.5
            )
            figure.add_tools(
                HoverTool(renderers=[circles], tooltips=[("(x,y)", "(@Year,@Data)")])
            )
        figure.xaxis.axis_label = "Year"
        figure.yaxis.axis_label = "Prevalence"
        self.figures.append(figure)
        return figure

    def add_bar_plot(self, plot_i, drugs, resistant, sensitive, undetermined, title):

        drugs = sorted(drugs)
        data = {
            "drugs": drugs,
            "resistant": resistant,
            "sensitive": sensitive,
            "undetermined": undetermined,
        }
        source = ColumnDataSource(data=data)

        figure = bokeh.plotting.figure(
            x_range=drugs,
            y_range=(0, 550),
            plot_height=400,
            plot_width=400,
            title=title,
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,tap",
            active_scroll="wheel_zoom",
            active_drag="pan",
        )

        figure.vbar(
            x=dodge("drugs", -0.25, range=figure.x_range),
            name="resistant",
            top="resistant",
            width=0.2,
            source=source,
            color=self.colour_options[0],
            legend_label="resistant",
        )

        figure.vbar(
            x=dodge("drugs", 0.0, range=figure.x_range),
            name="sensitive",
            top="sensitive",
            width=0.2,
            source=source,
            color=self.colour_options[1],
            legend_label="sensitive",
        )

        figure.vbar(
            x=dodge("drugs", 0.25, range=figure.x_range),
            name="undetermined",
            top="undetermined",
            width=0.2,
            source=source,
            color=self.colour_options[2],
            legend_label="undetermined",
        )

        hover = HoverTool()
        hover.tooltips = """
        <div>
            <div><strong>Count: </strong>@$name</div>
        </div>"""
        figure.add_tools(hover)
        figure.x_range.range_padding = 0.1
        figure.xgrid.grid_line_color = None
        figure.legend.location = "top_left"
        figure.legend.orientation = "horizontal"
        figure.xaxis.major_label_orientation = pi / 4
        figure.xaxis.axis_label = "Drugs"
        figure.yaxis.axis_label = "# of samples"
        self.figures.append(figure)
        return figure

    def fill_figure_grid(self):
        if (len(self.figures) % 2) != 0:
            self.figures.append(None)

    def plot_figure_grid(self):
        self.fill_figure_grid()
        figure_layout = np.array(self.figures).reshape(-1, self.ncol).tolist()
        grid = gridplot(figure_layout, plot_width=400, plot_height=400)
        bokeh.plotting.show(grid)


def assign_variables_colours(variables):
    # dictionary storing the colours for each variable
    keys = np.unique(variables)
    colour_options = (
        list(mcolors.TABLEAU_COLORS) + list(mcolors.XKCD_COLORS)[: len(keys)]
    )
    variable_colours = {keys[i]: colour_options[i] for i in range(len(keys))}
    return variable_colours
