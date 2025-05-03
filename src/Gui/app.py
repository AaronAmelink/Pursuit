from src.Model.Model import LikeModel
from src.database.DatabaseHandler import DatabaseHandler
from src.Controller.UserController import UserController
from src.Controller.JobController import JobController

class App:
    def __init__(self):
        self.db = DatabaseHandler(
            host="localhost",
            database="jobmatch",
            user="your_user",
            password="your_password"
        )
        self.model = LikeModel()
        self.auth = UserController(self.db)
        self.jobs = JobController(self.db, self.auth, self.model)

app = App()