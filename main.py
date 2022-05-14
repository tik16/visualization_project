import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.graph_objects as go

with st.echo(code_location='below'):

    '''
    ## Визуализация некоторых футбольных данных в Английской Премьер Лиге
    '''

    def all_available_seasons():
        return [str(start) + "-" + str(start+1)[-2:] for start in range(1993,2021)]

    @st.cache
    def get_data():
        return (
            pd.read_csv("results.csv", encoding="ISO-8859-1")
        )

    results = get_data()

    col1, col2 = st.columns(2)

    with col1:
        pick_season = st.selectbox("Результаты какого сезона вы хотите увидеть?",
                                   all_available_seasons())
    with col2:
        picked_season = results.loc[results["Season"] == pick_season,:]
        all_teams_in_picked_season = list(picked_season["HomeTeam"].unique())
        pick_team = st.selectbox("Выберете команду",
                                 all_teams_in_picked_season)

    st.write("Распределение по голам за матч")

    home_games = picked_season.loc[(picked_season["HomeTeam"] == pick_team),"FTHG"]
    away_games = picked_season.loc[(picked_season["AwayTeam"] == pick_team),"FTAG"]
    all_games = pd.concat([home_games, away_games])

    fig, ax = plt.subplots()
    ax.hist(x=all_games)
    ax.set_xlabel("Голов забито")
    st.pyplot(fig)






