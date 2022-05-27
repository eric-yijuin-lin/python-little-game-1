
from random import randint
from socre_module import ScoreInfo
from sprite_manager import ColorBlockSprite
from game_object import GameStatus
from socre_module import ScoreHelper
from coordinate_module import ColorCheckRangeEnum, CoordinateHelper


class GameManager:
    dimension_x = 8
    dimension_y = 8
    score = 0
    frame_delay = 30
    sprite_map = []
    selected_sprite_1: ColorBlockSprite = None
    selected_sprite_2: ColorBlockSprite = None
    game_status = GameStatus.Initializing
    color_dict = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (255, 0, 255),
        'cyan': (0, 255, 255),
    }

    def __init__(self) -> None:
        self.score_helper = ScoreHelper()
        self.coord_helper = CoordinateHelper(self.dimension_x, self.dimension_y)
        self.init_cell_map()
        self.action_dict = {
            GameStatus.Initializing: self.process_initializing,
            GameStatus.Idle: self.process_idle,
            GameStatus.SwapingForward: self.process_swap_forward,
            GameStatus.SwapingBack: self.process_swap_back,
            GameStatus.ShowingMatched: self.process_show_matched,
            GameStatus.ClearingBlock: self.process_clear_block,
            GameStatus.ClearingAnimation: self.process_clear_animation,
            GameStatus.ReAligningBlock: self.process_realign_block,
            GameStatus.ReAligningAnimation: self.process_realign_animation,
            GameStatus.NewBlockCreating: self.process_new_block_create,
            GameStatus.NewBlockDroping: self.process_new_block_drop,
        }

    def init_cell_map(self) -> None:
        for _ in range(0, self.dimension_x):
            self.sprite_map.append([None] * self.dimension_y)
        for x in range(0, self.dimension_x):
            for y in range(0, self.dimension_y):
                available_colors = self.get_available_color(x, y)
                rand_index = randint(0, len(available_colors) - 1)
                color = available_colors[rand_index]
                self.sprite_map[x][y] = ColorBlockSprite(x, y, 0.03, color)
        print('debug')

    def process_frame(self) -> None:
        if self.game_status not in self.action_dict:
            raise Exception(f'unrecognized game status: {self.game_status}')
        self.action_dict[self.game_status]()

    def process_initializing(self) -> None:
        return

    def process_idle(self) -> None:
        return

    def process_swap_forward(self) -> None:
        self.selected_sprite_1.process_frame()
        self.selected_sprite_2.process_frame()
        if self.selected_sprite_1.reached_destination() and self.selected_sprite_2.reached_destination():
            coord1 = self.selected_sprite_1.get_coord()
            coord2 = self.selected_sprite_2.get_coord()
            self.swap_sprite(coord1, coord2)
            if self.has_match(self.selected_sprite_1) or self.has_match(self.selected_sprite_2):
                self.game_status = GameStatus.ShowingMatched
                self.frame_delay = 30
            else:
                self.selected_sprite_1.set_destination_by_sprite(self.selected_sprite_2)
                self.selected_sprite_2.set_destination_by_sprite(self.selected_sprite_1)
                self.game_status = GameStatus.SwapingBack
            
    def process_swap_back(self) -> None:
        self.selected_sprite_1.process_frame()
        self.selected_sprite_2.process_frame()
        if self.selected_sprite_1.reached_destination() and self.selected_sprite_2.reached_destination():
            self.selected_sprite_1 = None
            self.selected_sprite_2 = None
            self.game_status = GameStatus.Idle
    
    def process_show_matched(self) -> None:
        if self.has_match(self.selected_sprite_1):
            self.set_matched_highlight(self.selected_sprite_1)
        if self.has_match(self.selected_sprite_2):
            self.set_matched_highlight(self.selected_sprite_2)
        self.frame_delay -= 1
        if self.frame_delay == 0:
            self.game_status = GameStatus.ClearingBlock

    def process_clear_block(self) -> None:
        matched_coords1 = self.get_matched_coordinates(self.selected_sprite_1)
        matched_coords2 = self.get_matched_coordinates(self.selected_sprite_2)
        matched_count1 = len(matched_coords1)
        matched_count2 = len(matched_coords2)
        combo = 2 if matched_count1 > 0 and matched_count2 > 0 else 1
        self.score_helper.add_score(matched_count1 + matched_count2, combo)
        self.clear_cells(matched_coords1)
        self.clear_cells(matched_coords2)
        self.selected_sprite_1 = None
        self.selected_sprite_2 = None
        self.game_status = GameStatus.ClearingAnimation
        self.frame_delay = 30

    def process_clear_animation(self) -> None:
        self.frame_delay -= 1
        if self.frame_delay == 0:
            self.game_status = GameStatus.NewBlockCreating

    def process_new_block_create(self) -> None:
        available_colors = list(self.color_dict.keys())
        for x in range(0, self.dimension_x):
            column = self.sprite_map[x]
            cleared_count = sum(i.cleared for i in column)
            for i in range(cleared_count):
                rand_index = randint(0, len(available_colors) - 1)
                color = available_colors[rand_index]
                column.insert(0, ColorBlockSprite(x, 0 - i -1, 0.03, color))
        self.game_status = GameStatus.ReAligningBlock

    def process_realign_block(self) -> None:
        self.set_drop_destination()
        self.game_status = GameStatus.ReAligningAnimation

    def process_realign_animation(self) -> None:
        not_reached_count = 0
        for column in self.sprite_map:
            cleared_count = sum(s.cleared for s in column)
            if cleared_count == 0:
                continue
            for sprite in column:
                sprite.process_frame()
                if not sprite.reached_destination():
                    not_reached_count += 1
        if not_reached_count == 0:
            self.refresh_realigned_map()
            self.game_status = GameStatus.Idle

    def process_new_block_drop(self) -> None:
        pass

    def has_match(self, sprite: ColorBlockSprite):
        matched_dict = self.get_matched_coordinates(sprite)
        return len(matched_dict) > 0

    def get_available_color(self, x: int, y: int) -> list:
        available_colors = list(self.color_dict.keys())
        color_stats = [
            self.get_color_histogram(x, y, ColorCheckRangeEnum.Top),
            self.get_color_histogram(x, y, ColorCheckRangeEnum.Left),
            self.get_color_histogram(x, y, ColorCheckRangeEnum.Bottom),
            self.get_color_histogram(x, y, ColorCheckRangeEnum.Right),
            self.get_color_histogram(x, y, ColorCheckRangeEnum.MiddleX),
            self.get_color_histogram(x, y, ColorCheckRangeEnum.MiddleY),
        ]
        for color_histogram in color_stats:
            for color_key in color_histogram.keys():
                if color_histogram[color_key] >= 2 and color_key in available_colors:
                    available_colors.remove(color_key)
        # dict.pop(key, None) # 不論 key 在不在都移除（好方法）
        return available_colors

    def get_color_histogram(self, x: int, y: int, range_enum: ColorCheckRangeEnum):
        colors = self.color_dict.keys()
        color_histogram = {}
        for color in colors:
            color_histogram[color] = 0
        
        check_range = self.coord_helper.get_color_check_range(x, y, range_enum)
        for i in range(check_range['x-start'], check_range['x-end']):
            for j in range(check_range['y-start'], check_range['y-end']):
                if not self.coord_helper.is_valid_coordinate(i, j):
                    continue
                temp_cell = self.sprite_map[i][j]
                if temp_cell is not None and temp_cell.color is not None:
                    color_histogram[temp_cell.color] += 1
        return color_histogram

    def set_selection(self, x: int, y: int) -> None:
        if not self.coord_helper.is_valid_coordinate(x, y):
            self.selected_sprite_1 = None
            self.selected_sprite_2 = None
            return
        if self.selected_sprite_1 is None:
            self.selected_sprite_1 = self.sprite_map[x][y]
            self.selected_sprite_1.show_sprite_info()
            return

        self.selected_sprite_2 = self.sprite_map[x][y]
        self.selected_sprite_2.show_sprite_info()
        if not self.coord_helper.is_neighbor(self.selected_sprite_1, self.selected_sprite_2):
            self.selected_sprite_1 = None
            self.selected_sprite_2 = None
            return
        self.selected_sprite_1.set_destination_by_sprite(self.selected_sprite_2)
        self.selected_sprite_2.set_destination_by_sprite(self.selected_sprite_1)
        self.game_status = GameStatus.SwapingForward

    def swap_sprite(self, coord1: tuple, coord2: tuple):
        x1 = coord1[0]
        y1 = coord1[1]
        x2 = coord2[0]
        y2 = coord2[1]
        temp_color = self.sprite_map[x1][y1].color

        self.sprite_map[x1][y1].x = x1
        self.sprite_map[x1][y1].y = y1
        self.sprite_map[x1][y1].color = self.sprite_map[x2][y2].color
        self.sprite_map[x2][y2].x = x2
        self.sprite_map[x2][y2].y = y2
        self.sprite_map[x2][y2].color = temp_color
        
    def set_matched_highlight(self, sprite: ColorBlockSprite) -> None:
        matched_coords = self.get_matched_coordinates(sprite)
        for coord in matched_coords:
            x = coord[0]
            y = coord[1]
            self.sprite_map[x][y].hilighted = True
        sprite.hilighted = True

    def get_matched_count(self, color: str, clear_coordinates: list) -> int:
        count = 0
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            if self.sprite_map[x][y].color == color:
                count += 1
        return count

    def get_matched_count_dict(self, sprite: ColorBlockSprite) -> dict:
        result = {}
        offset_dict = self.coord_helper.get_clear_coordinates_dict(sprite)
        for direction, dir_coords in offset_dict.items():
            dir_match = 0
            for coord in dir_coords:
                x = coord[0]
                y = coord[1]
                if self.sprite_map[x][y].color == sprite.color:
                    dir_match += 1
            if dir_match == 2:
                result[direction] = dir_match
        return result

    def get_matched_coordinates(self, sprite: ColorBlockSprite) -> set:
        results = set()
        sliding_windows = self.coord_helper.get_sliding_windows(sprite)
        for window in sliding_windows:
            if self.is_matched_window(sprite, window):
                for coord in window:
                    results.add(coord)
        return results

    def is_matched_window(self, sprite: ColorBlockSprite, coord_window: list) -> bool:
        for coord in coord_window:
            x = coord[0]
            y = coord[1]
            if self.sprite_map[x][y].color != sprite.color:
                return False
        return True

    def clear_cells(self, clear_coordinates: list) -> None:
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            self.sprite_map[x][y].cleared = True
        print(f'cleared{clear_coordinates}')

    def set_drop_destination(self) -> None:
        for column in self.sprite_map:
            drop_distance = 0
            for y in range(len(column) - 1, -1, -1):
                sprite = column[y]
                if sprite.cleared:
                    drop_distance += 1
                x = sprite.x
                y = sprite.y + drop_distance
                sprite.set_destination((x, y))

    def refresh_realigned_map(self) -> None:
        for x in range(0, self.dimension_x):
            cleared_count = sum(c.cleared for c in self.sprite_map[x])
            if cleared_count > 0:
                self.sprite_map[x] = list(filter(lambda x: (not x.cleared), self.sprite_map[x]))

    def get_score_info(self) -> ScoreInfo:
        return self.score_helper.get_score_info()