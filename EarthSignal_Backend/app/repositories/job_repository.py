from app.repositories.base import MongoRepository

class JobRepository(MongoRepository):
    def __init__(self, db):
        super().__init__(db, "analysis_runs")
