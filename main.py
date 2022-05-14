import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.graph_objects as go
import plotly_express as px
from vega_datasets import data

with st.echo(code_location='below'):

    '''
    ## Визуализация некоторых футбольных данных в Английской Премьер Лиге
    '''

    def all_available_seasons():
        return [str(start) + "-" + str(start+1)[-2:] for start in range(1993,2021)]


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
                                 all_teams_in_picked_season, key = 1)

    st.write("Распределение по голам за матч")

    home_games = picked_season.loc[(picked_season["HomeTeam"] == pick_team),"FTHG"]
    away_games = picked_season.loc[(picked_season["AwayTeam"] == pick_team),"FTAG"]
    all_games = pd.concat([home_games, away_games])

    fig, ax = plt.subplots()
    ax.hist(x=all_games)
    ax.set_xlabel("Голов забито")
    st.pyplot(fig)

    picked_season["home_points"] = 0
    picked_season["home_points"] = picked_season["home_points"].where(picked_season["FTR"] != "H", 3)
    picked_season["home_points"] = picked_season["home_points"].where(picked_season["FTR"] != "D", 1)

    picked_season["away_points"] = 0
    picked_season["away_points"] = picked_season["away_points"].where(picked_season["FTR"] != "A", 3)
    picked_season["away_points"] = picked_season["away_points"].where(picked_season["FTR"] != "D", 1)

    def get_overall_data(team):
        team_data_home = picked_season.loc[picked_season["HomeTeam"] == team, ["home_points", "DateTime"]]
        team_data_away = picked_season.loc[picked_season["AwayTeam"] == team, ["away_points", "DateTime"]]
        team_data = pd.concat([team_data_home, team_data_away])
        team_data = team_data.fillna(0)
        team_data["points"] = (team_data["home_points"] + team_data["away_points"]).cumsum()
        team_data["team"] = team
        team_data = team_data.drop(columns=["home_points", "away_points"])
        return team_data


    team_dates = pd.DataFrame()
    overall_results = pd.DataFrame()
    for i in range(len(all_teams_in_picked_season)):
        res = get_overall_data(all_teams_in_picked_season[i])
        if(i==0):
            team_dates = res["DateTime"].values
        else:
            res["DateTime"] = team_dates
        overall_results = pd.concat([overall_results,res])

    st.write("Динамика очков, набираемых командами")

    ##tt

    fig = px.bar(overall_results, x="team", y="points", color="team",
                 animation_frame="DateTime",range_y = [0, 100])
    st.plotly_chart(fig)






