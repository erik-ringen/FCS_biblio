import os
import pandas as pd
import numpy as np
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem import *
from nltk.stem.porter import *
import nltk

nltk.download('wordnet')

stemmer = PorterStemmer()

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

d = pd.read_csv("pubdata.csv")

processed_titles = d['title'].map(preprocess)
processed_words = [word for title in processed_titles for word in title]

original_titles = []
fcs_author = []

for i in range(len(processed_titles)):
    og_title = d['title'][i]
    author = d['fcs_author'][i]

    for word in processed_titles[i]:
        original_titles.append(og_title)
        fcs_author.append(author)

# Organize into dataframe
d_words = pd.DataFrame({'word':processed_words, 'title':original_titles, 'fcs_author':fcs_author})

for i in range(len(d_words)):
    if d_words['word'][i] == "evolutionari":
        d_words['word'][i] = "evolut"

word_count = {i:processed_words.count(i) for i in processed_words}
n_keep = 20
top_words = pd.DataFrame({'word':sorted(word_count, key=word_count.get, reverse=True)[0:n_keep]})

d_words_top = d_words.merge(top_words, how='inner')

# function for Stan-friendly IDs
def create_index(x):
    unique_values = pd.DataFrame({'uv':list(set(x))})

    x_id = []
    for value in x:
        x_id.append( np.where(unique_values['uv'] == value)[0][0] + 1  )

    return x_id

# Organize data for Stan
stan_data = {
    "word_id":create_index(d_words_top['word']),
    "paper_id":create_index(d_words_top['title']),
    "author_id":create_index(d_words_top['fcs_author'])
}

stan_data["N_obs"] = len(stan_data["word_id"])
stan_data["N_wo"] = max(stan_data["word_id"])
stan_data["N_author"] = max(stan_data["author_id"])
stan_data["N_paper"] = max(stan_data["paper_id"])

import cmdstanpy
from cmdstanpy import CmdStanModel
cmdstanpy.install_cmdstan()

# Compile stan model in C++ 
stan_model_path = os.getcwd() + "/fcs_model.stan"
stan_model = CmdStanModel(stan_file=stan_model_path)

# Sample with MCMC
fit = stan_model.sample(data=stan_data,chains=4,parallel_chains=4)

### Make a graph of word co-occurance, at the author level
import igraph
import random

# Extract word frequencies (logit scale)
wo_freq = fit.stan_variable("wo_v")
n_samps = np.shape(wo_freq)[0]

# Softmax function to convert to probabilities
def softmax(x):
    exp_x = np.exp(x)
    probs = exp_x/np.sum(exp_x)
    return probs

wo_prob = []

for samp in range(n_samps):
    wo_prob.append(softmax(wo_freq[samp,]))

med_wo_prob = np.median(wo_prob, 0)

# Extract author-wise correlation matrix
Rho_author = fit.stan_variable("Rho_author")

median_Rho = np.zeros((stan_data["N_wo"],stan_data["N_wo"]))
np.shape(median_Rho)
np.shape(Rho_author)

for i in range(0, stan_data["N_wo"]-1):
    for j in range(1, stan_data["N_wo"]):

        # Set edges < 0.05 to zero
        if np.median(Rho_author[:,i,j]) > np.abs(0.05):
            median_Rho[i,j] = np.median(Rho_author[:,i,j])
        else:
            median_Rho[i,j] = 0
        # exploit symmetry
        median_Rho[j,i] = median_Rho[i,j]

# Set diagonal = 0 for graph
for d in range(0, stan_data["N_wo"]):
    median_Rho[d,d] = 0

node_names = list(set(d_words_top["word"]))
node_names_relab = node_names

## Get full versions of stemmed words
for i in range(len(node_names_relab)):

    if node_names_relab[i] == "implic":
        node_names_relab[i] = "implications"

    if node_names_relab[i] == "studi":
        node_names_relab[i] = "study"

    if node_names_relab[i] == "evolut":
        node_names_relab[i] = "evolution"

    if node_names_relab[i] == "societi":
        node_names_relab[i] = "society"

    if node_names_relab[i] == "cultur":
        node_names_relab[i] = "culture"
    
    if node_names_relab[i] == "forag":
        node_names_relab[i] = "foraging"


conn_indices = np.where(median_Rho)
weights = median_Rho[conn_indices]

edges = zip(*conn_indices)

# init graph
G = igraph.Graph(edges=edges, directed=False)

G.vs['label'] = node_names_relab
G.vs['color'] = "rgba(132, 206, 184, 1)"
G.es['weight'] = weights
G.es['width'] = weights*10
G.es['color']= "rgba(1,1,1,0.3)"

visual_style = {}
visual_style["vertex_size"] = med_wo_prob * 500

random.seed(5) # make the graph reproducible

igraph.plot(G,
 layout="fruchterman_reingold",
  labels=True,
  vertex_frame_width=0.5,
   margin=80,
    target="word_cor.pdf",
    **visual_style)
