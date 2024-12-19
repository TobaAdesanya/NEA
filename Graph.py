from nba_api.stats.endpoints import teamgamelog, boxscoreadvancedv3
import pandas as pd
from nba_api.stats.static import teams
import statistics
import matplotlib.pyplot as plt
import numpy as np


def GameId(Team_Name):
    try:
        # Fetch game log data for the team 
        team_sched = teamgamelog.TeamGameLog(team_id=Team_Name, season="2024-25")  

        games_df = team_sched.get_data_frames() # convert to a list of tables
        if games_df[0].empty: # in case that no games have been played in the season specified
            print("No data available for this team or season.")
            return(False)
        # in case that no games have been played in the season specified 
        
        return games_df[0]["Game_ID"].tolist(), games_df[0]["WL"].tolist()# return all game ID's in a list

    except Exception as e:
        print(f"An error occurred: {e}")
        return "cannot be found"# in case of API failure
def AdvancedBoxScore(Games):
    try:
        #initalise list for boxscores
        Box_Scores = []
        for id in Games: #iterate through all the game ID's
            #add the box score to the list and return it
            Box_Scores.append(boxscoreadvancedv3.BoxScoreAdvancedV3(id).get_data_frames()[1])
        return Box_Scores
    except:#in case of API erorr
        return False
def CalcTR(Boxscores, id):
    Stats = []#Initialise list of stats
    for boxscore in Boxscores:#loop through each box score
        team_row = boxscore[boxscore['teamId'] == id]  # Filter for the row containing the specified team
        #add the NRtg, TS%, TOV% and DRB% to the list
        Stats.extend([team_row["netRating"].values[0], team_row["trueShootingPercentage"].values[0],team_row["estimatedTeamTurnoverPercentage"].values[0],team_row["defensiveReboundPercentage"].values[0]])
    NRtg = statistics.mean(Stats[::4])
    TS = statistics.mean(Stats[1::4])
    TOV = statistics.mean(Stats[2::4])
    DRB= statistics.mean(Stats[3::4])#calculate average value for each stat using index slicing 
    TR = ((NRtg + 20)*0.922) + (20*TS*0.499) - (20*TOV*0.168/100) + (20*DRB*0.170)#calc team rating
    return TR

def CalcTR(Boxscores, team):
    Stats = []
    for boxscore in Boxscores:
        team_row = boxscore[boxscore['teamId'] == team["id"]]  # Filter for the specific team
        Stats.extend([team_row["netRating"].values[0], team_row["trueShootingPercentage"].values[0],team_row["estimatedTeamTurnoverPercentage"].values[0],team_row["defensiveReboundPercentage"].values[0]])
    NRtg = statistics.mean(Stats[::4])
    TS = statistics.mean(Stats[1::4])
    TOV = statistics.mean(Stats[2::4])
    DRB= statistics.mean(Stats[3::4])
    TR = ((NRtg + 20)*0.922) + (20*TS*0.499) - (20*TOV*0.168/100) + (20*DRB*0.170)
    return TR

#lists showing what TR corresponds to win tally
TR = []
Win = []
#loop through all 30 teams
for team in teams.get_teams():
    #takes a long time so print to show how far in you are
    print("found",team["full_name"])
    #find 5 most recent game' ID's
    games = GameId(team["id"])
    wins = 0
    #sum and pass number of wins
    for result in games[1]:
        if result  == "W":
            wins = wins + 1
    Win.append(wins)
    #find advanced box scores
    Boxscores = AdvancedBoxScore(games[0])
    #add TR to list
    TR.append(CalcTR(Boxscores, team["id"]))


print(TR)
print(Win) 

#plot points, not 
plt.scatter(TR, Win)

# Adding labels and title
plt.xlabel("Team Rating")
plt.ylabel("Wins")
plt.title("Team Rating x Wins across season games")


# Show the graph
plt.show()
