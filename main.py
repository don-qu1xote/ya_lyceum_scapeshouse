import os
import sqlite3
import sys
import pygame
import sqlite3
from random import randint


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Mouse(pygame.sprite.Sprite):
    image = load_image("data/arrow.png")
    image = pygame.transform.scale(image, image.get_size())

    def __init__(self, group):
        super().__init__(group)
        self.image = Mouse.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEMOTION:
            x, y = args[0].pos
            self.rect.x, self.rect.y = x - self.image.get_size()[0] // 2, y - self.image.get_size()[1] // 2
        if not pygame.mouse.get_focused():
            self.rect.x, self.rect.y = -100, -100


class Level(pygame.sprite.Sprite):
    def __init__(self, group, level, mouse_sprites):
        sheet = load_image(f"data/coins{level}.png")
        sheet = pygame.transform.scale(sheet, sheet.get_size())
        columns, rows, x, y = 8, 1, 950 // 3 * (level - 1), 300
        super().__init__(group)
        self.mouse_sprites = mouse_sprites
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.p = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if pygame.sprite.collide_mask(self, self.mouse_sprites):
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if args:
                if args[0].type == pygame.MOUSEBUTTONDOWN:
                    self.p = True

    def __bool__(self):
        return self.p

    def regeneration(self):
        self.p = False


class GameOver(pygame.sprite.Sprite):
    image = load_image("data/gameover.png")
    image = pygame.transform.scale(image, image.get_size())

    def __init__(self, group):
        super().__init__(group)
        self.image = GameOver.image
        self.rect = self.image.get_rect()
        self.rect.width, self.rect.height = self.image.get_size()
        self.rect.x, self.rect.y = 0, 0


class Start(pygame.sprite.Sprite):
    image = load_image("data/start.png")
    image = pygame.transform.scale(image, image.get_size())

    def __init__(self, group):
        super().__init__(group)
        self.image = Start.image
        self.rect = self.image.get_rect()
        self.rect.width, self.rect.height = self.image.get_size()
        self.rect.x, self.rect.y = 0, 0


class AcceptOver(pygame.sprite.Sprite):
    image = load_image("data/ok.png")
    image = pygame.transform.scale(image, image.get_size())

    def __init__(self, group):
        super().__init__(group)
        self.image = AcceptOver.image
        self.rect = self.image.get_rect()
        self.rect.x = 950 / 2 - 75
        self.rect.y = 750 / 2 - 25

    def update(self, *args):
        self.r = args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos)

    def __bool__(self):
        return self.r

    def regeneration(self):
        self.r = False


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render_board(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, (255, 255, 255), (
                    self.left + j * self.cell_size, self.top + i * self.cell_size, self.cell_size, self.cell_size), 1)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        if self.left < x < self.left + self.width * self.cell_size and self.top < y < self.top + self.height * self.cell_size:
            row = (x - self.left) // self.cell_size
            col = (y - self.top) // self.cell_size
            return row, col
        return None

    def on_click(self, cell_coords):
        if cell_coords:
            row, col = cell_coords
            self.board[col][row] = 1 if self.board[col][row] == 0 else 0


