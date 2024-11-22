# Fall 2024 Database Project - Tigers

**November 22, 2024**

**Team Members:** Jacob Celis, Jan Jasa, Kyle Thompson, Mark Josephs

# Project Description

This project makes use of dependencies listed in requirements.txt and uses Python 3.10 or higher. The Tigers Database is included which consists of a baseball database with updated stats from the 2023 MLB season data (available from the most recent Lahman baseball database website). Configuration details can be found in csi3335f2024.py to connect to the Tigers Database. The project can be executed using run.py, which will run the web application itself using Flask and generate the Tigers Database. This software allows users to create accounts, log-in, query the Tigers Database by providing a team and yearID (which will generate a roster), and play the glorious immaculate grid. The admin user can view requests made to the database and ban users from the web application at will and without supervision.

# Admin Access
The admin can ban a user and view team roster requests by logging into the admin dashboard. Here is the login details for the aforementioned admin user:

Username: admin<br>
Password: adminpass

# Steps to run Web Application
1) Ensure you run the project in your virual environment.
2) Run run.py in your virtual environment.<br>
Example -> python run.py
3) In the web browser, navigate to the URL that the web application is hosted on.<br>
Example -> Running on http://127.0.0.1:5000
4) For deactivation, go to terminal and press CTRL + C to terminate without mercy.

# Updates

Users and requests table have been added to the Tigers Database. The user table will contain the admin user by default when the web app is ran. The requests table keeps a log of team and yearID requests made to generate a team roster. These requests can be retrieved in the admin dashboard. The code to generate these addtional tables can be located within the DatabaseSetup.py file.

Many of the tables in the Tigers database have been updated to include the most recent 2023 MLB season data. Tigers.sql is included in the project for these updates.

# Extra Credit
