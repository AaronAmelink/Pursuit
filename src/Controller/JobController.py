JOB_CACHE_MIN = 20
LIKES_MIN = 10

class JobController:
    def __init__(self, db_handler: DatabaseHandler, user_controller: UserController, model: LikeModel):
        self.db = db_handler
        self.user = user_controller  # Reference to auth controller
        self.model = model
        self._liked_jobs_cache: list[dict] | None = None
        self._jobs_cache: 

    def get_liked(self) -> list[dict]:
        """Returns cached liked jobs or queries DB if needed"""
        if self._liked_jobs_cache is None:
            self._refresh_liked_cache()
        return self._liked_jobs_cache

    def record_like(self, job_id: int) -> None:
        """Records a like and updates cache"""
        self.db.add_like(self.auth.current_user_id, job_id)
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

        # if LIKES (user_id) > LIKES_MIN: _rank_jobs()
        # else randomly select a job
        
        return selected_job
    
    def _refresh_job_cache(self) -> None:
        """Forces a cache update"""
        prefrences = self.user.get_preferences(self.user.user_id)
        self._jobs_cache = jobs.get_jobs(prefrences["preferred_title"], prefrences["preferred_location"])

    def _rank_jobs(self, jobs: list[Job]) -> list[Job]:
        """Returns a ranked list of jobs based on user preferences"""
        # Get liked jobs
        liked_jobs = self.get_liked()

        # Rank jobs using the model
        ranked_jobs = self.model.predict(jobs, liked_jobs)
        
        return ranked_jobs
    

    def update_likes() -> None:
        """Updates the model and likes in the database"""
        