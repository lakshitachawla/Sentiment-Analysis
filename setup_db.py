import mysql.connector
from werkzeug.security import generate_password_hash 
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

USERS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

ANALYSIS_HISTORY_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS analysis_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    input_text TEXT NOT NULL,
    positive_score DECIMAL(5, 2) NOT NULL,
    neutral_score DECIMAL(5, 2) NOT NULL,
    negative_score DECIMAL(5, 2) NOT NULL,
    predicted_class VARCHAR(10) NOT NULL,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_feedback VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""

def setup_database():
    conn = None
    cursor = None    
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"Setting up database '{MYSQL_DATABASE}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"USE {MYSQL_DATABASE}")
        print("Creating tables in Database....")
        cursor.execute(USERS_TABLE_SCHEMA)
        cursor.execute(ANALYSIS_HISTORY_TABLE_SCHEMA)
        conn.commit()
        print("All tables created successfully or already existed.")
        
        # D. Insert a secure default test user (for easy demo login)
        test_email = 'demo@senti.co'
        test_hash = generate_password_hash('testpassword') 
        
        insert_query = """
        INSERT INTO users (name, username, phone, email, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name=VALUES(name), 
            username=VALUES(username), 
            phone=VALUES(phone),
            password_hash=VALUES(password_hash)
        """
        test_data = ('Demo User', 'SentiCo_Analyst', '555-555-1212', test_email, test_hash)
        cursor.execute(insert_query, test_data)
        conn.commit()
        print(f"Default user '{test_email}' inserted.")
        
        print("\nMySQL database setup complete.")

    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
            print(f"Error: Could not connect to MySQL server")
        elif err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access denied.")
        else:
            print(f"An unexpected MySQL error occurred: {err}")
            
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    setup_database()
