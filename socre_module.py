
class ScoreInfo:
    total_score: int
    turn_score: int
    turn_combo: int = 1

    def __init__(self, turn_score: int, turn_combo: int, total_score: int) -> None:
        self.turn_score = turn_score
        self.turn_combo = turn_combo
        self.total_score = total_score


class ScoreHelper:
    def __init__(self) -> None:
        self.turn_matched_count = 0
        self.turn_score = 0
        self.turn_combo = 1
        self.total_score = 0

    def add_score(self, matched_count: int, combo: int, is_new_turn = True) -> None:
        if is_new_turn:
            self.turn_combo = combo
            self.turn_matched_count = matched_count
        else:
            self.turn_combo += combo
            self.turn_matched_count += matched_count

        count_weight = self.get_score_weight(self.turn_matched_count)
        combo_weight = self.get_score_weight(self.turn_combo)
        self.turn_score = 100 * count_weight * combo_weight
        self.total_score += self.turn_score

    def get_score_info(self) -> ScoreInfo:
        return ScoreInfo(self.tur, self.turn_combo, self.total_score)

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
