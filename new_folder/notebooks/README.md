# Pf6+ Jupyter Notebooks

These notebooks are a guide to using the Pf6+ dataset.

- 1_partners_270921.ipynb This notebook explores the Pf6+ metadata and shows the benefits that combining the GenRe data and Pf6 can have.
- 2_prevalence_DR_haps_270921.ipynb This shows some basic data analysis exploring the haplotypes and phenotypes.
- 3_phenotyper.ipynb This notebook runs through an example of using the phenotyper tool on a grc

## Dependencies

## Data Analysis

The directory called Data analysis contains the code used to produce the figures shown in the notebooks.

## Running the notebooks

### Running on Colab

You can run the notebooks on colab

### Running Locally

There are a few steps to follow before running these notebooks locally.

***Installing Dependencies***

Running this notebook on your own machine requires Python packages to be installed.
Open a terminal and follow these instructions:
1. Create a virtual environment by typing out the following commands
```
virtualenv pf6plus_notebooks_env
source pf6plus_notebooks_env/bin/activate
```
2. Install the dependencies in the virtual environment
```
pip uninstall -q -y shapely #if using locally, you need to uninstall other shapely versions first

pip uninstall -q -y imgaug # uninstalling other 'imgaug' versions due to colab incompatibility
pip install imgaug==0.2.5

!pip install -q shapely --no-binary shapely \
                                    cartopy \
                                    geopandas \
```

***Cloning the repo***

You will then need to clone this repository to your own machine.  Navigate to where you would like to store this and run the following command: 
```
git clone https://gitlab.com/malariagen/gsp/pf6plus.git
```
***Running Jupyter***

To launch Jupyter Notebook simply navigate to where you downloaded this repo to and run the following:

```
cd notebooks 
jupyter-notebook
```

***Exiting the virtual environment***

You will only have to install the dependencies once and then you will have everything you need installed in an environment.
To exit out of the environment simply type the following on the command line:

```
deactivate
```

If you want to enter the environment again you won't need to install anything again. Simply enter the following on the command line and it will load up everything you installed before:

```
source pf6plus_notebooks_env/bin/activate
```
