

# 🐯 Fall 2024 Project - Tigers Database

**📅 December 8, 2024**  
**👥 Team Members:** Jacob Celis, Jan Jasa, Kyle Thompson, Mark Josephs  

---

## 📖 Project Description

This project uses **Python 3.10 or higher** and dependencies listed in `requirements.txt`. It integrates the **Tigers Database**, a baseball database with updated stats from the **2023 MLB season** taken from the Lahman baseball database.

Key features:  
- **User Support**: Account creation and login/logout functionality.  
- **Roster Requests**: Generate a baseball team roster by specifying a team and year.  
- **Game Mode**: Play the **Immaculate Grid**.  
- **Admin Management**: Admin can view team roster requests and manage user access.  

The configuration file `csi3335f2024.py` provides information to connect to the Tigers Database. Use `run.py` to start the web application.

---

## 🔑 Admin Access

The admin dashboard enables:  
1. **Viewing Team Roster Requests**: Both the total request count and individual user requests.
2. **Banning and Unbanning Users** from accessing the Tigers Database.

**Admin Login Information:**  
- **Username:** `admin`  
- **Password:** `adminpass`  

---

## 🔄 Updating Tiger database with 2023 Lahman stats

Follow these steps to update the Tiger DB with 2023 stats:  

1. **Ensure baseball.sql is included in project**.  
2. **Create Tiger database in MariaDB**
   ```bash
   CREATE DATABASE TIGERS;
3. **Dump baseball.sql into Tigers database**<br>
   Navigate to where baseball.sql file is located and enter in terminal:
   ```bash
   mysql -u root -p tigers < baseball.sql;
5. **Run LahmanData.py**<br>
   Navigate to where LahmanData.py is located and run in terminal:
   ```bash
   python LahmanData.py
6. Tigers database will now include 2023 stats.

---

## 🚀 Running the Web Application

Follow these steps to launch the application:  

Before running project!<br>
Extract Tigers.sql from zip folder and include into the project
Web application will not run properly unless this is done.

1. **May need to install modules in terminal:**.
   ```bash
   pip install pymysql
   pip install werkzeug
   pip install flask
2. Navigate to where run.py is located and run `run.py` inside the terminal:  
   ```bash
   python run.py
3. Will need to wait 20-30 seconds for Tigers.sql to dump into database.
4. Click on link `Running on http://127.0.0.1:5000` in terminal or open your web browser and enter the hosted application URL:
   ```bash
   http://127.0.0.1:5000
5. To stop the application, press `CTRL + C` in the terminal.  

---

## 🔄 Updates

### New Tables Added:
- **users table**: Includes admin account upon the first run and stores all users for accessing the web app. 
- **roster_requests table**: Logs all team and year queries for generating team rosters. Requests are accessible via the admin dashboard.  

### Updated Data:
- The Tigers Database has been updated with stats from the **2023 MLB season**.  
- `Tigers.sql` includes the schema and new data.

### Database Initialization:
- The setup code for these additional tables can be found in `DatabaseSetup.py` (users and roster_requests).

---

## 🌟 Extra Credit
- **Admin Unban**: The admin user can unban a user after they have been banned.
- **Admin View Total Requests**: Admin user can view the total number of roster requests from all users.
- **Admin View User Requests**: Admin user can view each user's individual roster requests with timestamps.
- **User Profile**: Users can view their profile page and see their full name, username, and request count.
- **User Profile Roster Requests**: Users can view their own roster requests in the form of a scroll down menu.
- **User Profile Pics**: Users can choose from 8 images for a profile picture to customize their Tiger DB experience.
- **Player Search**: Users can search for a specific player, and see their stats throughout their career.
  
---

### ✨ Thank you for using the Tigers Database!
