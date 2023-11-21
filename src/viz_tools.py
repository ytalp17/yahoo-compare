import dash_mantine_components as dmc
import dash_core_components as dcc
from dash import html
from dash_iconify import DashIconify
from src.data_tools import get_markdown, get_season_data
from datetime import date


################### Header ########################
#About the modal, get triggered with a click on the info button.
modal = html.Div([
            dmc.Modal(
                dcc.Markdown(
                    get_markdown()), 
                    id="pop-up-modal", 
                    size="55%", 
                    zIndex=10000),
                dmc.Group([
                    dmc.Button(
                        "About", 
                        id="modal-button", 
                        size='sm', 
                        radius='sm',
                        variant="outline", 
                        color='violet',
                        rightIcon=DashIconify(icon="grommet-icons:info")
                        ),
                    ]
            ),
                
        ])


def set_header(yahoo_logo_src: callable) -> html.Div:
    return dmc.Header(
                className="Header",
                height="10vh", 
                children=[
                    dmc.Grid(
                        children=[
                            dmc.Col(
                                dmc.Grid(
                                    children =[
                                        dmc.Col(html.Img(id="logo1", src=yahoo_logo_src), span = 2),
                                        dmc.Col(dmc.Stack([
                                                    dmc.Title(className = 'header_title', children ="Yahoo Fantasy Basketball", order=2),
                                                    dmc.Title(className = 'header_subtitle', children = "Player Comparison Tool", order=4)
                                                    ], align="Stretch", spacing="s", justify="flex-start" ),
                                                span=10,
                                                )   
                                    ], gutter='md', style={"textAlign":"left"}
                                ),span=5, 
                            ),
                            dmc.Col(span="auto"),
                            dmc.Col(
                                dmc.Group([
                                modal,
                                ],
                                position="right", spacing="md"),
                                span=2,
                                )
                        ],
                        gutter="xl",
                    ),   
                ],        
        ), 


###################################################
#################### Tab 1  #######################
###################################################

##################
### COMPONENTS ###
##################

#################### Game Play & Minutes Accordions (Left and Right) ####################

#Left Accordion Component, contains  Game Played &  Minutes Played horizontal bars
left_accordion = dmc.Accordion(
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("Total Games Played"),
                                dmc.AccordionPanel(
                                dcc.Graph(
                                    id='upper_left_hbar', 
                                    style={'width': '%100'})
                                ),
                            ],
                            value="Left_Games",
                        ),
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("Total Minutes Played"),
                                dmc.AccordionPanel(
                                dcc.Graph(
                                    id='bottom_left_hbar', 
                                    style={'width':'%100'})
                                ),
                            ],
                            value="Left_Minutes",
                        ),
                    ],

                )


#Right Accordion Component, contains  Game Played &  Minutes Played horizontal bars
right_accordion = html.Div(dmc.Accordion(className='right_accordion',
                    children=[
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("Total Games Played", style={'textAlign': 'right'}),
                                dmc.AccordionPanel(
                                    dcc.Graph(
                                        id='upper_right_hbar', 
                                        style={'width':'%100' }
                                        )
                                ),
                            ],
                            value="Right_Games",

                        ),
                        dmc.AccordionItem(
                            [
                                dmc.AccordionControl("Total Minutes Played", style={'textAlign': 'right'}),
                                dmc.AccordionPanel(
                                    dcc.Graph(
                                        id='bottom_right_hbar', 
                                         style={'width':'%100'})
                                    ),
                            ],
                            value="Right_Minutes",
                        ),
                    ],
                    chevronPosition = "left",
                ),style={'display':'block'},
)

#################### Stats Cards (Left and Right) ####################

#Left Card component, contains aggregated stats tables with list view
left_stat_card = dmc.Card(
                    children=[
                        dmc.CardSection(
                            dmc.Text(className = "card_header_text", children ="Home Team Stats", weight=500),
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                        ),
                        dmc.CardSection(
                            id="left_stat_card",
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                            )
                    ],
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    style={"width": "75%"},
                )

