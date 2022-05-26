
from random import randint
from sprite_manager import ColorBlockSprite
from game_object import CellObject, GameStatus
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
        for _ in range(0, self.dimension_y):
            self.sprite_map.append([None] * self.dimension_x)
        for y in range(0, self.dimension_y):
            for x in range(0, self.dimension_x):
                available_colors = self.get_available_color(x, y)
                rand_index = randint(0, len(available_colors) - 1)
                color = available_colors[rand_index]
                self.sprite_map[y][x] = ColorBlockSprite(
                    CellObject(x, y, color), 0.03
                )

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
        self.selected_sprite_1.show_sprite_info()
        self.selected_sprite_2.show_sprite_info()
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
        self.score += self.get_score(matched_count1 + matched_count2, combo)
        self.clear_cells(matched_coords1)
        self.clear_cells(matched_coords2)
        self.selected_sprite_1 = None
        self.selected_sprite_2 = None
        self.game_status = GameStatus.ClearingAnimation
        self.frame_delay = 30

    def process_clear_animation(self) -> None:
        self.frame_delay -= 1
        if self.frame_delay == 0:
            self.game_status = GameStatus.ReAligningBlock

    def process_realign_block(self) -> None:
        for x in range(0, self.dimension_x):
            self.re_align_column(x)
        self.game_status = GameStatus.ReAligningAnimation

    def process_realign_animation(self) -> None:
        not_reached_count = 0
        for x in range(0, self.dimension_x):
            for y in range(0, self.dimension_y):
                sprite = self.sprite_map[y][x]
                sprite.process_frame()
                if not sprite.reached_destination():
                    not_reached_count += 1
        if not_reached_count == 0:
            self.game_status = GameStatus.NewBlockCreating

    def process_new_block_create(self) -> None:
        pass        

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
                temp_cell = self.sprite_map[j][i]
                if temp_cell is not None and temp_cell.color is not None:
                    color_histogram[temp_cell.color] += 1
        return color_histogram

    def set_selection(self, x: int, y: int) -> None:
        if not self.coord_helper.is_valid_coordinate(x, y):
            self.selected_sprite_1 = None
            self.selected_sprite_2 = None
            return
        if self.selected_sprite_1 is None:
            self.selected_sprite_1 = self.sprite_map[y][x]
            self.selected_sprite_1.show_sprite_info()
            return

        self.selected_sprite_2 = self.sprite_map[y][x]
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
        temp_color = self.sprite_map[y1][x1].color

        self.sprite_map[y1][x1].x = x1
        self.sprite_map[y1][x1].y = y1
        self.sprite_map[y1][x1].color = self.sprite_map[y2][x2].color
        self.sprite_map[y2][x2].x = x2
        self.sprite_map[y2][x2].y = y2
        self.sprite_map[y2][x2].color = temp_color
        
    def set_matched_highlight(self, sprite: ColorBlockSprite) -> None:
        matched_coords = self.get_matched_coordinates(sprite)
        for coord in matched_coords:
            x = coord[0]
            y = coord[1]
            self.sprite_map[y][x].hilighted = True
        sprite.hilighted = True

    def get_matched_count(self, color: str, clear_coordinates: list) -> int:
        count = 0
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            if self.sprite_map[y][x].color == color:
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
                if self.sprite_map[y][x].color == sprite.color:
                    dir_match += 1
            if dir_match == 2:
                result[direction] = dir_match
        return result

    def get_score(self, matched_count: int, combo: int):
        count_weight = self.get_score_weight(matched_count)
        combo_weight = self.get_score_weight(combo)
        return count_weight * 100 * combo_weight

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
            if self.sprite_map[y][x].color != sprite.color:
                return False
        return True

    def clear_cells(self, clear_coordinates: list) -> None:
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            self.sprite_map[y][x].cleared = True

    def re_align_column(self, col_idx: int) -> None:
        sprites = []
        for y in range(self.dimension_y -1, -1, -1):
            sprites.append(self.sprite_map[y][col_idx])
        
        drop_distance = 0
        for sprite in sprites:
            self.set_drop_destination(sprite, drop_distance)
            if sprite.cleared:
                drop_distance += 1
    
    def set_drop_destination(self, sprite: ColorBlockSprite, distance: int) -> None:
        x = sprite.x
        y = sprite.y + distance
        sprite.set_destination((x, y))

    def refresh_sprite_map(self) -> list:
        '''
        Refreshes sprite map status after clearing matched cells,
        also returns a list represents the cleared count of each column
        '''
        column_clear_count = []
        for x in range(0, self.dimension_x):
            count = 0
            for y in range(self.dimension_y -1, -1, -1):
                if self.sprite_map[y][x].cleared:
                    count += 1
                if self.coord_helper.is_valid_coordinate(x, y + count):
                    self.sprite_map[y][x].color = self.sprite_map[y + count][x].color
            column_clear_count.append(count)
        return column_clear_count