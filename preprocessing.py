import pandas as pd
import requests
import json
import pickle
import itertools

SECRET = "da0862f52b80519587abcb9bd23b344b"

# import data
movie_df = pd.read_json("data/movie_ids_01_28_2023.json", lines=True)
oscar_df = pd.read_csv("data/the_oscar_award.csv")

# create dictionary of oscar films
oscar_films = oscar_df[["year_film", "film"]].drop_duplicates().T.to_dict()

# SKIP if done before
def get_tmdb_movie(year_film: str, film: str) -> int:
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={SECRET}&language=en-US&query={film}&include_adult=false&year={year_film}"
    response = requests.get(search_url)
    if response.json()["total_results"] == 0:
        ret = None
    else:
        ret = response.json()["results"][0]
    return ret


# key: name_year
# value: tmdb's best match
tmdb_info = {}
for kwargs in oscar_films.values():
    name_year = f"{kwargs['film']}_{kwargs['year_film']}"
    tmdb_info[name_year] = get_tmdb_movie(**kwargs)

with open("tmdb_info.pickle", "wb") as handle:
    pickle.dump(tmdb_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

tmdb_pkl = open("tmdb_info.pickle", "rb")
tmdb_info = pickle.load(tmdb_pkl)


def get_tmdb_cast(movie_id: str) -> int:
    search_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={SECRET}&language=en-US"
    response = requests.get(search_url)
    return response.json()


cast_info = {v["id"]: "" for v in tmdb_info.values() if type(v) is dict}
for k in cast_info:
    if cast_info[k] == "":
        print(k)
        cast_info[k] = get_tmdb_cast(k)

with open("cast_info.pickle", "wb") as handle:
    pickle.dump(cast_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

cast_pkl = open("cast_info.pickle", "rb")
cast_info = pickle.load(cast_pkl)


with open("cast_info.pickle", "wb") as handle:
    pickle.dump(cast_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

cast_lu = {}

# key: cast pairing
# value: pairing
cast_cnt = {}
for c_json in cast_info.values():
    cast_ls = c_json["cast"]

    # add each actor into a lookup
    for cast in cast_ls:
        if cast["id"] not in cast_lu:

            cast_lu[cast["id"]] = {
                k: v
                for k, v in cast.items()
                if k in ["name", "original_name", "gender",]
            }
    id_ls = [c["id"] for c in cast_ls]
    id_comb = itertools.combinations(id_ls, 2)
    for pair in id_comb:
        if pair in cast_cnt:
            cast_cnt[pair] += 1
        else:
            cast_cnt[pair] = 1

cast_df = pd.DataFrame(cast_lu).T
cast_df.to_csv("cast_lu.csv")

pd.DataFrame.from_dict(id_comb, orient="index")


oscar_df = oscar_df.join(
    movie_df[["original_title", "id"]].set_index("original_title"), on="film"
)
# oscar_df['film'].str.lower().isin(movie_df['original_title'].str.lower()).sum()
req_url = "https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={SECRET}&language=en-US"

credit_dct = {}
for i in movie_df["id"]:
    response = requests.get(req_url.format(movie_id=i, SECRET=SECRET))
    credit_dct[i] = response.json()


response = requests.get()
val = dict(response.json())
val.keys()


movie_df
