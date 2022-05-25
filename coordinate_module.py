from enum import Enum
from sprite_manager import ColorBlockSprite
from game_object import CellObject

class ColorCheckRangeEnum(Enum):
    Top = 'Top',
    Left = 'Left',
    Bottom = 'Bottom',
    Right = 'Right',
    MiddleX = 'MiddleX',
    MiddleY = 'MiddleY'

class CoordinateHelper:
    # a list contains all coordinate offsets of a corss shape
    # that are going to be used for checking/clearing matched cells
    # offsets are pairs of (x, y)
    clearing_offsets = [
        (-2, 0), (-1, 0), (1, 0), (2, 0),
        (0, -2), (0, -1), (0, 1), (0, 2),
        (0, 0)
    ]
    def __init__(self, dimension_x: int, dimension_y: int) -> None:
        self.dimension_x = dimension_x
        self.dimension_y = dimension_y
    def is_valid_coordinate(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.dimension_x:
            return False
        if y < 0 or y >= self.dimension_y:
            return False
        return True

    def get_color_check_range(self, x: int, y: int, direction: ColorCheckRangeEnum) -> dict:
        check_range = {
            'x-start': x,
            'x-end': x+1,
            'y-start': y,
            'y-end': y+1,
        }
        if direction == ColorCheckRangeEnum.Top:
            check_range['y-start'] = y-2
        elif direction == ColorCheckRangeEnum.Bottom:
            check_range['y-end'] = y+3
        elif direction == ColorCheckRangeEnum.Left:
            check_range['x-start'] = x-2
        elif direction == ColorCheckRangeEnum.Right:
            check_range['x-end'] = x+3
        elif direction == ColorCheckRangeEnum.MiddleX:
            check_range['x-start'] = x-1
            check_range['x-end'] = x+2
        elif direction == ColorCheckRangeEnum.MiddleY:
            check_range['y-start'] = y-1
            check_range['y-end'] = y+2
        return check_range
    
    def is_neighbor(self, cell_1: ColorBlockSprite, cell_2: ColorBlockSprite):
        if cell_1.x - cell_2.x > 1 or cell_1.x - cell_2.x < -1:
            return False
        if cell_1.y - cell_2.y > 1 or cell_1.y - cell_2.y < -1:
            return False
        return True

    def get_clear_coordinates(self, cell: ColorBlockSprite):
        result = []
        for offset in self.clearing_offsets:
            if self.is_valid_coordinate(cell.x + offset[0], cell.y + offset[1]):
                result.append((cell.x + offset[0], cell.y + offset[1]))
        return result

    def get_clear_coordinates_dict(self, sprite: ColorBlockSprite) -> dict:
        result = {}
        all_offsets =  { # each direction contains 2 tuples of offsets
            'left': ((-1, 0), (-2, 0)),
            'right': ((1, 0), (2, 0)),
            'down': ((0, -1), (0, -2)),
            'up': ((0, 1), (0, 2)),
        }

        for key, value in all_offsets.items():
            is_dir_needed = True
            for offset in value:
                if not self.is_valid_coordinate(sprite.x + offset[0], sprite.y + offset[1]):
                    is_dir_needed = False
                    break
            if is_dir_needed:
                result[key] = value
        return result
