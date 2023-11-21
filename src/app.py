import dash_mantine_components as dmc
from dash import Dash, html, Input, Output, ALL, callback_context
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
import os
import re
import src.viz_tools as viz_tools 
from src.data_tools import (get_similar_players, get_season_data, get_Zscores, 
                        calculate_percentage_stats, aggregate_fantasy_stats, 
                        get_player_info, get_career_stats, fantasy_stats,
                        last_seasons_fantasy_stats, rank_stats, datemask_season_data)
                        
                        
app = Dash(__name__,
        external_stylesheets=[
            # include google fonts
            "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
            ],
        )

server = app.server  # Needed for gunicorn

############################ Get Paths ###################################
import os
project_path = os.getcwd()
team_logos_path = os.path.join(project_path, "assets/team_logos")

########################### Data Part ######################################
CareerStats = get_career_stats()
CareerStats202223_std = last_seasons_fantasy_stats(CareerStats)
PlayerInfo = get_player_info()
PlayerInfo2023 = get_player_info(still_active = True)
Season_total_2122 = get_season_data("2021-22", Aggregate = "Total")
Season_total_2223 = get_season_data("2022-23", Aggregate = "Total")

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
                      style={'width':1800, 'max-height':75, "border": 'rgb(0,0,0)',
                            "background": 'transparent','border-radius':0,})

#########################################
# "components": {"Text": {"styles": {"root": {"fontSize": "2vh"}}}}
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
Callback functions:

Overview:

Tab2:
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
def update_interval_stats(player,aggregate,interval):   
    interval_stats = datemask_season_data('2022-23', interval[0], interval[1], player, aggregate)
    
    fig = go.Figure(go.Barpolar(
        r=interval_stats.iloc[:,0].values,
        theta=interval_stats.index[:-1],
        marker_color=["#E4FF87", '#709BFF', '#0451CB', '#FFAA70', '#00AEEF', '#FFDF70', '#B6FFB4','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf'],
        marker_line_color="black",
        marker_line_width=2,
        opacity=0.55,
        text=[interval_stats.index[i] + ' = ' + str(interval_stats.iloc[i,0]) for i in range(len(interval_stats))],
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
                    range=[0, 50],
                    showline=False,
                    showticklabels=False,
                    ticks='',),
            ),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor= 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            font_color='white',
            font_size=14
        )
    
    fig.update_layout(
        margin=dict(t=10,b=10,pad=10),
        transition_duration=500
        )
    
    #text under the polar plot
    text = f"The player played total of {int(interval_stats.iloc[-1].values[0])} games in the given date range."

    
    if not aggregate == 'Total':
        fig.update_layout(
            polar=dict(
                hole=0.1,
                radialaxis=dict(
                    visible=True,
                    type='linear',
                    autotypenumbers='strict',
                    range=[0, 4],
                    showline=False,
                    showticklabels=False,
                    ticks='',),
            ),)
        
        return fig, text
        
    return fig, text
    

@app.callback(
    Output("ranking_table_card", "children"), 
    [
    Input("player-select", "value"),
    Input("ranking_agg_type", "value"),
    ]
)
def update_ranking_table(player_name:str, aggregate_type:str) -> dash_table.DataTable:
    
    rank_stats_df = rank_stats(aggregate_type, player_name)
    
    ranking_table = dash_table.DataTable(
                        id='similarity_DataTable',
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
    
    Player_CareerStats = CareerStats[CareerStats['NAME']== player_name]
    Player_CareerStats_updated = Player_CareerStats.drop(Player_CareerStats[Player_CareerStats['TEAM_ID'] == 0].index).groupby(['SEASON_ID','PLAYER_ID']).sum(numeric_only=True).reset_index()
    
    Player_CareerStats_updated['FG_PCT'] =  Player_CareerStats_updated['FGM']/ Player_CareerStats_updated['FGA']
    Player_CareerStats_updated['FT_PCT'] =  Player_CareerStats_updated['FTM']/ Player_CareerStats_updated ['FTA']   
    
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
        Output("birthday_text", "children"),
        Output("country_text", "children"),
        Output("school_text", "children"),
        Output("start_year_text", "children"),
        Output("draft_number_text", "children"),
        Output("position_text", "children"),
        ],

        [
        Input("player-select", "value"),
        ],
        prevent_initial_call=True,
)
def update_player_info_card(player_name:str) -> tuple[str, str, str, str, str, str, str]:
    
    id_for_img1 = int(PlayerInfo[PlayerInfo['name']==player_name].id.values[0])
    src = app.get_asset_url(f"nba_players/{id_for_img1}.png")  

    birthday = pd.to_datetime(PlayerInfo[PlayerInfo['name']==player_name].birthdate).iloc[0].date().strftime('%m-%d-%Y')
    country = PlayerInfo[PlayerInfo['name']==player_name].country.values[0]
    school = PlayerInfo[PlayerInfo['name']==player_name].school.values[0]
    startyear = int(float(PlayerInfo[PlayerInfo['name']==player_name].start_year.values[0]))
    draftnumber = PlayerInfo[PlayerInfo['name']==player_name]['draft number'].values[0]
    pos = PlayerInfo[PlayerInfo['name']==player_name]['position'].values[0]

    return src, birthday, country, school, startyear, draftnumber, pos

 
