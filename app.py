from flask import Flask, request, render_template, session, redirect
import sqlite3, math, requests
from nba_api.stats.endpoints import teamgamelog, boxscoreadvancedv3,leaguestandingsv3, leaderstiles,teamdetails, boxscoretraditionalv3, leaguegamefinder
import pandas as pd
from nba_api.stats.static import teams
import statistics
import matplotlib.pyplot as plt
import numpy as np
#define flask server

app = Flask(__name__)
app.secret_key = 'Test'




def TeamInfo(Team_Code, season):
        #URL to make request to
    url = "https://basketball-head.p.rapidapi.com/teams/{}/metadata/{}".format(Team_Code, season)

    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}#my unique API identifyer 
        
    response = requests.get(url, headers=headers)#make API request
    if 'body' in response.json():
        return response.json()["body"]#return data in the form of a dictionary
    return False


def TeamId(Team_Name):
    try: 
        #pull list of all teams and iterate through them
        for team in teams.get_teams():
                #when you find the team searched for, return its ID
                if Team_Name == team["full_name"]:
                    return(team["id"])
    except: # in case of API failure or (somehow) team isn't found
        return False


def GameId(Team_Name):
    try:
        # Fetch game log data for the team 
        team_sched = teamgamelog.TeamGameLog(team_id=TeamId(Team_Name), season="2024-25")  
        games_df = team_sched.get_data_frames() # convert to a list of tables
        if games_df[0].empty: # in case that no games have been played in the season specified 
            return False# in case that no games have been played in the season specified 
        return games_df[0].head()["Game_ID"].tolist() # return 5 most recent game ID's in a list
    except:# in case of API failure 
        return False


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


def ModelWinRate(TR):
#regression line for TR against win%
    return ((0.519/23)*TR) - (0.4/23)
    

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


def PercentageChange(num1, num2):
    return ((num1 - num2)/num2) * 100

###
def hash(password):
  #initialise value of "product" so that we can multiply the ascii values of each character in the passwordby it
  product = 1

  #go through each character in the password and multiply the ascii values of each character by eachother
  for password_counter in range(0,len(password)):

    #split is the ascii value of every character in the password
    split = ord(password[password_counter])
    product = product * split

  #add complexity by multiplying the product of all the asci values by he length of the origional password 
  product = product * len(password)
  #add more complexity by multiplying the lenght of this product by the product itself and raising them both to powers 
  product = (product)**2 * (len(str(product)))**3
  return int(math.sqrt(int(math.sqrt(product)*0.7))*0.034)


def PlayerInfo(Player_Code):
    #URL to request to
    url = "https://basketball-head.p.rapidapi.com/players/{}".format(Player_Code)

    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}#API key

    response = requests.get(url, headers=headers)# make request to API

    return response.json()["body"]#return dictionary 


def TeamCode(Team):
    url = "https://api.balldontlie.io/v1/teams" # URL to call to, returns all the teams
    headers = {"Authorization": "ba6f4deb-cf5d-46b0-917f-033c616dfd50"}
    response = requests.get(url, headers=headers)#make request

    if response.status_code == 200:#check if request was successful to avoid errors
        for team in response.json()['data']:#iterate through list of dictionaries. each dictionary is a team
            if team['full_name'].lower() == Team.lower():#compare entered team name to each team name in the list
                return team['abbreviation'] # return team code
    else:
                # return an error message if the request fails
                return ("Error")
    

def PlayerCode(FirstName,SurName):
    #URL to request to
    url = "https://basketball-head.p.rapidapi.com/players/search"

    payload = {
                "pageSize": 100,
                "firstname": FirstName,
                "lastname": SurName
            }#search parameters
    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com",
    "Content-Type": "application/json"
}#API key

    #make request to API
    response = requests.post(url, json=payload, headers=headers)
    if "body" in response.json():
    #check if the player entered exists
        if response.json()['body']:
            return response.json()['body'][0]["playerId"]#return player CODE
    
    return False


def TeamSched(Team_Code, season):
    #URL to request to 
    url = "https://basketball-head.p.rapidapi.com/teams/{}/schedule/{}".format(Team_Code, season)

    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}#API key
    # make request to API
    response = requests.get(url, headers=headers)
    if 'body' in response.json():
        if 'schedule' in response.json()["body"]:
            if response.json()['body']["schedule"]:
                return response.json()['body']#return list of teams games
    
    return False


