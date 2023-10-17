import pandas as pd
import numpy as np
import os


def get_season_data(Season, Aggregate = "Total"):
    '''
    type season in the style of '2022-23', '2021-22' etc.
    Data Glossary
    '''
    stats_col = ['PLAYER', 'PTS', 'FG3M', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FTM', 'FTA', 'MIN']
    appDataPath = "/Users/yberber/Documents/Projects/yahoo_mantine/data/"  

    if Season == '2021-22':
        Game_Log = pd.read_csv(os.path.join(appDataPath,'GameLog2021_22.csv'))    
    else:
        Game_Log = pd.read_csv(os.path.join(appDataPath,'GameLog2022_23.csv')) 

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

    appDataPath = "/Users/yberber/Documents/Projects/yahoo_mantine/data"  

    
    #arrange file name
    S_temp = Season.split('-')
    S1 = str(int(S_temp[0])-1)
    S2 = str(int(S_temp[1])-1)
    Previous_Season = S1 + '-' + S2
    
    df = get_season_data(Season, Aggregate)
    
    if Aggregate == 'Total':
        ps_df = pd.read_excel(os.path.join(appDataPath,f'BBM_PlayerRankings{Previous_Season}T.xls')) #only top ranked players
        cols = [ 'p', '3', 'r', 'a', 's', 'b', 'to', 'fg%', 'fga', 'ft%', 'fta', 'm', 'g']

    else:
        ps_df = pd.read_excel(os.path.join(appDataPath,f'BBM_PlayerRankings{Previous_Season}A.xls')) #only top ranked players
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

    
    