class Game(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.collor = ["#ED354C", "#FA50CB", "#A553E0", "#524FF7", "#4BA3F0"]
        self.board = [[randint(0, len(self.collor) - 1) for _ in range(width)] for _ in range(height)]
        self.anime = []
        self.frame = 0
        self.moves_count = 10
        self.score_count = 0
        self.regeneration()
        self.anime = []
        self.frame = 0
        self.select = (-1, -1)
        self.level = 1
        self.max_1, self.max_2, self.max_3 = 0, 0, 0
        self.start = True
        self.on_game = False

        self.game_over_sprites = pygame.sprite.Group()
        GameOver(self.game_over_sprites)

        self.accept_sprites = pygame.sprite.Group()
        AcceptOver(self.accept_sprites)

        self.start_sprites = pygame.sprite.Group()
        Start(self.start_sprites)

        self.mouse_sprites = pygame.sprite.Group()
        mouse = Mouse(self.mouse_sprites)

        self.level1_sprites = pygame.sprite.Group()
        Level(self.level1_sprites, 1, mouse)

        self.level2_sprites = pygame.sprite.Group()
        Level(self.level2_sprites, 2, mouse)

        self.level3_sprites = pygame.sprite.Group()
        Level(self.level3_sprites, 3, mouse)

    def set_complexity(self, level):
        self.collor = [["#ED354C", "#FA50CB", "#E153E0", "#524FF7", "#4BA3F0"],
                       ["#3C90DE", "#3FC3E8", "#42D1CB", "#3FE8B0", "#3CDE7A"],
                       ["#6ADE43", "#E8E446", "#E0BA4F", "#F7984A", "#F05543"]][level - 1]
        self.moves_count = 20 // level
        self.level = level
        self.start = False
        self.on_game = True

    def make_none(self, target_coords):
        yt, xt = target_coords
        if 0 <= yt < self.height and 0 <= xt < self.width:
            if self.board[yt][xt] == "":
                return
            if str(self.board[yt][xt]).isnumeric():
                self.board[yt][xt] = ""
            elif self.board[yt][xt] == "*":
                y, x = randint(0, self.height - 1), randint(0, self.width - 1)
                while self.board[y][x]:
                    self.star_click(target_coords, (y, x))
            elif self.board[yt][xt] == "+":
                self.bomb_click(target_coords, target_coords)
            elif self.board[yt][xt] == "|":
                self.vertical_rocket_click(target_coords, target_coords)
            elif self.board[yt][xt] == "-":
                self.horizontal_rocket_click(target_coords, target_coords)
            elif self.board[yt][xt] == ">":
                self.airplane_click(target_coords, target_coords)

    def save_board(self):
        if [[i[:] for i in self.board[:]]][0] not in self.anime:
            self.anime += [[i[:] for i in self.board[:]]]

    def regeneration(self):
        while self.check(bool=True) and self.has_moves():
            self.board = [[randint(0, len(self.collor) - 1) for _ in range(self.width)] for _ in range(self.height)]
        self.score_count = 0
        self.anime = []
        self.frame = 0

    def has_result(self, coords_1, coords_2):
        board = [i[:] for i in self.board[:]]
        y1, x1 = coords_1
        y2, x2 = coords_2
        self.board[y1][x1], self.board[y2][x2] = self.board[y2][x2], self.board[y1][x1]
        if self.check(selected_coords_1=coords_1, selected_coords_2=coords_2, bool=True):
            self.board = [i[:] for i in board[:]]
            return True
        self.board = board
        return False

    def has_moves(self):
        for i in range(self.height):
            for j in range(self.width - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return True
        for i in range(self.height - 1):
            for j in range(self.width):
                if self.board[i][j] == self.board[i + 1][j]:
                    return True
        return False

    def star_click(self, star_coords=(-1, -1), target_coords=(-1, -1)):
        ys, xs = star_coords
        yt, xt = target_coords
        self.board[xs][ys] = ""
        target = self.board[xt][yt]
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == target:
                    self.make_none((i, j))
                    self.score_count += 1
        self.down()
        self.check()

    def bomb_click(self, bomb_coords=(-1, -1), target_coords=(-1, -1)):
        ys, xs = bomb_coords
        yt, xt = target_coords
        self.board[xs][ys] = ""
        self.board[xt][yt] = ""
        self.score_count += 1
        for i in range(self.height):
            for j in range(self.width):
                if (i - xt) ** 2 + (j - yt) ** 2 <= 4:
                    self.make_none((i, j))
                    self.score_count += 1
        self.down()
        self.check()

    def vertical_rocket_click(self, rocket_coords=(-1, -1), target_coords=(-1, -1)):
        yr, xr = rocket_coords
        yt, xt = target_coords
        self.board[xr][yr], self.board[xt][yt] = self.board[xt][yt], self.board[xr][yr]
        self.board[xt][yt] = ""
        for i in range(self.height):
            self.make_none((i, yt))
            self.score_count += 1
        self.down()
        self.check()

    def horizontal_rocket_click(self, rocket_coords=(-1, -1), target_coords=(-1, -1)):
        yr, xr = rocket_coords
        yt, xt = target_coords
        self.board[xr][yr], self.board[xt][yt] = self.board[xt][yt], self.board[xr][yr]
        self.board[xt][yt] = ""
        for j in range(self.width):
            self.make_none((xt, j))
            self.score_count += 1
        self.down()
        self.check()

    def airplane_click(self, airplane_coords=(-1, -1), target_coords=(-1, -1)):
        ys, xs = airplane_coords
        yt, xt = target_coords
        self.board[xs][ys] = ""
        sosedi = [(xt, yt - 1), (xt - 1, yt), (xt + 1, yt), (xt, yt + 1)]
        self.board[xt][yt] = ""
        for i, j in sosedi:
            self.make_none((i, j))
            self.score_count += 1
        self.make_none((randint(0, self.height - 1), randint(0, self.width - 1)))
        self.score_count += 1
        self.down()
        self.check()

    def on_click(self, cell_coords):
        if not self.on_game:
            return
        if self.select == (-1, -1):
            self.select = cell_coords
        else:
            x1, y1 = self.select
            x2, y2 = cell_coords
            sosedi = [(x1, y1 - 1), (x1 - 1, y1), (x1 + 1, y1), (x1, y1 + 1)]
            if cell_coords in sosedi:

                if self.board[y1][x1] == "*":
                    self.moves_count -= 1
                    self.star_click(star_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "*":
                    self.moves_count -= 1
                    self.star_click(star_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "+":
                    self.moves_count -= 1
                    self.bomb_click(bomb_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "+":
                    self.moves_count -= 1
                    self.bomb_click(bomb_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "|":
                    self.moves_count -= 1
                    self.vertical_rocket_click(rocket_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "|":
                    self.moves_count -= 1
                    self.vertical_rocket_click(rocket_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "-":
                    self.moves_count -= 1
                    self.horizontal_rocket_click(rocket_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "-":
                    self.moves_count -= 1
                    self.horizontal_rocket_click(rocket_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == ">":
                    self.moves_count -= 1
                    self.airplane_click(airplane_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == ">":
                    self.moves_count -= 1
                    self.airplane_click(airplane_coords=cell_coords, target_coords=self.select)
                elif self.has_result((y1, x1), (y2, x2)):
                    self.moves_count -= 1
                    self.board[y1][x1], self.board[y2][x2] = self.board[y2][x2], self.board[y1][x1]
                    self.check(self.check(selected_coords_1=(y1, x1), selected_coords_2=(y2, x2)))
                self.select = (-1, -1)
            elif self.select == cell_coords:
                if self.board[y1][x1] == "*":
                    self.moves_count -= 1
                    self.star_click(star_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "*":
                    self.moves_count -= 1
                    self.star_click(star_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "+":
                    self.moves_count -= 1
                    self.bomb_click(bomb_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "+":
                    self.moves_count -= 1
                    self.bomb_click(bomb_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "|":
                    self.moves_count -= 1
                    self.vertical_rocket_click(rocket_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "|":
                    self.moves_count -= 1
                    self.vertical_rocket_click(rocket_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == "-":
                    self.moves_count -= 1
                    self.horizontal_rocket_click(rocket_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == "-":
                    self.moves_count -= 1
                    self.horizontal_rocket_click(rocket_coords=cell_coords, target_coords=self.select)
                elif self.board[y1][x1] == ">":
                    self.moves_count -= 1
                    self.airplane_click(airplane_coords=self.select, target_coords=cell_coords)
                elif self.board[y2][x2] == ">":
                    self.moves_count -= 1
                    self.airplane_click(airplane_coords=cell_coords, target_coords=self.select)
                self.select = (-1, -1)
            else:
                self.select = cell_coords

        if self.moves_count == -1:
            con = sqlite3.connect("data/tri.db")
            cur = con.cursor()
            result = cur.execute(f"""select od, dv, tr from levels
                                                                    where id = 0""").fetchall()
            for i in result:
                k = [*i]
            con.commit()
            con.close()
            self.on_game = False
            self.regeneration()
            if self.level == 1:
                self.max_1 = max(k[0], self.score_count)
            if self.level == 2:
                self.max_2 = max(k[1], self.score_count)
            if self.level == 3:
                self.max_3 = max(k[2], self.score_count)
            con = sqlite3.connect("data/tri.db")
            cur = con.cursor()
            result = cur.execute(f"""UPDATE levels SET od = {self.max_1}, dv = {self.max_2}, tr = {self.max_3}
                                        where id = 0""").fetchall()
            con.commit()
            con.close()

    def check(self, selected_coords_1=(-1, -1), selected_coords_2=(-1, -1), bool=False):
        while True:
            replacement = False

            for i in range(self.height):
                for j in range(self.width - 4):
                    if self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2] == \
                            self.board[i][j + 3] == self.board[i][j + 4]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i, j + 2), (i, j + 3), (i, j + 4)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i][j + 3] = self.board[i][j + 4] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "*"
                            self.score_count += 5 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i, j + 2), (i, j + 3), (i, j + 4)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i][j + 3] = self.board[i][j + 4] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "*"
                            self.score_count += 5 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i][j + 3] = self.board[i][j + 4] = ""
                            self.board[i][j] = "*"
                            self.score_count += 5 ** 2
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height - 4):
                for j in range(self.width):
                    if self.board[i][j] == self.board[i + 1][j] == self.board[i + 2][j] == \
                            self.board[i + 3][j] == self.board[i + 4][j]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i + 1, j), (i + 2, j), (i + 3, j), (i + 4, j)]:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = \
                                self.board[i + 3][j] = self.board[i + 4][j] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "*"
                            self.score_count += 5 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i + 1, j), (i + 2, j), (i + 3, j), (i + 4, j)]:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = \
                                self.board[i + 3][j] = self.board[i + 4][j] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "*"
                            self.score_count += 5 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = \
                                self.board[i + 3][j] = self.board[i + 4][j] = ""
                            self.board[i][j] = "*"
                            self.score_count += 5 ** 2
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height - 2):
                for j in range(self.width - 2):
                    # 0,0   0,1   0,2   1,0   2,0
                    if self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2] == \
                            self.board[i + 1][j] == self.board[i + 2][j]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j), (i + 2, j)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j] = self.board[i + 2][j] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j), (i + 2, j)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j] = self.board[i + 2][j] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j] = self.board[i + 2][j] = ""
                            self.board[i][j] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 0,0   0,1   0,2   1,1   2,1
                    elif self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2] == \
                            self.board[i + 1][j + 1] == self.board[i + 2][j + 1]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j + 1), (i + 2, j + 1)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 1] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j + 1), (i + 2, j + 1)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 1] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 1] = ""
                            self.board[i][j] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 0,0   0,1   0,2   1,2   2,2
                    elif self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2] == \
                            self.board[i + 1][j + 2] == self.board[i + 2][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j + 2), (i + 2, j + 2)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i, j + 2), (i + 1, j + 2), (i + 2, j + 2)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            self.board[i][j] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 1,0   1,1   0,2   1,2   2,2
                    elif self.board[i + 1][j] == self.board[i + 1][j + 1] == self.board[i][j + 2] == \
                            self.board[i + 1][j + 2] == self.board[i + 2][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i + 1, j), (i + 1, j + 1), (i, j + 2), (i + 1, j + 2),
                                                 (i + 2, j + 2)]:
                            self.board[i + 1][j] = self.board[i + 1][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i + 1, j), (i + 1, j + 1), (i, j + 2), (i + 1, j + 2),
                                                   (i + 2, j + 2)]:
                            self.board[i + 1][j] = self.board[i + 1][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i + 1][j] = self.board[i + 1][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            self.board[i + 1][j + 2] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 2,0   2,1   0,2   1,2   2,2
                    elif self.board[i + 2][j] == self.board[i + 2][j + 1] == self.board[i][j + 2] == \
                            self.board[i + 1][j + 2] == self.board[i + 2][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i + 2, j), (i + 2, j + 1), (i, j + 2), (i + 1, j + 2),
                                                 (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i + 2, j), (i + 2, j + 1), (i, j + 2), (i + 1, j + 2),
                                                   (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 2] = \
                                self.board[i + 1][j + 2] = self.board[i + 2][j + 2] = ""
                            self.board[i + 1][j + 2] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 2,0   2,1   0,1   1,1   2,2
                    elif self.board[i + 2][j] == self.board[i + 2][j + 1] == self.board[i][j + 1] == \
                            self.board[i + 1][j + 1] == self.board[i + 2][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i + 2, j), (i + 2, j + 1), (i, j + 1), (i + 1, j + 1),
                                                 (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 1] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i + 2, j), (i + 2, j + 1), (i, j + 1), (i + 1, j + 1),
                                                   (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 1] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j + 1] = \
                                self.board[i + 1][j + 1] = self.board[i + 2][j + 2] = ""
                            self.board[i + 1][j + 1] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 2,0   2,1   0,0   1,0   2,2
                    elif self.board[i + 2][j] == self.board[i + 2][j + 1] == self.board[i][j] == \
                            self.board[i + 1][j] == self.board[i + 2][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i + 2, j), (i + 2, j + 1), (i, j), (i + 1, j), (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i + 2, j), (i + 2, j + 1), (i, j), (i + 1, j), (i + 2, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 2][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i + 2][j] = self.board[i + 2][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 2][j + 2] = ""
                            self.board[i][j] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                    # 2,0   1,1   0,0   1,0   1,2
                    elif self.board[i + 2][j] == self.board[i + 1][j + 1] == self.board[i][j] == \
                            self.board[i + 1][j] == self.board[i + 1][j + 2]:
                        replacement = True
                        if selected_coords_1 in [(i + 2, j), (i + 1, j + 1), (i, j), (i + 1, j), (i + 1, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 1][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 1][j + 2] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        elif selected_coords_2 in [(i + 2, j), (i + 1, j + 1), (i, j), (i + 1, j), (i + 1, j + 2)]:
                            self.board[i + 2][j] = self.board[i + 1][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 1][j + 2] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "+"
                            self.score_count += 4 ** 2
                            self.down()
                        else:
                            self.board[i + 2][j] = self.board[i + 1][j + 1] = self.board[i][j] = \
                                self.board[i + 1][j] = self.board[i + 1][j + 2] = ""
                            self.board[i][j] = "+"
                            self.score_count += 4 ** 2
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height):
                for j in range(self.width - 3):
                    if self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2] == self.board[i][j + 3]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i, j + 2), (i, j + 3)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = self.board[i][j + 3] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "|"
                            self.score_count += 2 ** 3
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i, j + 2), (i, j + 3)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = self.board[i][j + 3] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "|"
                            self.score_count += 2 ** 3
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = self.board[i][j + 3] = ""
                            self.board[i][j] = "|"
                            self.score_count += 2 ** 3
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height - 3):
                for j in range(self.width):
                    if self.board[i][j] == self.board[i + 1][j] == self.board[i + 2][j] == self.board[i + 3][j]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i + 1, j), (i + 2, j), (i + 3, j)]:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = self.board[i + 3][j] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = "-"
                            self.score_count += 2 ** 3
                            self.down()
                        elif selected_coords_2 in [(i, j), (i + 1, j), (i + 2, j), (i + 3, j)]:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = self.board[i + 3][j] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = "-"
                            self.score_count += 2 ** 3
                            self.down()
                        else:
                            self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = self.board[i + 3][j] = ""
                            self.board[i][j] = "-"
                            self.score_count += 2 ** 3
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height - 1):
                for j in range(self.width - 1):
                    if self.board[i][j] == self.board[i][j + 1] == self.board[i + 1][j] == self.board[i + 1][j + 1]:
                        replacement = True
                        if selected_coords_1 in [(i, j), (i, j + 1), (i + 1, j), (i + 1, j + 1)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i + 1][j] = self.board[i + 1][
                                j + 1] = ""
                            x, y = selected_coords_1
                            self.board[x][y] = ">"
                            self.score_count += 2 ** 2
                            self.down()
                        elif selected_coords_2 in [(i, j), (i, j + 1), (i + 1, j), (i + 1, j + 1)]:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i + 1][j] = self.board[i + 1][
                                j + 1] = ""
                            x, y = selected_coords_2
                            self.board[x][y] = ">"
                            self.score_count += 2 ** 2
                            self.down()
                        else:
                            self.board[i][j] = self.board[i][j + 1] = self.board[i + 1][j] = self.board[i + 1][
                                j + 1] = ""
                            self.board[i][j] = ">"
                            self.score_count += 2 ** 2
                            self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height):
                for j in range(self.width - 2):
                    if self.board[i][j] == self.board[i][j + 1] == self.board[i][j + 2]:
                        replacement = True
                        self.board[i][j] = self.board[i][j + 1] = self.board[i][j + 2] = ""
                        self.score_count += 3
                        self.down()
            if replacement:
                if bool:
                    return bool
                continue

            for i in range(self.height - 2):
                for j in range(self.width):
                    if self.board[i][j] == self.board[i + 1][j] == self.board[i + 2][j]:
                        replacement = True
                        self.board[i][j] = self.board[i + 1][j] = self.board[i + 2][j] = ""
                        self.score_count += 3
                        self.down()
            if replacement:
                if bool:
                    return bool
                continue
            break
        return False

    def down(self):
        while any("" in mas for mas in self.board):
            for i in range(self.height - 1):
                for j in range(self.width):
                    if self.board[i + 1][j] == "":
                        self.board[i + 1][j], self.board[i][j] = self.board[i][j], self.board[i + 1][j]
                        self.save_board()
                    if self.board[i][j] == "" and i == 0:
                        self.board[i][j] = randint(0, len(self.collor) - 1)
        if not self.has_moves():
            self.regeneration()

    def render(self, screen):
        if self.on_game:
            if self.anime != [] and self.frame < len(self.anime):
                board = self.anime[self.frame]
                self.frame += 1
            else:
                board = [i[:] for i in self.board[:]]
            for i in range(self.height):
                for j in range(self.width):
                    if self.select == (j, i):
                        pygame.draw.rect(screen, (255, 255, 255),
                                         (self.left + j * self.cell_size + 2, self.top + i * self.cell_size + 2,
                                          self.cell_size - 4, self.cell_size - 4), 3)
                        pygame.draw.rect(screen, (0, 0, 0),
                                         (self.left + j * self.cell_size + 17, self.top + i * self.cell_size,
                                          self.cell_size - 34, self.cell_size))
                        pygame.draw.rect(screen, (0, 0, 0),
                                         (self.left + j * self.cell_size, self.top + i * self.cell_size + 17,
                                          self.cell_size, self.cell_size - 34))
                    if str(board[i][j]).isnumeric():
                        pygame.draw.circle(screen, self.collor[board[i][j]], (
                            self.left + j * self.cell_size + self.cell_size // 2,
                            self.top + i * self.cell_size + self.cell_size // 2), self.cell_size * 0.49 - 1)
                        pygame.draw.rect(screen, self.collor[(1 + board[i][j]) % len(self.collor)],
                                         (self.left + j * self.cell_size + self.cell_size * 0.3,
                                          self.top + i * self.cell_size + self.cell_size * 0.3,
                                          self.cell_size * 0.4, self.cell_size * 0.4))
                    elif board[i][j] == "*":
                        pygame.draw.polygon(screen, self.collor[0],
                                            [(self.left + j * self.cell_size + self.cell_size * 0.5,
                                              self.top + i * self.cell_size + self.cell_size * 0.1),
                                             (self.left + j * self.cell_size + self.cell_size * 0.27,
                                              self.top + i * self.cell_size + self.cell_size * 0.9),
                                             (self.left + j * self.cell_size + self.cell_size * 0.9,
                                              self.top + i * self.cell_size + self.cell_size * 0.4),
                                             (self.left + j * self.cell_size + self.cell_size * 0.1,
                                              self.top + i * self.cell_size + self.cell_size * 0.4),
                                             (self.left + j * self.cell_size + self.cell_size * 0.73,
                                              self.top + i * self.cell_size + self.cell_size * 0.9)])
                        pygame.draw.circle(screen, self.collor[0], (
                            self.left + j * self.cell_size + self.cell_size // 2,
                            self.top + i * self.cell_size + self.cell_size * 0.55), self.cell_size * 0.19 - 1)
                    elif board[i][j] == "+":
                        pygame.draw.circle(screen, self.collor[0], (
                            self.left + j * self.cell_size + self.cell_size // 2,
                            self.top + i * self.cell_size + self.cell_size * 0.55), self.cell_size * 0.29 - 1)
                    elif board[i][j] == "-":
                        pygame.draw.polygon(screen, self.collor[0],
                                            [(self.left + j * self.cell_size + self.cell_size * 0.49,
                                              self.top + i * self.cell_size + self.cell_size * 0.1),
                                             (self.left + j * self.cell_size + self.cell_size * 0.1,
                                              self.top + i * self.cell_size + self.cell_size * 0.49),
                                             (self.left + j * self.cell_size + self.cell_size * 0.49,
                                              self.top + i * self.cell_size + self.cell_size * 0.88),
                                             (self.left + j * self.cell_size + self.cell_size * 0.88,
                                              self.top + i * self.cell_size + self.cell_size * 0.49)])
                        pygame.draw.rect(screen, (0, 0, 0),
                                         (self.left + j * self.cell_size + 30, self.top + i * self.cell_size,
                                          self.cell_size - 60, self.cell_size))
                    elif board[i][j] == "|":
                        pygame.draw.polygon(screen, self.collor[0],
                                            [(self.left + j * self.cell_size + self.cell_size * 0.49,
                                              self.top + i * self.cell_size + self.cell_size * 0.1),
                                             (self.left + j * self.cell_size + self.cell_size * 0.1,
                                              self.top + i * self.cell_size + self.cell_size * 0.49),
                                             (self.left + j * self.cell_size + self.cell_size * 0.49,
                                              self.top + i * self.cell_size + self.cell_size * 0.88),
                                             (self.left + j * self.cell_size + self.cell_size * 0.88,
                                              self.top + i * self.cell_size + self.cell_size * 0.49)])
                        pygame.draw.rect(screen, (0, 0, 0),
                                         (self.left + j * self.cell_size, self.top + i * self.cell_size + 30,
                                          self.cell_size, self.cell_size - 60))
                    elif board[i][j] == ">":
                        pygame.draw.polygon(screen, self.collor[0],
                                            [(self.left + j * self.cell_size + self.cell_size * 0.88,
                                              self.top + i * self.cell_size + self.cell_size * 0.5),
                                             (self.left + j * self.cell_size + self.cell_size * 0.12,
                                              self.top + i * self.cell_size + self.cell_size * 0.12),
                                             (self.left + j * self.cell_size + self.cell_size * 0.35,
                                              self.top + i * self.cell_size + self.cell_size * 0.5),
                                             (self.left + j * self.cell_size + self.cell_size * 0.12,
                                              self.top + i * self.cell_size + self.cell_size * 0.88)])

                    font = pygame.font.Font(None, 30)
                    text = font.render(f"число ходов:", True, (100, 100, 100))
                    text_x = self.left + self.width * self.cell_size + (200 - text.get_width()) // 2
                    text_y = 2 + 150
                    screen.blit(text, (text_x, text_y))

                    font = pygame.font.Font(None, 100)
                    text = font.render(f"{self.moves_count}", True, (100, 100, 100))
                    text_x = self.left + self.width * self.cell_size + (200 - text.get_width()) // 2
                    text_y = text.get_height() // 2 + 150
                    screen.blit(text, (text_x, text_y))

                    font = pygame.font.Font(None, 30)
                    text = font.render(f"баллы:", True, (100, 100, 100))
                    text_x = self.left + self.width * self.cell_size + (200 - text.get_width()) // 2
                    text_y = 2 + 450
                    screen.blit(text, (text_x, text_y))

                    font = pygame.font.Font(None, 100)
                    text = font.render(f"{self.score_count // 3}", True, (100, 100, 100))
                    text_x = self.left + self.width * self.cell_size + (200 - text.get_width()) // 2
                    text_y = text.get_height() // 2 + 450
                    screen.blit(text, (text_x, text_y))

    def spr(self, screen, vnt=None):
        clock.tick(v // fps)
        if not self.on_game:
            if self.start:
                self.start_sprites.draw(screen)

                con = sqlite3.connect("data/tri.db")
                cur = con.cursor()
                result = cur.execute(f"""select od, dv, tr from levels
                                                        where id = 0""").fetchall()
                for i in result:
                    k = [*i]
                for j in range(len(k)):
                        font = pygame.font.Font(None, 50)
                        text = font.render(f"{k[j]}", True, (100, 100, 100))
                        text_x = 950 // 3 * j
                        text_y = text.get_height() // 2 + 450
                        screen.blit(text, (text_x, text_y))
                con.commit()
                con.close()


                self.level1_sprites.draw(screen)
                self.level1_sprites.update()
                if vnt:
                    self.level1_sprites.update(vnt)
                    if self.level1_sprites.sprites()[0]:
                        self.set_complexity(1)
                        self.level1_sprites.sprites()[0].regeneration()


                self.level2_sprites.draw(screen)
                self.level2_sprites.update()
                if vnt:
                    self.level2_sprites.update(vnt)
                    if self.level2_sprites.sprites()[0]:
                        self.set_complexity(2)
                        self.level2_sprites.sprites()[0].regeneration()

                self.level3_sprites.draw(screen)
                self.level3_sprites.update()
                if vnt:
                    self.level3_sprites.update(vnt)
                    if self.level3_sprites.sprites()[0]:
                        self.set_complexity(3)
                        self.level3_sprites.sprites()[0].regeneration()

            else:
                self.game_over_sprites.draw(screen)

                self.accept_sprites.draw(screen)
                if vnt:
                    self.accept_sprites.update(vnt)
                    if self.accept_sprites.sprites()[0]:
                        self.start = True
                        self.on_game = False
                        self.accept_sprites.sprites()[0].regeneration()
            if vnt:
                self.mouse_sprites.update(vnt)


if __name__ == "__main__":
    pygame.init()
    size = screen_width, screen_height = 950, 750
    screen = pygame.display.set_mode(size)
    nazhali = board = Game(10, 10)
    board.set_view(25, 25, 70)
    pygame.display.set_caption("скейпсхаус")
    running = True
    v = 5000
    fps = 60
    clock = pygame.time.Clock()
    mouse_sprites = pygame.sprite.Group()
    Mouse(mouse_sprites)
    while running:
        screen.fill("#000000")
        board.spr(screen)
        for event in pygame.event.get():
            board.spr(screen, vnt=event)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                nazhali = 1
            if event.type == pygame.MOUSEBUTTONUP:
                if nazhali:
                    naznali = 0
                    board.get_click(event.pos)
        board.render(screen)
        pygame.display.flip()
        clock.tick(v // fps)
    pygame.quit()
