import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.graph_objects as go
import plotly_express as px

with st.echo(code_location='below'):

    '''
        # Визуализация некоторых футбольных данных в Английской Премьер Лиге
    '''

    def all_available_seasons():
        return [str(start) + "-" + str(start+1)[-2:] for start in range(2000,2021)]


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

    '''
            ## Распределение по голам за матч в сезоне
        '''

    home_games = picked_season.loc[(picked_season["HomeTeam"] == pick_team),"FTHG"]
    away_games = picked_season.loc[(picked_season["AwayTeam"] == pick_team),"FTAG"]
    all_games = pd.concat([home_games, away_games])

    h1 = picked_season.loc[(picked_season["HomeTeam"] == pick_team),"FTAG"]
    h2 = picked_season.loc[(picked_season["AwayTeam"] == pick_team), "FTHG"]
    h3 = pd.concat([h1, h2])

    col31, col32 = st.columns(2)

    with col31:
        fig, ax = plt.subplots()
        ax.hist(x=all_games)
        ax.set_xlabel("Голы")
        ax.set_ylabel("Кол-во матчей")
        ax.set_title("Забитые голы")
        st.pyplot(fig)

    with col32:
        fig, ax = plt.subplots()
        ax.hist(x=h3)
        ax.set_xlabel("Голы")
        ax.set_ylabel("Кол-во матчей")
        ax.set_title("Пропущенные голы")
        st.pyplot(fig)





    picked_season["home_points"] = 0
    picked_season["home_fouls"] = 0
    picked_season["home_points"] = picked_season["home_points"].where(picked_season["FTR"] != "H", 3)
    picked_season["home_points"] = picked_season["home_points"].where(picked_season["FTR"] != "D", 1)

    picked_season["away_points"] = 0
    picked_season["away_points"] = picked_season["away_points"].where(picked_season["FTR"] != "A", 3)
    picked_season["away_points"] = picked_season["away_points"].where(picked_season["FTR"] != "D", 1)

    def get_overall_data(team):
        team_data_home = picked_season.loc[picked_season["HomeTeam"] == team,
                                           ["home_points", "DateTime","HF","Referee","FTHG","FTR","HS"]]
        team_data_away = picked_season.loc[picked_season["AwayTeam"] == team,
                                           ["away_points", "DateTime","AF","Referee","FTAG","FTR","AS"]]
        team_data_home["home"] = 1
        team_data_away["home"] = 0
        team_data = pd.concat([team_data_home, team_data_away])
        team_data = team_data.fillna(0)
        team_data["points"] = (team_data["home_points"] + team_data["away_points"]).cumsum()
        team_data["raw_points"] = team_data["home_points"] + team_data["away_points"]
        team_data["fouls"] = team_data["AF"] + team_data["HF"]
        team_data["team"] = team
        team_data["goals"] = team_data["FTHG"] + team_data["FTAG"] + 0.02
        team_data["win"] = "Поражение"
        team_data["win"] = team_data["win"].where(team_data["raw_points"] != 3, "Победа")
        team_data["win"] = team_data["win"].where(team_data["raw_points"] != 1, "Ничья")
        team_data["shots"] = team_data["HS"] + team_data["AS"]
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

    '''
        ## Динамика очков, набираемых командами на протяжении сезона
    '''

    fig = px.bar(overall_results, x="team", y="points", color="team",
                 animation_frame="DateTime",range_y = [0, 100])
    st.plotly_chart(fig)

    '''
        ## Количество голов на протяжении сезона
    '''

    pick_team = st.selectbox("Снова выберете команду",
                             all_teams_in_picked_season, key=2)

    team_data = get_overall_data(pick_team)

    ### FROM: https://altair-viz.github.io/gallery/scatter_with_minimap.html

    zoom = alt.selection_interval(encodings=["x", "y"])

    minimap = (
        alt.Chart(team_data)
            .mark_point()
            .add_selection(zoom)
            .encode(
            x="DateTime",
            y="goals",
            color=alt.condition(zoom, "win", alt.value("lightgray"))
        )
            .properties(
            width=200,
            height=200,
            title="Миникарта для выбора более детального вида",
        )
    )

    detail = (
        alt.Chart(team_data)
            .mark_point()
            .encode(
            x=alt.X(
                "DateTime", scale=alt.Scale(domain={"selection": zoom.name, "encoding": "x"})
            ),
            y=alt.Y(
                "goals",
                scale=alt.Scale(domain={"selection": zoom.name, "encoding": "y"}),
            ),
            color="win",
        )
            .properties(width=600, height=400, title="Количество голов за матч")
    )

    st.altair_chart(detail | minimap)

    ### END FROM

    '''
        ## Зависимость ударов и голов за один матч
    '''

    team_data["scale"] = 1
    team_data["scale"] = team_data["scale"].where(team_data["win"]!="Победа", 3)
    team_data["scale"] = team_data["scale"].where(team_data["win"]!="Ничья", 2)
    fig = px.scatter(team_data, x="shots", y="goals",
                     size="scale", color="win",
                     hover_name="fouls", size_max=20)
    st.plotly_chart(fig)








