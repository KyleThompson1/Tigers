import csv
import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='password', # Change to (Your password to MariaDB)
        database='Tigers'
    )

# ------------------------------- People Table -------------------------------
def update_people_stats():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'people' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/People.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'people' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings with None (to represent NULL in MySQL)
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'nan':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO people (
                            playerID, birthYear, birthMonth, birthDay, birthCity, birthCountry, 
                            birthState, deathYear, deathMonth, deathDay, deathCountry, deathState, 
                            deathCity, nameFirst, nameLast, nameGiven, weight, height, bats, 
                            throws, debutDate, finalGameDate
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) 
                        ON DUPLICATE KEY UPDATE
                            birthMonth = VALUES(birthMonth),
                            birthDay = VALUES(birthDay),
                            birthCity = VALUES(birthCity),
                            birthCountry = VALUES(birthCountry),
                            birthState = VALUES(birthState),
                            deathYear = VALUES(deathYear),
                            deathMonth = VALUES(deathMonth),
                            deathDay = VALUES(deathDay),
                            deathCountry = VALUES(deathCountry),
                            deathState = VALUES(deathState),
                            deathCity = VALUES(deathCity),
                            nameFirst = VALUES(nameFirst),
                            nameLast = VALUES(nameLast),
                            nameGiven = VALUES(nameGiven),
                            weight = VALUES(weight),
                            height = VALUES(height),
                            bats = VALUES(bats),
                            throws = VALUES(throws),
                            debutDate = VALUES(debutDate),
                            finalGameDate = VALUES(finalGameDate)
                    """, (
                        row['playerID'], row['birthYear'], row['birthMonth'], row['birthDay'], row['birthCity'], row['birthCountry'],
                        row['birthState'], row['deathYear'], row['deathMonth'], row['deathDay'], row['deathCountry'], row['deathState'],
                        row['deathCity'], row['nameFirst'], row['nameLast'], row['nameGiven'], row['weight'], row['height'],
                        row['bats'], row['throws'], row['debutDate'], row['finalGameDate']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'people' table.")

    except Exception as e:
        print(f"An error occurred while updating 'people' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'people' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Batting Table -------------------------------
def update_batting_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'batting' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Batting.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'batting' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO batting (
                            playerID, yearId, stint, teamID, b_G, b_AB, b_R, b_H, b_2B, b_3B, b_HR, 
                            b_RBI, b_SB, b_CS, b_BB, b_SO, b_IBB, b_HBP, b_SH, b_SF, b_GIDP
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            b_G = VALUES(b_G),
                            b_AB = VALUES(b_AB),
                            b_R = VALUES(b_R),
                            b_H = VALUES(b_H),
                            b_2B = VALUES(b_2B),
                            b_3B = VALUES(b_3B),
                            b_HR = VALUES(b_HR),
                            b_RBI = VALUES(b_RBI),
                            b_SB = VALUES(b_SB),
                            b_CS = VALUES(b_CS),
                            b_BB = VALUES(b_BB),
                            b_SO = VALUES(b_SO),
                            b_IBB = VALUES(b_IBB),
                            b_HBP = VALUES(b_HBP),
                            b_SH = VALUES(b_SH),
                            b_SF = VALUES(b_SF),
                            b_GIDP = VALUES(b_GIDP)
                    """, (
                        row['playerID'], row['yearID'], row['stint'], row['teamID'], row['b_G'], row['b_AB'],
                        row['b_R'], row['b_H'], row['b_2B'], row['b_3B'], row['b_HR'], row['b_RBI'], row['b_SB'],
                        row['b_CS'], row['b_BB'], row['b_SO'], row['b_IBB'], row['b_HBP'], row['b_SH'],
                        row['b_SF'], row['b_GIDP']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'batting' table.")

    except Exception as e:
        print(f"An error occurred while updating 'batting' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'batting' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")

def update_awards_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'awards' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/AwardsPlayers.csv', 'r', encoding='latin1') as csvfile1, \
                open('Lahman CSVs/AwardsManagers.csv', 'r', encoding='latin1') as csvfile2:

            reader1 = csv.DictReader(csvfile1)
            reader2 = csv.DictReader(csvfile2)

            # Combine both readers into one iterable
            all_rows = list(reader1) + list(reader2)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'awards' table.")

            for row in all_rows:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings with None (to represent NULL in MySQL)
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'nan':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO awards (
                            awardID, yearID, playerID, lgID, tie, notes
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            tie = VALUES(tie),
                            notes = VALUES(notes)
                    """, (
                        row['awardID'], row['yearID'], row['playerID'],
                        row['lgID'], row['tie'], row['notes']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting row: {row} - {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'awards' table.")

    except Exception as e:
        print(f"An error occurred while updating 'awards' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'awards' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")

def update_awardsshare_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'awardsshare' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/AwardsSharePlayers.csv', 'r', encoding='latin1') as csvfile1, \
                open('Lahman CSVs/AwardsShareManagers.csv', 'r', encoding='latin1') as csvfile2:

            reader1 = csv.DictReader(csvfile1)
            reader2 = csv.DictReader(csvfile2)

            # Combine both readers into one iterable
            all_rows = list(reader1) + list(reader2)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'awardsshare' table.")

            for row in all_rows:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings with None (to represent NULL in MySQL)
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'nan':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO awardsshare (
                            awardID, yearID, playerID, lgID, pointsWon, pointsMax, votesFirst
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            pointsWon = VALUES(pointsWon),
                            pointsMax = VALUES(pointsMax),
                            votesFirst = VALUES(votesFirst)
                    """, (
                        row['awardID'], row['yearID'], row['playerID'], row['lgID'],
                        row['pointsWon'], row['pointsMax'], row['votesFirst']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting row: {row} - {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'awardsshare' table.")

    except Exception as e:
        print(f"An error occurred while updating 'awardsshare' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'awardsshare' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Allstarfull Table -------------------------------
def update_allstarfull_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'allstarfull' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/AllStarFull.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'allstarfull' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO allstarfull (
                            playerID, yearID, gameID, teamID, lgID, GP, startingPos
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            gameID = VALUES(gameID),
                            teamID = VALUES(teamID),
                            lgID = VALUES(lgID),
                            GP = VALUES(GP),
                            startingPos = VALUES(startingPos)
                    """, (
                        row['playerID'], row['yearID'], row['gameID'], row['teamID'], row['lgID'], row['GP'], row['startingPos']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'allstarfull' table.")

    except Exception as e:
        print(f"An error occurred while updating 'allstarfull' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'allstarfull' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Appearances Table -------------------------------
def update_appearances_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'appearances' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Appearances.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'appearances' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO appearances (
                            playerID, yearID, teamID, G_all, GS, G_batting, G_defense, G_p,
                            G_c, G_1b, G_2b, G_3b, G_ss, G_lf, G_cf, G_rf, G_of, G_dh, G_ph, G_pr
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            G_all = VALUES(G_all),
                            GS = VALUES(GS),
                            G_batting = VALUES(G_batting),
                            G_defense = VALUES(G_defense),
                            G_p = VALUES(G_p),
                            G_c = VALUES(G_c),
                            G_1b = VALUES(G_1b),
                            G_2b = VALUES(G_2b),
                            G_3b = VALUES(G_3b),
                            G_ss = VALUES(G_ss),
                            G_lf = VALUES(G_lf),
                            G_cf = VALUES(G_cf),
                            G_rf = VALUES(G_rf),
                            G_of = VALUES(G_of),
                            G_dh = VALUES(G_dh),
                            G_ph = VALUES(G_ph),
                            G_pr = VALUES(G_pr)
                    """, (
                        row['playerID'], row['yearID'], row['teamID'], row['G_all'], row['GS'], row['G_batting'],
                        row['G_defense'], row['G_p'], row['G_c'], row['G_1b'], row['G_2b'], row['G_3b'], row['G_ss'],
                        row['G_lf'], row['G_cf'], row['G_rf'], row['G_of'], row['G_dh'], row['G_ph'], row['G_pr']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'appearances' table.")

    except Exception as e:
        print(f"An error occurred while updating 'appearances' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'appearances' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")

# ------------------------------- Battingpost Table -------------------------------
def update_battingpost_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'battingpost' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/BattingPost.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'battingpost' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO battingpost (
                            playerID, yearID, teamID, round, b_G, b_AB, b_R, b_H, b_2B, b_3B, 
                            b_HR, b_RBI, b_SB, b_CS, b_BB, b_SO, b_IBB, b_HBP, b_SH, b_SF, b_GIDP
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            b_G = VALUES(b_G),
                            b_AB = VALUES(b_AB),
                            b_R = VALUES(b_R),
                            b_H = VALUES(b_H),
                            b_2B = VALUES(b_2B),
                            b_3B = VALUES(b_3B),
                            b_HR = VALUES(b_HR),
                            b_RBI = VALUES(b_RBI),
                            b_SB = VALUES(b_SB),
                            b_CS = VALUES(b_CS),
                            b_BB = VALUES(b_BB),
                            b_SO = VALUES(b_SO),
                            b_IBB = VALUES(b_IBB),
                            b_HBP = VALUES(b_HBP),
                            b_SH = VALUES(b_SH),
                            b_SF = VALUES(b_SF),
                            b_GIDP = VALUES(b_GIDP)
                    """, (
                        row['playerID'], row['yearID'], row['teamID'], row['round'], row['b_G'], row['b_AB'], row['b_R'],
                        row['b_H'], row['b_2B'], row['b_3B'], row['b_HR'], row['b_RBI'], row['b_SB'], row['b_CS'],
                        row['b_BB'], row['b_SO'], row['b_IBB'], row['b_HBP'], row['b_SH'], row['b_SF'], row['b_GIDP']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'battingpost' table.")

    except Exception as e:
        print(f"An error occurred while updating 'battingpost' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'battingpost' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")

# ------------------------------- Collegeplaying Table -------------------------------
def update_collegeplaying_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'collegeplaying' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/CollegePlaying.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'collegeplaying' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO collegeplaying (
                            playerID, schoolID, yearID
                        ) VALUES (
                            %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            schoolID = VALUES(schoolID),
                            yearID = VALUES(yearID)
                    """, (
                        row['playerID'], row['schoolID'], row['yearID']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} with schoolID {row['schoolID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'collegeplaying' table.")

    except Exception as e:
        print(f"An error occurred while updating 'collegeplaying' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'collegeplaying' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Fielding Table -------------------------------
def update_fielding_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'fielding' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Fielding.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'fielding' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif key == 'f_ZR':  # Handle double values for f_ZR
                        row[key] = float(value) if value else None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO fielding (
                            playerID, yearID, stint, teamID, position, f_G, f_GS, f_InnOuts, f_PO, f_A, f_E, f_DP,
                            f_PB, f_WP, f_SB, f_CS, f_ZR
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            f_G = VALUES(f_G),
                            f_GS = VALUES(f_GS),
                            f_InnOuts = VALUES(f_InnOuts),
                            f_PO = VALUES(f_PO),
                            f_A = VALUES(f_A),
                            f_E = VALUES(f_E),
                            f_DP = VALUES(f_DP),
                            f_PB = VALUES(f_PB),
                            f_WP = VALUES(f_WP),
                            f_SB = VALUES(f_SB),
                            f_CS = VALUES(f_CS),
                            f_ZR = VALUES(f_ZR)
                    """, (
                        row['playerID'], row['yearID'], row['stint'], row['teamID'], row['position'], row['f_G'],
                        row['f_GS'], row['f_InnOuts'], row['f_PO'], row['f_A'], row['f_E'], row['f_DP'], row['f_PB'],
                        row['f_WP'], row['f_SB'], row['f_CS'], row['f_ZR']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'fielding' table.")

    except Exception as e:
        print(f"An error occurred while updating 'fielding' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'fielding' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- FieldingPost Table -------------------------------
def update_fieldingpost_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'fieldingpost' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/FieldingPost.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'fieldingpost' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO fieldingpost (
                            playerID, yearID, teamID, round, position, f_G, f_GS, f_InnOuts, f_PO, f_A, f_E, f_DP,
                            f_TP, f_PB
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            f_G = VALUES(f_G),
                            f_GS = VALUES(f_GS),
                            f_InnOuts = VALUES(f_InnOuts),
                            f_PO = VALUES(f_PO),
                            f_A = VALUES(f_A),
                            f_E = VALUES(f_E),
                            f_DP = VALUES(f_DP),
                            f_TP = VALUES(f_TP),
                            f_PB = VALUES(f_PB)
                    """, (
                        row['playerID'], row['yearID'], row['teamID'], row['round'], row['position'], row['f_G'],
                        row['f_GS'], row['f_InnOuts'], row['f_PO'], row['f_A'], row['f_E'], row['f_DP'], row['f_TP'],
                        row['f_PB']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'fieldingpost' table.")

    except Exception as e:
        print(f"An error occurred while updating 'fieldingpost' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'fieldingpost' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Franchises Table -------------------------------
def update_franchises_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'franchises' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Franchises.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'franchises' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO franchises (
                            franchID, franchName, active, NAassoc
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            franchName = VALUES(franchName),
                            active = VALUES(active),
                            NAassoc = VALUES(NAassoc)
                    """, (
                        row['franchID'], row['franchName'], row['active'], row['NAassoc']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting franchID {row['franchID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'franchises' table.")

    except Exception as e:
        print(f"An error occurred while updating 'franchises' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'franchises' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- HallOfFame Table -------------------------------
def update_halloffame_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'halloffame' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/HallOfFame.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'halloffame' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO halloffame (
                            playerID, yearID, votedBy, ballots, needed, votes, inducted, category, note
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            votedBy = VALUES(votedBy),
                            ballots = VALUES(ballots),
                            needed = VALUES(needed),
                            votes = VALUES(votes),
                            inducted = VALUES(inducted),
                            category = VALUES(category),
                            note = VALUES(note)
                    """, (
                        row['playerID'], row['yearid'], row['votedBy'], row['ballots'], row['needed'], row['votes'],
                        row['inducted'], row['category'], row['note']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearid']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'halloffame' table.")

    except Exception as e:
        print(f"An error occurred while updating 'halloffame' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'halloffame' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Homegames Table -------------------------------
def update_homegames_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'homegames' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/HomeGames.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'homegames' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO homegames (
                            teamID, parkID, yearID, firstGame, lastGame, games, openings, attendance
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            firstGame = VALUES(firstGame),
                            lastGame = VALUES(lastGame),
                            games = VALUES(games),
                            openings = VALUES(openings),
                            attendance = VALUES(attendance)
                    """, (
                        row['teamID'], row['parkID'], row['yearID'], row['firstGame'], row['lastGame'], row['games'],
                        row['openings'], row['attendance']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting teamID {row['teamID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'homegames' table.")

    except Exception as e:
        print(f"An error occurred while updating 'homegames' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'homegames' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Managers Table -------------------------------
def update_managers_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'managers' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Managers.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'managers' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO managers (
                            playerID, yearID, teamID, inSeason, manager_G, manager_W, manager_L, teamRank, plyrMgr
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            manager_G = VALUES(manager_G),
                            manager_W = VALUES(manager_W),
                            manager_L = VALUES(manager_L),
                            teamRank = VALUES(teamRank),
                            plyrMgr = VALUES(plyrMgr)
                    """, (
                        row['playerID'], row['yearID'], row['teamID'], row['inseason'], row['manager_G'], row['manager_W'],
                        row['manager_L'], row['teamRank'], row['plyrMgr']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'managers' table.")

    except Exception as e:
        print(f"An error occurred while updating 'managers' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'managers' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Parks Table -------------------------------
def update_parks_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'parks' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Parks.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'parks' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO parks (
                            parkID, park_alias, park_name, city, state, country
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            park_alias = VALUES(park_alias),
                            park_name = VALUES(park_name),
                            city = VALUES(city),
                            state = VALUES(state),
                            country = VALUES(country)
                    """, (
                        row['parkID'], row['park_alias'], row['park_name'], row['city'], row['state'], row['country']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting parkID {row['parkID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'parks' table.")

    except Exception as e:
        print(f"An error occurred while updating 'parks' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'parks' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Pitching Table -------------------------------
def update_pitching_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'pitching' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Pitching.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'pitching' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif key in ['p_BAOpp', 'p_ERA']:  # Handle double values
                        row[key] = float(value) if value else None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO pitching (
                            playerID, yearID, stint, teamID, p_W, p_L, p_G, p_GS, p_CG, p_SHO, p_SV,
                            p_IPOuts, p_H, p_ER, p_HR, p_BB, p_SO, p_BAOpp, p_ERA, p_IBB, p_WP, 
                            p_HBP, p_BK, p_BFP, p_GF, p_R, p_SH, p_SF, p_GIDP
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            p_W = VALUES(p_W),
                            p_L = VALUES(p_L),
                            p_G = VALUES(p_G),
                            p_GS = VALUES(p_GS),
                            p_CG = VALUES(p_CG),
                            p_SHO = VALUES(p_SHO),
                            p_SV = VALUES(p_SV),
                            p_IPOuts = VALUES(p_IPOuts),
                            p_H = VALUES(p_H),
                            p_ER = VALUES(p_ER),
                            p_HR = VALUES(p_HR),
                            p_BB = VALUES(p_BB),
                            p_SO = VALUES(p_SO),
                            p_BAOpp = VALUES(p_BAOpp),
                            p_ERA = VALUES(p_ERA),
                            p_IBB = VALUES(p_IBB),
                            p_WP = VALUES(p_WP),
                            p_HBP = VALUES(p_HBP),
                            p_BK = VALUES(p_BK),
                            p_BFP = VALUES(p_BFP),
                            p_GF = VALUES(p_GF),
                            p_R = VALUES(p_R),
                            p_SH = VALUES(p_SH),
                            p_SF = VALUES(p_SF),
                            p_GIDP = VALUES(p_GIDP)
                    """, (
                        row['playerID'], row['yearID'], row['stint'], row['teamID'], row['p_W'], row['p_L'], row['p_G'],
                        row['p_GS'], row['p_CG'], row['p_SHO'], row['p_SV'], row['p_IPOuts'], row['p_H'], row['p_ER'],
                        row['p_HR'], row['p_BB'], row['p_SO'], row['p_BAOpp'], row['p_ERA'], row['p_IBB'], row['p_WP'],
                        row['p_HBP'], row['p_BK'], row['p_BFP'], row['p_GF'], row['p_R'], row['p_SH'], row['p_SF'],
                        row['p_GIDP']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'pitching' table.")

    except Exception as e:
        print(f"An error occurred while updating 'pitching' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'pitching' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- PitchingPost Table -------------------------------
def update_pitchingpost_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'pitchingpost' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/PitchingPost.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'pitchingpost' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif key in ['p_BAOpp', 'p_ERA']:  # Handle float values
                        row[key] = float(value) if value else None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO pitchingpost (
                            playerID, yearID, round, teamID, p_W, p_L, p_G, p_GS, p_CG, p_SHO, p_SV, 
                            p_IPOuts, p_H, p_ER, p_HR, p_BB, p_SO, p_BAOpp, p_ERA, p_IBB, p_WP, p_HBP, 
                            p_BK, p_BFP, p_GF, p_R, p_SH, p_SF, p_GIDP
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            p_W = VALUES(p_W),
                            p_L = VALUES(p_L),
                            p_G = VALUES(p_G),
                            p_GS = VALUES(p_GS),
                            p_CG = VALUES(p_CG),
                            p_SHO = VALUES(p_SHO),
                            p_SV = VALUES(p_SV),
                            p_IPOuts = VALUES(p_IPOuts),
                            p_H = VALUES(p_H),
                            p_ER = VALUES(p_ER),
                            p_HR = VALUES(p_HR),
                            p_BB = VALUES(p_BB),
                            p_SO = VALUES(p_SO),
                            p_BAOpp = VALUES(p_BAOpp),
                            p_ERA = VALUES(p_ERA),
                            p_IBB = VALUES(p_IBB),
                            p_WP = VALUES(p_WP),
                            p_HBP = VALUES(p_HBP),
                            p_BK = VALUES(p_BK),
                            p_BFP = VALUES(p_BFP),
                            p_GF = VALUES(p_GF),
                            p_R = VALUES(p_R),
                            p_SH = VALUES(p_SH),
                            p_SF = VALUES(p_SF),
                            p_GIDP = VALUES(p_GIDP)
                    """, (
                        row['playerID'], row['yearID'], row['round'], row['teamID'], row['p_W'], row['p_L'], row['p_G'],
                        row['p_GS'], row['p_CG'], row['p_SHO'], row['p_SV'], row['p_IPOuts'], row['p_H'], row['p_ER'],
                        row['p_HR'], row['p_BB'], row['p_SO'], row['p_BAOpp'], row['p_ERA'], row['p_IBB'], row['p_WP'],
                        row['p_HBP'], row['p_BK'], row['p_BFP'], row['p_GF'], row['p_R'], row['p_SH'], row['p_SF'],
                        row['p_GIDP']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'pitchingpost' table.")

    except Exception as e:
        print(f"An error occurred while updating 'pitchingpost' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'pitchingpost' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Salaries Table -------------------------------
def update_salaries_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'salaries' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Salaries.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'salaries' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif key == 'salary':  # Handle float values for salary
                        row[key] = float(value) if value else None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO salaries (
                            playerID, yearId, teamID, salary
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            salary = VALUES(salary)
                    """, (
                        row['playerID'], row['yearID'], row['teamID'], row['salary']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting playerID {row['playerID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'salaries' table.")

    except Exception as e:
        print(f"An error occurred while updating 'salaries' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'salaries' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Schools Table -------------------------------
def update_schools_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'schools' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Schools.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'schools' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO schools (
                            schoolId, school_name, school_city, school_state, school_country
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            school_name = VALUES(school_name),
                            school_city = VALUES(school_city),
                            school_state = VALUES(school_state),
                            school_country = VALUES(school_country)
                    """, (
                        row['schoolID'], row['school_name'], row['school_city'], row['school_state'], row['school_country']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting schoolID {row['schoolID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'schools' table.")

    except Exception as e:
        print(f"An error occurred while updating 'schools' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'schools' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- SeriesPost Table -------------------------------
def update_seriespost_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'seriespost' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/SeriesPost.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'seriespost' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO seriespost (
                            teamIDwinner, teamIDloser, yearID, round, wins, losses, ties
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            wins = VALUES(wins),
                            losses = VALUES(losses),
                            ties = VALUES(ties)
                    """, (
                        row['teamIDwinner'], row['teamIDloser'], row['yearID'], row['round'],
                        row['wins'], row['losses'], row['ties']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting series for year {row['yearID']} and round {row['round']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'seriespost' table.")

    except Exception as e:
        print(f"An error occurred while updating 'seriespost' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'seriespost' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")


# ------------------------------- Teams Table -------------------------------
def update_teams_table():
    connection = None
    cursor = None
    total_rows = 0
    successful_updates = 0
    failed_updates = 0

    print("Starting update for the 'teams' table...")

    try:
        # Open the CSV file and read its contents
        with open('Lahman CSVs/Teams.csv', 'r', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)

            # Get a database connection
            connection = get_db_connection()
            cursor = connection.cursor()

            # Debug: Confirm the database connection
            print("Database connection established successfully for 'teams' table.")

            for row in reader:
                total_rows += 1  # Track the total number of rows processed

                # Replace empty strings or NULL strings with None for SQL compatibility
                for key, value in row.items():
                    if value == '' or value.strip().lower() == 'null':
                        row[key] = None
                    elif value.isdigit():  # Ensure numeric values are integers
                        row[key] = int(value)
                    elif key in ['team_FP', 'team_ERA']:  # Convert float values
                        row[key] = float(value) if value else None

                try:
                    # Insert or update the row in the database
                    cursor.execute("""
                        INSERT INTO teams (
                            teamID, yearID, lgID, franchID, divID, team_rank, team_G, team_G_home, team_W, team_L,
                            DivWin, WCWin, LgWin, WSWin, team_R, team_AB, team_H, team_2B, team_3B, team_HR,
                            team_BB, team_SO, team_SB, team_CS, team_HBP, team_SF, team_RA, team_ER, team_ERA,
                            team_CG, team_SHO, team_SV, team_IPouts, team_HA, team_HRA, team_BBA, team_SOA,
                            team_E, team_DP, team_FP, team_name, park_name, team_attendance, team_BPF, team_PPF
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            team_rank = VALUES(team_rank),
                            team_G = VALUES(team_G),
                            team_G_home = VALUES(team_G_home),
                            team_W = VALUES(team_W),
                            team_L = VALUES(team_L),
                            DivWin = VALUES(DivWin),
                            WCWin = VALUES(WCWin),
                            LgWin = VALUES(LgWin),
                            WSWin = VALUES(WSWin),
                            team_R = VALUES(team_R),
                            team_AB = VALUES(team_AB),
                            team_H = VALUES(team_H),
                            team_2B = VALUES(team_2B),
                            team_3B = VALUES(team_3B),
                            team_HR = VALUES(team_HR),
                            team_BB = VALUES(team_BB),
                            team_SO = VALUES(team_SO),
                            team_SB = VALUES(team_SB),
                            team_CS = VALUES(team_CS),
                            team_HBP = VALUES(team_HBP),
                            team_SF = VALUES(team_SF),
                            team_RA = VALUES(team_RA),
                            team_ER = VALUES(team_ER),
                            team_ERA = VALUES(team_ERA),
                            team_CG = VALUES(team_CG),
                            team_SHO = VALUES(team_SHO),
                            team_SV = VALUES(team_SV),
                            team_IPouts = VALUES(team_IPouts),
                            team_HA = VALUES(team_HA),
                            team_HRA = VALUES(team_HRA),
                            team_BBA = VALUES(team_BBA),
                            team_SOA = VALUES(team_SOA),
                            team_E = VALUES(team_E),
                            team_DP = VALUES(team_DP),
                            team_FP = VALUES(team_FP),
                            team_name = VALUES(team_name),
                            park_name = VALUES(park_name),
                            team_attendance = VALUES(team_attendance),
                            team_BPF = VALUES(team_BPF),
                            team_PPF = VALUES(team_PPF)
                    """, (
                        row['teamID'], row['yearID'], row['lgID'], row['franchID'], row['divID'], row['team_rank'], row['team_G'],
                        row['team_G_home'], row['team_W'], row['team_L'], row['DivWin'], row['WCWin'], row['LgWin'], row['WSWin'],
                        row['team_R'], row['team_AB'], row['team_H'], row['team_2B'], row['team_3B'], row['team_HR'], row['team_BB'],
                        row['team_SO'], row['team_SB'], row['team_CS'], row['team_HBP'], row['team_SF'], row['team_RA'], row['team_ER'],
                        row['team_ERA'], row['team_CG'], row['team_SHO'], row['team_SV'], row['team_IPouts'], row['team_HA'], row['team_HRA'],
                        row['team_BBA'], row['team_SOA'], row['team_E'], row['team_DP'], row['team_FP'], row['team_name'], row['park_name'],
                        row['team_attendance'], row['team_BPF'], row['team_PPF']
                    ))

                    # Track successful updates
                    successful_updates += 1

                except Exception as query_error:
                    # Log only failed rows
                    failed_updates += 1
                    print(f"Error upserting teamID {row['teamID']} for year {row['yearID']}: {query_error}")

        # Commit the changes
        connection.commit()
        print("Database changes committed successfully for 'teams' table.")

    except Exception as e:
        print(f"An error occurred while updating 'teams' table: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        # Print summary
        print(f"\nSummary for 'teams' table:")
        print(f"Total rows processed: {total_rows}")
        print(f"Successful updates: {successful_updates}")
        print(f"Failed updates: {failed_updates}\n\n")

# ------------- UPDATES FOR ALL TABLES HERE -------------
update_people_stats()
update_batting_table()
update_awards_table()
update_awardsshare_table()
update_allstarfull_table()
update_appearances_table()
update_battingpost_table()
update_collegeplaying_table()
update_schools_table()
update_fielding_table()
update_fieldingpost_table()
update_franchises_table()
update_halloffame_table()
update_homegames_table()
update_managers_table()
update_parks_table()
update_pitching_table()
update_pitchingpost_table()
update_salaries_table()
update_seriespost_table()
update_teams_table()