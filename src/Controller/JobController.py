class JobController:
    def __init__(self, db_handler: DatabaseHandler, user_controller: UserController):
        self.db = db_handler
        self.user = user_controller  # Reference to auth controller
        self._liked_jobs_cache: list[dict] | None = None

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