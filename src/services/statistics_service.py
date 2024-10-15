class StatisticsService:
    def __init__(self):
        self.stats = {}

    def log_message(self, user_id):
        self.stats[user_id] = self.stats.get(user_id, 0) + 1

    def get_user_stats(self, user_id):
        return self.stats.get(user_id, 0)
