import dash_mantine_components as dmc
from dash import Dash, html, Input, Output, State
import dash_core_components as dcc
import plotly.graph_objects as go
from dash import dash_table
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
import os
import pathlib



app = Dash(__name__,
    external_stylesheets=[
    # include google fonts
    "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
    ],
)

server = app.server  # Needed for gunicorn



### functions #################
def get_season_data(Season, Aggregate = "Total"):
    '''
    type season in the style of '2022-23', '2021-22' etc.
    Data Glossary
    '''
    stats_col = ['PLAYER', 'PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FTM', 'FTA', 'MIN']
    #path
    BASE_PATH = pathlib.Path(__file__).parent.resolve()
    DATA_PATH = BASE_PATH.joinpath("data").resolve()


    if Season == '2021-22':
        Game_Log = pd.read_csv(DATA_PATH.joinpath("GameLog2021_22.csv")
)    
    else:
        Game_Log = pd.read_csv(DATA_PATH.joinpath("GameLog2022_23.csv")) 

    Game_Log=Game_Log.rename(columns = {'PLAYER_NAME':'PLAYER'})
    
    Game_Played = Game_Log[['PLAYER','MIN']].groupby('PLAYER').count()['MIN']

    
    if Aggregate == "Total":
        stats = Game_Log[stats_col].groupby('PLAYER').sum()
        
    else: #PerGame (Average)
        stats = Game_Log[stats_col].groupby('PLAYER').mean()
    
    stats['G'] = Game_Played
    stats = stats[stats['G'] > 25]
    
    return stats

        
def get_Zscores(Season, Aggregate = "Total"):
    #path
    BASE_PATH = pathlib.Path(__file__).parent.resolve()
    DATA_PATH = BASE_PATH.joinpath("data").resolve()
    
    #arrange file name
    S_temp = Season.split('-')
    S1 = str(int(S_temp[0])-1)
    S2 = str(int(S_temp[1])-1)
    Previous_Season = S1 + '-' + S2
    
    df = get_season_data(Season, Aggregate)

    
    if Aggregate == 'Total':
        ps_df = pd.read_excel(DATA_PATH.joinpath(f'BBM_PlayerRankings{Previous_Season}T.xls')) #only top ranked players
        cols = [ 'p', '3', 'r', 'a', 's', 'b', 'to', 'fg%', 'fga', 'ft%', 'fta', 'm', 'g']

    else:
        ps_df = pd.read_excel(DATA_PATH.joinpath(f'BBM_PlayerRankings{Previous_Season}A.xls')) #only top ranked players
        cols = [ 'p/g', '3/g', 'r/g', 'a/g', 's/g', 'b/g', 'to/g', 'fg%', 'fga/g', 'ft%', 'fta/g', 'm/g', 'g']

            
    #get players who played more than 20 games among first 150 ranked in previous season 
    ##calculate population metrics from the gathered data
    filtered_ps_df = ps_df.iloc[:150][ps_df.iloc[:150].g>20]
    filtered_ps_df = filtered_ps_df[cols]
    
    if Aggregate != 'Total':
        filtered_ps_df.columns = [ 'p', '3', 'r', 'a', 's', 'b', 'to', 'fg%', 'fga', 'ft%', 'fta', 'm', 'g']
    
    sums_ = filtered_ps_df.sum()
    means_ = filtered_ps_df.mean()
    sdevs_ = filtered_ps_df.std()
    
    adjusted_fg = (df['FGM'] + (sums_['fga'] * means_['fg%']))/ (df['FGA']+ sums_['fga'])
    adjusted_ft = (df['FTM'] + (sums_['fta'] * means_['ft%']))/ (df['FTA']+ sums_['fta'])

    means_['AFG%'] = adjusted_fg.mean()
    means_['AFT%'] = adjusted_ft.mean()
    sdevs_['AFG%'] = adjusted_fg.std()
    sdevs_['AFT%'] = adjusted_ft.std()
    
    #constract Z-scores df
    Z_scores = pd.DataFrame()
    
    Z_scores['PTS_ZS'] = ((df['PTS']-means_['p'])/sdevs_['p']) 
    Z_scores['FG3M_ZS'] = ((df['FG3M']-means_['3'])/sdevs_['3']) 
    Z_scores['REB_ZS'] = ((df['REB']-means_['r'])/sdevs_['r']) 
    Z_scores['AST_ZS'] = ((df['AST']-means_['a'])/sdevs_['a']) 
    Z_scores['STL_ZS'] = ((df['STL']-means_['s'])/sdevs_['s']) 
    Z_scores['BLK_ZS'] = ((df['BLK']-means_['b'])/sdevs_['b']) 
    Z_scores['TOV_ZS'] = -((df['TOV']-means_['to'])/sdevs_['to']) #beware the minus!
    
    #adjusted by volume
    Z_scores['FG%_ZS'] = ((adjusted_fg-means_['AFG%'])/sdevs_['AFG%']) 
    Z_scores['FT%_ZS'] = ((adjusted_ft-means_['AFT%'])/sdevs_['AFT%'])
    #Z_scores['FG%_ZS'] = (((df['FGM']/df['FGA']) - means_['fg%'])/sdevs_['fg%']) * df['FGA']/means_['fga']
    #Z_scores['FT%_ZS'] = (((df['FTM']/df['FTA']) - means_['ft%'])/sdevs_['ft%']) * df['FTA']/means_['fta']

    
    #extra (you can consider to add total game played and or total minutes metrics as well)
    #Z_scores['MIN_ZS'] = ((df['MIN']-means_['m'])/sdevs_['m'])*0.1
    #Z_scores['G_ZS'] = ((df['G']-means_['g'])/sdevs_['g'])*0.6

    return Z_scores


