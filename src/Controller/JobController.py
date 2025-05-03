from src.Model.Model import LikeModel
from src.Model.Jobs import Job, get_jobs
from src.database.DatabaseHandler import DatabaseHandler
from src.Controller.UserController import UserController
import random
import pickle
import os

JOB_CACHE_MIN = 20
LIKES_MIN = 10

class JobController:
    def __init__(self, db_handler: DatabaseHandler, user_controller: UserController):
        self.db = db_handler
        self.user = user_controller
        self.model = None
        self._liked_jobs_cache: list[dict] | None = None
        self._jobs_cache: list[Job]
        self._load_model()

    def get_liked(self) -> list[dict]:
        """Returns cached liked jobs or queries DB if needed"""
        if self._liked_jobs_cache is None:
            self._refresh_liked_cache()
        return self._liked_jobs_cache

    def record_like(self, swipe_label: bool) -> None:
        """Records a like and updates cache"""
        job_id = self.db.get_job_id(self.model.current_job.job_title, self.model.current_job.job_employer, self.model.current_job.job_location)
        
        if job_id is None:
            raise ValueError("Job ID not found in database")
        
        self.db.add_like(self.user.user_id, job_id, swipe_label)

        self.model.give_feedback(swipe_label)

        self._refresh_liked_cache()

    def _refresh_liked_cache(self) -> None:
        """Forces a cache update"""
        self._liked_jobs_cache = self.db.get_liked_jobs(self.user.user_id)

    def get_job(self) -> Job:
        """Returns predicted job"""
        if self._jobs_cache < JOB_CACHE_MIN:
            self._refresh_job_cache()

        if len(self.get_liked()) >= LIKES_MIN:
            ranked_jobs = self._rank_jobs(self._jobs_cache)
            selected_job = ranked_jobs[0]
        else:
            # Random selection for cold start
            selected_job = random.choice(self._jobs_cache)
        
        self.model.current_job = selected_job

        self.db.add_job(selected_job.job_title, selected_job.job_employer, selected_job.job_location, selected_job.job_url)
        return selected_job
    
    def _refresh_job_cache(self) -> None:
        """Forces a cache update"""
        prefrences = self.user.get_preferences(self.user.user_id)
        self._jobs_cache = get_jobs(prefrences["preferred_title"], prefrences["preferred_location"])

    def _rank_jobs(self, jobs: list[Job]) -> list[Job]:
        """Returns a ranked list of jobs based on user preferences"""
        return sorted(
            jobs,
            key=lambda job: self.model.predict(job),
            reverse=True
        )
    


    def _load_model(self) -> bool:
        """Loads the model from the user-specific path in database.
        Returns True if successful, False otherwise."""
        try:
            user_id = self.user.current_user_id
            if user_id is None:
                raise ValueError("No authenticated user")
            
            model_path = self.db.get_model_path(user_id)
            if not model_path:
                raise FileNotFoundError("No model path found for user")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            with open(model_path, 'rb') as f:
                loaded_model = pickle.load(f)
                self.model = LikeModel(None, loaded_model)
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def _save_model(self) -> bool:
        """Saves the current model to the user-specific path in database.
        Returns True if successful, False otherwise."""
        try:
            user_id = self.user.current_user_id
            if user_id is None:
                raise ValueError("No authenticated user")
            
            model_path = self.db.get_model_path(user_id)
            if not model_path:
                model_path = os.path.abspath(f"models/user_{user_id}_model.pkl")
                self.db.update_model_path(user_id, model_path)
                
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model.model, f)
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
