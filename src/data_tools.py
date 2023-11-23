import numpy as np
import pandas as pd
import pathlib
import pickle

from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance
from nba_api.stats.endpoints import PlayerGameLogs


#############################################################################################
#################### Data Manuplation / Feature Engineering Functions #######################
#############################################################################################

fantasy_stats = ['PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']

global DATA_PATH, BASE_PATH, ASSET_PATH
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()
ASSET_PATH = BASE_PATH.joinpath("assets").resolve()


def get_season_data(Season: str, Aggregate: str = "Total", raw= False) -> pd.DataFrame:
    '''
    Type season in the style of '2022-23', '2023-24' etc.
    Returns df with aggregated (total or avg) classic fantasy stats + MIN + Game_played columns.
    The index of the df is PLAYER (player name)
    '''
    stats_col = ['PLAYER', 'PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FTM', 'FTA', 'MIN']
    
    if Season != '2023-24':
        #path
        extension = '.csv'
        Season = Season.replace('-', '_')
        file_name = 'GameLog' + Season + extension 
        Game_Log= pd.read_csv(DATA_PATH.joinpath(file_name))
    else:
        Game_Log =  PlayerGameLogs(season_nullable='2023-24').get_data_frames()[0]
        
    Game_Log= Game_Log.rename(columns = {'PLAYER_NAME':'PLAYER'})
    
    if raw == True:
        return Game_Log
    
    Game_Played = Game_Log[['PLAYER','MIN']].groupby('PLAYER').count()['MIN']

    if Aggregate == "Total":
        stats = Game_Log[stats_col].groupby('PLAYER').sum()
        
    else: #PerGame (Average)
        stats = Game_Log[stats_col].groupby('PLAYER').mean()
    
    stats['G'] = Game_Played
    
    '''
    #filters out the ones who played in the indicated season but still not an active player.    
    if still_active_players:
        PlayerInfo = get_player_info(False) #miscellenous info about active players
        tmp_df = stats.merge(PlayerInfo[['name']], right_on=['name'], left_on = stats.index)
        tmp_df.index = tmp_df.name
        tmp_df = tmp_df.drop('name', axis=1)
        return tmp_df
    
    else:
        return stats
    '''
    return stats.round(2)
    
def get_Zscores(df: pd.DataFrame, Season: str, Aggregate : str = "Total", still_active_players: bool = False) -> pd.DataFrame:
    '''
    Retruns df with Z-scores of the fantasy stats.
    The Index of the df is PLAYER name.
    '''
    
    #arrange file name
    S_temp = Season.split('-')
    S1 = str(int(S_temp[0])-1)
    S2 = str(int(S_temp[1])-1)
    Previous_Season = S1 + '_' + S2
    
    #df = get_season_data(Season, Aggregate)

    if Aggregate == 'Total':
         with open(f'/Users/yberber/Documents/Projects/yahoo_mantine/data/pop_par{Previous_Season}T.pkl', 'rb') as f:
            ps_df = pickle.load(f) # deserialize using load()
            

    else:
         with open(f'/Users/yberber/Documents/Projects/yahoo_mantine/data/pop_par{Previous_Season}A.pkl', 'rb') as f:
            ps_df = pickle.load(f) # deserialize using load()
            
    
    #constract Z-scores df
    Z_scores = pd.DataFrame()
    
    adjusted_fg = (df['FGM'] + (ps_df['sums_']['fga'] * ps_df['means_']['fg%']))/ (df['FGA']+ ps_df['sums_']['fga'])
    adjusted_ft = (df['FTM'] + (ps_df['sums_']['fta'] * ps_df['means_']['ft%']))/ (df['FTA']+ ps_df['sums_']['fta'])

    
    Z_scores['PTS_ZS'] = ((df['PTS']-ps_df['means_']['p'])/ps_df['sdevs_']['p']) 
    Z_scores['FG3M_ZS'] = ((df['FG3M']-ps_df['means_']['3'])/ps_df['sdevs_']['3']) 
    Z_scores['REB_ZS'] = ((df['REB']-ps_df['means_']['r'])/ps_df['sdevs_']['r']) 
    Z_scores['AST_ZS'] = ((df['AST']-ps_df['means_']['a'])/ps_df['sdevs_']['a']) 
    Z_scores['STL_ZS'] = ((df['STL']-ps_df['means_']['s'])/ps_df['sdevs_']['s']) 
    Z_scores['BLK_ZS'] = ((df['BLK']-ps_df['means_']['b'])/ps_df['sdevs_']['b']) 
    Z_scores['TOV_ZS'] = -((df['TOV']-ps_df['means_']['to'])/ps_df['sdevs_']['to']) #beware the minus!
    
    #adjusted by volume
    Z_scores['FG%_ZS'] = ((adjusted_fg-ps_df['means_']['AFG%'])/ps_df['sdevs_']['AFG%']) 
    Z_scores['FT%_ZS'] = ((adjusted_ft-ps_df['means_']['AFT%'])/ps_df['sdevs_']['AFT%'])
    #Z_scores['FG%_ZS'] = (((df['FGM']/df['FGA']) - ps_df['meanss_']['fg%'])/ps_df['sdevs_']['fg%']) * df['FGA']/ps_df['meanss_']['fga']
    #Z_scores['FT%_ZS'] = (((df['FTM']/df['FTA']) - ps_df['meanss_']['ft%'])/ps_df['sdevs_']['ft%']) * df['FTA']/ps_df['meanss_']['fta']
    
    #extra (you can consider to add total game played and or total minutes metrics as well)
    #Z_scores['MIN_ZS'] = ((df['MIN']-ps_df['meanss_']['m'])/ps_df['sdevs_']['m'])*0.1
    #Z_scores['G_ZS'] = ((df['G']-ps_df['meanss_']['g'])/ps_df['sdevs_']['g'])*0.6

    return Z_scores


