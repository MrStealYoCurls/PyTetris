# Import necessary libraries
import pygame
from pygame.image import load
from pygame.time import get_ticks

from os import path
from random import choice
from sys import exit
from os.path import join


# Game Settings
Columns = 10
Rows = 20
Cell_Size = 40
Game_Width, Game_Height = Columns * Cell_Size, Rows * Cell_Size

# Sidebar size
Sidebar_Width = 200
Preview_Height_Fraction = 0.65
Pause_Fraction = 0.1
Score_Height_Fraction = 1 - Preview_Height_Fraction - Pause_Fraction

# Window
Padding = 20
Window_Width = Game_Width + Sidebar_Width + Padding * 3
Window_Height = Game_Height + Padding * 2

# Game behaviour
Update_Start_Speed = 400
Move_Wait_Time = 200
Rotate_Wait_Time = 200
Block_Offset = pygame.Vector2(Columns // 2, -1)

# Colors
Red = '#da635b'
Orange = '#e29047'
Yellow = '#f4dd7d'
Green = '#6fc3b6'
Teal = '#008080'
Blue = '#4c5fdf'
Purple = '#7359e0'
Gray = '#1C1C1C'
Line_Color = '#FFFFFF'

# Shapes
Tetrominos = {
    'T': {'shape': [(0, 0), (-1, 0), (1, 0), (0, -1)], 'color': Purple},
    'O': {'shape': [(0, 0), (0, -1), (1, 0), (1, -1)], 'color': Yellow},
    'J': {'shape': [(0, 0), (0, -1), (0, 1), (-1, 1)], 'color': Blue},
    'L': {'shape': [(0, 0), (0, -1), (0, 1), (1, 1)], 'color': Orange},
    'I': {'shape': [(0, 0), (0, -1), (0, -2), (0, 1)], 'color': Teal},
    'S': {'shape': [(0, 0), (-1, 0), (0, -1), (1, -1)], 'color': Green},
    'Z': {'shape': [(0, 0), (1, 0), (0, -1), (-1, -1)], 'color': Red}
}

Score_Data = {1: 40, 2: 100, 3: 300, 4: 1200}


# Timer Class
class Timer:
    def __init__(self, duration, repeated=False, func=None):
        self.repeated = repeated
        self.func = func
        self.duration = duration

        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration and self.active:

            # call a function
            if self.func and self.start_time != 0:
                self.func()

            # reset timer
            self.deactivate()

            # repeat the timer
            if self.repeated:
                self.activate()


# Game Class
class Game:
    def __init__(self, get_next_shape, update_score):
        # general
        self.surface = pygame.Surface((Game_Width, Game_Height))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft=(Padding, Padding))
        self.sprites = pygame.sprite.Group()

        # game connection
        self.get_next_shape = get_next_shape
        self.update_score = update_score

        # lines
        self.line_surface = self.surface.copy()
        self.line_surface.fill((0, 255, 0))
        self.line_surface.set_colorkey((0, 255, 0))
        self.line_surface.set_alpha(120)

        # Tetromino
        self.field_data = [[0 for x in range(Columns)] for y in range(Rows)]
        self.tetromino = Tetromino(
            choice(list(Tetrominos.keys())),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

        # timer
        self.down_speed = Update_Start_Speed
        self.down_speed_faster = self.down_speed * 0.3
        self.down_pressed = False
        self.timers = {
            'vertical move': Timer(self.down_speed, True, self.move_down),
            'horizontal move': Timer(Move_Wait_Time),
            'rotate': Timer(Rotate_Wait_Time)
        }
        self.timers['vertical move'].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

        # sound
        self.landing_sound = pygame.mixer.Sound(join('sound', 'landing.wav'))
        self.landing_sound.set_volume(0.1)

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += Score_Data[num_lines] * self.current_level

        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.3
            self.timers['vertical move'].duration = self.down_speed

        self.update_score(self.current_lines, self.current_score, self.current_level)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.pos.y < 0:
                exit()

    def create_new_tetromino(self):
        self.landing_sound.play()
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):

        for col in range(1, Columns):
            x = col * Cell_Size
            pygame.draw.line(self.line_surface, Line_Color, (x, 0), (x, self.surface.get_height()), 1)

        for row in range(1, Rows):
            y = row * Cell_Size
            pygame.draw.line(self.line_surface, Line_Color, (0, y), (self.surface.get_width(), y))

        self.surface.blit(self.line_surface, (0, 0))

    def input(self):
        keys = pygame.key.get_pressed()

        # checking horizontal movement
        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()

        # check for rotation
        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

        # down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed

    def check_finished_rows(self):

        # get the full row indexes
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:

                # delete full rows
                for block in self.field_data[delete_row]:
                    block.kill()

                # move down blocks
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # rebuild the field data
            self.field_data = [[0 for x in range(Columns)] for y in range(Rows)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # update score
            self.calculate_score(len(delete_rows))

    def run(self):

        # update
        self.input()
        self.timer_update()
        self.sprites.update()

        # drawing
        self.surface.fill(Gray)
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (Padding, Padding))
        pygame.draw.rect(self.display_surface, Line_Color, self.rect, 2, 2)


