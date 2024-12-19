import requests
import re

def PlayerCode():
    #take user inputs
    FirstName = input("Enter First Name")
    SurName = input("Enter Surname ")
    #save the names to be passed onto later functions for formatting
    names = []
    names.append(FirstName)
    names.append(SurName)
    #check strings aren't empty
    if FirstName and SurName:

    #URL to make request to
        url = "https://basketball-head.p.rapidapi.com/players/search"

        payload = {
                    "pageSize": 100,
                    "firstname": FirstName,
                    "lastname": SurName
                }#Search parameters 
        headers = {
                    "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
                    "x-rapidapi-host": "basketball-head.p.rapidapi.com",
                    "Content-Type": "application/json"
                }#my unique API identifyer 
        #make API request
        response = requests.post(url, json=payload, headers=headers)
        #return only if there is data on the entered player
        if response.json()['body']:
            names.append(response.json()['body'][0]["playerId"])
            return names
        else:
            #in case of an error(below two returns, return string of length 2 NOT 3
            return names
    return names




def Player_validate_season():
    #infinite loop to run until a valid input is entered letting the function return the value and terminate
    season_checker = True
    while season_checker:
        input_season = input("please enter the season you wish to search in the form xxxx and make sure its between 1947 and 2025")
        
        Format = r'^\d{4}$' # Regular expression to match "xxxx" format where x is a digit
        
        # Check if input matches the pattern
        if not re.match(Format, input_season):
            print("Invalid format. Please use 'xxxx'.")

        
        if input_season.isnumeric(): # check the input can be casted into an integer
            if 1947 <= int(input_season) <= 2025:# range Check if input_season is in a valid range
                return int(input_season)
            else:
                print("Invalid season range. Please enter a year between 1947 and 2025")
        else: 
            print("Please enter the only digits")
        #^error messages 


def GetPlayerGames():
    Game_List = []# initialise list of games
    #check if PlayerCode only returned the player names (len = 2) or the PlayerCode as well (len =3)
    names = PlayerCode()
    if len(names) == 3:
        season = int(Player_validate_season())
        url = "https://basketball-head.p.rapidapi.com/players/{}/games/{}".format(names[2],season)
        payload = { "pageSize": 100 }
        headers = {
            "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
            "x-rapidapi-host": "basketball-head.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if not 'body' in response.json(): 
            print("{} {} did not play in the {}/{} season".format(names[0], names[1], season-1,(season % 100)))
        else:
            Team_Code = TeamCode()
            for game in response.json()["body"]:
                if game["opponent"] == Team_Code:
                    Game_List.append(game)
            if Game_List == []:
                print("{} {} did not play any games against {} in {}".format(names[0], names[1], Team_Code, season))
            else:
                print(Game_List)
    #error message
    else:
        print("'{} {}' was not found in the database.".format(names[0], names[1]))
GetPlayerGames()
def PlayerInfo():
    #check if PlayerCode only returned the player names (len = 2) or the PlayerCode as well (len =3)
    names = PlayerCode()
    if len(names) == 3:
        #URL to request to
        url = "https://basketball-head.p.rapidapi.com/players/{}".format(names[2])

        headers = {
                "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
                "x-rapidapi-host": "basketball-head.p.rapidapi.com"
            }#API key

        response = requests.get(url, headers=headers)# make request to API

        print(response.json())#print returned dictionary
    else:
        #error message
        print("'{} {}' was not found in the database.".format(names[0], names[1]))


#####


def Team_validate_season():
    season_checker = True
    while season_checker:
        input_season = input("please enter the season you wish to search in the form xxxx-xxxx and make sure its between 1980-1981 and 2024-2025")
        # Regular expression to match "xxxx-xxxx" format where x is a digit
        Format = r'^\d{4}-\d{4}$'
        
        # Check if input matches the pattern
        if not re.match(Format, input_season):
            print("Invalid format. Please use 'xxxx-xxxx'.")
            

        # Split the input to extract both years
        years = input_season.split("-")
        print(years)
        # Check if the years are within the valid range and if end_year is start_year + 1
        if len(years) == 2 and years[0].isnumeric() and years[1].isnumeric():
            if 1980 <= int(years[0]) <= 2024 and int(years[0]) == int(years[1]) - 1:
                Season_Checker =  False
                print("loop broken")
                return input_season
            else:
                print("Invalid season range. The start year must be between 1980 and 2024, and the second year must be start_year + 1.")
        else: 
            print("please only enter digits 1-9 other than the hyphen to seperate the two years")

def TeamCode():
    url = "https://api.balldontlie.io/v1/teams"
    headers = {
              "Authorization": "ba6f4deb-cf5d-46b0-917f-033c616dfd50"
              }
    response = requests.get(url, headers=headers)
    while True:
        FullName = input("enter opposition team name").lower()
        if response.status_code == 200:
            for team in response.json()['data']:
                if team['full_name'].lower() == FullName:
                    print("{} was found and has the code {}".format(FullName, team['abbreviation']))
                    return team['abbreviation']
                
          
            print("Sorry, but the team '{}' could not be found.".format(FullName))
        else:
                # Print an error message if the request fails
                print("{} Error. Unable to connect to API (response generated by Toba)".format(response.status_code))
                print(response.text)



def TeamInfo(TeamCode):
    if TeamCode != "":
        url = "https://basketball-head.p.rapidapi.com/teams/{}/metadata/{}".format(TeamCode, Team_validate_season())

        headers = {
            "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
            "x-rapidapi-host": "basketball-head.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        print(response.json())
    else:
        print("Team: `{}` not found. Make sure the Team is spelled correctly and you have typed their FULL name. This program is NOT caps sensitive ".format(FullName))

def TeamRoster(TeamCode):
    if TeamCode != "":
        url = "https://basketball-head.p.rapidapi.com/teams/{}/roster/{}".format(TeamCode, Team_validate_season())

        headers = {
            "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
            "x-rapidapi-host": "basketball-head.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        print( response.json()["body"]["roster"])
    else:
        print("Team: `{}` not found. Make sure the Team is spelled correctly and you have typed their FULL name. This program is NOT caps sensitive ".format(FullName))

def TeamSched(TeamCode):
    if TeamCode != "":
        url = "https://basketball-head.p.rapidapi.com/teams/{}/schedule/{}".format(TeamCode, Team_validate_season())

        headers = {
            "x-rapidapi-key": "8305d69966mshea9ff44e213c030p193d6ajsndb41cebeea5a",
            "x-rapidapi-host": "basketball-head.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        print(response.json())
    else:
        print("Team: `{}` not found. Make sure the Team is spelled correctly and you have typed their FULL name. This program is NOT caps sensitive ".format(FullName))
