from __future__ import annotations # to allow type hint of class itself
from score_module import ScoreInfo 
from game_object import CellObject

alpha_table = [
    255, 213, 171, 129, 87, 45, 3, 0, 42, 84, 126, 168, 210, 252,
    255, 213, 171, 129, 87, 45, 3, 0, 42, 84, 126, 168, 210, 252,
]

class SpriteBase:
    x: int
    y: int
    speed: float
    direction: str # only 'up', 'down', 'left', 'right'
    img: str
    color: str
    cleared: bool
    
    def __init__(self,
            x: int,
            y: int,
            speed: float,
            direction: str,
            img: str = '',
            color: str = '',
            cleared = False) -> None:
        self.x = x
        self.y = y
        self.img = img
        self.color = color
        self.cleared = cleared
        self.set_speed(speed)
        self.set_direction(direction)
        
    def set_direction(self, direction: str) -> None:
        direction = direction.lower()
        if direction in ['let', 'right', 'up', 'down']:
            self.direction = direction
    def set_speed(self, speed) -> None:
        if speed < 0:
            speed = speed * -1
        self.speed = speed

    def process_frame(self) -> None:
        pass

class ColorBlockSprite(SpriteBase):
    destination: tuple = None # (x, y)
    hilighted: bool = False
    alpha: int = 255
    def __init__(self, x: int, y: int, speed: float, color:str) -> None:
        super().__init__(
            x,
            y,
            speed,
            'down',
            '',
            color,
            False)

    def set_destination(self, dest: tuple) -> None:
        if dest[0] > self.x:
            self.direction = 'right'
        elif dest[0] < self.x:
            self.direction = 'left'
        elif dest[1] > self.y:
            self.direction = 'down'
        elif dest[1] < self.y:
            self.direction = 'up'
        self.destination = dest
    def set_destination_by_sprite(self, sprite: ColorBlockSprite) -> None:
        dest = (sprite.x, sprite.y)
        self.set_destination(dest)

    def set_alpha(self, frame_seed: int):
        self.alpha = alpha_table[frame_seed]

    def move(self) -> None:
        if self.reached_destination():
            return
        if self.direction == 'left':
            self.x -= self.speed
            if self.x < self.destination[0]:
                self.x = self.destination[0]
        elif self.direction == 'right':
            self.x += self.speed
            if self.x > self.destination[0]:
                self.x = self.destination[0]
        elif self.direction == 'up':
            self.y -= self.speed
            if self.y < self.destination[1]:
                self.y = self.destination[1]
        elif self.direction == 'down':
            self.y += self.speed
            if self.y > self.destination[1]:
                self.y = self.destination[1]
        # print(f'moving: x={self.x}, y={self.y}')

    def process_frame(self) -> None:
        self.move()

    def reached_destination(self) -> bool:
        if self.destination is None:
            return False
        reach_x = True
        reach_y = True
        if self.direction == 'left' and self.x > self.destination[0]:
            reach_x = False
        elif self.direction == 'right' and self.x < self.destination[0]:
            reach_x = False
        elif self.direction == 'up' and self.y > self.destination[1]:
            reach_y = False
        elif self.direction == 'down' and self.y < self.destination[1]:
            reach_y = False

        return reach_x and reach_y

    def get_coord(self) -> tuple:
        return (self.x, self.y)

    def show_sprite_info(self) -> None:
        print(f'x={self.x}, y={self.y}, color={self.color}')

    def get_sprite_info(self) -> str:
        return f'x={self.x}, y={self.y}, color={self.color}'

class ScoreSprite(SpriteBase):
    alpha: int = 0
    score_info = ScoreInfo()
    def __init__(self, x: int, y: int, speed: float, color: str = '') -> None:
        super().__init__(
            x,
            y,
            speed,
            'up',
            '',
            color,
            False)

    def set_score(self, coordinate: tuple, score_info: ScoreInfo):
        x = coordinate[0]
        y = coordinate[1]
        if y < 1:
            y = 1

        self.x = x
        self.y = y
        self.score_info = score_info
        self.alpha = 255

    def process_frame(self) -> None:
        if self.alpha == 0:
            return
            
        self.alpha -= 4
        if self.alpha <= 100:
            self.alpha = 0
