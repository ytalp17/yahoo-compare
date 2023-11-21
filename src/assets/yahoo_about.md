
### What is this dashboard about?
This is a basketball (NBA) roster (team)/player comparison tool which is built merely for fun. However, one can 
freely utilize it to improve their "Fantasy Basketball" game.

### What does this dashboard shows?
The dashboard consists of three columns and is designed in a way that the side columns contain a dropdown menu that 
helps you to determine your roster, two horizontal bar plots that show total/per game minutes and total number of games per season, and a table that aggregates   fantasy stats of your roster; while the center column holds a polar graph and two stat sheets (tables) for the corresponding home and away teams.

It is a good sign for a player to be able to spread his performance throughout the season. The total number of games played per season is not only a good metric to characterize the injury proneness of a player but also his performance consistency. Thus, a bar chart that shows the total season of games played by a player is also placed.

You can build your roster by selecting your players one by one from the dropdown menu that allows multiple selections. You can find your player by simply typing his name on the search bar of the dropdown menu.         

The polar graph in the center compares the nine default categories widely used in 9-category leagues visually, while two stat sheets for each corresponding roster on the side columns are there for the ones who are after for a more precise, numerical comparison.

In addition to statistics of 9 categories, one can see z-scores of the corresponding statistics by simly clicking on the "Z-scores" tab. 

In order to calculate Z-scores for the statistics that we are interested in, a conceptual population is created for each season by collecting 
the data of the top 188 players of the previous season, then the players who played less than a total of 25 games in that season filtered out.

Z-scores of the statistics, except FG% and FT%, are calculated by following the classical formula that uses the population mean and the population standard deviation for the corresponding statistics. On the other hand  Z-scores of FG% and FT% are weighted by players' shooting volume.


### Why weighted Z-scores for FG% and FT%?
The rationale behind taking 'shooting attempt' weighted Z-scores of FG% and FT% stats can be explained by a short example: making a 10 out of 10 free throws is much harder than 2 out of 2 while the percentage is %100 for both cases.
    
### Where did you get your data?
All data was downloaded from [Basketball Monster](https://basketballmonster.com/default.aspx) website.


&copy Yigitalp Berber                      
