# -*- coding: utf-8 -*-
import pandas as pd
from data_analysis.plotting import Subplots


def plot_samples_per_country_and_study_histogram(dataset):
    # Find samples per country and study
    samples_per_country_and_study = (
        dataset.groupby(["Country", "Study"]).size().unstack().fillna(0)
    )
    # Plot
    figure = Subplots(colours=True)
    figure.add_bar_plot_stacked(
        samples_per_country_and_study,
        "Countries",
        "Studies Contributing to Pf6+ Across Countries",
        list(samples_per_country_and_study.index),
    )


def plot_temporal_samples_histogram(dataset):
    # Find samples per year for WGS and amplicon
    process_and_year_count = (
        dataset.groupby(["Process", "Year"]).size().unstack().fillna(0).transpose()
    )
    process_and_year_count["GenRe-Mekong"] = process_and_year_count.drop(
        ["WGS"], axis=1
    ).sum(axis=1)
    process_and_year_count = process_and_year_count.rename(columns={"WGS": "Pf6"})
    # Plot
    figure = Subplots(colours=True)
    figure.add_bar_plot_stacked(
        process_and_year_count[["Pf6", "GenRe-Mekong"]],
        "Year",
        "Year of Collection for Samples in Pf6 and GenRe-Mekong",
        (
            min(process_and_year_count.index) - 0.5,
            max(process_and_year_count.index) + 0.5,
        ),
    )


def plot_temporal_samples_grouped_by_study_histogram(dataset):
    grouped_by_year_and_study = (
        dataset.groupby(["Year", "Study"]).size().unstack().fillna(0)
    )
    figure = Subplots(colours=True)
    figure.add_bar_plot_stacked(
        grouped_by_year_and_study,
        "Year",
        "Studies Contributing to Pf6+ Across Years",
        (
            min(grouped_by_year_and_study.index) - 0.5,
            max(grouped_by_year_and_study.index) + 0.5,
        ),
    )
