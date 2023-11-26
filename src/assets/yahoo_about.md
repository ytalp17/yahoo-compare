
### What is this dashboard about?
This is a basketball (NBA) roster (team)/player comparison tool which is built merely for fun. However, one can 
freely utilize it to improve their "Fantasy Basketball" game.

### What does this dashboard shows?
The dashboard consists of two tabs: team-wise and player-wise tabs, consequently. While one can use the former to compare aggregate key statistics of multiple players, the latter is for player-focused analysis.

The team-wise tab consists of three columns and is designed in a way that the side columns contain a dropdown menu that helps you to determine your roster, two horizontal bar plots that show total/per game minutes and total number of games per season, and a table that presents aggregated fantasy stats of your roster;  the center column holds a polar graph and two stat sheets (tables) for the corresponding home (the top one) and away teams.

It is a good sign for a player to be able to spread his performance throughout the season. The total number of games played per season is not only a good metric to characterize the injury proneness of a player but also his performance consistency. Thus, a bar chart that shows the total season of games played by a player is also placed as indicated.

You can build your roster by selecting your players one by one from the dropdown menu that allows multiple selections. You can find your player by simply typing his name on the search bar of the dropdown menu. 
The polar graph in the center compares the nine default categories widely used in 9-category leagues visually, while two stat sheets for each corresponding roster on the side columns are there for the ones who are after for a more precise, numerical comparison.

In addition to statistics of nine categories, one can see Z-scores of the corresponding category statistics by simply clicking the "Z-scores" tab.

Z-scores are a better metric to see the broader picture because they give us an idea of how an individual value compares to the rest of a distribution. For example, it is hard to answer a question such as: "How good having one block per game is?" You can easily have this kind of question if you know the corresponding Z-score: if it is zero, it means that all player, on average, makes one block per game in the league. On the other hand, positive values can be interpreted as the stat is above the mean. Moreover, the Z-score of 2.32 means that the stat is in the top %1 in the league.

On the other hand, the player-wise tab allows users to go in-depth analysis for an NBA player. One can either select a specific player of interest from the dropdown menu in the "player info card" or click on one of the logos of an NBA team to get a random player from the roster of the selected team.

Career fantasy statistics with minutes and game-played stats of the selected player can be viewed on the scatterplot just right of the player info card. 

One also can pick a data range and compare the stats of a player in that interval with his whole season's stats by utilizing the "player interval card". Moreover, the current ranking of the player in each category can be acquired from the "category stats card", while the "similar players card" can be used to list similar players to the selected player given the selected categories.

More info about the cards can be found by hovering over the info symbol on the right-top corner of the respective card.

### Why weighted Z-scores for FG% and FT%?
The rationale behind taking 'shooting attempt' weighted Z-scores of FG% and FT% stats can be explained by a short example: making a 10 out of 10 free throws is much harder than 2 out of 2 while the percentage is %100 for both cases.
    
### Where did you get your data?
- All data regarding to the previous seasons were downloaded from [Basketball Monster](https://basketballmonster.com/default.aspx) website.
- For the current season data, [nba_api](https://pypi.org/project/nba_api/) python package is being utilized.
- All the player images and team logos are scraped from [the official nba website](nba.com). 



&copy Yigitalp Berber                      
