!["PF6+ logo"](pf6plus_documentation/images/pf6plus-logo.png)

# Pf6+

**_Analysis of aggregated phenotype and genotype data (amplicon + Pf6 WGS)._**

This repository provides an issue tracker and technical documentation for Pf6+.

For further information, please see the [Pf6+ data user guide](https://malariagen.github.io/Pf6plus/).

If you find a bug with any public data or documentation, please raise an issue on this repo.

## Contents
  * [Pf6+ Documentation](#Pf6-Documentation)
    * [Viewing the Documentation](#Viewing-the-Documentation)
    * [Running the Code in Colab](#Running-the-Code-in-Colab)
    * [Running the Notebooks Locally](#Running-the-Notebooks-Locally)
      * [Dependencies](#Dependencies)
      * [How to Install Python Modules in a Virtual Environment](#How-to-Install-Python-Modules-in-a-Virtual-Environment)
      * [Cloning the Repository](#Cloning-the-Repository)
      * [Running Jupyter](#Running-Jupyter)
  * [Documentation for Developers](#Documentation-for-Developers)
    * [Deployment](#Deployment)
    * [Making Changes to the Notebooks](#Making-Changes-to-the-Notebooks)
    * [Data Analysis](#Data-Analysis)
    * [Developing on JupyterLab on the Farm](#Developing-on-JupyterLab-on-the-Farm)

## Pf6+ Documentation

Included in the `pf6plus_documentation` directory in this repository is a set of notebooks. They are a guide to using the Pf6+ dataset.

- **1_partners_270921.ipynb** : This notebook explores the Pf6+ metadata and shows the benefits that combining the GenRe data and Pf6 can have.
- **2_prevalence_DR_haps_270921.ipynb** : This notebook shows some basic data analysis exploring the haplotypes and phenotypes.
- **3_phenotyper.ipynb This notebook** : This notebook runs through an example of using the phenotyper tool on a GRC.

### Viewing the Documentation

You can view the documentation [here](https://malariagen.github.io/Pf6plus/). All of the plots are interactive, so if you hover over points more information will be shown and you can zoom in and out with the tool bar.

### Running the Code in Colab

The most simple way to run the code yourself is to open the notebooks in Colab. To do this open the [documentation](https://malariagen.github.io/Pf6plus/) and select the notebook you would like to open from the three options. Click on the rocket icon in the top right hand corner and select Colab, as shown below.

!["Open colab](pf6plus_documentation/images/open_colab.png)

The notebooks contain instructions for getting setup to run the code in colab.

### Running the Notebooks Locally

To run the notebooks on your own machine you will need to clone this repository and install the following dependencies: 

#### Dependencies

- Jupyter
- Python3 
- numpy
- folium
- matplotlib
- bokeh
- pandas

#### How to Install Python Modules in a Virtual Environment

Running this notebook on your own machine requires Python packages to be installed. We recommend doing this in a virtual environment. 
Open a terminal and follow these instructions:

1. Create a virtual environment by typing out the following commands, replacing `<path to python3>`.

```
virtualenv -p <path to python3> pf6plus_notebooks_env
source pf6plus_notebooks_env/bin/activate
```

2. Install the dependencies in the virtual environment

```
pip install numpy folium matplotlib bokeh pandas 
```

You will only have to install the dependencies once and then you will have everything you need installed in an environment.
To exit out of the environment simply type the following on the command line:

```
deactivate
```

If you want to enter the environment again you won't need to install anything again. Simply enter the following on the command line and it will load up everything you installed before:

```
source pf6plus_notebooks_env/bin/activate
```

#### Cloning the Repository

You will then need to clone this repository to your own machine. Navigate to where you would like to store this and run the following command:

```
git clone https://gitlab.com/malariagen/gsp/pf6plus.git
```

#### Running Jupyter

To launch Jupyter Notebook simply navigate to where you cloned this repo and run the following:

```
cd notebooks
jupyter-notebook
```

## Documentation for Developers

The documentation is a set of Jupyter Notebooks contained in the `pf6plus_documentation/notebooks/` directory.

### Deployment

The notebooks are deployed automatically as a Jupyter Book to GitHub Pages by a GitHub Workflow. This is configured in `Pf6plus/.github/workflows/gh-pages.yml` to install dependencies, build the book, and push it to `gh-pages`. The dependencies are listed in `requirements-deploy.txt`. This will run when a change to anything in the `pf6plus_documentation/` directory is merged into the master branch.

The configuration for the Jupyter Book is set up in the `pf6plus_documentation/` directory by three files:

- **\_config.yml** : contains the configuration for the book.
- **\_toc.yml** : configures the layout for the different sections of the book.
- **landing-page.md** : formats the landing page for opening the book.

### Making Changes to the Notebooks

Make any changes you wish to make on a branch.
You should test these changes locally before merging them into the master branch. You will need jupyter-book installed to do this, you can install this with `pip` if you do not already have it.
Navigate to the head directory of the repository and run the following to build the Jupyter Book locally.

```
jupyter-book build pf6plus_documentation
```

If everything is successful this should output a link. Copy and paste this into your browser to check that your changes have been successful.

### Data Analysis

The `pf6plus_documentation/notebooks/data_analysis/` directory contains the code used to produce the figures shown in the notebooks. If you make any changes to the code, you will need to re-run the notebooks for the changes to be reflected in the plots.

### Developing on JupyterLab on the Farm

1. Log into the farm 
2. Clone the [bsub jupyterlab repository](https://github.com/wtsi-hgi/bsub_jupyter_lab)
3. Clone the [pf6plus repository](https://github.com/malariagen/Pf6plus)
4. From the head directory of `bsub_jupyter_lab` run the following command, replacing `<team>` with your lsf group:
```
./bsub_jupyter_lab.sh -g <team> -c 4 -m 50000 -q normal
```
5. Copy the link that is output into your browser and JupyterLab should load
6. Create a virtual environment and activate it
```
virtualenv -p <path to python3> pf6plus_env
pf6plus_env/bin/activate
```
7. Install using pip
```
pip install ipykernel numpy folium matplotlib bokeh pandas
```
8. Manually add the kernel so you can select it in the notebook
```
python -m ipykernel install --user --name=pf6plus_env
```
9. Open notebook and set kernel to `pf6plus_env`
10. When you are done with this environment you can remove it as an option from your jupyter notebooks by running:
```
jupyter kernelspec uninstall myenv 
```