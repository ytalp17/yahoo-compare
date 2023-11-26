import dash_mantine_components as dmc
from dash import Dash, html, Input, Output, ALL, callback_context
import plotly.graph_objects as go
import pandas as pd 
from dash import dash_table
import os
import re
import viz_tools as viz_tools 
from data_tools import (get_similar_players, get_season_data, get_Zscores, 
                        calculate_percentage_stats, aggregate_fantasy_stats, 
                        get_player_info, get_career_stats,
                        rank_stats, datemask_season_data)


############################ Get Paths ###################################
project_path = os.getcwd()
team_logos_path = os.path.join(project_path, "src/assets/team_logos")
assets_path = os.path.join(project_path, "src/assets")



app = Dash(__name__, assets_folder=assets_path,
        external_stylesheets=[
            # include google fonts
            "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
            ],
        )

server = app.server  # Needed for gunicorn

########################### Data Part ######################################
fantasy_stats = ['PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']

CareerStats = get_career_stats()
PlayerInfo = get_player_info()

GameLog2023_24 = get_season_data("2023-24", Aggregate = "Total", raw = True)
#Season_total_2122 = get_season_data("2021-22", Aggregate = "Total")
Season_total_2223 = get_season_data("2022-23", Aggregate = "Total")
Zscore_total_2223 = get_Zscores(Season_total_2223, "2022-23", Aggregate = "Total")

Season_avg_2223 = get_season_data("2022-23", Aggregate = "Avg")
Zscore_avg_2223 = get_Zscores(Season_avg_2223, "2022-23", Aggregate = "Total")

Season_total_2324 = get_season_data("2023-24", Aggregate = "Total")
Zscore_total_2324 = get_Zscores(Season_total_2324, "2023-24", Aggregate = "Total")

Season_avg_2324 = get_season_data("2023-24", Aggregate = "Avg")
Zscore_avg_2324 = get_Zscores(Season_avg_2324, "2023-24", Aggregate = "Avg")

fantasy_stats_dict = {'PLAYER': 'Player Name',
                      'PTS': 'Points',
                      'FG3M': '3 Points',
                      'REB': 'Rebounds',
                      'AST': 'Assists',
                      'STL': 'Steals',
                      'BLK': 'Blocks',
                      'TOV': 'Turnovers',
                      'FG%': 'Field Goal %',
                      'FG_PCT': 'Field Goal %',
                      'FT%': 'Free Throw %',
                      'FT_PCT': 'Free Throw %',
                      'MIN': 'Minutes',
                      'GP': 'Game Plays',
                      }


#Complementary App Layout
team_logos = dmc.Grid([viz_tools.team_logos(teams, app.get_asset_url(f"team_logos/{teams}")) for teams in os.listdir(team_logos_path)],
                      style={'width':1800, 'height': 60,'max-height':60, "border": 'rgb(0,0,0)',
                            "background": 'transparent','border-radius':0,})

#########################################
app.layout = dmc.MantineProvider(
    inherit=True,
    theme={"colorScheme": "dark"},
    withGlobalStyles=True,
    children=[
        #Header   
        html.Div(viz_tools.set_header(app.get_asset_url("yahoo_fantasy_icon.png"))),
        #Tabs
        html.Div(className='Tabs',  children=[
            dmc.Tabs(
                [  
                dmc.TabsList(
                    [
                        dmc.Tab("Team-wise", value="Team"),
                        dmc.Tab("Player-wise", value="Player"),
                        
                    ]
                ),
                #Tab1
                dmc.TabsPanel(
                    [
                    viz_tools.tab1_layout
                    ], value="Team"),
                #Tab2
                dmc.TabsPanel(
                    [
                    viz_tools.set_team_logos_container(team_logos),
                    viz_tools.tab2_layout(app.get_asset_url(f"nba_players/{2544}.png"))
                    ], value="Player", 
                    ),
                ],
                color="violet",
                orientation="horizontal",
                value="Team",
            )
        ],
        )
    ]
)

""" ----------------------------------------------------------------------------
Tab 2 Callback functions:

Overview:

pop_up_modal: modal-button -> pop-up-modal
update_player_similarity_table: player-select, chechbox-group -> player-similarity-table
update_career_graph: player-select, stat_type_graph -> career_graph
update_player_info_card: player-select -> player_image_src, birthday_text, country_text, school_text, start_year_text, draft_number_text, position_text
 
---------------------------------------------------------------------------- """

