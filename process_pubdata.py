import pandas as pd
from scholarly import scholarly

# extract publication data for FCS from Google Scholar ####
scholar_names = [
    "Noa Lavi",
    "Sheina Lew-Levy",
    "Rachel Reckin",
    "Dorsa Amir",
    "Stephen Kissler",
    "Renee Hagen",
    "Sarah M. Pope",
    "Eleanor Fleming",
    "Annemieke Milks",
    "Adam H. Boyette",
    "David Friesem",
    "Illaria Pretelli",
    "Helen Elizabeth Davis",
    "Gul Deniz Salali",
    "Erik Ringen",
    "Alyssa Crittenden",
    "Zachary H. Garfield",
    "Temechegn G. Bira"
]

# Create empty lists to fill
title = []
fcs_author = []
pub_year = []

for sc in scholar_names:

    search_query = scholarly.search_author(sc)
    first_author_result = next(search_query, "no_profile")
    if sc == "Illaria Pretelli":
        first_author_result = next(search_query, "no_profile") # make sure we get the right Illaria

    if first_author_result != "no_profile":
        # Retrieve all the details for the author
        author = scholarly.fill(first_author_result)

        for pub in author['publications']:

            title.append( str(pub['bib']['title']) )

            if "pub_year" in pub['bib']:
                pub_year.append( int(pub['bib']['pub_year']) )
            else:
                pub_year.append(-99)

            fcs_author.append(sc)
      
# Organize into dataframe
df = pd.DataFrame(list(zip(title, pub_year, fcs_author)),
               columns = ['title', 'pub_year', 'fcs_author'])

df.head()

# Deal with cases where multiple FCS scholars on the same paper
author_title = df.groupby('title')['fcs_author'].unique().reset_index()
author_title['fcs_author'] = author_title['fcs_author'].apply(lambda x: str(x))

df2 = pd.merge(df.drop(columns=['fcs_author']), author_title, how = "left", on = "title")

# Remove dupes and undated misc 
df_filtered = df2.drop_duplicates("title").query('pub_year > 1999')

# Export data
df_filtered.to_csv('pubdata.csv', index=False)
