import pandas as pd
pd.set_option('display.max_rows',1000)
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


#Link to fbref url for the data
url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"

#create empty list
pl_list = []

#
pl_list.append(pd.read_html(url,index_col=False,flavor='lxml')[0])
pl_list = pd.concat(pl_list, axis = 0, ignore_index = True)

#Get rid of NAs and rename xG colums to show home and away
pl_df = pl_list[pl_list['Wk'].notna()]
pl_df = pl_df.rename(columns={'xG': 'xG_home', 'xG.1': 'xG_away'})

#Separate score into home and away
pl_df['home_score'] = pl_df['Score'].str[0]
pl_df['away_score'] = pl_df['Score'].str[2]

#Get rid of unneccessary columns
pl_df = pl_df.drop(['Match Report', 'Notes'], axis = 1)

#Convert to python datetime format
pl_df['Date'] = pd.to_datetime(pl_df['Date'])
pl_df.sort_values(by = 'Date', inplace = True)
pl_df = pl_df[['Wk','Day','Date', 'Time', 'Home', 'home_score', 'xG_home', 'away_score', 'xG_away', 'Away', 'Attendance', 'Venue', 'Referee']]

#Just pull necessary columns
pl_df = pl_df.dropna()
pl_df = pl_df[['Date','Home','home_score','xG_home','away_score','xG_away','Away']].reset_index(drop=True)

#Calculate mean home and away xG of the PL
league_mean_home_xG = round((pl_df['xG_home'].mean()),2)
league_mean_away_xG = round((pl_df['xG_away'].mean()),2)

#Sum home xG and create table
home_attacking_strength = pl_df.groupby('Home').agg({'xG_home': 'sum', 'Home':['count','first']})
home_attacking_strength.columns = ['xG_home', 'TotalGames', 'Home']

#Define home attack rating by diving total home xG by total games and by the league average home xG and add to data frame
home_attack_rating = (home_attacking_strength['xG_home'] / home_attacking_strength['TotalGames']) / league_mean_home_xG
home_attacking_strength.loc[:, "AttackingRating"] = home_attack_rating
home_attacking_strength = home_attacking_strength.reset_index(drop = True)
home_attacking_strength = pd.DataFrame(home_attacking_strength)
home_attacking_strength.sort_values('AttackingRating', ascending = False)

#Sum away xG and create table
away_attacking_strength = pl_df.groupby('Away').agg({'xG_away': 'sum', 'Away':['count','first']})
away_attacking_strength.columns = ['xG_away', 'TotalGames', 'Away']

#Define away attack rating by diving total away xG by total games and by the league average away xG and add to data frame
away_attack_rating = (away_attacking_strength['xG_away'] / away_attacking_strength['TotalGames']) / league_mean_away_xG
away_attacking_strength.loc[:, "AttackingRating"] = away_attack_rating
away_attacking_strength = away_attacking_strength.reset_index(drop = True)
away_attacking_strength = pd.DataFrame(away_attacking_strength)
away_attacking_strength.sort_values('AttackingRating', ascending = False)

#Sum home xG against and create table
home_defensive_strength = pl_df.groupby('Home').agg({'xG_away': 'sum', 'Home':['count','first']})
home_defensive_strength.columns = ['xG_conceded', 'TotalGames', 'Home']

#Calulating home defense ratings based off xG conceded
home_defense_rating = (home_defensive_strength['xG_conceded'] / home_defensive_strength['TotalGames']) / league_mean_away_xG
home_defensive_strength.loc[:, 'DefenseRating'] = home_defense_rating
home_defensive_strength = home_defensive_strength.reset_index(drop = True)
home_defensive_strength = pd.DataFrame(home_defensive_strength)
home_defensive_strength.sort_values('DefenseRating', ascending = True)

#Sum home xG against and create table
away_defensive_strength = pl_df.groupby('Away').agg({'xG_home': 'sum', 'Away':['count','first']})
away_defensive_strength.columns = ['xG_conceded', 'TotalGames', 'Away']

#Calulating home defense ratings based off xG conceded
away_defense_rating = (away_defensive_strength['xG_conceded'] / away_defensive_strength['TotalGames']) / league_mean_home_xG
away_defensive_strength.loc[:, 'DefenseRating'] = away_defense_rating
away_defensive_strength = away_defensive_strength.reset_index(drop = True)
away_defensive_strength = pd.DataFrame(away_defensive_strength)
away_defensive_strength.sort_values('DefenseRating', ascending = True)

#Overall team attack ratings
overall_attack_rating = (home_attack_rating + away_attack_rating)/2
overall_attack_rating.sort_values(ascending = False)

#Overall team defense ratings
overall_defense_rating = (home_defense_rating + away_defense_rating)/2 
overall_defense_rating.sort_values(ascending = True)

import numpy as np
from scipy.stats import poisson
import seaborn as sb

#Extract Liverpool's home attacking rating and City's away defence rating
lfc_home_attack_rating = home_attacking_strength[home_attacking_strength['Home'] == 'Liverpool']['AttackingRating']
lfc_home_attack_rating = float(lfc_home_attack_rating)
mcfc_away_defense_rating = away_defensive_strength[away_defensive_strength['Away'] == 'Manchester City']['DefenseRating']
mcfc_away_defense_rating = float(mcfc_away_defense_rating)
#Then extract City's away attacking rating and Liverpool's home defense rating
lfc_home_defense_rating = home_defensive_strength[home_defensive_strength['Home'] == 'Liverpool']['DefenseRating']
lfc_home_defense_rating = float(lfc_home_defense_rating)
mcfc_away_attack_rating = away_attacking_strength[away_attacking_strength['Away'] == 'Manchester City']['AttackingRating']
mcfc_away_attack_rating = float(mcfc_away_attack_rating)

#Calculate Liverpool's expected home xG and City's expected away xG based on the xG model
lfc_home_xG = (lfc_home_attack_rating * mcfc_away_defense_rating) * league_mean_home_xG
mcfc_away_xG = (mcfc_away_attack_rating * lfc_home_defense_rating) * league_mean_away_xG

home_xG = lfc_home_xG
away_xG = mcfc_away_xG

max_goals = 8
goals_range = np.arange(0, max_goals + 1)

#Use poisson distn with λ = 0 to calculate probabilities of 0 goals for each team
home_zero_pmf = poisson.pmf(0, home_xG)
away_zero_pmf = poisson.pmf(0, away_xG)

#Repeat but for  probabilities of non zero goals with λ = expected xG
home_nonzero_pmf = poisson.pmf(goals_range, home_xG)
away_nonzero_pmf = poisson.pmf(goals_range, away_xG)

#Combine probabilities
home_pmf = (1 - home_zero_pmf) * home_nonzero_pmf
away_pmf = (1 - away_zero_pmf) * away_nonzero_pmf

goals_prob_matrix = np.outer(home_pmf, away_pmf)

#Convert to square matrix
goals_prob_matrix = goals_prob_matrix.reshape(max_goals + 1, max_goals + 1)
#Normalise probabilites over truncated range
goals_prob_matrix /= goals_prob_matrix.sum()

fig, ax = plt.subplots(figsize=(12, 8))
sb.heatmap(goals_prob_matrix, cmap = "flare", annot = True, fmt = ".4f", square = True, xticklabels = goals_range, yticklabels = goals_range)

plt.xlabel("Away team goals")
plt.ylabel("Home team goals")
plt.title("Goals probability matrix")

plt.show()