'''----------------Modal Callback functions--------------------'''
@app.callback(
        Output("pop-up-modal", "opened"),
        Input("modal-button", "n_clicks"),
        prevent_initial_call=True,
    )
def pop_up_modal(n_clicks:int) -> bool:
    return True

'''----------------Tab 2 Callback functions--------------------'''
@app.callback(
    [
    Output("interval_stats_graph", "figure"), 
    Output("games_text", "children")
    ],
    [
    Input("player-select", "value"), 
    Input("ranking_agg_type2", "value"),
    Input("date-range-picker", "value")
    ]
)

def update_interval_stats(player, aggregate, interval):   
    fantasy_stats = ['PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FTM', 'FTA', 'MIN']

    interval_stats = datemask_season_data(GameLog2023_24, interval[0], interval[1], player, aggregate)
    interval_stats_modified = interval_stats.drop(['G'])
    interval_stats_modified.loc['FG%'] = (interval_stats_modified.loc['FGM']/interval_stats_modified.loc['FGA']).round(2)
    interval_stats_modified.loc['FT%'] = (interval_stats_modified.loc['FTM']/interval_stats_modified.loc['FTA']).round(2)
    interval_stats_modified = interval_stats_modified.drop(['FGM','FGA','FTM','FTA'])
    interval_stats_modified = pd.concat([interval_stats_modified, interval_stats_modified.iloc[[0]]], axis=0)

    if aggregate != 'Total':
        s_stats = Season_avg_2324[Season_avg_2324.index.isin([player])][fantasy_stats].T
        s_stats.loc['FG%'] = (s_stats.loc['FGM']/s_stats.loc['FGA']).round(2)
        s_stats.loc['FT%'] = (s_stats.loc['FTM']/s_stats.loc['FTA']).round(2)
        s_stats = s_stats.drop(['FGM','FGA','FTM','FTA'])
        s_stats_modified = pd.concat([s_stats, s_stats.iloc[[0]]], axis=0)
    else:
        s_stats = Season_total_2324[Season_total_2324.index.isin([player])][fantasy_stats].T
        s_stats.loc['FG%'] = (s_stats.loc['FGM']/s_stats.loc['FGA']).round(2)
        s_stats.loc['FT%'] = (s_stats.loc['FTM']/s_stats.loc['FTA']).round(2)
        s_stats = s_stats.drop(['FGM','FGA','FTM','FTA'])
        s_stats_modified = pd.concat([s_stats, s_stats.iloc[[0]]], axis=0)
        
        
    fig = go.Figure(
        go.Scatterpolar(
            name = 'Season',
            r= interval_stats_modified.iloc[:,0].values,
            theta=interval_stats_modified.index,
            marker_line_color="black",
            marker_line_width=2,
            #opacity=0.55,
            text=[interval_stats_modified.index[i] + ' = ' + str(interval_stats_modified.iloc[i,0]) for i in range(len(interval_stats_modified))],
            hoverinfo="text",
            )
        )
    
    #add general stats
    fig.add_trace(
        go.Scatterpolar(
            name = 'Interval',
            r=s_stats_modified.iloc[:,0].values,
            theta=s_stats_modified.index,
            marker_line_color="black",
            marker_line_width=2,
            text=[s_stats_modified.index[i] + ' = ' + str(s_stats_modified.iloc[i,0]) for i in range(len(s_stats_modified))],
            hoverinfo="text",
            )
        )

    fig.update_layout(
            polar=dict(
                hole=0.1,
                radialaxis=dict(
                    visible=True,
                    type='linear',
                    autotypenumbers='strict',
                    showline=False,
                    showticklabels=False,
                    ticks='',),
            ),
            showlegend=True,
            template="plotly_dark",
            paper_bgcolor= 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_color='white',
            font_size=14
        )
    
    fig.update_layout(
        margin=dict(t=10,b=10,pad=10),
        )
    
    #text under the polar plot
    text = f"The player played total of {int(interval_stats.iloc[-1].values[0])} games in the given date range."

    return fig, text
    