def TeamRoster(Team_Code, season):
    #URL to request to 
    url = "https://basketball-head.p.rapidapi.com/teams/{}/roster/{}".format(Team_Code, season)

    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}#API key
    # make request to API
    response = requests.get(url, headers=headers)
    if 'body' in response.json():
        if 'roster' in response.json()["body"]:
            if response.json()['body']["roster"]:
                return response.json()['body']#return list of teams games
    
    return False


def PlayerAdvancedStats(PlayerCode):
    if PlayerCode:
        url = "https://basketball-head.p.rapidapi.com/players/{}/stats/Advanced".format()

        querystring = {"seasonType":"Regular"}

        headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}

        response = requests.get(url, headers=headers, params=querystring)

        return response.json()["body"]
    else: 
        return False


def CareerStats(Player_Code,Type, period, Stat_Type):
    #ur to request to. user can choose the player and the period of the stats
    url = "https://basketball-head.p.rapidapi.com/players/{}/stats/{}".format(Player_Code,Stat_Type)
    querystring = {"seasonType": Type,
               "seasonId":period }# search parameters. 
    headers = {
	"x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
	"x-rapidapi-host": "basketball-head.p.rapidapi.com"
}#API key

    response = requests.get(url, headers=headers, params=querystring)#make request to API

    return response.json()["body"]#return list of stats