#Right Card component, contains aggregated stats tables with list view
right_stat_card = dmc.Card(
                    className='Right_Card',
                    children=[
                        dmc.CardSection(
                            dmc.Text(className = "card_header_text", children ="Away Team Stats", weight=500),
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                            ),
                        dmc.CardSection(id='right_stat_card',
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                            ),
                    ],
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    style={"width": "75%",'display': 'inline-block','textAlign': 'right'}
                )


#Radioesk Component (Select type of aggregate fnc: Total or Average)
aggregate_type = dmc.SegmentedControl(
                    id="agg_type",
                    value= 'Total',
                    data=[{"value": "Total", "label": "Total"},
                        {"value": "Average", "label": "Average"}],
                    size= 'xs',
                    radius='lg',
                    color="violet",
                )


#Tables within tabs (Main Stats & Z-scores Tables)
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
                                                value="Z-scores",
                                        ),
                                        dmc.Tab(
                                            dmc.Tooltip(
                                                multiline=True,
                                                position = 'top-end',
                                                width=250,
                                                withArrow=True,
                                                transition="fade",
                                                transitionDuration=200,
                                                label= "Scroll tables right for more columns.",
                                                children=[html.I(DashIconify(icon="material-symbols:info-outline", width=20))], 
                                            ),
                                            value="settings", ml="auto", disabled = True,
                                            ),
                                    ]
                                ),
                            ],
                            id="table-tabs",
                            style={'display':'inline-block',"paddingTop": 25, "width": '90%',"textAlign":"center"},
                            color='violet',
                            value='Main Stats',
                        ),
                        html.Div(id="tabs-content", style={'display':'inline-block',"paddingTop": 15, "width": '80%',"textAlign":"center"}),
                    ]
                )

##################
##### LAYOUT #####
##################


left_column_section = dmc.Col(
                        [
                            html.H3('HOME TEAM'),
                            dmc.MultiSelect(
                                id="SelectPlayer_leftdropdown",
                                placeholder="Select Player(s)",
                                searchable=True,
                                nothingFound="No Player Found",
                                clearable=True,
                                style={"width": '100%', "marginBottom": 10, "marginTop": 5,},
                                value = ["Nikola Jokic"],
                            ),
                            
                            left_accordion,
                            
                            html.Div(className='Left_Card_div',children=[left_stat_card]),
                        ],
                        style={"textAlign":"left"}, 
                        span=3
                    )


center_column_section = dmc.Col(
                            html.Div([
                                dcc.Graph(
                                    id='polar_graph', 
                                    style={'autosize': True},
                                    ),
                                
                                html.Div(className = "Radio_Button",
                                    children =[
                                        dmc.RadioGroup(
                                            [dmc.Radio(label=l, value=v, color='violet') for l, v in [["Season 2021-22", "2021-22"], ["Season 2022-23", "2022-23"]]],
                                                id="radio-select-season",
                                                value="2021-22",
                                                size="sm", 
                                            ),
                                        
                                            html.Div([aggregate_type], style={'padding-top':'15px'}),
                                    ], 
                                    style={"textAlign":"center"}
                                ),
                                
                                Tables_with_tabs,
                                
                                 dmc.Group(
                                    [   dmc.Text("Made with", size="sm"),
                                        html.I(DashIconify(icon="noto-v1:purple-heart")),
                                        dmc.Text("by Yigitalp Berber", size="sm")
                                    ],
                                    position='center', 
                                    spacing = 'xs', 
                                    style={'marginTop': 50}),
                            ], 
                            style={"textAlign":"center"}
                            ), 
                        span=6
                        )