@app.callback(
        [Output("player-select", "value")],
        [Input({'type': 'teams_logo_image', 'index': ALL}, 'n_clicks')],
        prevent_initial_call=True,
    )
def update_playa_info(ndx:int) -> str: 
    ctx = callback_context
    element_id = ctx.triggered[0]['prop_id'].replace(".n_clicks", "")
    team_id = re.findall("\d+", element_id)[0]
    player_name = PlayerInfo2023[PlayerInfo2023['team_id']==int(team_id)].sample(1).name.values[0]

    return [player_name]


'''----------------Tab 1 Callback functions--------------------'''

@app.callback(
    [
    Output("SelectPlayer_leftdropdown", "data"),
    Output("SelectPlayer_rightdropdown", "data"),

    ],       
    Input("radio-select-season", "value"),
)
def update_options(season):
    if season == "2021-22":
        Season_total_2122 = get_season_data(season, Aggregate = "Total")
        data = [{"label": val, "value": val} for val in Season_total_2122.index.tolist()]
        return data, data
    
    elif season== "2022-23":
        Season_total_2223 = get_season_data(season, Aggregate = "Total")
        data = [{"label": val, "value": val} for val in Season_total_2223.index.tolist()]
        return data, data
    
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
def update_polargraph(P1, P2, season, agg_type):
    #P1 : left ; P2 : right

    if agg_type== 'Total':
        season_total = get_season_data(season, Aggregate = "Total")
        season_totalp = calculate_percentage_stats(season_total)
        season_totalp['FT%'] = 100*season_totalp['FT%']
        season_totalp['FG%'] = 100*season_totalp['FG%']
        

    else:
        season_total = get_season_data(season, Aggregate = "Average")
        season_totalp = calculate_percentage_stats(season_total)
        season_totalp['FT%'] = season_totalp['FT%']
        season_totalp['FG%'] = season_totalp['FG%']

    avg_min = season_totalp['MIN'].median().round(1)
    avg_game = season_totalp['G'].median().round(0)

    #Horizontal plots################ü
    #upper_left
    x_ul = season_total[season_total.index.isin(P1)]['G'].values
    yl = season_total[season_total.index.isin(P1)].index.values

    fig_upper_left = go.Figure(data=[
                        go.Bar(
                            x=x_ul,
                            y=yl,
                            orientation='h',
                            opacity=0.45,
                            width = 0.5, 
                        )],
                    )
    
    fig_upper_left.update_layout(transition_duration=500)
    
    fig_upper_left.update_layout(
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
            tickvals = [0, 25, avg_game, 65, 82],
            domain=[0, 0.90],
            range=[0, 82],
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

    fig_upper_left.add_vline(x=avg_game, line_width=2, line_dash="dash")

    #bottom_left
    x_bl = season_total[season_total.index.isin(P1)]['MIN'].values

    fig_bottom_left = go.Figure(data=[
                        go.Bar(
                            x=x_bl,
                            y=yl,
                            orientation='h',
                            #marker_color='#ff5d9e', #white#5F3DC4
                            opacity=0.45,
                            width = 0.5, 
                            showlegend=True,
                        
                        )],
                    )
    
    fig_bottom_left.update_layout(transition_duration=500)
    
    fig_bottom_left.update_layout(
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
            tickvals = [0, 750, avg_min, 2000, 2800],
            showticklabels=True,
            domain=[0, 0.95],
            range=[0, 2800],
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

    fig_bottom_left.add_vline(x=avg_min, line_width=2, line_dash="dash")


    #upper right
    x_ur = season_total[season_total.index.isin(P2)]['G'].values
    yr = season_total[season_total.index.isin(P2)].index.values

    fig_upper_right = go.Figure(data=[
                        go.Bar(
                            x=x_ur,
                            y=yr,
                            orientation='h',
                            marker_color='#EF553B',
                            opacity=0.70,
                            width = 0.5,                       
                        )]
                    )
    
    fig_upper_right.update_layout(transition_duration=500)

    fig_upper_right.update_layout(
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
            tickvals = [0, 25, avg_game, 65, 82],
            showgrid=False,
            domain=[0.1, 0.95],
            range=[0, 82],
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

    fig_upper_right.add_vline(x=avg_game, line_width=2, line_dash="dash")


    #bottom right
    x_br = season_total[season_total.index.isin(P2)]['MIN'].values

    fig_bottom_right = go.Figure(data=[
                        go.Bar(
                            x=x_br,
                            y=yr,
                            orientation='h',
                            marker_color='#EF553B',
                            opacity=0.70,
                            width = 0.5,

                        )]
                    )
    
    fig_bottom_right.update_layout(transition_duration=500)
    
    fig_bottom_right.update_layout(

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
            tickvals = [0, 750, avg_min, 2000, 2800],
            showgrid=False,
            domain=[0.1, 0.95],
            range=[0, 2800],
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

    fig_bottom_right.add_vline(x=avg_min, line_width=2, line_dash="dash")


    #########Polar Plot    ############
    
    #P1 (right dropdown)
    P1_for_plot = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P1)][fantasy_stats]).T.round(2)
    P1_for_plot.columns = ['Score']

    #P2 (right dropdown)
    P2_for_plot = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P2)][fantasy_stats]).T.round(2)
    P2_for_plot.columns = ['Score']
    
    #P1 (left dropdown)
    fig = go.Figure(
            data=go.Scatterpolar(
            r=P1_for_plot['Score'],
            theta=P1_for_plot.index,
            fill='toself',
            #fillcolor='#ff5d9e',
            #line_color='rgb(40,132,117)',
            #marker_color='#ff5d9e',
            #opacity=.65,
            hoverinfo="text",
            name="",
            text=[P1_for_plot.index[i] + ' = ' + str(P1_for_plot['Score'][i]) for i in range(len(P1_for_plot))]
        )   )
    
    #P2 (right dropdown)
    fig.add_trace(
        go.Scatterpolar(
            r=P2_for_plot['Score'],
            theta=P2_for_plot.index,
            fill='toself',
            #fillcolor='#5F3DC4',
            #line_color='rgb(40,132,117)',
            #marker_color='#5F3DC4',
            #opacity=.65,
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
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            font_size=14
        )
    
    fig.update_layout(transition_duration=500)
    
    return fig, fig_upper_left, fig_bottom_left, fig_upper_right, fig_bottom_right


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


    if agg_type== 'Total':
        season_total = get_season_data(season, Aggregate = "Total")
        season_totalp = calculate_percentage_stats(season_total)
        Zscores = get_Zscores(season, Aggregate = "Total")

    else:
        season_total = get_season_data(season, Aggregate = "Average")
        season_totalp = calculate_percentage_stats(season_total)
        Zscores = get_Zscores(season, Aggregate = "Average")


    #For left side
    P1_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in fantasy_stats],
                            data= season_totalp[season_totalp.index.isin(P1)].reset_index().round(2)[fantasy_stats].to_dict('records'),
                            style_as_list_view=True,

                            style_header={'backgroundColor': 'rgb(28,28,33)',
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
        
    
    P1_Zscore_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in ['PLAYER'] + Zscores.columns.values.tolist()], 
                            data=Zscores[Zscores.index.isin(P1)].reset_index().round(2).to_dict('records'),
                            style_as_list_view=True,

                            style_header={'backgroundColor': 'rgb(28,28,33)',
                                          'color':'rgb(180,181,185)',
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
    
    season_totalp[season_totalp.index.isin(P1)].reset_index().round(2)[fantasy_stats].to_dict('records')
    
    #For Right Side
    P2_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in fantasy_stats],
                            data= season_totalp[season_totalp.index.isin(P2)].reset_index().round(2)[fantasy_stats].to_dict('records'),
                            style_as_list_view=True,

                            style_header={'backgroundColor': 'rgb(28,28,33)',
                                          'color':'rgb(180,181,185)',
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

                            style_header={'backgroundColor': 'rgb(28,28,33)',
                                          'color':'rgb(180,181,185)',
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

