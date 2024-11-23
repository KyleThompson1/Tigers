

# 🐯 Fall 2024 Database Project - Tigers

**📅 November 22, 2024**  
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
- **`users` table**: Includes the default admin account upon the first run.  
- **`requests` table**: Logs all team and yearID queries for generating team rosters. Logs are accessible via the admin dashboard.  

### Updated Data:
- The Tigers Database has been updated with stats from the **2023 MLB season**.  
- `Tigers.sql` includes the schema and new data.

### Database Initialization:
- The setup code for these additional tables can be found in `DatabaseSetup.py`.

---

## 🌟 Extra Credit
Extra credit features are detailed below. 🎉  

---

### ✨ Thank you for using the Tigers Database!