class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):

        # setup
        self.shape = shape
        self.block_positions = Tetrominos[shape]['shape']
        self.color = Tetrominos[shape]['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    # collisions
    def next_move_horizontal_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    # movement
    def move_horizontal(self, amount):
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_new_tetromino()

    # rotate
    def rotate(self):
        if self.shape != 'O':

            # 1. pivot point
            pivot_pos = self.blocks[0].pos

            # 2. new block positions
            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            # 3. collision check
            for pos in new_block_positions:
                # horizontal
                if pos.x < 0 or pos.x >= Columns:
                    return

                # field check -> collision with other pieces
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

                # vertical / floor check
                if pos.y > Rows:
                    return

            # 4. implement new positions
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):

        # general
        super().__init__(group)
        self.image = pygame.Surface((Cell_Size, Cell_Size))
        self.image.fill(color)

        # position
        self.pos = pygame.Vector2(pos) + Block_Offset
        self.rect = self.image.get_rect(topleft=self.pos * Cell_Size)

    def rotate(self, pivot_pos):

        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < Columns:
            return True

        if field_data[int(self.pos.y)][x]:
            return True

    def vertical_collide(self, y, field_data):
        if y >= Rows:
            return True

        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True

    def update(self):
        self.rect.topleft = self.pos * Cell_Size


# Preview Class
class Preview:
    def __init__(self):
        # general
        self.display_surface = pygame.display.get_surface()
        self.surface = pygame.Surface((Sidebar_Width, Game_Height * Preview_Height_Fraction))
        self.rect = self.surface.get_rect(topright=(Window_Width - Padding, Padding))

        # shapes
        self.shape_surfaces = {shape: load(path.join('graphics', f'{shape}.png')).convert_alpha() for shape in
                               Tetrominos.keys()}
        # image position data
        self.increment_height = self.surface.get_height() / 3

    def display_pieces(self, shapes):
        for i, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            rect = shape_surface.get_rect(center=(x, y))
            self.surface.blit(shape_surface, rect)

    def run(self, next_shapes):
        self.surface.fill(Gray)
        self.display_pieces(next_shapes)
        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, Line_Color, self.rect, 2, 2)


# Score Class
class Score:
    def __init__(self):
        self.surface = pygame.Surface(
            (Sidebar_Width, Game_Height * Score_Height_Fraction - Padding))
        self.rect = self.surface.get_rect(
            bottomright=(Window_Width - Padding, Window_Height - Padding))
        self.display_surface = pygame.display.get_surface()

        # font
        self.font = pygame.font.Font(join('graphics', 'Russo_One.ttf'), 30)

        # increment
        self.increment_height = self.surface.get_height() / 3

        # data
        self.score = 0
        self.level = 1
        self.lines = 0

    def display_text(self, pos, text):
        text_surface = self.font.render(f'{text[0]}: {text[1]}', True, 'white')
        text_rext = text_surface.get_rect(center=pos)
        self.surface.blit(text_surface, text_rext)

    def run(self):
        self.surface.fill(Gray)
        for i, text in enumerate([('Score', self.score), ('Level', self.level), ('Lines', self.lines)]):
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            self.display_text((x, y), text)

        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, Line_Color, self.rect, 2, 2)


# PyTetris Script
class Main:
    def __init__(self):
        # general
        pygame.init()
        self.display_surface = pygame.display.set_mode((Window_Width, Window_Height))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Tetris')

        # shapes
        self.next_shapes = [choice(list(Tetrominos.keys())) for shape in range(3)]

        # components
        self.game = Game(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()

        # Check if pasued
        self.paused = False

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(Tetrominos.keys())))
        return next_shape

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # display
            self.display_surface.fill(Gray)

            # components
            self.game.run()
            self.score.run()
            self.preview.run(self.next_shapes)

            # updating the game
            pygame.display.update()
            self.clock.tick()


if __name__ == '__main__':
    main = Main()
    main.run()