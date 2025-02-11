import sqlite3

def create_database():
    """
    Create the `user_responses` table in the database if it doesn't exist.
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            choice1 TEXT,                              -- First choice selection
            choice2 TEXT,                              -- Second choice selection
            choice3 TEXT,                              -- Third choice selection
            choice1_initial TEXT,                      -- Initial selection for choice 1
            choice2_initial TEXT,                      -- Initial selection for choice 2
            choice3_initial TEXT,                      -- Initial selection for choice 3
            choice1_final TEXT,                        -- Final selection after reconsideration for choice 1
            choice2_final TEXT,                        -- Final selection after reconsideration for choice 2
            choice3_final TEXT,                        -- Final selection after reconsideration for choice 3
            reconsider_set INTEGER,                    -- Which set triggered reconsideration (1-3)
            data_driven_tool_suggestion  TEXT,                        -- data_driven_tool_suggestion  suggested alternative
            changed_decision BOOLEAN,                  -- Whether user changed their decision
            save_life_years INTEGER,                   -- Rating: Save life years
            advantage_disadvantaged INTEGER,           -- Rating: Advantage to disadvantaged
            benefit_future INTEGER,                    -- Rating: Benefit others in future
            first_come INTEGER,                        -- Rating: First-come first-served
            treatment_success INTEGER,                 -- Rating: Treatment success likelihood
            treatment_effort INTEGER,                  -- Rating: Treatment effort required
            medication_effect INTEGER,                 -- Rating: Medication effectiveness
            random_selection INTEGER,                  -- Rating: Random selection preference
            gender TEXT,                              -- Demographics: Gender
            age INTEGER,                              -- Demographics: Age
            religion TEXT,                            -- Demographics: Religion
            general_health TEXT,                      -- Health status
            illness TEXT,                             -- Recent illness history
            children TEXT,                            -- Children status
            ip_address TEXT,                          -- User IP
            city TEXT,                                -- Location: City
            region TEXT,                              -- Location: Region
            country TEXT,                             -- Location: Country
            session_start TIMESTAMP,                  -- Session start time
            session_end TIMESTAMP                     -- Session end time
        )
    ''')

    conn.commit()
    conn.close()

def add_columns_if_not_exist():
    """
    Check and add missing columns to the `user_responses` table dynamically.
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(user_responses);")
    existing_columns = [col[1] for col in cursor.fetchall()]

    required_columns = {
        "choice1": "TEXT",
        "choice2": "TEXT",
        "choice3": "TEXT",
        "choice1_initial": "TEXT",
        "choice2_initial": "TEXT",
        "choice3_initial": "TEXT",
        "choice1_final": "TEXT",
        "choice2_final": "TEXT",
        "choice3_final": "TEXT",
        "reconsider_set": "INTEGER",
        "data_driven_tool_suggestion ": "TEXT",
        "changed_decision": "BOOLEAN",
        "save_life_years": "INTEGER",
        "advantage_disadvantaged": "INTEGER",
        "benefit_future": "INTEGER",
        "first_come": "INTEGER",
        "treatment_success": "INTEGER",
        "treatment_effort": "INTEGER",
        "medication_effect": "INTEGER",
        "random_selection": "INTEGER",
        "gender": "TEXT",
        "age": "INTEGER",
        "religion": "TEXT",
        "general_health": "TEXT",
        "illness": "TEXT",
        "children": "TEXT",
        "ip_address": "TEXT",
        "city": "TEXT",
        "region": "TEXT",
        "country": "TEXT",
        "session_start": "TIMESTAMP",
        "session_end": "TIMESTAMP"
    }

    for column, column_type in required_columns.items():
        if column not in existing_columns:
            print(f"Adding column: {column}")
            cursor.execute(f'ALTER TABLE user_responses ADD COLUMN "{column}" {column_type}')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing database schema...")
    create_database()
    add_columns_if_not_exist()
    print("Database setup completed successfully!")