def rank_stats(total: pd.DataFrame,  player_name: str) -> pd.DataFrame:
    
    #total = get_Zscores('2022-23',agg_type)
    if total[total.index==player_name].empty:
        tmp = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        return pd.DataFrame(data = np.c_[fantasy_stats,tmp], columns = ['STATS','RANK'])
    
    total = total.reset_index()

    fstats = ['PTS_ZS', 'FG3M_ZS', 'REB_ZS', 'AST_ZS', 'STL_ZS', 'BLK_ZS', 'TOV_ZS','FG%_ZS', 'FT%_ZS']
    rankings = []

    for stat in fstats:        
        if stat == 'TOV':
            tmp = total.sort_values([stat], ascending=True).reset_index(drop=True)
            rankings.append(tmp[tmp.PLAYER == player_name].index.values + 1 )
            continue
        tmp = total.sort_values([stat], ascending=False).reset_index(drop=True)
        rankings.append(tmp[tmp.PLAYER == player_name].index.values + 1)

    return pd.DataFrame(np.c_[fantasy_stats,rankings], columns = ['STATS','RANK'])


def calculate_percentage_stats(season_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Calculates percentage stats.
    '''

    try:
        season_df['FG%'] = season_df['FGM']/season_df['FGA']
        season_df['FT%'] = season_df['FTM']/season_df['FTA']
        return(season_df)

    except:
        zeros_df_cols = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']
        return pd.DataFrame(data=[np.zeros(10)],columns = zeros_df_cols)

    
def aggregate_fantasy_stats(df: pd.DataFrame) -> pd.DataFrame:
    '''
    sum fantasy stats except percentage stats, average them.
    '''
    
    if df.empty:
        empty_df_cols = ['PLAYER','PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'FT%']
        return pd.DataFrame(data=[np.zeros(10)],columns = empty_df_cols)
        
    final = []
    for i in df.columns:
        if i in [col for col in df.columns if '%' in col]:
            final.append(df[i].mean())
        else:
            final.append(df[i].sum())

    f_df = pd.DataFrame(final).T
    f_df.columns = df.columns

    return f_df

def drop_multiple_team_records(df: pd.DataFrame) -> pd.DataFrame:
    '''
        Some players were transfered in the middle of the season. For these players there are three records (rows)
    that summarizes their season performance; his first team perf, second team perf, and total.
    Hence, this function keeps the total row and get rid of the rest of the records for every player who had multiple 
    teams for the last season (2022-23).
    '''
    
    indexes_to_drop = np.array([])

    for index, row in df.iterrows():
        if row['TEAM_ID'] == 0:
            player_id = row['PLAYER_ID']
            drop_rows = df[(df['PLAYER_ID']==player_id) & (df['TEAM_ID']!=0)]
            indexes_to_drop = np.r_[indexes_to_drop, drop_rows.index.values]
         
    df_clean = df.drop(indexes_to_drop, axis=0)
    
    return  df_clean


def last_seasons_fantasy_stats(df: pd.DataFrame) -> pd.DataFrame:
    '''
    The recent season, 2023-24 is taken as the benchmark season where all the calculations are made by using stats of this season.
    '''
    
    global fantasy_stats_columns
    fantasy_stats_columns = ['GP','PTS', 'FGA', 'FGM', 'FG3M', 'FTA', 'FTM', 'REB', 'AST', 'STL', 'BLK', 'TOV']

    df_last_season = df[df['SEASON_ID']=='2023-24']

    df_last_season = drop_multiple_team_records(df_last_season)
    
    columns = ['name'] + fantasy_stats_columns
    df_last_season = df_last_season[columns]
    
    df_last_season.index = df_last_season['name']
    df_last_season = df_last_season.drop(['name'], axis=1)
    df_last_season = df_last_season.div(df_last_season['GP'], axis=0).round(2) #from totals to pergame stats
    df_last_season = df_last_season.drop(['GP'],axis=1)
    
    return df_last_season


def get_similar_players(df: pd.DataFrame, selected_stats: list ,player_name: str, top : int = 9) -> pd.DataFrame:
    '''
    Calculate similarity scores for all the active players wrt a given player.
    This fnc uses "cosine distance" as a similarity metric.
    '''
    
    df_last_season = last_seasons_fantasy_stats(df)
    
    std = StandardScaler()
    df_std_values = std.fit_transform(df_last_season)
    
    df_std = pd.DataFrame(data = df_std_values, columns = df_last_season.columns)
    df_std.index = df_last_season.index
    
    if 'FT_PCT' in selected_stats:
        selected_stats.remove('FT_PCT')
        selected_stats.append('FTM')
        selected_stats.append('FTA')
        
    if 'FG_PCT' in selected_stats:
        selected_stats.remove('FG_PCT')
        selected_stats.append('FGM')
        selected_stats.append('FGA')
        
    df_std = df_std[selected_stats]
    dist=[]
    for i in range (0, len(df_std.index)):
        dist.append(distance.cosine(df_std.loc[player_name,:].values, df_std.iloc[i].values))
    
    df_std['cosine_dist'] = dist
    
    top_similarity_df = df_std['cosine_dist'].sort_values().reset_index().iloc[1:top].reset_index(drop=True)
    top_similarity_df = top_similarity_df.drop(['cosine_dist'], axis=1)
    top_similarity_df.columns = ['PLAYER']
    
    return top_similarity_df

def datemask_season_data(df: pd.DataFrame, Start_Date: str, End_Date: str, Player: str, Aggregate: str = "Total") -> pd.DataFrame:
    '''
    Get the stats of the selected player from a given date range.
    '''
    stats_col = ['PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FTM', 'FTA', 'MIN']
    
    player_specific = df[df['PLAYER'] == Player]
    mask = (player_specific['GAME_DATE'] > Start_Date) & (player_specific['GAME_DATE'] <= End_Date)
    player_specific = player_specific.loc[mask]
    player_specific = player_specific.drop('PLAYER', axis =1)
    game = len(player_specific)
    
    if Aggregate == "Total":
        stats = player_specific[stats_col].sum()
        G = pd.DataFrame([game],columns = ['G'])
        stats = pd.concat([stats,G.T], axis=0).round(2)
        
    else: #PerGame (Average)
        stats = player_specific[stats_col].mean()
        G = pd.DataFrame([game],columns = ['G'])
        stats = pd.concat([stats,G.T], axis=0).round(2)

    return stats

def get_markdown() -> str:
    f = open(ASSET_PATH.joinpath('yahoo_about.md'), 'r') 
    return f.read()

def get_player_info() -> pd.DataFrame:
    """
    still_active returns df of player names who played in 2022-23 season and still an active nba player,
    and their recent team.
    """
    df = pd.read_csv(DATA_PATH.joinpath('PlayerInfo.csv'))
    
    return df

def get_career_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH.joinpath('Career_Stats.csv'))
    return df

def get_player_list() -> list:
    '''
    Return list of active 2023-24 player names.
    '''
    with open(f'/Users/yberber/Documents/Projects/yahoo_mantine/data/players_list.pkl', 'rb') as f:
        player_list = pickle.load(f) # deserialize using load()

    return player_list