def calculate_percentage_stats(season_df):

    try:
        season_df['FG%'] = season_df['FGM']/season_df['FGA']
        season_df['FT%'] = season_df['FTM']/season_df['FTA']
        return(season_df)

    except:
        return pd.DataFrame(data=[np.zeros(10)],columns = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%'])


        
    
def aggregate_fantasy_stats(df):
    
    if df.empty:
        return pd.DataFrame(data=[np.zeros(10)],columns = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%'])
        
    final = []

    for i in df.columns:
        if i in [col for col in df.columns if '%' in col]:
            final.append(df[i].mean())
        else:
            final.append(df[i].sum())

    f_df = pd.DataFrame(final).T
    f_df.columns = df.columns

    return f_df

    
    



########################### Data Part ######################################
#21-22 Total
Season_total_2122 = get_season_data("2021-22", Aggregate = "Total")
Season_total_2223 = get_season_data("2022-23", Aggregate = "Total")


#Data For Radio options (label, value)
data = [["Season 2021-22", "2021-22"], ["Season 2022-23", "2022-23"]]
fantasy_stats = ['PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']


########################### App Layout ######################################

#Stat type select
stat_select = dmc.SegmentedControl(id="stat_type",
    value= 'Total',
    data=[{"value": "Total", "label": "Total"},
          {"value": "Average", "label": "Average"}],
    size= 'sm',
    radius='lg',
    color="violet",
)

left_accordion = dmc.Accordion(
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Total Games Played"),
                dmc.AccordionPanel(
                   dcc.Graph(id='upper_left_hbar', 
                                          style={'width': 340})
                ),
            ],
            value="Games",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Total Minutes Played"),
                dmc.AccordionPanel(
                   dcc.Graph(id='bottom_left_hbar', 
                                          style={'width': 340})
                ),
            ],
            value="Minutes",
        ),
    ],

)

right_accordion = dmc.Accordion(
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Total Games Played", style={'textAlign': 'right'},
                ),
                dmc.AccordionPanel(
                   dcc.Graph(id='upper_right_hbar', 
                                          style={'width': 340, })
                ),
            ],
            value="Games",

        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Total Minutes Played", style={'textAlign': 'right'},
                ),
                dmc.AccordionPanel(
                   dcc.Graph(id='bottom_right_hbar', 
                                          style={'width': 340})
                ),
            ],
            value="Minutes",

        ),
    ],
    chevronPosition = "left",

)