@app.callback(
    Output("ranking_table_card", "children"), 
    [
    Input("player-select", "value"),
    Input("ranking_agg_type", "value"),
    ]
)
def update_ranking_table(player_name:str, aggregate_type:str) -> dash_table.DataTable:
    
    if aggregate_type == 'Total':
        rank_stats_df = rank_stats(Zscore_total_2324, player_name)
    else:
        rank_stats_df = rank_stats(Zscore_avg_2324, player_name)
    
    ranking_table = dash_table.DataTable(
                        id='ranking_DataTable',
                        columns=[{"name": i, "id": i} for i in rank_stats_df.columns],
                        data= rank_stats_df.to_dict('records'),
                        style_as_list_view=True,
                        style_header={'backgroundColor': 'rgba(0,0,0,0)' ,
                                        'color':'rgb(237, 234, 222)',
                                        'border': 'none',
                                        },
                        style_data={'backgroundColor': 'rgba(0,0,0,0)',
                                    'color': 'rgb(180,181,185)',
                                    'border': '0.7px solid rgb(55, 58, 64)',},
                
                        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                    'whiteSpace': 'normal', 'fontSize':'14', 'font-family':'Roboto, sans-serif',
                                    'backgroundColor': 'rgba(0,0,0,0)'},   
                        )
    return ranking_table
    

@app.callback(
    Output("similarity_table_card", "children"), 
    [
    Input("player-select", "value"),
    Input("checkbox-group", "value"),
    ]
)
def update_player_similarity_table(player_name:str, selected_stats:str) -> dash_table.DataTable:

    similarity_df = get_similar_players(CareerStats, selected_stats, player_name)
    
    similarity_table = dash_table.DataTable(
                            id='similarity_DataTable',
                            columns=[{"name": i, "id": i} for i in similarity_df.columns],
                            data= similarity_df.to_dict('records'),
                            style_as_list_view=True,
                            style_header={'backgroundColor': 'rgba(0,0,0,0)' ,
                                          'color':'rgb(237, 234, 222)',
                                          'border': 'none',
                                         },
                            style_data={'backgroundColor': 'rgba(0,0,0,0)',
                                        'color': 'rgb(180,181,185)',
                                        'border': '0.7px solid rgb(55, 58, 64)',},
                    
                            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                        'whiteSpace': 'normal', 'fontSize':'14', 'font-family':'Roboto, sans-serif',
                                        'backgroundColor': 'rgba(0,0,0,0)'},   
                            )
    return similarity_table


@app.callback(
    Output("career_graph", "figure"), 
    [
    Input("player-select", "value"),
    Input("stat_type_graph", "value"),
    ]
)
def update_career_graph(player_name:str, stat:str) -> go.Figure:
    
    Player_CareerStats = CareerStats[CareerStats['name']== player_name]
    Player_CareerStats_updated = Player_CareerStats.drop(Player_CareerStats[Player_CareerStats['TEAM_ID'] == 0].index).groupby(['SEASON_ID','PLAYER_ID']).sum(numeric_only=True).reset_index()
        
    career_fig = go.Figure(
        data =[
            go.Scatter(
                x=Player_CareerStats_updated.SEASON_ID,
                y=Player_CareerStats_updated[stat],
                mode="lines+markers",
                name= stat,
                hovertemplate = "%{y} <extra></extra>", # hide trace name!
            )
        ]
    )

    career_fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)'
    )
    
    career_fig.update_xaxes(type='category')
    
    career_fig.add_trace(
        go.Bar(
            x=Player_CareerStats_updated.SEASON_ID,
            y=Player_CareerStats_updated.GP,
            yaxis="y2",
            name="Game Played",
            marker_color="IndianRed",
            opacity=0.45,
            hovertemplate = "%{y} <extra></extra>", # hide trace name!
            )
    )
    
    career_fig.update_layout(
        template= 'plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h',
                    yanchor="top",
                    y=1.25,
                    xanchor="left",
                    x=0.01,
                    font=dict(size= 10)),
        xaxis = dict(showgrid= False),
        yaxis = dict(title=dict(text=f'Total {fantasy_stats_dict[stat]}'),
                     showgrid= False,
                ),
        yaxis2=dict(
                    side='right', 
                    range=[0, 200],
                    overlaying="y",
                    showgrid=False, 
                    showticklabels=False,
                ),
        margin=dict(b=15,t=15,r=15),
        hovermode="x",
    )   
    
    return career_fig


