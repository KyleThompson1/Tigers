

# 🐯 Fall 2024 Database Project - Tigers

**📅 November 30, 2024**  
**👥 Team Members:** Jacob Celis, Jan Jasa, Kyle Thompson, Mark Josephs  

---

## 📖 Project Description

This project uses **Python 3.10 or higher** and the dependencies outlined in `requirements.txt`. It integrates the **Tigers Database**, a baseball database with updated stats from the **2023 MLB season** taken from the Lahman baseball database.

Key features:  
- **User Management**: Account creation and login functionality.  
- **Roster Queries**: Generate team rosters by specifying a team and yearID.  
- **Game Mode**: Play the **Immaculate Grid**.  
- **Admin Control**: Admin can review database requests and manage user access (including banning users).  

The configuration file `csi3335f2024.py` provides all details to connect to the Tigers Database. Use `run.py` to start the web application.

---

## 🔑 Admin Access

The admin dashboard enables:  
1. **Viewing Team Roster Requests** by users.  
2. **Banning Users** from the web application.  

**Default Admin Credentials:**  
- **Username:** `admin`  
- **Password:** `adminpass`  

---

## 🚀 How to Run the Web Application

Follow these steps to launch the application:  

1. **Activate your virtual environment**.  
2. Run `run.py` inside the virtual environment:  
   ```bash
   python run.py
3. Open your web browser and navigate to the hosted application URL:
   ```bash
   Running on http://127.0.0.1:5000
5. To stop the application, press `CTRL + C` in the terminal.  

---

## 🔄 Updates

### New Tables Added:
- **users table**: Includes the default admin account upon the first run.  
- **roster_requests table**: Logs all team and yearID queries for generating team rosters. Logs are accessible via the admin dashboard.  

### Updated Data:
- The Tigers Database has been updated with stats from the **2023 MLB season**.  
- `Tigers.sql` includes the schema and new data.

### Database Initialization:
- The setup code for these additional tables can be found in `DatabaseSetup.py`.

---

## 🌟 Extra Credit
- **Admin Unban**: The admin user can unban a user after they have been banned.
- **Admin View Total Requests**: Admin user can view the total number of roster requests from all users.
- **Admin View User Requests**: Admin user can view each user's individual roster requests with timestamps.
- **User Profile**: Users can view their profile page and see their full name, username, and request count.
- **User Profile Roster Requests**: Users can view their own roster requests in the form of a scroll down menu.
- **User Profile Pics**: Users can choose from 8 images for a profile picture to customize their Tiger DB experience.
  
---

### ✨ Thank you for using the Tigers Database!