#Tables with tabs

Tables_with_tabs = html.Div(
    [
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab("Main Stats",
                                value="Main Stats",
                               
                                ), 

                        dmc.Tab("Z-Scores",
                                value="Z-scores"),
                    ]
                ),
            ],
            id="table-tabs",
            #value="Main Stats",
            style={"paddingTop": 25},
            color='violet',
        ),
        html.Div(id="tabs-content", style={"paddingTop": 15}),
    ]
)

#CARDS

left_card = dmc.Card(
    children=[dmc.CardSection(
            dmc.Group(
                    dmc.Text("Home Team Stats", weight=500),
                position="apart",
            ),
            withBorder=True,
            inheritPadding=True,
            py="xs",
        ),
        dmc.CardSection(id="Left_Card",
            withBorder=True,
            inheritPadding=True,
            py="xs",
            )
        ],
    withBorder=True,
    shadow="md",
    radius="md",
    style={"width": 230},
)

right_card = dmc.Card(className='Right_Card',
    children=[
        dmc.CardSection(
            dmc.Group(
                    dmc.Text("Away Team Stats", weight=500),
                position="right",
            ),
            withBorder=True,
            inheritPadding=True,
            py="xs",
            ),
        dmc.CardSection(id='Right_Card',
            withBorder=True,
            inheritPadding=True,
            py="xs",
            ),
        
        ],
    withBorder=True,
    shadow="md",
    radius="md",
    style={"width": 230,'display': 'inline-block','textAlign': 'right', "paddingTop": 15,}
)


text = dcc.Markdown(
            children=(
                        """
                        ### What is this dashboard about?
                        This is a basketball (NBA) roster (team)/player comparison tool which is built merely for fun. However, one can 
                        freely utilize it to improve their "Fantasy Basketball" game.
                        
                        ### What does this dashboard shows?
                        The dashboard consists of three columns and is designed in a way that the side columns contain a dropdown menu that 
                        helps you to determine your roster, two horizontal bar plots that show total/per game minutes and total number of games 
                        per season, and a table that aggregates   fantasy stats of your roster; while the center column holds a polar graph 
                        and two stat sheets (tables) for the corresponding home and away teams.

                        It is a good sign for a player to be able to spread his performance throughout the season. The total number of games played per 
                        season is not only a good metric to characterize the injury proneness of a player but also his performance consistency. 
                        Thus, a bar chart that shows the total season of games played by a player is also placed.
                        
                        You can build your roster by selecting your players one by one from the dropdown menu that allows multiple selections. 
                        You can find your player by simply typing his name on the search bar of the dropdown menu.         

                        The polar graph in the center compares the nine default categories widely used in 9-category leagues visually, while two 
                        stat sheets for each corresponding roster on the side columns are there for the ones who are after for a more precise, numerical comparison.
                        
                        In addition to statistics of 9 categories, one can see z-scores of the corresponding statistics by simly clicking on the "Z-scores" tab. 

                        In order to calculate Z-scores for the statistics that we are interested in, a conceptual population is created for each season by collecting 
                        the data of the top 188 players of the previous season, then the players who played less than a total of 25 games in that season filtered out.
                        
                        Z-scores of the statistics, except FG% and FT%, are calculated by following the classical formula that uses the population mean and 
                        the population standard deviation for the corresponding statistics. On the other hand  Z-scores of FG% and FT% are weighted by players' shooting volume.

                        
                        ### Why weighted Z-scores for FG% and FT%?
                        The rationale behind taking 'shooting attempt' weighted Z-scores of FG% and FT% stats can be explained by a short example: making a 10 out of 10
                        free throws is much harder than 2 out of 2 while the percentage is %100 for both cases.
                         
                        ### Where did you get your data?
                        All data was downloaded from [Basketball Monster](https://basketballmonster.com/default.aspx) website.




                        &copy Yigitalp Berber                      
                    """
        )
    )