@app.callback(
        [
        Output("player_image", "src"),
        Output("country_text", "children"),
        Output("school_text", "children"),
        Output("start_year_text", "children"),
        Output("draft_number_text", "children"),
        Output("position_text", "children"),     
        Output("birthday_text", "children"),
        ],

        [
        Input("player-select", "value"),
        ],
        prevent_initial_call=True,
)
def update_player_info_card(player_name:str) -> tuple[str, str, str, str, str, str, str]:
    
    id_for_img1 = int(PlayerInfo[PlayerInfo['name']==player_name].id.values[0])
    src = app.get_asset_url(f"nba_players/{id_for_img1}.png")  

    #birthday = pd.to_datetime(PlayerInfo[PlayerInfo['name']==player_name].birthdate).iloc[0].date().strftime('%m-%d-%Y')
    country = PlayerInfo[PlayerInfo['name']==player_name].country.values[0]
    school = PlayerInfo[PlayerInfo['name']==player_name].school.values[0]
    startyear = int(float(PlayerInfo[PlayerInfo['name']==player_name].start_year.values[0]))
    draftnumber = PlayerInfo[PlayerInfo['name']==player_name]['draft number'].values[0]
    pos = PlayerInfo[PlayerInfo['name']==player_name]['position'].values[0]
    age= PlayerInfo[PlayerInfo['name']==player_name]['PLAYER_AGE'].values[0]

    return src, country, school, startyear, draftnumber, pos, age

 
