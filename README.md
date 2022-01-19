# FCS_biblio
Bibliometric analysis of research in the interdisciplinary [Forager Child Studies collective](https://foragerchildstudies.wixsite.com/home).

<p align="center">
<figure class="image">
<img src="https://github.com/erik-ringen/FCS_biblio/blob/main/img/word_cor.png" width="500">
  <figcaption>Top 20 words from the titles of research articles authored by Forager Child Studies (FCS) members, scraped from Google Scholar. Vertex size is proportional to the frequency of each word, and edge width is proportional to the author-level correlation between each words (i.e., their co-occurrence frequency). I average over variation between authors and between articles using a multilevel categorical (i.e., multinomial) model, defined in "fcs_model.stan". This adjustment accounts for unbalanced sampling (i.e., some authors have more articles than others) and thus produces a clearer mapping of research topics in FCS. </figcaption>
</figure>
</p>

# Setup

Before proceeding, make sure that you have either [Anaconda](https://docs.anaconda.com/anaconda/install/index.html) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed. Once you do, open your terminal and:

(1) Clone this repository

```
git clone https://github.com/erik-ringen/FCS_biblio
cd FCS_biblio
```

(2) Install the conda environment

```
conda env create --file environment.yml
```

(3) Activate the conda environment

```
conda activate FCS_biblio
```

All scripts in this repository should now run seamlessly.

# Reproducing analyses

To download publication data from Google Scholar, run the following from your terminal:
```
python process_pubdata.py
```

To do a textual analysis of the publication data and reproduce the main figure shown above, run:

```
python pub_analysis.py
```

Note that this will take a few minutes to run, as the Stan model is compiled into C++ code and sampled using MCMC.
