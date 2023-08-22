import pandas as pd
import pickle
import itertools

# load statics
tmdb_pkl = open("tmdb_info.pickle", "rb")
tmdb_info = pickle.load(tmdb_pkl)

cast_pkl = open("cast_info.pickle", "rb")
cast_info = pickle.load(cast_pkl)

movie_df = pd.read_json("data/movie_ids_01_28_2023.json", lines=True)
oscar_df = pd.read_csv("data/the_oscar_award.csv")

# create dictionary of oscar films
oscar_films = oscar_df[["year_film", "film"]].drop_duplicates().T.to_dict()


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
                if k
                in [
                    "name",
                    "original_name",
                    "gender",
                ]
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

cast_mat = pd.DataFrame(
    [[i_1, i_2, v] for (i_1, i_2), v in cast_cnt.items()],
    columns=["actor_1", "actor_2", "connection"],
)


oscar_df = oscar_df.join(
    movie_df[["original_title", "id"]].set_index("original_title"), on="film"
)