@app.callback(
        [Output("player-select", "value")],
        [Input({'type': 'teams_logo_image', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True,
    )
def update_playa_info(ndx:int) -> str: 
    ctx = callback_context
    element_id = ctx.triggered[0]['prop_id'].replace(".n_clicks", "")
    team_id = re.findall("\d+", element_id)[0]
    player_name = PlayerInfo[PlayerInfo['team_id']==int(team_id)].sample(1).name.values[0]

    return [player_name]


""" ----------------------------------------------------------------------------
Tab 1 Callback functions:

Overview:

update_dropdown_options: radio-select-season -> SelectPlayer_leftdropdown, SelectPlayer_rightdropdown
update_tab1graphs:SelectPlayer_leftdropdown, SelectPlayer_rightdropdown, season-select, agg_type ->
polar_graph, upper_left_hbar, bottom_left_hbar, upper_right_hbar, bottom_right_hbar
table-tabs,SelectPlayer_leftdropdown, SelectPlayer_rightdropdown, season-select, agg_type -> tabs-content,
right_stat_card, left_stat_card
---------------------------------------------------------------------------- """

@app.callback(
    [
    Output("SelectPlayer_leftdropdown", "data"),
    Output("SelectPlayer_rightdropdown", "data"),

    ],       
    Input("radio-select-season", "value"),
)
def update_dropdown_options(season):
    if season== "2022-23":
        dropdown_options = [{"label": val, "value": val} for val in Season_total_2223.index.tolist()]
        return dropdown_options, dropdown_options
    else:
        dropdown_options = [{"label": val, "value": val} for val in Season_total_2324.index.tolist()]
        return dropdown_options, dropdown_options

    
@app.callback(
    [
    Output('polar_graph', 'figure'),
    Output('upper_left_hbar', 'figure'),
    Output('bottom_left_hbar', 'figure'),
    Output('upper_right_hbar', 'figure'),
    Output('bottom_right_hbar', 'figure'),
    ],

    [    
    Input('SelectPlayer_leftdropdown', 'value'),
    Input('SelectPlayer_rightdropdown', 'value'),
    Input('radio-select-season', 'value'),
    Input("agg_type", "value"),
    ]
)
def update_tab1graphs(P1, P2, season, agg_type):
    #P1 : left dropdown ; P2 : right dropdown
    
    if season=='2022-23':
        if agg_type== 'Total':
            df = calculate_percentage_stats(Season_total_2223)
            df['FT%'] = 100*df['FT%']
            df['FG%'] = 100*df['FG%']
        else:
            df = calculate_percentage_stats(Season_avg_2223)

    else: #season==2023-24
        if agg_type== 'Total':
            df = calculate_percentage_stats(Season_total_2324)
            df['FT%'] = 100*df['FT%']
            df['FG%'] = 100*df['FG%']
        else:
            df = calculate_percentage_stats(Season_avg_2324)
            
    game_stat = df['G'].median().round(2)
    min_stat =df['MIN'].median().round(2)
        
    #Horizontal plots################
    #upper_left
    x_uleft = df[df.index.isin(P1)]['G'].values
    yleft= P1

    fig_upper_left = go.Figure(data=[
                        go.Bar(
                            x=x_uleft,
                            y=yleft,
                            orientation='h',
                            opacity=0.45,
                            width = 0.5, 
                        )],
                    )
        
    fig_upper_left.update_layout(
        transition_duration=500,
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.90],
        ),
        xaxis=dict(
            zeroline=True,
            showline=False,
            showgrid=False,
            showticklabels=True,
            tickmode = 'array',
            tickvals = [df['G'].min(), game_stat, df['G'].max()],
            domain=[0, 0.90],
            range=[0, df['G'].max()],
            title="Total Game Played",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=5,
            l=3,
            r=1,
            t=3),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
    )

    fig_upper_left.add_vline(x=game_stat, line_width=2, line_dash="dash")

    #bottom_left
    x_bleft = df[df.index.isin(P1)]['MIN'].values

    fig_bottom_left = go.Figure(data=[
                        go.Bar(
                            x=x_bleft,
                            y=yleft,
                            orientation='h',
                            opacity=0.45,
                            width = 0.5, 
                            showlegend=True,
                        
                        )],
                    )
        
    fig_bottom_left.update_layout(
        transition_duration=500,
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.95],
        ),
        xaxis=dict(
            zeroline=True,
            showline=False,
            showgrid=False,
            tickmode = 'array',
            tickvals = [df['MIN'].min(), min_stat, df['MIN'].max()],
            showticklabels=True,
            domain=[0, 0.95],
            range=[0, df['MIN'].max()],
            title="Total Minutes Played",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=10,
            l=3,
            r=1,
            t=3),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
    )

    fig_bottom_left.add_vline(x=min_stat, line_width=2, line_dash="dash")


    #upper right
    x_uright = df[df.index.isin(P2)]['G'].values
    yright= P2

    fig_upper_right = go.Figure(data=[
                        go.Bar(
                            x=x_uright,
                            y=yright,
                            orientation='h',
                            marker_color='#EF553B',
                            opacity=0.5,
                            width = 0.5,                       
                        )]
                    )
    
    fig_upper_right.update_layout(
        transition_duration=500,
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.95], mirror='allticks', side='right', automargin=True,
        ),
        xaxis=dict(
            zeroline=True,
            showline=False,
            showticklabels=True,
            tickmode = 'array',
            tickvals =  [df['G'].min(), game_stat, df['G'].max()],
            showgrid=False,
            domain=[0.1, 0.95],
            range=[0, df['G'].max()],
            autorange="reversed",
            title="Total Game Played",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=5,
            l=1,
            r=3,
            t=3),
        showlegend=False,
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig_upper_right.add_vline(x=game_stat, line_width=2, line_dash="dash")


    #bottom right
    x_bright = df[df.index.isin(P2)]['MIN'].values

    fig_bottom_right = go.Figure(data=[
                        go.Bar(
                            x=x_bright,
                            y=yright,
                            orientation='h',
                            marker_color='#EF553B',
                            opacity=0.5,
                            width = 0.5,
                        )]
                    )
    
    fig_bottom_right.update_layout(
        transition_duration=500,
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            domain=[0, 0.95], mirror='allticks', side='right', automargin=True,
        ),
        xaxis=dict(
            zeroline=True,
            showline=False,
            showticklabels=True,
            tickmode = 'array',
            tickvals = [df['MIN'].min(), min_stat, df['MIN'].max()],
            showgrid=False,
            domain=[0.1, 0.95],
            range=[0,  df['MIN'].max()],
            autorange="reversed",
            title="Game Played-Previous Season",
            titlefont={"color": "white"},
        ),
        margin=dict(
            b=5,
            l=1,
            r=3,
            t=3),
        showlegend=False,
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig_bottom_right.add_vline(x=min_stat, line_width=2, line_dash="dash")

    ###################################
    ########    Polar Plot    #########
    ###################################
    
    #P1 (right dropdown)
    P1_for_plot = aggregate_fantasy_stats(df[df.index.isin(P1)][fantasy_stats]).T.round(2)
    P1_for_plot.columns = ['Score']

    #P2 (right dropdown)
    P2_for_plot = aggregate_fantasy_stats(df[df.index.isin(P2)][fantasy_stats]).T.round(2)
    P2_for_plot.columns = ['Score']
    
    #P1 (left dropdown)
    fig = go.Figure(
            data=go.Scatterpolar(
                r=P1_for_plot['Score'],
                theta=P1_for_plot.index,
                fill='toself',
                opacity=.90,
                hoverinfo="text",
                name="",
                text=[P1_for_plot.index[i] + ' = ' + str(P1_for_plot['Score'][i]) for i in range(len(P1_for_plot))]
            )   
        )
    
    #P2 (right dropdown)
    fig.add_trace(
        go.Scatterpolar(
            r=P2_for_plot['Score'],
            theta=P2_for_plot.index,
            fill='toself',
            opacity=.85,
            hoverinfo="text",
            name="",
            text=[P2_for_plot.index[i] + ' = ' + str(P2_for_plot['Score'][i]) for i in range(len(P2_for_plot))]
            )
        )
    
    fig.update_layout(
        polar=dict(
            hole=0.1,
            radialaxis=dict(
                visible=True,
                type='linear',
                autotypenumbers='strict',
                autorange=True,
                range=[0, 500],
                angle=90,
                showline=False,
                showticklabels=False,
                ticks='',),
                #gridcolor='rgb(40,132,117)'),
        ),
        margin=dict(b=65,t=65),
        transition_duration=500,
        showlegend=False,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        font_size=14,
    )
        
    return fig, fig_upper_left, fig_bottom_left, fig_upper_right, fig_bottom_right

