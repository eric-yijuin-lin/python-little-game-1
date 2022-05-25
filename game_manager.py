
from random import randint
from sprite_manager import ColorBlockSprite
from game_object import CellObject, GameStatus
from coordinate_module import ColorCheckRangeEnum, CoordinateHelper


class GameManager:
    dimension_x = 8
    dimension_y = 8
    score = 0
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
    # def debug_color(self, x, y):
    #     available_colors = self.get_available_color(x, y)
    #     rand_index = randint(0, len(available_colors) - 1)
    #     rand_color = available_colors[rand_index]
    #     self.cell_map[y][x] = rand_color 

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
            print(f'selected: x={x}, y={y}, sprite.x={self.selected_sprite_1.x}, sprite.y={self.selected_sprite_1.y}, sprite.color={self.selected_sprite_1.color}')
            return

        self.selected_sprite_2 = self.sprite_map[y][x]
        print(f'selected: x={x}, y={y}, sprite.x={self.selected_sprite_1.x}, sprite.y={self.selected_sprite_1.y}, sprite.color={self.selected_sprite_1.color}')
        if not self.coord_helper.is_neighbor(self.selected_sprite_1, self.selected_sprite_2):
            self.selected_sprite_1 = None
            self.selected_sprite_2 = None
            return
        # self.selected_sprite_1.color = 'black'
        # self.selected_sprite_2.color = 'black'
        self.game_status = GameStatus.SwapCellRead

    def swap_cell(self, cell_1: CellObject, cell_2: CellObject):
        temp_x = cell_1.x
        temp_y = cell_1.y
        temp_color = cell_1.color
        self.sprite_map[cell_1.y][cell_1.x].x = cell_2.x
        self.sprite_map[cell_1.y][cell_1.x].y = cell_2.y
        self.sprite_map[cell_1.y][cell_1.x].color = cell_2.color
        self.sprite_map[cell_2.y][cell_2.x].x = temp_x
        self.sprite_map[cell_2.y][cell_2.x].y = temp_y
        self.sprite_map[cell_2.y][cell_2.x].color = temp_color
        
    def process_turn(self, cell_1: CellObject, cell_2) -> int:
        clear_cordinates1 = self.coord_helper.get_clear_coordinates(cell_1)
        clear_cordinates2 = self.coord_helper.get_clear_coordinates(cell_2)
        matched_count1 = self.get_matched_count(cell_1.color, clear_cordinates1)
        matched_count2 = self.get_matched_count(cell_2.color, clear_cordinates2)
        if matched_count1 == 0 and matched_count2 == 0:
            # no matched, swap back
            self.swap_cell(self.selected_sprite_1, self.selected_sprite_2)
            return

        combo = 2 if (matched_count1 > 0 and matched_count2 > 0) else 1
        score = self.get_score(matched_count1, combo) + self.get_score(matched_count2, combo)
        self.clear_cells(clear_cordinates1)
        self.clear_cells(clear_cordinates2)

        return score


    def get_matched_count(self, color: str, clear_coordinates: list) -> int:
        count = 0
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            if self.sprite_map[y][x].color == color:
                count += 1
        return count

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

    def clear_cells(self, clear_coordinates: list) -> None:
        for coord in clear_coordinates:
            x = coord[0]
            y = coord[1]
            self.sprite_map[y][x] = None
