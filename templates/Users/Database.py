import os
import sqlite3
db_path = 'users.db'
if os.path.exists(db_path):
    print("Database exists")
else:
    #connect to database
  conn = sqlite3.connect('users.db')
  
  # Create a cursor objject to interact with the database
  cursor = conn.cursor()
  
  #create table with the following columns 
  cursor.execute(''' 
  CREATE TABLE IF NOT EXISTS users (
      Username TEXT PRIMARY KEY NOT NULL,
      Password TEXT NOT NULL,
      Fname TEXT NOT NULL,
      Surname TEXT NOT NULL,
      Email TEXT NOT NULL,
      Age INTEGER NOT NULL,
      Code TEXT NOT NULL,           
      Team TEXT NOT NULL
  ) 
  ''')
  
  # save the changes 
  conn.commit()
  print("Database Created, called 'users.db'")
    