modal = html.Div(
    [
        dmc.Modal(title=text, id="modal-size-55", size="55%", zIndex=10000),
        dmc.Group(
            [
                dmc.Button("About", id="55-modal-button", 
                           size='sm', 
                           radius='sm',
                           variant="outline", 
                           color='violet',
                           rightIcon=DashIconify(icon="grommet-icons:info"),),

            ]
        ),
    ]
)



#########################################

app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    inherit=False,
    withGlobalStyles=True,
    withNormalizeCSS=True,

    children=[
        
        #Header
        html.Div(
        dmc.Header(
                className="Header",
                height=90, 
                children=[
                    dmc.Grid(
                        children=[
                            dmc.Col(
                                dmc.Group(
                                    [html.Img(id="logo1", src=app.get_asset_url("yahoo_fantasy_icon.png")),
                                               dmc.Stack([
                                                    dmc.Title(f"Yahoo Fantasy Basketball", order=2),
                                                    dmc.Title(f"Player Comparison Tool", order=4)
                                                ], align="Stretch", spacing="s", justify="flex-start", ),
                                    ], style={"textAlign":"left"}),
                                    span=4,
                                    ),
                                dmc.Col(span=6),
                                dmc.Col(
                                    dmc.Group([
                                    modal,
                                    html.Img(id="logo2", src=app.get_asset_url("basketball_icon.png")),

                                    ],
                                    position="right", spacing="md"),
                                    span=2,
                                )
                                

                        ],
                        gutter="xl",
                    ),   
                ],        
        ), 
        #style={"backgroundColor": "#9c86e2"},
    ),

    html.Div(className='Tabs',children=[
    dmc.Tabs(
    [
        dmc.TabsList(
            [
                dmc.Tab("Team-wise", value="Team"),
                dmc.Tab("Player-wise", value="Player"),
            ]
        ),

    
    
    dmc.TabsPanel([
        #Middle Grid
        html.Div(
            dmc.Grid(className="Middle", 
                     children=[
                        #Left component
                        dmc.Col(
                            html.Div([
                                html.H3('HOME TEAM'),
                                dmc.MultiSelect(
                                    data=[{"label": val, "value": val} for val in Season_total_2122.index.tolist()],
                                    placeholder="Select Player(s)",
                                    id="SelectPlayer_leftdropdown",
                                    searchable=True,
                                    nothingFound="No Player Found",
                                    clearable=True,
                                    style={"width": 320, "marginBottom": 10},
                                    value = ["Nikola Jokic"],
                                ),
                                left_accordion,
                                html.Div(className='Left_Card_div',children=[left_card]),
            
                            ],
                            style={"textAlign":"left"}), 
                            span="auto"
                        ), 
                        #Middle Component
                        dmc.Col(
                            html.Div([
                                dcc.Graph(id='polar_graph', 
                                          style={'autosize': True},
                                        ),

                                html.Div(className = "Radio_Button",
                                         children =[
                                            dmc.RadioGroup(
                                                [dmc.Radio(l, value=v, color='violet') for l, v in data],
                                                id="radio-select-season",
                                                value="2021-22",
                                                size="sm", 
                                            ),
                                            html.Div([stat_select], style={'padding-top':'15px'}),
                                        ], 
                                        style={"textAlign":"center"}
                                ),
                                Tables_with_tabs,
                                 dmc.Group(
                                        [   dmc.Text("Made with", size="sm"),
                                            html.I(DashIconify(icon="noto-v1:purple-heart")),
                                            dmc.Text("by Yigitalp Berber", size="sm")
                                        ],
                                        position='center', spacing = 'xs', style={'marginTop': 75}),

                            ], style={"textAlign":"center"}
                            ), span=5
                        ),
                        #Right Compnent
                        dmc.Col(className="Right_Component", children = [
                            html.H3('AWAY TEAM', style= {'textAlign': 'right'}),
                            html.Div(className="Right_Dropdown", children=[
                                dmc.MultiSelect(
                                    data=[{"label": val, "value": val} for val in Season_total_2122.index.tolist()],
                                    placeholder="Select Player(s)",
                                    id="SelectPlayer_rightdropdown",
                                    searchable=True,
                                    nothingFound="No Player Found",
                                    clearable=True,
                                    style={"width": 320, "marginBottom": 10, 'textAlign': 'right'},
                                    value = ["Joel Embiid"],
                                ),], style={'display':'inline-block', 'textAlign': 'right',}),
                                right_accordion,
                                html.Div(className='Right_Card_div',children=[right_card])
                            ], 
                            span="auto",
                            ),

                    ], gutter="xl",
            ),
        ),
    ], value="Team"),




    #Second Tab
    dmc.TabsPanel(dmc.Text("In progress...", align="left"), value="Player"),



    ],
    color="violet",
    orientation="horizontal",
    value="Team",
)

    ],

)]
)



