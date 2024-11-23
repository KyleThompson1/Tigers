# This file sets up the database
import pymysql
from werkzeug.security import generate_password_hash
from csi3335f2024 import mysql

def initialize_database():

    # Connect to the MariaDB server (without specifying a database initially)
    server_connection = pymysql.connect(
        host=mysql['host'],
        user=mysql['user'],
        password=mysql['password']
    )

    # Create a cursor object for the server connection
    server_cursor = server_connection.cursor()

    # SQL code to create the Tigers database if it does not exist
    create_database_sql = "CREATE DATABASE IF NOT EXISTS Tigers"

    # Execute the SQL code to create the database
    server_cursor.execute(create_database_sql)

    # Close the server connection cursor and connection
    server_cursor.close()
    server_connection.close()

    # Connect to the Tigers database
    db_connection = pymysql.connect(
        host=mysql['host'],
        user=mysql['user'],
        password=mysql['password'],
        database=mysql['database']  # Connect to the Tigers database
    )

    # Create a cursor object to execute SQL queries in the Tigers database
    cursor = db_connection.cursor()

    # SQL code for creating the users table with role (for admin or regular user)
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT(11) AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) DEFAULT NULL,
        last_name VARCHAR(50) DEFAULT NULL,
        banned TINYINT(1) DEFAULT 0 NOT NULL,
        role ENUM('regular user', 'admin') NOT NULL DEFAULT 'regular user'
    )
    """

    # Execute SQL code to create the users table
    cursor.execute(create_users_table_sql)

    # Hash the admin password using Scrypt (to maintain consistency with other users)
    admin_password = "adminpass"
    hashed_password = generate_password_hash(admin_password, method='scrypt')

    # Insert admin user if not exists
    insert_admin_user_sql = """
    INSERT INTO users (username, password, first_name, last_name, role)
    SELECT * FROM (SELECT %s AS username, %s AS password, NULL AS first_name, NULL AS last_name, 'admin' AS role) AS tmp
    WHERE NOT EXISTS (
        SELECT username FROM users WHERE username = 'admin'
    ) LIMIT 1;
    """

    cursor.execute(insert_admin_user_sql, ('admin', hashed_password))

    # Commit changes to the database
    db_connection.commit()

    # Close the cursor and database connection
    cursor.close()
    db_connection.close()

# Call the function to initialize the database
initialize_database()
