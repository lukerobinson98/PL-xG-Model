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

#Plotting team home attack and defense ratings
home_attacking_strength['path'] = 'Desktop/Python/PL-xG-Model/team-badges/' + home_attacking_strength['Home'] + '.png'
home_defensive_strength['path'] = 'Desktop/Python/PL-xG-Model/team-badges/' + home_defensive_strength['Home'] + '.png'

def getImage(path):
    return OffsetImage(plt.imread(path), zoom=.05, alpha=1)

# Set background colour
bgcol = '#fafafa'

# Create initial plot
fig, ax = plt.subplots(figsize=(9, 6), dpi=120)
fig.set_facecolor(bgcol)
ax.set_facecolor(bgcol)
ax.scatter(home_attacking_strength['AttackingRating'], home_defensive_strength['DefenseRating'], c=bgcol)

# Change plot spines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_color('#ccc8c8')
ax.spines['bottom'].set_color('#ccc8c8')

# Change ticks
plt.tick_params(axis='x', labelsize=12, color='#ccc8c8')
plt.tick_params(axis='y', labelsize=12, color='#ccc8c8')


for index, row in home_attacking_strength.iterrows():
    ab = AnnotationBbox(getImage(row['path']), (row['xG/90'], row['xGA/90']),
                        frameon=False)
    ax.add_artist(ab)