right_column_section = dmc.Col(className="Right_Component", 
                            children = [
                                html.H3('AWAY TEAM', style= {'textAlign': 'right'}),
                                
                                html.Div(className="Right_Dropdown", 
                                    children=[
                                        dmc.MultiSelect(
                                            placeholder="Select Player(s)",
                                            id="SelectPlayer_rightdropdown",
                                            searchable=True,
                                            nothingFound="No Player Found",
                                            clearable=True,
                                            style={"width": '100%', "marginTop": 5,"marginBottom": 10, 'textAlign': 'right'},
                                            value = ["Joel Embiid"],
                                        ),
                                    ], 
                                    style={'display':'block', 
                                           'textAlign': 'right',}),
                                
                                right_accordion,
                                
                                html.Div(className='Right_Card_div',children=[right_stat_card]),
                            ], 
                            span=3,
                        )

tab1_layout = dmc.Grid(className="Middle", 
                children=[
                    left_column_section,
                    center_column_section,
                    right_column_section
                ], 
                gutter="xl",
            )


###################################################
#################### Tab 2  #######################
###################################################

##################
### COMPONENTS ###
##################

still_active_2023_players = get_season_data('2022-23', 'Total', still_active_players = True)

#################### Player Info Card ##############

PlayerSelect_dropdown = [dmc.Select(
                            placeholder="Select Player",
                            id="player-select",
                            data=[{"label": val, "value": val} for val in still_active_2023_players.index.tolist()],
                            value= 'LeBron James',
                            style={"width": '100%', 'display': 'inline-block', "text-align":'left', 'justify': 'center'}, 
                            searchable=True,
                            clearable=False,
                            dropdownPosition="top-start",
                            maxDropdownHeight=180,
                        ),
                         ]


