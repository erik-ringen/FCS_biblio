# FCS_biblio
Bibliometric analysis of Forager Child Studies research

# Setup

Before proceeding, make sure that you have either [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed. Once you do, open your terminal and:

(1) Clone this repository

```
git clone https://https://github.com/erik-ringen/FCS_biblio
```

(2) Install the conda environment

```
conda env create --file enironment.yml
```

(3) Activate the conda environment

```
conda activate FCS_biblio
```

All scripts in this repository should now run seamlessly.

# Re-producing analysis

To download publication data from Google Scholar, run the following from your terminal:
```
python process_pubdata.py
```

To do a textual analysis of the publication data and reproduce the main figure shown above, run:

```
python pub_analysis.py
```

Note that this will take a few minutes to run, as the Stan model is compiled into C++ code and sampled using MCMC.