################## Call-backs ############################


@app.callback(
        Output(f"modal-size-55", "opened"),
        Input(f"55-modal-button", "n_clicks"),
        State(f"modal-size-55", "opened"),
        prevent_initial_call=True,
    )
def toggle_modal(n_clicks, opened):
    return not opened


@app.callback(
    [
    Output("SelectPlayer_leftdropdown", "data"),
    Output("SelectPlayer_rightdropdown", "data"),

    ],       
    Input("radio-select-season", "value"),
    prevent_initial_call=True
)
def update_options(season):
    if season == "2021-22":
        data = [{"label": val, "value": val} for val in Season_total_2122.index.tolist()]
        return data, data
    elif season== "2022-23":
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
    Input("stat_type", "value"),

    ]
)
def update_polargraph(P1, P2, season, stat_type):
    #P1 : left ; P2 : right

    if stat_type== 'Total':
        season_total = get_season_data(season, Aggregate = "Total")
        season_totalp = calculate_percentage_stats(season_total)
        season_totalp['FT%'] = 100*season_totalp['FT%']
        season_totalp['FG%'] = 100*season_totalp['FG%']


    else:
        season_total = get_season_data(season, Aggregate = "Average")
        season_totalp = calculate_percentage_stats(season_total)
        season_totalp['FT%'] = 10*season_totalp['FT%']
        season_totalp['FG%'] = 10*season_totalp['FG%']

    avg_min = season_totalp['MIN'].median().round(1)
    avg_game = season_totalp['G'].median().round(0)

    #Horizontal plots################

    #upper_left
    x_ul = season_total[season_total.index.isin(P1)]['G'].values
    yl = season_total[season_total.index.isin(P1)].index.values

    fig_upper_left = go.Figure(data=[
                        go.Bar(
                            x=x_ul,
                            y=yl,
                            orientation='h',
                            marker_color='#ff5d9e', #white
                            opacity=0.8,
                            width = 0.5, 
                        )],
                    )
    
    
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
            tickvals = [0, 25, avg_game, 60, 75],
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
                            marker_color='#ff5d9e', #white
                            opacity=0.8,
                            width = 0.5, 
                            showlegend=True,
                        
                        )],
                    )
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
                            marker_color='#5F3DC4', #violet
                            opacity=0.8,
                            width = 0.5,                       
                        )]
                    )

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
            tickvals = [0, 25, avg_game, 60, 75],
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
                            marker_color='#5F3DC4', #violet
                            opacity=0.8,
                            width = 0.5,

                        )]
                    )
    
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
    #P1 (left dropdown)
    P1_for_plot = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P1)][fantasy_stats]).T.round(2)
    P1_for_plot.columns = ['Score']


    list_scores = [P1_for_plot.index[i].capitalize() + ' = ' + str(P1_for_plot['Score'][i]) for i in
                       range(len(P1_for_plot))]
    
    text_scores_1 = 'Team 1'
    for i in list_scores:
        text_scores_1 += '<br>' + i


    #P2 (right dropdown)
    P2_for_plot = aggregate_fantasy_stats(season_totalp[season_totalp.index.isin(P2)][fantasy_stats]).T.round(2)
    P2_for_plot.columns = ['Score']

    list_scores = [P2_for_plot.index[i].capitalize() + ' = ' + str(P2_for_plot['Score'][i]) for i in
                       range(len(P2_for_plot))]
              
    text_scores_2 = 'Team 2 '
    for i in list_scores:
        text_scores_2 += '<br>' + i


    fig = go.Figure(
            data=go.Scatterpolar(
            r=P1_for_plot['Score'],
            theta=P1_for_plot.index,
            fill='toself',
            marker_color='white', 
            opacity=0.75,
            hoverinfo="text",
            name=text_scores_1,
            text=[P1_for_plot.index[i] + ' = ' + str(P1_for_plot['Score'][i]) for i in range(len(P1_for_plot))]
        )   )
    
    fig.add_trace(
        go.Scatterpolar(
            r=P2_for_plot['Score'],
            theta=P2_for_plot.index,
            fill='toself',
            fillcolor='#5F3DC4',
            hoverinfo="text",
            opacity=0.55,
            name=text_scores_2,
            text=[P2_for_plot.index[i] + ' = ' + str(P2_for_plot['Score'][i]) for i in range(len(P2_for_plot))]
        )
        )
    
    
    fig.update_layout(
            polar=dict(
                hole=0.1,
                bgcolor='rgb(9,65,69)',
                radialaxis=dict(
                    visible=True,
                    type='linear',
                    autotypenumbers='strict',
                    autorange=True,
                    range=[0, 500],
                    angle=90,
                    showline=False,
                    showticklabels=False,
                    ticks='',
                    gridcolor='rgb(40,132,117)'),
            ),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            font_size=14
        )
    
    
    return fig, fig_upper_left, fig_bottom_left, fig_upper_right, fig_bottom_right