def player_card(asset_src: callable) -> dmc.Grid:
    return dmc.Card(
                children=[
                    dmc.CardSection(
                        [
                            dmc.Grid(
                            children=[
                                dmc.Col(html.Div(
                                    dmc.Stack([
                                        dmc.Image(
                                            id='player_image',
                                            src= asset_src,
                                            width='100%',
                                            height='100%',
                                            withPlaceholder=True,
                                            placeholder=[dmc.Loader(color="gray", size="sm")],
                                            ), 
                                        dmc.Group([html.Div(PlayerSelect_dropdown)],
                                            position="center",
                                            ),
                                        ], justify="space-around", align="center", 
                                        ),

                                        ), #Div 
                                        span='auto'
                                        ),

                                dmc.Col(html.Div(
                                            dmc.Stack(
                                            [
                                                dmc.Group([
                                                DashIconify(icon="cil:birthday-cake", width=20, height=20),
                                                dmc.Text("1984-12-30", id='birthday_text',size="md"),
                                                ]),
                                                dmc.Group([
                                                DashIconify(icon="gis:earth", width=20, height=20),
                                                dmc.Text("USA", id='country_text', size="md"),
                                                ]),
                                                dmc.Group([
                                                DashIconify(icon="iconoir:position", width=20, height=20),
                                                dmc.Text("F", id ='position_text',size="md"),
                                                ]),
                                                dmc.Group([
                                                DashIconify(icon="ic:outline-school", width=20, height=20),
                                                dmc.Text("Vincent-St. Mary", id='school_text', size="md"),
                                                ]),
                                                dmc.Group([
                                                DashIconify(icon="ic:baseline-start", width=20, height=20),
                                                dmc.Text("2003",id='start_year_text', size="md"),
                                                ]),
                                                dmc.Group([
                                                DashIconify(icon="carbon:license-third-party-draft", width=20, height=20),
                                                dmc.Text("1",id='draft_number_text', size="md"),
                                                ]),
                            
                                            ],
                                            justify="space-around", align="flex-start", spacing="xs",
                                            ),
                                        ), span=1),
                                ], gutter=60, grow=1,
                            ), 
                        ]
                    )
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                style={'height': 290, 'width': '100%','display': 'inline-block', 
                       'textAlign': 'left', "padding": 32, }
            )


#################### Team Logos Bar ##############


def team_logos(team_id: str, team_img_src: callable) -> html.Img:
    
    return html.Img(
            className='Litem',
            id={'index': f"{team_id}", 'type': 'teams_logo_image'}, 
            src=team_img_src,
            height=60,
            width=60,
            style= {"background": 'transparent',
                    "padding": 5,
                    "opacity":0.85,
                    'border-radius':0,
},
            )
    
def set_team_logos_container(teams: dmc.Group) -> dmc.Container:
     
        return  dmc.ScrollArea( 
                    className='Lcontainer',
                    children = [teams],
                    style = {   
                                "background": 'transparent',
                                "padding":10,
                                'border-radius':0,
                                'textAlign':'center',
                                'marginLeft':'2rem',
                                'marginRight':'2rem',
                                'marginBottom': '0.5rem',
                                'marginTop': '1rem',
                            },
                )
           
          
    
#################### Career Stat Plot Card ##############
    
career_stat_plot_card = dmc.Card(className='Grid_Card',
                            children=[
                                dmc.CardSection([
                                    dcc.Graph(id='career_graph', 
                                    style={'display':'inline-block','height':'82%','width':'96%', 'textAlign': 'center', 'margin': 10, 
                                           'marginBottom': 0}),
                
                                    dmc.SegmentedControl(
                                        id="stat_type_graph",
                                        value= 'PTS',
                                        data=[{"value": val, "label": val} for val in ['MIN', 'PTS', 'FG_PCT', 'FG3M', 'FT_PCT', 'REB', 'AST', 'STL', 'BLK', 'TOV']],
                                        size= 'xs',
                                        radius='sm',
                                        color="violet",
                                        style={'height': '12%','width':'96%','textAlign': 'center'}
                                        )
                                    ], style={'display':'inline-block','height':280, },
                                )
                            ],
                            withBorder=True,
                            shadow="md",
                            radius="md",
                            style={'textAlign': 'center','height':290,}
                        )


#################### Similiar Players Card ##############

similarity_card  = dmc.Card(className='Grid_Card',
                    children=[
                        dmc.CardSection(className = 'Card_Header', children = [
                            dmc.Group([
                                dmc.Text(className="card_header_text",children =["Similar Players"], weight=500),
                                dmc.Tooltip(
                                    multiline=True,
                                    width='100%',
                                    withArrow=True,
                                    transition="fade",
                                    transitionDuration=200,
                                    label= "This card shows the similiar players to your player given"
                                    "the selected fantasy statistics. Statistics of 2022-23 season are"
                                    "used as the benchmark data, and cosine similiarty metric is used"
                                    "to find the listed similar players.",
                                    children=[DashIconify(icon="material-symbols:info-outline", width=20)]
                                    ),
                                ],
                            position="apart",
                            ),],
                            withBorder=True,
                            inheritPadding=True,
                            py="sm",
                            my='sm',
                        ),
                        html.Div([
                            dmc.Container(
                                id="similarity_table_card",
                                ml=0.75,
                                pl=0.75,
                                mt="xs",
                                style={'height': '50%'}
                                ),
                            dmc.CheckboxGroup(
                                id="checkbox-group",
                                offset="sm",
                                my="xs",
                                size='xs',
                                children=[
                                    dmc.Checkbox(label="PTS", value="PTS",  color = 'violet'),
                                    dmc.Checkbox(label="FG%", value="FG_PCT", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="FT%", value="FT_PCT", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="AST", value="AST", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="TOV", value="TOV", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="REB", value="REB", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="BLK", value="BLK", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="STL", value="STL", size = 'xs', color = 'violet'),
                                    dmc.Checkbox(label="FG3M", value="FG3M", size = 'xs', color = 'violet'),
                                ],
                                value=["PTS", "AST", "REB", "TOV"],
                                style={'display':'grid', 'justify-content': 'space-evenly','height': '40%'},
                                ),
                            ], 
                                   
                        ),
                    ],
                    withBorder=True,
                    shadow="md",
                    radius="md",
                )


#################### Ranking Card ##############

ranking_card = dmc.Card(className='Grid_Card',
                    children=[
                        dmc.CardSection(className = 'Card_Header', children = [
                            dmc.Group([
                                dmc.Text(className = "card_header_text", children = ["Category Rankings"], weight=500),
                                dmc.SegmentedControl(
                                    id="ranking_agg_type",
                                    value= 'Total',
                                    data=[{"value": "Total", "label": "Total"},
                                          {"value": "Average", "label": "Average"}],
                                    color="violet",
                                    radius="lg",
                                    size='xs',
                                ),
                                dmc.Tooltip(
                                    multiline=True,
                                    width=220,
                                    withArrow=True,
                                    transition="fade",
                                    transitionDuration=200,
                                    label= "This card shows the 9-cat rankings of your player for 2022-23 season."
                                    " Rankings are calculated by sorting calculated Z-scores of respective categories."
                                    " A synthetic population that contains top 150 players who played at least 20 games"
                                    "through out the 2021-22 season is created to calculate population parameters for each category.",
                                    children=[DashIconify(icon="material-symbols:info-outline", width=20)]
                                    ),
                                ],
                            position="apart",
                            ),],
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                            my='xs',
                        ),
                        html.Div([
                            dmc.Container(
                                id="ranking_table_card",
                                ml=0.75,
                                pl=0.75,
                                mt="xs",
                                mb=60,
                                style={'height': '60%', 'width': '100'},
                                ),
                        ],     
                        ),
                    ],
                    withBorder=True,
                    shadow="md",
                    radius="md",   
                )


#################### Interval Stats Card ##############

interval_stats = dmc.Card(className='Grid_Card',
                    children=[
                        dmc.CardSection(className = 'Card_Header', children = [
                            dmc.Group([
                                dmc.Text(className = "card_header_text", children =["Player Interval Stats"], weight=500),
                                dmc.SegmentedControl(
                                    id="ranking_agg_type2",
                                    value= 'Total',
                                    data=[{"value": "Total", "label": "Total"},
                                          {"value": "Average", "label": "Average"}],
                                    size= "xs",
                                    color="violet",
                                    radius="lg",
                                ),
                                dmc.Tooltip(
                                    multiline=True,
                                    width=220,
                                    withArrow=True,
                                    transition="fade",
                                    transitionDuration=200,
                                    label=" This card shows stats of your players in a given data range.",
                                    children=[DashIconify(icon="material-symbols:info-outline", width=20)]
                                    ),
                                ],
                            position="apart",
                            ),],
                            withBorder=True,
                            inheritPadding=True,
                            py="xs",
                            my='xs',
                        ),
                        dcc.Graph(id='interval_stats_graph', style={'height': '70%'}),
                        html.Div([
                            dmc.DateRangePicker(
                            id="date-range-picker",
                            minDate=date(2022, 10, 18),
                            value=[date(2022, 10, 18), date(2022, 11, 22)],
                            maxDate=date(2023, 4, 9),
                            inputFormat="YYYY-DD-MM",
                            dropdownPosition="top-start",
                            my="xs"),
                            
                            dmc.Text(id='games_text', size="xs"),
                        ]
                        ),
                        
                    ],
                    withBorder=True,
                    shadow="md",
                    radius="md",
                )



##################
##### LAYOUT #####
##################

def tab2_layout(player_img_src: callable) -> dmc.Grid:
    return html.Div([dmc.Grid(className='tab2',
                children=[
                    dmc.Col([
                        player_card(player_img_src),
                        ], 
                        span=5, 
                        ),
                    
                    dmc.Col([
                            career_stat_plot_card
                        ], 
                        span=7, 
                        ),
                ],
                gutter="sm",
            ),
            dmc.Grid(className='tab2',
                children=[
                    dmc.Col([
                        html.Div(interval_stats)
                        ], 
                        span=4, 
                        ),
                    dmc.Col([
                        html.Div(ranking_card)
                        ], 
                        span=4, 
                        ),
                    dmc.Col([
                        html.Div(similarity_card)
                        ], 
                        span=4, 
                        ),
                ],
                gutter="sm",
            ),
            
    ])