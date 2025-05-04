from src.Model.Model import LikeModel
from src.Model.Jobs import Job, get_jobs
from src.database.DatabaseHandler import DatabaseHandler
from src.Controller.UserController import UserController
import random
import pickle
import os

JOB_CACHE_MIN = 20
JOB_CACHE_PROCESSED_MIN = 5
LIKES_MIN = 10
JOB_CACHE_GRAB_AMOUNT = 100

class JobController:
    def __init__(self, db_handler: DatabaseHandler, user_controller: UserController):
        self.db = db_handler
        self.user = user_controller
        self.model = None
        self._liked_jobs_cache: list[dict] | None = None
        self._jobs_cache: list[Job] = []
        self._processed_jobs_cache: list[Job] = []
        

    def get_liked(self) -> list[dict]:
        """Returns cached liked jobs or queries DB if needed"""
        if self._liked_jobs_cache is None:
            self._refresh_liked_cache()
        return self._liked_jobs_cache
    
    def remove_like(self, job_url: str) -> None:
        if self.user is None or self.user.user_id is None:
            raise ValueError("No authenticated user")
        """Removes a like and updates cache"""
        self.db.remove_like(self.user.user_id, job_url)
        self._liked_jobs_cache = [job for job in self._liked_jobs_cache if job["job_url"] != job_url]


    def record_like(self, swipe_label: bool, job_title, job_employer, job_location,  job_url) -> None:
        """Records a like and updates cache"""
        
        if self.model.current_job in self._processed_jobs_cache:
            self._processed_jobs_cache.remove(self.model.current_job)
                
        if swipe_label:
            self.db.add_like(self.user.user_id, job_title, job_employer, job_location, job_url)

        self.model.give_feedback(swipe_label)

        self._refresh_liked_cache()

    def _refresh_liked_cache(self) -> None:
        """Forces a cache update"""
        self._liked_jobs_cache = self.db.get_liked_jobs(self.user.user_id)


    def get_job(self) -> Job:
        """Returns predicted job"""
        if len(self._jobs_cache) < JOB_CACHE_MIN or len(self._processed_jobs_cache) < JOB_CACHE_PROCESSED_MIN:
            self._refresh_job_cache()

        if len(self.get_liked()) >= LIKES_MIN:
            ranked_jobs = self._rank_jobs(self._processed_jobs_cache)
            selected_job = ranked_jobs[0]
        else:
            selected_job = random.choice(self._processed_jobs_cache)

        self._processed_jobs_cache.remove(selected_job)
        
        self.model.current_job = selected_job

        return selected_job
    
    def _refresh_job_cache(self) -> None:
        if self.user is None or self.user.user_id is None:
            raise ValueError("No authenticated user")
        
        """Forces a cache update"""
        if (self._jobs_cache is None or len(self._jobs_cache) < JOB_CACHE_MIN):
            preferences = self.user.get_preferences()
            self._jobs_cache = get_jobs(
                job_title=preferences["preferred_title"],
                job_location=preferences["preferred_location"],
                number_of_results=JOB_CACHE_GRAB_AMOUNT
            )
        
        if (self._processed_jobs_cache is None or len(self._processed_jobs_cache) < JOB_CACHE_PROCESSED_MIN):
                # Process jobs without modifying the list during iteration
            for job in self._jobs_cache[:JOB_CACHE_PROCESSED_MIN+1]:
                job.get_keywords()
                self._processed_jobs_cache.append(job)
            self._jobs_cache = self._jobs_cache[JOB_CACHE_PROCESSED_MIN:]

    def _rank_jobs(self, jobs: list[Job]) -> list[Job]:
        """Returns a ranked list of jobs based on user preferences"""
        return sorted(
            jobs,
            key=lambda job: self.model.predict(job.keywords),
            reverse=True
        )


    def _load_model(self) -> bool:
        """Loads the model from the user-specific path in database.
        Returns True if successful, False otherwise."""
        try:
            user_id = self.user.user_id
            if user_id is None:
                raise ValueError("No authenticated user")
            
            model_path = self.db.get_model_path(user_id)
            if not model_path:
                raise FileNotFoundError("No model path found for user")
            
            if not os.path.exists(model_path):
                self.model = LikeModel(model_type="SGDClassifier")
                return True
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def _save_model(self) -> bool:
        """Saves the current model to the user-specific path in database.
        Returns True if successful, False otherwise."""
        try:
            user_id = self.user.user_id
            if user_id is None:
                raise ValueError("No authenticated user")
            
            model_path = self.db.get_model_path(user_id)
            if not model_path:
                model_path = os.path.abspath(f"models/{self.db.get_username(self.user.user_id)}_model.pkl")
                self.db.update_model_path(user_id, model_path)
                
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            return True
            
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
