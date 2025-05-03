from src.database.DatabaseHandler import DatabaseHandler
from src.Controller.UserController import UserController
from src.Controller.JobController import JobController
from dotenv import load_dotenv
import os

class App:
    def __init__(self):
        load_dotenv()

        self.db = DatabaseHandler(
            host="localhost",
            database="pursuit",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.auth = UserController(self.db)
        self.jobs = JobController(self.db, self.auth)

app = App()