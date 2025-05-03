import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Dict
import os

class DatabaseHandler:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self._initialize_db()

    def _get_connection(self) -> mysql.connector.MySQLConnection:
        """Create and return a new database connection"""
        try:
            return mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def _initialize_db(self) -> None:
        """Create tables if they don't exist"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # Users table (unchanged)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS USERS (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        user_password VARCHAR(255) NOT NULL,
                        preferred_title VARCHAR(255),
                        preferred_location VARCHAR(255),
                        model_path VARCHAR(512),
                        creation_time DATETIME NOT NULL
                    )
                """)
                
                # Jobs table (new)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS JOBS (
                        job_id INT AUTO_INCREMENT PRIMARY KEY,
                        job_title VARCHAR(255) NOT NULL,
                        job_employer VARCHAR(255) NOT NULL,
                        job_location VARCHAR(255) NOT NULL,
                        job_url VARCHAR(255),
                        posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    )
                """)
                
                # Likes table (normalized)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS LIKES (
                        like_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        job_id INT NOT NULL,
                        swipe_label INT NOT NULL DEFAULT -1, -- -1 = not shown, 0 = passed, 1 = liked
                        swipe_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (job_id) REFERENCES JOBS(job_id) ON DELETE CASCADE,
                        UNIQUE KEY (user_id, job_id),  -- Prevent duplicate likes
                    )
                """)
                conn.commit()


    def user_exists(self, username: str) -> bool:
        """Check if username exists"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM USERS WHERE username = %s", (username,))
                return cursor.fetchone() is not None

    def create_user(self, username: str, password: str) -> int | None:
        """Create new user and return user_id with default model path"""
        try:
            with open('model.pkl', 'w') as file:
                model_path = os.path.abspath(f"models/{username}_model.pkl")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO USERS 
                        (username, user_password, model_path, creation_time)
                        VALUES (%s, %s, %s, %s)
                    """, (username, password, model_path, datetime.now()))
                    conn.commit()
                    return cursor.lastrowid
        except Error as e:
            print(f"Error creating user: {e}")
            return None

    def verify_user(self, username: str, password: str) -> int | None:
        """Verify credentials and return user_id if valid"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id FROM USERS 
                    WHERE username = %s AND user_password = %s
                """, (username, password))
                result = cursor.fetchone()
                return result[0] if result else None

    def get_user_preferences(self, user_id: int) -> Dict[str, str | None]:
        """Get user's preferences (title/location)"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT preferred_title, preferred_location 
                    FROM USERS WHERE user_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                return {
                    'preferred_title': result[0] if result else None,
                    'preferred_location': result[1] if result else None
                }

    def get_username(self, user_id: int) -> str | None:
        """Get username by user_id"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT username FROM USERS WHERE user_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None

    def update_preferences(self, user_id: int, title: str, location: str) -> bool:
        """Update user's job preferences"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE USERS 
                    SET preferred_title = %s, preferred_location = %s
                    WHERE user_id = %s
                """, (title, location, user_id))
                conn.commit()
                return cursor.rowcount > 0



    def get_liked_jobs(self, user_id: int) -> list[dict]:
        """Returns all jobs liked by a user"""
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT j.job_id, j.title, j.employer, j.location, j.posted_at
                    FROM jobs j
                    JOIN likes l ON j.job_id = l.job_id
                    WHERE l.user_id = %s AND l.swipe_label = 1
                    ORDER BY l.swipe_time DESC
                """, (user_id,))
                return cursor.fetchall()

    def add_like(self, user_id: int, job_id: int, swipe_label: int) -> None:
        """Records a like in the database"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO likes (user_id, job_id, swipe_label)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE swipe_time = CURRENT_TIMESTAMP
                """, (user_id, job_id))
                conn.commit()

    def add_job(self, job_title: str, job_employer: str, job_location: str, job_url: str) -> int:
        """Adds a new job to the database and returns its ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO jobs (job_title, job_employer, job_location, job_url)
                    VALUES (%s, %s, %s, %s)
                """, (job_title, job_employer, job_location, job_url))
                conn.commit()
                return cursor.lastrowid

    def get_job_id(self, job_title: str, job_employer: str, job_location: str) -> int | None:
        """Retrieve job ID based on title, employer, and location"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT job_id FROM jobs 
                    WHERE job_title = %s AND job_employer = %s AND job_location = %s
                """, (job_title, job_employer, job_location))
                result = cursor.fetchone()
                return result[0] if result else None



    def get_model_path(self, user_id: int) -> str | None:
        """Retrieve the stored model path for a user"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT model_path FROM USERS 
                    WHERE user_id = %s
                """, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def verify_model_path(self, user_id: int) -> bool:
        """
        Verify the model file exists at the stored path.
        Returns True if valid, False if missing or no user.
        """
        path = self.get_model_path(user_id)
        if not path:
            return False
        
        return os.path.isfile(path)
    

