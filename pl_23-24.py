import pandas as pd
pd.set_option('display.max_rows',1000)

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