@app.route("/register")
def Sign_Up():
    Fname = request.args.get('ForeName')
    Sname = request.args.get('SurName')
    email = request.args.get('email')
    age = request.args.get('age')
    username = request.args.get('username')
    password = request.args.get('password')
    Team = request.args.get('Team')
    try: 
        Team_Code = TeamCode(Team)
        if Team_Code != "Error":
        #connect to database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            #insert the entered details into the database
            cursor.execute('''
                INSERT INTO users (Username, Password, Fname, Surname, Email, Age, Code, Team )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, hash(password), Fname, Sname, email, age, Team_Code, Team))
            #save these changes and close the connection to the database
            conn.commit()
            conn.close()
            session['username'] = username
            session['Team_Code'] = Team_Code
            session["Team"] = Team
            return redirect('http://127.0.0.1:5000/index')
        else:
            return """
                <!DOCTYPE html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body>
                        <h1>Connection Error</h1>
                    <p>Server side error connecting to the API. Please try to sign up again</p>
                    <a href="http://127.0.0.1:5500/templates/Users/register.html">Return to Sign Up</a><br><br>
                    <p>Already have an account?</p>
                    <a href="http://127.0.0.1:5500/templates/Users/login.html">Log In</a>
                </body>
                </html>
                """

    except:
            #in cases where an error occurs (this would have to be because the userame isn't unique and the username is the primary key) this HTML displays an eror message and a link back to the form 
        return """
                <!DOCTYPE html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body>
                        <h1>Username Already taken</h1>
                    <p>Please select a new username</p>
                    <a href="http://127.0.0.1:5500/templates/Users/register.html">Return to Sign Up</a><br><br>
                    <p>Already have an account?</p>
                    <a href="http://127.0.0.1:5500/templates/Users/login.html">Log In</a>
                </body>
                </html>
                """


@app.route('/login')
def logging():
    #pull forms from front end
    username = request.args.get('username')
    password = request.args.get('password')
    #connect to and pull everything out of the users table
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    #iterate through users checking entered details against database
    for user in users:
        if username == user[0]:
            if user[1] == str(hash(password)):
                #add the team name, code and username to session
                session["Team_Code"] = user[6]
                session["Team"] = user[7]
                session["username"] = username
                #take user to home screne
                return redirect('/index')
            else: 
                response_html = f"""
                <!DOCTYPE html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body>
                        <h1>Unsuccesful Login</h1>
                    <p>Incorrect Password. Please Check and Try again</p>
                    <a href="http://127.0.0.1:5500/templates/Users/login.html">Return to Log In</a>
                </body>
                </html>
                """
                return response_html
    response_html = f"""
                <!DOCTYPE html>
                <head>
                    <meta charset="UTF-8">
                </head>
                <body>
                        <h1>Unsuccesful Login</h1>
                    <p>Username not found. Please Check and Try again</p>
                    <a href="http://127.0.0.1:5500/templates/Users/login.html">Return to Log In </a><<br><br>
                    <a href="http://127.0.0.1:5500/templates/Users/register.html">Sign Up</a>
                </body>
                </html>
                """
    return response_html
          

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user from session
    #return user to login page
    return redirect("http://127.0.0.1:5500/templates/Users/login.html")


@app.route('/index')
def home():
    username = session.get('username')
    if username:
        #pull rest of details from session
        Team_Code = session.get('Team_Code')
        Team = session.get("Team")
        #find the schedule of users fav team
        Sched=TeamSched(Team_Code,"2024-2025")["schedule"]
        if Sched:
        #iterte through every game in that schedule
            for game in Sched:
                if game["teamPoints"] == "":
                    #find the game that hasn't been played yet, and return the one before that
                    return render_template("index.html", username=username,Game=Sched[int(game["gameOrder"])-2], Team=Team, Standing=leaguestandingsv3.LeagueStandingsV3().get_data_frames()[0][["TeamName", "Record", "Conference","L10"]].to_html())
                #return final game of season if season completed
            return render_template("index.html", username=username,Sched=Sched[81], Standing=leaguestandingsv3.LeagueStandingsV3().get_data_frames()[0][["TeamName", "Record", "Conference","L10"]].to_html())
        return render_template("index.html",Flag=True, username=username,Sched="Currently Having Porblems Connecting to the API", Standing=leaguestandingsv3.LeagueStandingsV3().get_data_frames()[0][["TeamName", "Record", "Conference","L10"]].to_html())
    else:
        return redirect("http://127.0.0.1:5500/templates/Users/login.html")
    

@app.route("/predictor")
def predictor():
    #pull inputs from form
    Team1 = request.args.get('Team1')
    Team2 = request.args.get('Team2')
    #don't proceed until user sends form and that they don't enter the same team twice
    if (Team1 and Team2) and (Team1 != Team2):
        #find last 5 game ID's
        games1 = GameId(Team1)
        games2 = GameId(Team2)
        if games1 and games2:
            #find box scores for those 5 games
            stats1 = AdvancedBoxScore(games1)
            stats2 = AdvancedBoxScore(games2)
            if stats1 and stats2:
                #calc TR
                TR1 = CalcTR(stats1,TeamId(Team1))
                TR2 = CalcTR(stats2,TeamId(Team2))
                Change = PercentageChange(ModelWinRate(TR1), ModelWinRate(TR2))
                #if successful, pass both TR's and team names
                return render_template("predictor.html",Change=Change, TR1=TR1,TR2=TR2, Team1=Team1, Team2=Team2)
        return render_template("predictor.html", TR1="Error",TR2="Error", Team1=Team1, Team2=Team2)
    #initialialise variables so the code displays Predictor.html
    return render_template("predictor.html", Tr1=None,Tr2=None, Team1=None, Team2=None)


@app.route("/PlayerSearch")
def PlayerSearch():
    #pull forms from frontend
    Fname = request.args.get('Fname') 
    Surname = request.args.get('Surname')
    Type = request.args.get('Type')
    Period = request.args.get('Period')
    Stat_Type = request.args.get('Stat_Type') 
    #only start  process once forms submitted
    if Fname and Surname:
        #find code for submitted player
        Player_code = PlayerCode(Fname, Surname)
        if Player_code:
            #pass the code and other inputs into stat function if player exists
            Box_Score=CareerStats(Player_code, Type, Period, Stat_Type)
            if Box_Score:
                #if the paramaters are valid, pass the result
                return render_template("Searches/PlayerSearch.html",Info = PlayerInfo(Player_code), Box_Score=Box_Score, Error=False)
            else:
                #error message for if player exists but invalid parameters (e.g. player didn't play in the entered year)
                return render_template("Searches/PlayerSearch.html",Info = PlayerInfo(Player_code), Box_Score=False, Error="'{} {}' was in our database but your other parameters were invalid.".format(Fname, Surname))

        else:
            ##error message for invalid player name
            return render_template("Searches/PlayerSearch.html", Info = False, Box_Score=False,  Error="'{} {}' could not be found. Please try searching a new player.".format(Fname, Surname))
    else:
        #initialialise Box_Score so the code displays PlayerSearch.html
        return render_template("Searches/PlayerSearch.html", Box_Score=None)
    

@app.route("/Compare")
def Compare():
    #player 1 parameters from form
    Fname1 = request.args.get('Fname1') 
    Surname1 = request.args.get('Surname1')
    Period1 = request.args.get('Period1')
    #Player 2 Parameters from form
    Fname2 = request.args.get('Fname2') 
    Surname2 = request.args.get('Surname2')
    Period2 = request.args.get('Period2')
    #parameters for bothfrom form
    Type = request.args.get('Type')
    Stat_Type = request.args.get('Stat_Type') 
    #only start  process once forms submitted
    if Fname1 and Fname1:
        #find codes for submitted players
        Player_code1 = PlayerCode(Fname1, Surname1)
        Player_code2 = PlayerCode(Fname2, Surname2)
        #check if both players exist
        if Player_code1 and Player_code2:
            #pass parameters into stat function
            Box_Score1=CareerStats(Player_code1, Type, Period1, Stat_Type)
            Box_Score2=CareerStats(Player_code2, Type, Period2, Stat_Type)
            #check if both passes returned a valid response
            if Box_Score1 and Box_Score2:
                #eror message: return both box scores
                return render_template("Searches/Compare.html", Box_Score1=Box_Score1, Box_Score2=Box_Score2, Player1=(Fname1+Surname1),Player2=(Fname2+Surname2))
            else:
                #error message: at least 1 of the parameters was invalid
                return render_template("Searches/Compare.html", error="Both '{} {}' and '{} {}' were in our database but your other parameters were invalid.".format(Fname1, Surname1, Fname2, Surname2))

        else: #error message: at least one of the players doesn't exist
            return render_template("Searches/Compare.html", erorr="Either '{} {}' or '{} {}' could not be found. Please try again.".format(Fname1, Surname1, Fname2, Surname2))
    else:
        #initialialise Box_Score so the code displays Compare.html
        return render_template("Searches/Compare.html", error=None)   


@app.route("/leader")
def Leader():
    Stat = request.args.get('Stat') 
    Subject = request.args.get('Subject')
    Period = request.args.get('Period')
    Game_Type= request.args.get('Game_Type')
    if Stat:
        #pull table from API
        df = leaderstiles.LeadersTiles(season_type_playoffs=Game_Type, season=Period, player_or_team=Subject, stat=Stat).get_data_frames()[0]
        if df.empty:
            return render_template("leaders.html",Table="Search yielded no results, Please try again")
        # Define the expected column headers
        else:
            expected_columns = ["RANK", Subject.upper(), "TEAM_NAME", Stat]
            # Check if all expected columns are present in the DataFrame
            if all(column in df.columns for column in expected_columns):
                return render_template("leaders.html",Table=leaderstiles.LeadersTiles(season_type_playoffs=Game_Type, season=Period, player_or_team=Subject,stat=Stat).get_data_frames()[0][["RANK",Subject.upper(),"TEAM_NAME",Stat]].to_html())
            else:
                return render_template("leaders.html",Table=df.to_html())
    return render_template("leaders.html", Table=None)


@app.route("/TeamSearch")
def TeamSearch():
    Team = request.args.get('Team')
    Type = request.args.get('Type')
    Season = request.args.get('Season')
    function_list = [TeamInfo, TeamRoster, TeamSched]
    if Team :
        result = function_list[int(Type)](TeamCode(Team),Season)
        if result:
            return render_template("Searches/TeamSearch.html", Table=result, error=None)
        else:
            return render_template("Searches/TeamSearch.html", Table=None, error="error retrieving data")
    return render_template("Searches/TeamSearch.html", Table=None, error=None)
    

@app.route("/GameSearch")
def GameSearch():
    team = request.args.get('Name')
    opponent = request.args.get('Opp')
    if (team and opponent) and (team != opponent):
        ID=leaguegamefinder.LeagueGameFinder(player_or_team_abbreviation="T",team_id_nullable=TeamId(team), vs_team_id_nullable=TeamId(opponent) ).get_data_frames()[0].head(1)["GAME_ID"].values[0]
        Box_Score1 = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=ID).get_data_frames()[0][["teamName","nameI","minutes",
            "fieldGoalsMade",
            "fieldGoalsAttempted",
            "threePointersMade",
            "threePointersAttempted",
            "freeThrowsMade",
            "freeThrowsAttempted",
            "reboundsTotal",
            "assists",
            "steals",
            "blocks", 
            "turnovers",
            "points",  ]].to_html()
        Box_score2 = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=ID).get_data_frames()[2][["teamName", "fieldGoalsMade", "fieldGoalsAttempted","points" ]].to_html()
        return render_template("Searches/GameSearch.html", Table1=Box_Score1, Table2=Box_score2)
    return render_template("Searches/GameSearch.html", Table1=None, Table2=None)











if __name__ == '__main__':
    app.run(debug=True)