#Update Tables
@app.callback(
        [
        Output("tabs-content", "children"), 
        Output("left_stat_card", "children"),
        Output("right_stat_card", "children"),
        ],

        [
        Input("table-tabs", "value"),
        Input('SelectPlayer_leftdropdown', 'value'),
        Input('SelectPlayer_rightdropdown', 'value'),
        Input('radio-select-season', 'value'),
        Input("agg_type", "value"),
        ]
        )
def update_tables(active, P1, P2, season, agg_type):
    fantasy_stats = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']
    aggregate_stats = fantasy_stats[1:]
    
    if season=='2022-23':
        if agg_type== 'Total':
            season_totalp = calculate_percentage_stats(Season_total_2223) #calculates percentage stats
            Zscores = Zscore_total_2223
        else:
            season_totalp = calculate_percentage_stats(Season_avg_2223)
            Zscores = Zscore_avg_2223
            
    else: #season==2023-24
        if agg_type== 'Total':
            season_totalp = calculate_percentage_stats(Season_total_2324)
            Zscores = Zscore_total_2324
        else:
            season_totalp = calculate_percentage_stats(Season_avg_2324)
            Zscores = Zscore_avg_2324

    style_header_midtables = {'backgroundColor': 'rgb(28,28,33)',
                                'color':'rgb(237, 234, 222)',
                                'border': 'none',
                                }
    style_data_midtables = {'backgroundColor': '#212529',
                                'color': 'rgb(180,181,185)',
                                'border': '0.7px solid rgb(55, 58, 64)',
                                }
    style_cell_midtables = {'textAlign': 'center', 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                'whiteSpace': 'normal', 'fontSize':13, 'font-family':'Roboto, sans-serif',
                                'backgroundColor': 'rgb(28, 28,33)',
                                'border': 'thin solid #FFFFFF',
                                }
    style_midtable = {'borderRadius': '4px', 'overflowX': 'scroll', 
                        'border': '1px solid rgb(55, 58, 64)',
                        }
    
    ######Tables under tabs in the MIDDLE section.
    ##Top table is P1 table 
    P1_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in fantasy_stats],
                            data= season_totalp[season_totalp.index.isin(P1)].reset_index().round(2)[fantasy_stats].to_dict('records'),
                            style_as_list_view=True,
                            style_header= style_header_midtables,
                            style_data= style_data_midtables,
                            style_cell= style_cell_midtables,
                            style_table=style_midtable
                            )
        
    P1_Zscore_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in ['PLAYER'] + Zscores.columns.values.tolist()], 
                            data=Zscores[Zscores.index.isin(P1)].reset_index().round(2).to_dict('records'),
                            style_as_list_view=True,
                            style_header= style_header_midtables,
                            style_data= style_data_midtables,
                            style_cell= style_cell_midtables,
                            style_table= style_midtable,
                            )
    
    #Left aggregate table
    P1_aggregate_data = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P1)][aggregate_stats]).T.round(2).reset_index()
    P1_aggregate_data.columns = ['STATS', 'SCORES'] #go around

    P1_aggregate_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in P1_aggregate_data.columns],
                            data= P1_aggregate_data.to_dict('records'),
                            style_as_list_view=True,
                            style_header={'backgroundColor': 'rgba(0,0,0,0)' ,
                                          'color':'rgb(237, 234, 222)',
                                          'border': 'none',
                                         },
                            style_data={'backgroundColor': 'rgba(0,0,0,0)',
                                        'color': 'rgb(180,181,185)',
                                        'border': '0.7px solid rgb(55, 58, 64)',},
                            style_cell={'textAlign': 'left', 'minWidth': '40px', 'width': '100px', 'maxWidth': '100x',
                                        'whiteSpace': 'normal', 'fontSize':14, 'font-family':'Roboto, sans-serif',
                                        'backgroundColor': 'rgba(0,0,0,0)'},     
                            fill_width=False,
                            )
        
    ##Bottom table is P2 table 
    P2_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in fantasy_stats],
                            data= season_totalp[season_totalp.index.isin(P2)].reset_index().round(2)[fantasy_stats].to_dict('records'),
                            style_as_list_view=True,
                            style_header={'backgroundColor': 'rgba(0,0,0,0)' ,
                                          'color':'rgb(237, 234, 222)',
                                          'border': 'none',
                                         },
                            style_data={'backgroundColor': '#212529',
                                        'color': 'rgb(180,181,185)',
                                        'border': '0.7px solid rgb(55, 58, 64)',
                                        },
                            style_cell={'textAlign': 'center', 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal', 'fontSize':13, 'font-family':'Roboto, sans-serif',
                                        'backgroundColor': 'rgb(28, 28,33)',
                                        'border': 'thin solid #FFFFFF',
                                        },
                            style_table={'borderRadius': '4px', 'overflowX': 'scroll', 
                                         'border': '1px solid rgb(55, 58, 64)',
                                         },
                            )
        
    P2_Zscore_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in ['PLAYER'] + Zscores.columns.values.tolist()], 
                            data=Zscores[Zscores.index.isin(P2)].reset_index().round(2).to_dict('records'),
                            style_as_list_view=True,
                            style_header=style_header_midtables,
                            style_data={'backgroundColor': '#212529',
                                        'color': 'rgb(180,181,185)',
                                        'border': '0.7px solid rgb(55, 58, 64)',
                                        },
                            style_cell={'textAlign': 'center', 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                                        'whiteSpace': 'normal', 'fontSize':13, 'font-family':'Roboto, sans-serif',
                                        'backgroundColor': 'rgb(28, 28,33)',
                                        'border': 'thin solid #FFFFFF',
                                        },
                            style_table={'borderRadius': '4px', 'overflowX': 'scroll', 
                                         'border': '1px solid rgb(55, 58, 64)',
                                         },
                            )
    
    P2_aggregate_data = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P2)][aggregate_stats]).T.round(2).reset_index()
    P2_aggregate_data.columns = ['STATS', 'SCORES'] #go around

    P2_aggregate_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in P2_aggregate_data.columns],
                            data= P2_aggregate_data.to_dict('records'),
                            style_as_list_view=True,
                            #'#34354A' highlight color
                            style_header={'backgroundColor': 'rgba(0,0,0,0)' ,
                                          'color':'rgb(237, 234, 222)',
                                          'border': 'none',
                                         },
                            style_data={'backgroundColor': 'rgba(0,0,0,0)',
                                        'color': 'rgb(180,181,185)',
                                        'border': '1px solid rgb(55, 58, 64)',},
                            style_cell={'textAlign': 'right', 'minWidth': '40px', 'width': '100px', 'maxWidth': '100x',
                                        'whiteSpace': 'normal', 'fontSize':14, 'font-family':'Roboto, sans-serif',
                                        'backgroundColor': 'rgba(0,0,0,0)'},     
                                        
                            fill_width=False,
                            )

    if active == "Main Stats":
        return [dmc.Text("Home Team", style={'padding-bottom':'10px'}), P1_total_table, dmc.Text("Away Team", style={'padding-top':'25px','padding-bottom':'10px'}), P2_total_table], [P1_aggregate_total_table], [P2_aggregate_total_table]
    else:
        return [dmc.Text("Home Team", style={'padding-bottom':'10px'}), P1_Zscore_table, dmc.Text("Away Team", style={'padding-top':'25px','padding-bottom':'10px'}), P2_Zscore_table], [P1_aggregate_total_table], [P2_aggregate_total_table]


if __name__ == '__main__':
    app.run(debug=True)
