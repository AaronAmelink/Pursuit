from src.Model.Model import LikeModel
from src.Model.Jobs import Job, get_jobs
from src.database.DatabaseHandler import DatabaseHandler
from src.Controller.UserController import UserController
import random

JOB_CACHE_MIN = 20
LIKES_MIN = 10

class JobController:
    def __init__(self, db_handler: DatabaseHandler, user_controller: UserController, model: LikeModel):
        self.db = db_handler
        self.user = user_controller  # Reference to auth controller
        self.model = model
        self._liked_jobs_cache: list[dict] | None = None
        self._jobs_cache: list[Job]

    def get_liked(self) -> list[dict]:
        """Returns cached liked jobs or queries DB if needed"""
        if self._liked_jobs_cache is None:
            self._refresh_liked_cache()
        return self._liked_jobs_cache

    def record_like(self, job_id: int, swipe_label: bool) -> None:
        """Records a like and updates cache"""
        self.db.add_like(self.auth.current_user_id, job_id, swipe_label)
        job = self.model.current_job
        self.db.add_job(job.job_title, job.job_employer, job.job_location, job.job_url)
        self._refresh_liked_cache()

    def _refresh_liked_cache(self) -> None:
        """Forces a cache update"""
        self._liked_jobs_cache = self.db.get_liked_jobs(
            self.auth.current_user_id
        )

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
        