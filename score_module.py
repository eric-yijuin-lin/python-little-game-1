
class ScoreInfo:
    total_score = 0
    turn_score = 0
    turn_combo = 0
    turn_matched_count = 0
    max_combo = 0
    max_matched_count = 0

class ScoreHelper:
    score_info = ScoreInfo()
    def __init__(self) -> None:
        pass

    def add_score(self, matched_count: int, combo: int, reset_combo = True) -> None:
        if reset_combo:
            self.score_info.turn_combo = combo
            self.score_info.turn_matched_count = matched_count
        else:
            self.score_info.turn_combo += combo
            self.score_info.turn_matched_count += matched_count

        if self.score_info.max_combo < self.score_info.turn_combo:
            self.score_info.max_combo = self.score_info.turn_combo
        if self.score_info.max_matched_count < self.score_info.turn_matched_count:
            self.score_info.max_matched_count = self.score_info.turn_matched_count

        count_weight = self.get_score_weight(self.score_info.turn_matched_count)
        combo_weight = self.get_score_weight(self.score_info.turn_combo)
        self.score_info.turn_score = 100 * matched_count * count_weight * combo_weight
        self.score_info.total_score += self.score_info.turn_score

    def get_score_info(self) -> ScoreInfo:
        return self.score_info

    def get_score_weight(self, count: int):
        if count <= 3:
            return 1.0
        if count <= 4:
            return 1.2
        if count <= 5:
            return 1.5
        if count <= 6:
            return 2
        if count <= 7:
            return 3
        else:
            return 3 + (count - 7) * (count - 7)