@app.callback(
        [
        Output("tabs-content", "children"), 
        Output("Left_Card", "children"),
        Output("Right_Card", "children"),
        ],

        [
        Input("table-tabs", "value"),
        Input('SelectPlayer_leftdropdown', 'value'),
        Input('SelectPlayer_rightdropdown', 'value'),
        Input('radio-select-season', 'value'),
        Input("stat_type", "value"),
        ]
        
        )
def update_tables(active, P1, P2, season, stat_type):
    fantasy_stats = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']
    aggregate_stats = fantasy_stats[1:]


    if stat_type== 'Total':
        season_total = get_season_data(season, Aggregate = "Total")
        season_totalp = calculate_percentage_stats(season_total)
        Zscores = get_Zscores(season, Aggregate = "Total")

    else:
        season_total = get_season_data(season, Aggregate = "Average")
        season_totalp = calculate_percentage_stats(season_total)
        Zscores = get_Zscores(season, Aggregate = "Average")


    #For left side

    P1_total_table = dash_table.DataTable(
                            columns=[{"name": i, "id": i} for i in sorted(fantasy_stats)],
                            data= season_totalp[season_totalp.index.isin(P1)].reset_index().round(2)[fantasy_stats].to_dict('records'),
                            style_as_list_view=True,

                            style_header={'backgroundColor': 'rgb(28,28,33)',
                                          'color':'rgb(180,181,185)',
                                          'border': 'none',
                                          },
                            style_data={'backgroundColor': '#212529',
                                        'color': 'rgb(180,181,185)',
                                        'border': '1px solid rgb(55, 58, 64)',
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
                                        'border': '1px solid rgb(55, 58, 64)',
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
                                        'border': '1px solid rgb(55, 58, 64)',},
                            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
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
                                        'border': '1px solid rgb(55, 58, 64)',
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
                                        'border': '1px solid rgb(55, 58, 64)',
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
                            style_cell={'textAlign': 'right', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
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




