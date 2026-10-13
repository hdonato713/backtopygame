import pygame


# ============================================================================
# SETOR OMEGA: DESCIDA AO NUCLEO - VERSAO EXPANDIDA
# FPS pseudo-3D em um unico arquivo. Nao usa imagens, sons, mapas ou fontes
# externas. Todos os cenarios, monstros, efeitos e interfaces sao desenhados
# apenas com primitivas do pygame.
# ============================================================================

SCREEN_W = 960
SCREEN_H = 600
VIEW_W = 320
VIEW_H = 200
FPS = 60
MAP_SIZE = 25


def clamp(value, low, high):
    return max(low, min(high, value))


def shade(color, factor):
    return tuple(clamp(int(channel * factor), 0, 255) for channel in color)


def make_empty_floor():
    grid = []
    for y in range(MAP_SIZE):
        row = []
        for x in range(MAP_SIZE):
            row.append("1" if x in (0, MAP_SIZE - 1) or y in (0, MAP_SIZE - 1) else ".")
        grid.append(row)
    return grid


def wall_h(grid, y, x1, x2, material="1", gaps=()):
    for x in range(x1, x2 + 1):
        if x not in gaps:
            grid[y][x] = material


def wall_v(grid, x, y1, y2, material="1", gaps=()):
    for y in range(y1, y2 + 1):
        if y not in gaps:
            grid[y][x] = material


def build_maps():
    # Andar 1: laboratorios abandonados e uma camara trancada pelo cartao azul.
    floor0 = make_empty_floor()
    wall_v(floor0, 7, 1, 11, "2", (4, 9))
    wall_h(floor0, 11, 1, 15, "2", (3, 12))
    wall_v(floor0, 15, 1, 13, "3", (6,))
    wall_h(floor0, 14, 1, 23, "1", (5, 11, 18))
    wall_v(floor0, 10, 14, 23, "2", (17, 21))
    wall_h(floor0, 6, 9, 14, "4", (11,))
    wall_h(floor0, 18, 1, 9, "3", (4,))
    wall_v(floor0, 4, 18, 23, "3", (21,))
    # Camara do elevador/escada do primeiro andar.
    wall_h(floor0, 16, 17, 23, "3")
    wall_h(floor0, 22, 17, 23, "3")
    wall_v(floor0, 17, 16, 22, "3")
    wall_v(floor0, 23, 16, 22, "3")
    floor0[19][17] = "B"

    # Andar 2: alojamentos, enfermaria e acesso ao nucleo pelo cartao vermelho.
    floor1 = make_empty_floor()
    wall_h(floor1, 7, 1, 23, "2", (4, 13, 21))
    wall_v(floor1, 10, 1, 16, "3", (5, 11))
    wall_h(floor1, 13, 1, 18, "1", (3, 8, 14))
    wall_v(floor1, 18, 1, 14, "4", (4, 10))
    wall_v(floor1, 6, 13, 23, "2", (16, 21))
    wall_h(floor1, 19, 1, 15, "3", (4, 11))
    wall_v(floor1, 13, 14, 23, "1", (17, 22))
    # Camara do acesso ao terceiro andar.
    wall_h(floor1, 15, 16, 23, "4")
    wall_h(floor1, 22, 16, 23, "4")
    wall_v(floor1, 16, 15, 22, "4")
    wall_v(floor1, 23, 15, 22, "4")
    floor1[18][16] = "R"

    # Andar 3: nucleo de contencao. A saida X fica na parede externa direita.
    floor2 = make_empty_floor()
    wall_h(floor2, 6, 1, 23, "3", (3, 9, 17, 22))
    wall_v(floor2, 8, 1, 18, "2", (4, 10, 16))
    wall_v(floor2, 17, 6, 23, "4", (9, 15, 21))
    wall_h(floor2, 12, 8, 23, "1", (11, 19))
    wall_h(floor2, 18, 1, 17, "2", (3, 12))
    wall_v(floor2, 5, 18, 23, "3", (21,))
    wall_h(floor2, 21, 17, 23, "4", (20, 23))
    wall_v(floor2, 21, 12, 20, "3", (16,))
    floor2[21][24] = "X"

    return tuple(tuple("".join(row) for row in floor) for floor in (floor0, floor1, floor2))


MAPS = build_maps()
MAP_W = MAP_SIZE
MAP_H = MAP_SIZE

WALL_COLORS = {
    "1": (48, 75, 91),
    "2": (105, 45, 48),
    "3": (64, 48, 95),
    "4": (82, 82, 72),
    "B": (30, 103, 196),
    "R": (188, 39, 37),
    "X": (197, 151, 42),
}

FLOOR_NAMES = (
    "NIVEL 1 - LABORATORIOS",
    "NIVEL 2 - ALOJAMENTOS",
    "NIVEL 3 - NUCLEO",
)

ENEMY_DATA = {
    "rastejante": {
        "name": "RASTEJANTE",
        "hp": 35,
        "speed": 2.15,
        "damage": 5,
        "attack_delay": 0.58,
        "color": (89, 173, 78),
        "eye": (255, 244, 91),
        "scale": 0.48,
        "radius": 0.20,
        "detect": 7.5,
        "ranged": False,
    },
    "cacador": {
        "name": "CACADOR",
        "hp": 65,
        "speed": 1.58,
        "damage": 9,
        "attack_delay": 0.78,
        "color": (153, 39, 43),
        "eye": (255, 236, 142),
        "scale": 0.76,
        "radius": 0.24,
        "detect": 9.5,
        "ranged": False,
    },
    "demonio": {
        "name": "DEMONIO",
        "hp": 105,
        "speed": 1.02,
        "damage": 13,
        "attack_delay": 0.98,
        "color": (189, 57, 47),
        "eye": (255, 205, 51),
        "scale": 0.91,
        "radius": 0.27,
        "detect": 10.0,
        "ranged": False,
    },
    "bruto": {
        "name": "BRUTAMONTES",
        "hp": 220,
        "speed": 0.63,
        "damage": 21,
        "attack_delay": 1.25,
        "color": (118, 60, 145),
        "eye": (255, 93, 57),
        "scale": 1.10,
        "radius": 0.33,
        "detect": 8.0,
        "ranged": False,
    },
    "espectro": {
        "name": "ESPECTRO",
        "hp": 80,
        "speed": 1.34,
        "damage": 11,
        "attack_delay": 0.82,
        "color": (69, 138, 164),
        "eye": (176, 249, 255),
        "scale": 0.84,
        "radius": 0.22,
        "detect": 12.0,
        "ranged": False,
    },
    "atirador": {
        "name": "ATIRADOR",
        "hp": 90,
        "speed": 0.72,
        "damage": 8,
        "attack_delay": 1.28,
        "color": (185, 119, 42),
        "eye": (255, 48, 35),
        "scale": 0.82,
        "radius": 0.25,
        "detect": 11.0,
        "ranged": True,
    },
}

POWER_INFO = {
    "infinite": ("MUNICAO INFINITA", (255, 211, 65), 12.0),
    "rapid": ("CADENCIA MAXIMA", (255, 82, 55), 12.0),
    "speed": ("VELOCIDADE AUMENTADA", (75, 213, 255), 14.0),
}


class Player:
    def __init__(self):
        self.pos = pygame.Vector2(2.5, 2.5)
        self.direction = pygame.Vector2(1.0, 0.0)
        self.plane = pygame.Vector2(0.0, 0.66)
        self.radius = 0.20
        self.speed = 2.72
        self.health = 100
        self.max_health = 100


class Enemy:
    def __init__(self, floor, x, y, kind, hidden=False):
        data = ENEMY_DATA[kind]
        self.floor = floor
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.radius = data["radius"]
        self.attack_timer = 0.0
        self.hit_flash = 0.0
        self.alerted = False
        self.path_target = None
        self.path_timer = 0.0
        self.hidden = hidden
        self.just_revealed = 0.0

    @property
    def alive(self):
        return self.hp > 0


class Pickup:
    def __init__(self, floor, x, y, kind):
        self.floor = floor
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        self.active = True
        self.respawn_timer = 0.0


class Stair:
    def __init__(self, floor, x, y, target_floor, target_x, target_y, direction):
        self.floor = floor
        self.pos = pygame.Vector2(x, y)
        self.target_floor = target_floor
        self.target_pos = pygame.Vector2(target_x, target_y)
        self.direction = direction


class Missile:
    def __init__(self, floor, pos, direction):
        self.floor = floor
        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction).normalize()
        self.speed = 5.9
        self.age = 0.0
        self.alive = True


class Explosion:
    def __init__(self, floor, pos):
        self.floor = floor
        self.pos = pygame.Vector2(pos)
        self.age = 0.0
        self.duration = 0.56


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Setor Omega: Descida ao Nucleo")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.view = pygame.Surface((VIEW_W, VIEW_H)).convert()
        self.clock = pygame.time.Clock()
        self.font_tiny = pygame.font.Font(None, 19)
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 34)
        self.font_large = pygame.font.Font(None, 69)
        self.font_title = pygame.font.Font(None, 84)
        self.running = True
        self.mouse_captured = False
        self.first_mouse_motion = True
        self.show_map = False
        self.rng_state = 90210
        self.reset_game(show_intro=True)

    # ------------------------------------------------------------------
    # Criacao e estado geral
    # ------------------------------------------------------------------
    def make_enemies(self):
        # floor, x, y, tipo, escondido. Os escondidos despertam quando o
        # jogador chega perto, criando emboscadas sem qualquer asset externo.
        data = (
            (0, 5.5, 3.5, "rastejante", False),
            (0, 10.5, 3.5, "cacador", False),
            (0, 12.5, 8.5, "demonio", False),
            (0, 20.5, 5.5, "atirador", False),
            (0, 3.5, 12.5, "espectro", True),
            (0, 7.5, 16.5, "rastejante", True),
            (0, 13.5, 17.5, "bruto", False),
            (0, 21.5, 18.5, "cacador", True),
            (1, 4.5, 4.5, "cacador", False),
            (1, 13.5, 3.5, "espectro", True),
            (1, 21.5, 3.5, "atirador", False),
            (1, 7.5, 9.5, "rastejante", False),
            (1, 14.5, 9.5, "demonio", False),
            (1, 21.5, 10.5, "bruto", True),
            (1, 3.5, 16.5, "espectro", True),
            (1, 21.5, 20.5, "demonio", True),
            (2, 3.5, 3.5, "rastejante", False),
            (2, 11.5, 3.5, "espectro", True),
            (2, 20.5, 3.5, "atirador", False),
            (2, 13.5, 9.5, "demonio", True),
            (2, 22.5, 9.5, "bruto", False),
            (2, 11.5, 15.5, "espectro", False),
            (2, 8.5, 20.5, "demonio", False),
            (2, 22.5, 22.5, "atirador", False),
        )
        return [Enemy(*entry) for entry in data]

    def make_pickups(self):
        return [
            Pickup(0, 4.5, 8.5, "medkit"),
            Pickup(0, 11.5, 7.5, "infinite"),
            Pickup(0, 3.5, 15.5, "speed"),
            Pickup(0, 13.5, 20.5, "rapid"),
            Pickup(0, 21.5, 3.5, "blue_key"),
            Pickup(1, 3.5, 10.5, "medkit"),
            Pickup(1, 14.5, 5.5, "rapid"),
            Pickup(1, 8.5, 16.5, "infinite"),
            Pickup(1, 20.5, 12.5, "speed"),
            Pickup(1, 21.5, 5.5, "red_key"),
            Pickup(2, 5.5, 5.5, "medkit"),
            Pickup(2, 11.5, 10.5, "speed"),
            Pickup(2, 19.5, 9.5, "rapid"),
            Pickup(2, 3.5, 20.5, "infinite"),
            Pickup(2, 19.5, 19.5, "medkit"),
        ]

    def make_stairs(self):
        return [
            Stair(0, 20.5, 19.5, 1, 2.5, 2.5, "SUBIR"),
            Stair(1, 2.5, 2.5, 0, 20.5, 19.5, "DESCER"),
            Stair(1, 20.5, 18.5, 2, 2.5, 21.5, "SUBIR"),
            Stair(2, 2.5, 21.5, 1, 20.5, 18.5, "DESCER"),
        ]

    def reset_game(self, show_intro=False):
        self.player = Player()
        self.current_floor = 0
        self.enemies = self.make_enemies()
        self.pickups = self.make_pickups()
        self.stairs = self.make_stairs()
        self.missiles = []
        self.explosions = []
        self.keys_owned = {"blue": False, "red": False}
        self.power_timers = {"infinite": 0.0, "rapid": 0.0, "speed": 0.0}
        self.state = "intro" if show_intro else "playing"
        self.ammo = 18
        self.magazine_size = 18
        self.reload_timer = 0.0
        self.fire_timer = 0.0
        self.missile_timer = 0.0
        self.muzzle_timer = 0.0
        self.hit_marker_timer = 0.0
        self.damage_flash = 0.0
        self.recoil = 0.0
        self.pitch = 0.0
        self.enemy_grace_timer = 1.25
        self.stair_cooldown = 0.0
        self.interact_ready = True
        self.walk_clock = 0.0
        self.walk_amount = 0.0
        self.message = ""
        self.message_timer = 0.0
        self.total_kills = 0
        self.exit_unlocked = False
        self.z_buffer = [1000.0] * VIEW_W
        self.show_map = False
        self.scare_timer = 0.0
        self.blackout_timer = 0.0
        self.floor_banner_timer = 0.0
        self.ambush_flags = {"blue": False, "red": False, "core": False}
        self.light_flicker = 0
        self.flicker_clock = 0.0
        self.ambient_clock = 7.0
        self.set_mouse_capture(not show_intro)

    def set_mouse_capture(self, captured):
        self.mouse_captured = captured
        pygame.event.set_grab(captured)
        pygame.mouse.set_visible(not captured)
        pygame.mouse.get_rel()
        self.first_mouse_motion = True

    def start_playing(self):
        self.state = "playing"
        self.set_mouse_capture(True)

    def notify(self, text, duration=1.7):
        self.message = text
        self.message_timer = duration

    def rand(self):
        self.rng_state = (1664525 * self.rng_state + 1013904223) & 0xFFFFFFFF
        return self.rng_state / 4294967296.0

    def living_enemies(self, floor=None):
        return sum(
            1 for enemy in self.enemies
            if enemy.alive and (floor is None or enemy.floor == floor)
        )

    # ------------------------------------------------------------------
    # Mapa, portas, colisao e raycasting
    # ------------------------------------------------------------------
    def map_cell(self, x, y, floor=None):
        if floor is None:
            floor = self.current_floor
        ix = int(x)
        iy = int(y)
        if ix < 0 or iy < 0 or ix >= MAP_W or iy >= MAP_H:
            return "1"
        return MAPS[floor][iy][ix]

    def is_wall_cell(self, cell):
        if cell == ".":
            return False
        if cell == "B" and self.keys_owned["blue"]:
            return False
        if cell == "R" and self.keys_owned["red"]:
            return False
        return True

    def is_blocked(self, x, y, radius=0.18, floor=None):
        if floor is None:
            floor = self.current_floor
        points = (
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius),
        )
        return any(self.is_wall_cell(self.map_cell(px, py, floor)) for px, py in points)

    def move_with_collision(self, pos, movement, radius, floor):
        new_x = pos.x + movement.x
        if not self.is_blocked(new_x, pos.y, radius, floor):
            pos.x = new_x
        new_y = pos.y + movement.y
        if not self.is_blocked(pos.x, new_y, radius, floor):
            pos.y = new_y

    def player_position_clear(self, x, y):
        if self.is_blocked(x, y, self.player.radius):
            return False
        candidate = pygame.Vector2(x, y)
        for enemy in self.enemies:
            if not enemy.alive or enemy.hidden or enemy.floor != self.current_floor:
                continue
            minimum = (self.player.radius + enemy.radius) * 0.84
            if candidate.distance_squared_to(enemy.pos) < minimum * minimum:
                return False
        return True

    def move_player_with_collision(self, movement):
        new_x = self.player.pos.x + movement.x
        if self.player_position_clear(new_x, self.player.pos.y):
            self.player.pos.x = new_x
        new_y = self.player.pos.y + movement.y
        if self.player_position_clear(self.player.pos.x, new_y):
            self.player.pos.y = new_y

    def next_path_step(self, start_position, goal_position, floor):
        start = (int(start_position.x), int(start_position.y))
        goal = (int(goal_position.x), int(goal_position.y))
        if start == goal:
            return pygame.Vector2(goal[0] + 0.5, goal[1] + 0.5)
        queue = [start]
        queue_index = 0
        parents = {start: None}
        while queue_index < len(queue):
            current = queue[queue_index]
            queue_index += 1
            if current == goal:
                break
            x, y = current
            for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if neighbor in parents:
                    continue
                if self.is_wall_cell(self.map_cell(neighbor[0], neighbor[1], floor)):
                    continue
                parents[neighbor] = current
                queue.append(neighbor)
        if goal not in parents:
            return None
        step = goal
        while parents[step] is not None and parents[step] != start:
            step = parents[step]
        return pygame.Vector2(step[0] + 0.5, step[1] + 0.5)

    def cast_ray(self, origin, ray_direction, floor=None, maximum_steps=90):
        if floor is None:
            floor = self.current_floor
        map_x = int(origin.x)
        map_y = int(origin.y)
        ray_x = ray_direction.x
        ray_y = ray_direction.y
        delta_x = abs(1.0 / ray_x) if abs(ray_x) > 0.000001 else 1000000.0
        delta_y = abs(1.0 / ray_y) if abs(ray_y) > 0.000001 else 1000000.0
        if ray_x < 0:
            step_x = -1
            side_x = (origin.x - map_x) * delta_x
        else:
            step_x = 1
            side_x = (map_x + 1.0 - origin.x) * delta_x
        if ray_y < 0:
            step_y = -1
            side_y = (origin.y - map_y) * delta_y
        else:
            step_y = 1
            side_y = (map_y + 1.0 - origin.y) * delta_y
        side = 0
        hit_cell = "1"
        distance = 1000.0
        for _ in range(maximum_steps):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
                distance = side_x - delta_x
            else:
                side_y += delta_y
                map_y += step_y
                side = 1
                distance = side_y - delta_y
            hit_cell = self.map_cell(map_x, map_y, floor)
            if self.is_wall_cell(hit_cell):
                break
        distance = max(0.0001, distance)
        wall_position = (
            origin.y + distance * ray_y if side == 0
            else origin.x + distance * ray_x
        )
        wall_position -= int(wall_position)
        return distance, side, hit_cell, wall_position

    def has_line_of_sight(self, start, end, floor=None):
        if floor is None:
            floor = self.current_floor
        offset = end - start
        distance = offset.length()
        if distance <= 0.001:
            return True
        ray_distance, _, _, _ = self.cast_ray(start, offset / distance, floor)
        return ray_distance + 0.06 >= distance

    # ------------------------------------------------------------------
    # Entrada, tiros e interacoes
    # ------------------------------------------------------------------
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                        self.set_mouse_capture(False)
                    elif self.state == "paused":
                        self.start_playing()
                    elif self.state == "intro":
                        self.running = False
                    elif self.state in ("dead", "won"):
                        self.running = False
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.state in ("intro", "paused"):
                        self.start_playing()
                    elif self.state in ("dead", "won"):
                        self.reset_game(show_intro=False)
                elif event.key == pygame.K_r and self.state == "playing":
                    self.start_reload()
                elif event.key == pygame.K_e and self.state == "playing":
                    if self.interact_ready:
                        self.interact_ready = False
                        self.try_interact()
                elif event.key == pygame.K_m:
                    self.show_map = not self.show_map
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    self.interact_ready = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state in ("intro", "paused"):
                    self.start_playing()
                elif self.state == "playing":
                    if event.button == 1:
                        self.shoot()
                    elif event.button == 3:
                        self.launch_missile()
            elif event.type == pygame.MOUSEMOTION and self.state == "playing":
                if self.first_mouse_motion:
                    self.first_mouse_motion = False
                    continue
                turn = event.rel[0] * 0.105
                self.player.direction.rotate_ip(turn)
                self.player.plane.rotate_ip(turn)
                self.pitch = clamp(self.pitch - event.rel[1] * 0.07, -48.0, 48.0)
            elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -999):
                if self.state == "playing":
                    self.state = "paused"
                    self.set_mouse_capture(False)

    def nearby_stair(self):
        closest = None
        closest_distance = 999.0
        for stair in self.stairs:
            if stair.floor != self.current_floor:
                continue
            distance = self.player.pos.distance_to(stair.pos)
            if distance < 0.85 and distance < closest_distance:
                closest = stair
                closest_distance = distance
        return closest

    def near_exit(self):
        return (
            self.current_floor == 2
            and self.player.pos.distance_squared_to(pygame.Vector2(24.0, 21.5)) < 1.35 * 1.35
        )

    def try_interact(self):
        if self.stair_cooldown > 0.0:
            return
        stair = self.nearby_stair()
        if stair is None and self.near_exit():
            if self.living_enemies() > 0:
                self.notify("SAIDA BLOQUEADA - " + str(self.living_enemies()) + " AMEACAS", 1.4)
            elif not (self.keys_owned["blue"] and self.keys_owned["red"]):
                self.notify("CREDENCIAIS INCOMPLETAS", 1.2)
            elif not self.exit_unlocked:
                self.notify("SISTEMA DA SAIDA AINDA BLOQUEADO", 1.0)
            else:
                self.state = "won"
                self.set_mouse_capture(False)
            return
        if stair is None:
            self.notify("NENHUM ACESSO POR PERTO", 0.75)
            return
        self.current_floor = stair.target_floor
        self.player.pos = pygame.Vector2(stair.target_pos)
        self.player.direction = pygame.Vector2(1.0, 0.0)
        self.player.plane = pygame.Vector2(0.0, 0.66)
        self.missiles = []
        self.explosions = []
        self.stair_cooldown = 0.8
        self.enemy_grace_timer = 0.65
        self.floor_banner_timer = 2.2
        self.blackout_timer = 0.25
        self.notify(FLOOR_NAMES[self.current_floor], 1.8)

    def start_reload(self):
        if self.reload_timer > 0.0:
            return
        if self.power_timers["infinite"] > 0.0:
            self.ammo = self.magazine_size
            self.notify("MUNICAO INFINITA ATIVA", 0.8)
            return
        if self.ammo >= self.magazine_size:
            self.notify("O PENTE JA ESTA CHEIO", 0.9)
            return
        self.reload_timer = 1.22
        self.notify("RECARREGANDO...", 1.2)

    def shoot(self):
        if self.fire_timer > 0.0 or self.reload_timer > 0.0:
            return
        infinite = self.power_timers["infinite"] > 0.0
        rapid = self.power_timers["rapid"] > 0.0
        if self.ammo <= 0 and not infinite:
            self.notify("SEM BALAS - PRESSIONE R", 1.2)
            return
        if not infinite:
            self.ammo -= 1
        self.fire_timer = 0.072 if rapid else 0.215
        self.muzzle_timer = 0.062
        self.recoil = min(1.5, self.recoil + (0.40 if rapid else 1.0))
        wall_distance, _, _, _ = self.cast_ray(self.player.pos, self.player.direction)
        target = None
        target_distance = 1000.0
        for enemy in self.enemies:
            if (
                not enemy.alive or enemy.hidden
                or enemy.floor != self.current_floor
            ):
                continue
            to_enemy = enemy.pos - self.player.pos
            along = to_enemy.dot(self.player.direction)
            if along <= 0.0:
                continue
            lateral_squared = max(0.0, to_enemy.length_squared() - along * along)
            hit_radius = enemy.radius + 0.035
            if lateral_squared > hit_radius * hit_radius:
                continue
            half_chord = (hit_radius * hit_radius - lateral_squared) ** 0.5
            if along - half_chord >= wall_distance - 0.001:
                continue
            projected = self.project_point(enemy.pos)
            if projected is None:
                continue
            _, depth = projected
            sprite_height = clamp(
                int(VIEW_H * ENEMY_DATA[enemy.kind]["scale"] / depth),
                4,
                VIEW_H * 3,
            )
            horizon = clamp(VIEW_H // 2 + int(self.pitch / 2.0), 24, VIEW_H - 24)
            sprite_top = horizon - sprite_height * 0.55
            sprite_bottom = sprite_top + sprite_height
            if not sprite_top - 2 <= VIEW_H // 2 <= sprite_bottom + 2:
                continue
            if along < target_distance:
                target = enemy
                target_distance = along
        if target is not None:
            damage = 23 if rapid else 27
            was_alive = target.alive
            target.hp = max(0, target.hp - damage)
            target.hit_flash = 0.12
            target.alerted = True
            self.hit_marker_timer = 0.11
            if was_alive and not target.alive:
                self.total_kills += 1
                self.notify(ENEMY_DATA[target.kind]["name"] + " ELIMINADO", 1.0)

    def launch_missile(self):
        if self.missile_timer > 0.0:
            self.notify("PLASMA RECARREGANDO", 0.65)
            return
        start = self.player.pos + self.player.direction * 0.36
        if self.is_blocked(start.x, start.y, 0.08):
            self.notify("SEM ESPACO PARA LANCAR", 0.8)
            return
        self.missiles.append(Missile(self.current_floor, start, self.player.direction))
        self.missile_timer = 2.25
        self.recoil = 1.5
        self.notify("MISSIL DE PLASMA", 0.6)

    # ------------------------------------------------------------------
    # Atualizacao
    # ------------------------------------------------------------------
    def update(self, dt):
        dt = min(dt, 0.05)
        if self.state != "playing":
            return
        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.missile_timer = max(0.0, self.missile_timer - dt)
        self.muzzle_timer = max(0.0, self.muzzle_timer - dt)
        self.hit_marker_timer = max(0.0, self.hit_marker_timer - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)
        self.recoil = max(0.0, self.recoil - dt * 7.8)
        self.message_timer = max(0.0, self.message_timer - dt)
        self.enemy_grace_timer = max(0.0, self.enemy_grace_timer - dt)
        self.stair_cooldown = max(0.0, self.stair_cooldown - dt)
        self.scare_timer = max(0.0, self.scare_timer - dt)
        self.blackout_timer = max(0.0, self.blackout_timer - dt)
        self.floor_banner_timer = max(0.0, self.floor_banner_timer - dt)
        for key in self.power_timers:
            self.power_timers[key] = max(0.0, self.power_timers[key] - dt)
        self.flicker_clock -= dt
        if self.flicker_clock <= 0.0:
            self.flicker_clock = 0.055 + self.rand() * 0.12
            self.light_flicker = int(self.rand() * 20)
            if self.rand() < 0.025:
                self.blackout_timer = max(self.blackout_timer, 0.07 + self.rand() * 0.08)
        self.ambient_clock -= dt
        if self.ambient_clock <= 0.0:
            self.ambient_clock = 7.0 + self.rand() * 9.0
            if self.living_enemies(self.current_floor) > 0 and self.message_timer <= 0.0:
                messages = (
                    "VOCE OUVE PASSOS NO ESCURO",
                    "ALGO SE MOVE ATRAS DAS PAREDES",
                    "O SISTEMA DE LUZES ESTA FALHANDO",
                )
                self.notify(messages[int(self.rand() * len(messages)) % len(messages)], 1.45)

        if self.reload_timer > 0.0:
            self.reload_timer -= dt
            if self.reload_timer <= 0.0:
                self.reload_timer = 0.0
                self.ammo = self.magazine_size
                self.notify("ARMA CARREGADA", 0.75)

        # Segurar o botao so vira fogo automatico durante o powerup de cadencia.
        if self.power_timers["rapid"] > 0.0 and pygame.mouse.get_pressed(3)[0]:
            self.shoot()

        self.update_player(dt)
        self.update_enemies(dt)
        if self.state != "playing":
            return
        self.update_missiles(dt)
        self.update_pickups(dt)
        self.update_explosions(dt)
        self.update_objective()

    def update_player(self, dt):
        keys = pygame.key.get_pressed()
        forward_value = int(keys[pygame.K_w]) - int(keys[pygame.K_s])
        strafe_value = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        movement = pygame.Vector2()
        if forward_value:
            movement += self.player.direction * forward_value
        if strafe_value:
            right = pygame.Vector2(-self.player.direction.y, self.player.direction.x)
            movement += right * strafe_value
        moving = movement.length_squared() > 0.0
        if moving:
            speed_factor = 1.72 if self.power_timers["speed"] > 0.0 else 1.0
            movement = movement.normalize() * self.player.speed * speed_factor * dt
            self.move_player_with_collision(movement)
            self.walk_clock = (self.walk_clock + dt * 320.0 * speed_factor) % 360.0
            self.walk_amount = min(1.0, self.walk_amount + dt * 8.0)
        else:
            self.walk_amount = max(0.0, self.walk_amount - dt * 8.0)

    def reveal_enemy(self, enemy):
        enemy.hidden = False
        enemy.alerted = True
        enemy.just_revealed = 0.8
        enemy.attack_timer = max(enemy.attack_timer, 0.55)
        self.enemy_grace_timer = max(self.enemy_grace_timer, 0.24)
        self.scare_timer = max(self.scare_timer, 0.9)
        self.blackout_timer = max(self.blackout_timer, 0.16)
        self.notify("MOVIMENTO DETECTADO!", 0.9)

    def wake_floor_ambush(self, floor, flag, message):
        if self.ambush_flags[flag]:
            return 0
        self.ambush_flags[flag] = True
        awakened = 0
        for enemy in self.enemies:
            if enemy.alive and enemy.hidden and enemy.floor == floor:
                enemy.hidden = False
                enemy.alerted = True
                enemy.just_revealed = 0.95
                enemy.attack_timer = 0.72
                awakened += 1
        if awakened:
            self.enemy_grace_timer = max(self.enemy_grace_timer, 0.42)
            self.scare_timer = max(self.scare_timer, 1.05)
            self.blackout_timer = max(self.blackout_timer, 0.34)
            self.notify(message, 1.25)
        return awakened

    def damage_player(self, amount, message="VOCE FOI ATINGIDO!"):
        self.player.health = max(0, self.player.health - amount)
        self.damage_flash = 0.24
        self.notify(message, 0.65)
        if self.player.health <= 0:
            self.state = "dead"
            self.set_mouse_capture(False)

    def update_enemies(self, dt):
        # A travessia obrigatoria do nucleo aciona a ultima emboscada. Assim,
        # nenhum inimigo dormente fica perdido para sempre em uma sala opcional.
        if (
            self.current_floor == 2 and not self.ambush_flags["core"]
            and (self.player.pos.x > 7.0 or self.player.pos.y < 17.0)
        ):
            self.wake_floor_ambush(2, "core", "O NUCLEO ACORDOU!")
        for enemy in self.enemies:
            if not enemy.alive or enemy.floor != self.current_floor:
                continue
            enemy.attack_timer = max(0.0, enemy.attack_timer - dt)
            enemy.hit_flash = max(0.0, enemy.hit_flash - dt)
            enemy.path_timer = max(0.0, enemy.path_timer - dt)
            enemy.just_revealed = max(0.0, enemy.just_revealed - dt)
            if enemy.hidden:
                trigger_radius = 3.8 if enemy.kind in ("cacador", "rastejante") else 3.15
                if enemy.pos.distance_squared_to(self.player.pos) < trigger_radius * trigger_radius:
                    self.reveal_enemy(enemy)
                continue
        if self.enemy_grace_timer > 0.0:
            return

        for enemy in self.enemies:
            if (
                not enemy.alive or enemy.hidden
                or enemy.floor != self.current_floor
            ):
                continue
            to_player = self.player.pos - enemy.pos
            distance_squared = to_player.length_squared()
            if distance_squared <= 0.0001:
                continue
            distance = distance_squared ** 0.5
            data = ENEMY_DATA[enemy.kind]
            can_see = (
                distance < data["detect"]
                and self.has_line_of_sight(enemy.pos, self.player.pos, enemy.floor)
            )
            if can_see or distance < 1.8:
                enemy.alerted = True
            if not enemy.alerted:
                continue

            if can_see:
                direction = to_player / distance
                enemy.path_target = None
                enemy.path_timer = 0.0
            else:
                if (
                    enemy.path_target is None
                    or enemy.path_timer <= 0.0
                    or enemy.pos.distance_squared_to(enemy.path_target) < 0.04
                ):
                    enemy.path_target = self.next_path_step(enemy.pos, self.player.pos, enemy.floor)
                    enemy.path_timer = 0.31
                if enemy.path_target is None:
                    continue
                path_vector = enemy.path_target - enemy.pos
                if path_vector.length_squared() <= 0.0001:
                    continue
                direction = path_vector.normalize()

            ranged_shot = data["ranged"] and can_see and 1.35 < distance < 7.4
            melee_distance = 0.70 + enemy.radius * 0.25
            should_move = distance > melee_distance and not ranged_shot
            if should_move:
                movement = direction * data["speed"] * dt
                old_position = pygame.Vector2(enemy.pos)
                self.move_with_collision(enemy.pos, movement, enemy.radius, enemy.floor)
                overlaps = any(
                    other is not enemy and other.alive and not other.hidden
                    and other.floor == enemy.floor
                    and enemy.pos.distance_squared_to(other.pos)
                    < (enemy.radius + other.radius) ** 2 * 0.62
                    for other in self.enemies
                )
                if overlaps:
                    enemy.pos = old_position
                if enemy.pos.distance_squared_to(old_position) < 0.00000001:
                    alternate = pygame.Vector2(-direction.y, direction.x)
                    if int((enemy.pos.x + enemy.pos.y) * 10) % 2:
                        alternate *= -1
                    self.move_with_collision(
                        enemy.pos,
                        alternate * data["speed"] * dt * 0.68,
                        enemy.radius,
                        enemy.floor,
                    )
            elif enemy.attack_timer <= 0.0 and can_see:
                enemy.attack_timer = data["attack_delay"]
                if ranged_shot:
                    self.damage_player(data["damage"], "DISPARO VINDO DA ESCURIDAO!")
                    self.scare_timer = max(self.scare_timer, 0.24)
                else:
                    self.damage_player(data["damage"])
                if self.state != "playing":
                    return

    def update_pickups(self, dt):
        for pickup in self.pickups:
            if pickup.kind in POWER_INFO and not pickup.active:
                pickup.respawn_timer = max(0.0, pickup.respawn_timer - dt)
                if pickup.respawn_timer <= 0.0:
                    pickup.active = True
            if not pickup.active or pickup.floor != self.current_floor:
                continue
            if pickup.pos.distance_squared_to(self.player.pos) > 0.28:
                continue
            if pickup.kind == "medkit":
                if self.player.health >= self.player.max_health:
                    continue
                healed = min(35, self.player.max_health - self.player.health)
                self.player.health += healed
                pickup.active = False
                self.notify("KIT MEDICO  +" + str(healed) + " HP", 1.3)
            elif pickup.kind == "blue_key":
                pickup.active = False
                self.keys_owned["blue"] = True
                awakened = self.wake_floor_ambush(0, "blue", "CARTAO AZUL: ALGO ACORDOU!")
                if not awakened:
                    self.notify("CARTAO AZUL - ACESSO LIBERADO", 2.0)
            elif pickup.kind == "red_key":
                pickup.active = False
                self.keys_owned["red"] = True
                awakened = self.wake_floor_ambush(1, "red", "CARTAO VERMELHO: EMBOSCADA!")
                if not awakened:
                    self.notify("CARTAO VERMELHO - NUCLEO LIBERADO", 2.0)
            elif pickup.kind in POWER_INFO:
                title, _, duration = POWER_INFO[pickup.kind]
                self.power_timers[pickup.kind] = duration
                if pickup.kind == "infinite":
                    self.ammo = self.magazine_size
                    self.reload_timer = 0.0
                pickup.active = False
                pickup.respawn_timer = 30.0
                self.notify(title + "  " + str(int(duration)) + "s", 1.6)

    def explode(self, floor, position):
        self.explosions.append(Explosion(floor, position))
        blast_radius = 2.15
        for enemy in self.enemies:
            if not enemy.alive or enemy.hidden or enemy.floor != floor:
                continue
            distance = enemy.pos.distance_to(position)
            if distance > blast_radius:
                continue
            if not self.has_line_of_sight(position, enemy.pos, floor):
                continue
            damage = max(22, int(88 * (1.0 - distance / blast_radius)))
            was_alive = enemy.alive
            enemy.hp = max(0, enemy.hp - damage)
            enemy.hit_flash = 0.18
            enemy.alerted = True
            if was_alive and not enemy.alive:
                self.total_kills += 1
                self.notify(ENEMY_DATA[enemy.kind]["name"] + " EXPLODIU", 1.0)

    def update_missiles(self, dt):
        for missile in self.missiles:
            if not missile.alive or missile.floor != self.current_floor:
                continue
            missile.age += dt
            step_distance = missile.speed * dt / 5.0
            for _ in range(5):
                next_pos = missile.pos + missile.direction * step_distance
                if self.is_blocked(next_pos.x, next_pos.y, 0.08, missile.floor):
                    missile.alive = False
                    self.explode(missile.floor, missile.pos)
                    break
                missile.pos = next_pos
                hit_enemy = False
                for enemy in self.enemies:
                    if (
                        not enemy.alive or enemy.hidden
                        or enemy.floor != missile.floor
                    ):
                        continue
                    radius = enemy.radius + 0.12
                    if enemy.pos.distance_squared_to(missile.pos) <= radius * radius:
                        missile.alive = False
                        self.explode(missile.floor, missile.pos)
                        hit_enemy = True
                        break
                if hit_enemy:
                    break
            if missile.age > 4.2 and missile.alive:
                missile.alive = False
                self.explode(missile.floor, missile.pos)
        self.missiles = [missile for missile in self.missiles if missile.alive]

    def update_explosions(self, dt):
        for explosion in self.explosions:
            explosion.age += dt
        self.explosions = [
            explosion for explosion in self.explosions
            if explosion.age < explosion.duration
        ]

    def update_objective(self):
        should_unlock = (
            self.keys_owned["blue"] and self.keys_owned["red"]
            and self.living_enemies() == 0
        )
        if should_unlock and not self.exit_unlocked:
            self.exit_unlocked = True
            self.floor_banner_timer = 3.0
            self.notify("CONTENCAO LIMPA - SAIDA DOURADA ABERTA", 2.8)

    # ------------------------------------------------------------------
    # Renderizacao pseudo-3D
    # ------------------------------------------------------------------
    def draw_background(self, horizon):
        base = 9 + self.current_floor * 2
        self.view.fill((base, base + 2, base + 7))
        top = clamp(horizon, 0, VIEW_H)
        for y in range(0, top, 4):
            factor = y / max(1, top)
            color = (
                int(5 + 11 * factor),
                int(7 + 12 * factor),
                int(13 + 15 * factor),
            )
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 4))
        for y in range(top, VIEW_H, 4):
            factor = (y - top) / max(1, VIEW_H - top)
            color = (
                int(27 - 17 * factor),
                int(25 - 16 * factor),
                int(29 - 18 * factor),
            )
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 4))
        pygame.draw.line(self.view, (42, 37, 44), (0, top), (VIEW_W, top))

    def draw_walls(self, horizon):
        for x in range(VIEW_W):
            camera_x = 2.0 * x / VIEW_W - 1.0
            ray_direction = self.player.direction + self.player.plane * camera_x
            distance, side, cell, wall_position = self.cast_ray(self.player.pos, ray_direction)
            self.z_buffer[x] = distance
            wall_height = min(VIEW_H * 4, int(VIEW_H / distance))
            draw_start = horizon - wall_height // 2
            draw_end = horizon + wall_height // 2
            base_color = WALL_COLORS.get(cell, (78, 78, 78))
            face_factor = 0.69 if side else 1.0
            fog_factor = clamp(1.02 - distance / 11.5, 0.10, 1.0)
            stripe = int(wall_position * 10.0) % 2
            stripe_factor = 0.81 if stripe else 1.0
            pulse = 1.0
            if cell in ("B", "R", "X"):
                pulse = 0.88 + ((pygame.time.get_ticks() // 180) % 3) * 0.06
            color = shade(base_color, face_factor * fog_factor * stripe_factor * pulse)
            pygame.draw.line(
                self.view,
                color,
                (x, max(0, draw_start)),
                (x, min(VIEW_H - 1, draw_end)),
            )
            if draw_start >= 0:
                self.view.set_at((x, draw_start), shade(color, 1.32))

    def project_point(self, world_position):
        relative = world_position - self.player.pos
        determinant = (
            self.player.plane.x * self.player.direction.y
            - self.player.direction.x * self.player.plane.y
        )
        if abs(determinant) < 0.000001:
            return None
        inverse = 1.0 / determinant
        transform_x = inverse * (
            self.player.direction.y * relative.x
            - self.player.direction.x * relative.y
        )
        transform_y = inverse * (
            -self.player.plane.y * relative.x
            + self.player.plane.x * relative.y
        )
        if transform_y <= 0.04:
            return None
        screen_x = int((VIEW_W / 2.0) * (1.0 + transform_x / transform_y))
        return screen_x, transform_y

    def make_enemy_surface(self, width, height, enemy):
        width = max(4, width)
        height = max(5, height)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        data = ENEMY_DATA[enemy.kind]
        body = (245, 245, 245) if enemy.hit_flash > 0.0 else data["color"]
        dark = shade(body, 0.43)
        eye = data["eye"]

        if enemy.kind == "rastejante":
            pygame.draw.ellipse(surface, dark, (0, height * 2 // 5, width, height * 2 // 5))
            pygame.draw.ellipse(surface, body, (width // 7, height // 3, width * 5 // 7, height // 2))
            for leg_x in (width // 8, width * 3 // 8, width * 5 // 8, width * 7 // 8):
                pygame.draw.line(surface, dark, (width // 2, height * 2 // 3), (leg_x, height - 1), max(1, width // 16))
            pygame.draw.circle(surface, eye, (width * 2 // 5, height // 2), max(1, width // 11))
            pygame.draw.circle(surface, eye, (width * 3 // 5, height // 2), max(1, width // 11))
        elif enemy.kind == "cacador":
            pygame.draw.polygon(surface, dark, ((width // 2, 0), (0, height * 3 // 4), (width // 4, height - 1), (width * 3 // 4, height - 1), (width - 1, height * 3 // 4)))
            pygame.draw.polygon(surface, body, ((width // 2, height // 10), (width // 5, height * 3 // 4), (width * 4 // 5, height * 3 // 4)))
            pygame.draw.line(surface, eye, (width // 3, height // 3), (width * 2 // 3, height // 3), max(1, width // 10))
        elif enemy.kind == "bruto":
            pygame.draw.polygon(surface, dark, ((width // 4, height // 4), (0, 0), (width // 2, height // 5)))
            pygame.draw.polygon(surface, dark, ((width * 3 // 4, height // 4), (width - 1, 0), (width // 2, height // 5)))
            pygame.draw.ellipse(surface, dark, (0, height // 6, width, height * 5 // 6))
            pygame.draw.rect(surface, body, (width // 8, height // 4, width * 3 // 4, height * 3 // 5), border_radius=max(1, width // 8))
            pygame.draw.circle(surface, eye, (width * 2 // 5, height * 2 // 5), max(1, width // 12))
            pygame.draw.circle(surface, eye, (width * 3 // 5, height * 2 // 5), max(1, width // 12))
        elif enemy.kind == "espectro":
            ghost = body + (185,)
            pygame.draw.polygon(surface, ghost, ((width // 2, 0), (width // 8, height // 3), (0, height - 1), (width // 3, height * 4 // 5), (width // 2, height - 1), (width * 2 // 3, height * 4 // 5), (width - 1, height - 1), (width * 7 // 8, height // 3)))
            pygame.draw.ellipse(surface, dark, (width // 5, height // 5, width * 3 // 5, height // 3))
            pygame.draw.circle(surface, eye, (width * 2 // 5, height // 3), max(1, width // 12))
            pygame.draw.circle(surface, eye, (width * 3 // 5, height // 3), max(1, width // 12))
        elif enemy.kind == "atirador":
            pygame.draw.rect(surface, dark, (width // 7, height // 8, width * 5 // 7, height * 4 // 5), border_radius=max(1, width // 9))
            pygame.draw.rect(surface, body, (width // 5, height // 6, width * 3 // 5, height // 2))
            pygame.draw.circle(surface, eye, (width // 2, height // 3), max(1, width // 7))
            pygame.draw.rect(surface, (35, 31, 28), (width * 3 // 5, height // 2, width * 2 // 5, max(2, height // 9)))
            pygame.draw.circle(surface, (255, 63, 34), (width - 2, height // 2 + max(1, height // 18)), max(1, width // 13))
        else:
            pygame.draw.polygon(surface, dark, ((width // 5, height // 4), (0, 0), (width // 2, height // 5)))
            pygame.draw.polygon(surface, dark, ((width * 4 // 5, height // 4), (width - 1, 0), (width // 2, height // 5)))
            pygame.draw.ellipse(surface, dark, (width // 8, height // 7, width * 3 // 4, height * 4 // 5))
            pygame.draw.ellipse(surface, body, (width // 6, height // 8, width * 2 // 3, height * 3 // 5))
            pygame.draw.circle(surface, eye, (width * 2 // 5, height * 3 // 10), max(1, width // 13))
            pygame.draw.circle(surface, eye, (width * 3 // 5, height * 3 // 10), max(1, width // 13))

        if enemy.just_revealed > 0.0:
            pygame.draw.rect(surface, (255, 45, 35, 180), surface.get_rect(), max(1, width // 18))
        return surface

    def pickup_color(self, kind):
        if kind == "medkit":
            return (77, 225, 113)
        if kind == "blue_key":
            return (45, 139, 255)
        if kind == "red_key":
            return (255, 70, 58)
        return POWER_INFO[kind][1]

    def make_pickup_surface(self, width, height, pickup):
        surface = pygame.Surface((max(4, width), max(4, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        color = self.pickup_color(pickup.kind)
        dark = shade(color, 0.38)
        pygame.draw.ellipse(surface, (color[0], color[1], color[2], 70), (0, height // 2, width, height // 2))
        if pickup.kind == "medkit":
            pygame.draw.rect(surface, dark, (width // 10, height // 4, width * 4 // 5, height * 3 // 5), border_radius=max(1, width // 10))
            pygame.draw.rect(surface, color, (width // 8, height // 5, width * 3 // 4, height * 3 // 5), max(1, width // 16), border_radius=max(1, width // 10))
            pygame.draw.rect(surface, (235, 255, 238), (width * 2 // 5, height // 3, width // 5, height // 3))
            pygame.draw.rect(surface, (235, 255, 238), (width // 3, height * 2 // 5, width // 3, height // 6))
        elif pickup.kind in ("blue_key", "red_key"):
            pygame.draw.rect(surface, dark, (width // 6, height // 6, width * 2 // 3, height * 2 // 3), border_radius=max(1, width // 8))
            pygame.draw.rect(surface, color, (width // 5, height // 5, width * 3 // 5, height * 3 // 5), max(1, width // 10), border_radius=max(1, width // 8))
            pygame.draw.circle(surface, (235, 245, 255), (width // 2, height * 2 // 5), max(1, width // 10))
            pygame.draw.line(surface, (235, 245, 255), (width // 3, height * 3 // 5), (width * 2 // 3, height * 3 // 5), max(1, width // 13))
        else:
            pygame.draw.circle(surface, (color[0], color[1], color[2], 65), (width // 2, height // 2), min(width, height) // 2)
            pygame.draw.circle(surface, dark, (width // 2, height // 2), min(width, height) * 2 // 5)
            pygame.draw.circle(surface, color, (width // 2, height // 2), min(width, height) // 3, max(1, width // 12))
            if pickup.kind == "infinite":
                pygame.draw.line(surface, color, (width // 4, height // 2), (width * 3 // 4, height // 2), max(2, width // 8))
                pygame.draw.circle(surface, color, (width // 3, height // 2), max(1, width // 7), max(1, width // 14))
                pygame.draw.circle(surface, color, (width * 2 // 3, height // 2), max(1, width // 7), max(1, width // 14))
            elif pickup.kind == "rapid":
                pygame.draw.polygon(surface, color, ((width * 3 // 5, height // 6), (width // 3, height // 2), (width // 2, height // 2), (width * 2 // 5, height * 5 // 6), (width * 3 // 4, height * 2 // 5), (width * 3 // 5, height * 2 // 5)))
            else:
                pygame.draw.polygon(surface, color, ((width // 5, height * 3 // 5), (width * 3 // 5, height // 4), (width * 2 // 5, height // 2), (width * 4 // 5, height * 2 // 5), (width * 2 // 5, height * 4 // 5)))
        return surface

    def make_stair_surface(self, width, height, stair):
        surface = pygame.Surface((max(4, width), max(4, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        color = (114, 205, 255) if stair.direction == "SUBIR" else (198, 151, 255)
        pygame.draw.ellipse(surface, (color[0], color[1], color[2], 70), (0, height * 2 // 3, width, height // 3))
        pygame.draw.ellipse(surface, color, (width // 10, height * 2 // 3, width * 4 // 5, height // 4), max(1, width // 13))
        if stair.direction == "SUBIR":
            points = ((width // 2, height // 8), (width // 5, height // 2), (width * 2 // 5, height // 2), (width * 2 // 5, height * 3 // 4), (width * 3 // 5, height * 3 // 4), (width * 3 // 5, height // 2), (width * 4 // 5, height // 2))
        else:
            points = ((width // 2, height * 3 // 4), (width // 5, height * 2 // 5), (width * 2 // 5, height * 2 // 5), (width * 2 // 5, height // 6), (width * 3 // 5, height // 6), (width * 3 // 5, height * 2 // 5), (width * 4 // 5, height * 2 // 5))
        pygame.draw.polygon(surface, color, points)
        return surface

    def make_missile_surface(self, width, height):
        surface = pygame.Surface((max(3, width), max(3, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        pygame.draw.circle(surface, (58, 159, 255, 100), (width // 2, height // 2), max(1, min(width, height) // 2))
        pygame.draw.circle(surface, (115, 232, 255), (width // 2, height // 2), max(1, min(width, height) // 3))
        pygame.draw.circle(surface, (235, 255, 255), (width // 2, height // 2), max(1, min(width, height) // 7))
        return surface

    def make_explosion_surface(self, width, height, explosion):
        surface = pygame.Surface((max(4, width), max(4, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        progress = clamp(explosion.age / explosion.duration, 0.0, 1.0)
        radius = max(2, int(min(width, height) * (0.22 + progress * 0.28)))
        alpha = int(255 * (1.0 - progress))
        pygame.draw.circle(surface, (255, 73, 26, alpha // 2), (width // 2, height // 2), radius)
        pygame.draw.circle(surface, (255, 191, 48, alpha), (width // 2, height // 2), max(1, int(radius * 0.68)))
        pygame.draw.circle(surface, (255, 250, 205, alpha), (width // 2, height // 2), max(1, int(radius * 0.28)))
        return surface

    def blit_occluded_sprite(self, surface, left, top, depth):
        width, height = surface.get_size()
        visible_runs = []
        run_start = None
        screen_start = max(0, left)
        screen_end = min(VIEW_W, left + width)
        for screen_x in range(screen_start, screen_end):
            visible = depth < self.z_buffer[screen_x] + 0.05
            if visible and run_start is None:
                run_start = screen_x
            elif not visible and run_start is not None:
                visible_runs.append((run_start, screen_x))
                run_start = None
        if run_start is not None:
            visible_runs.append((run_start, screen_end))
        for start, end in visible_runs:
            source_x = start - left
            self.view.blit(surface, (start, top), (source_x, 0, end - start, height))
        return visible_runs

    def draw_sprites(self, horizon):
        objects = []
        for enemy in self.enemies:
            if enemy.alive and not enemy.hidden and enemy.floor == self.current_floor:
                objects.append((enemy.pos.distance_squared_to(self.player.pos), "enemy", enemy))
        for pickup in self.pickups:
            if pickup.active and pickup.floor == self.current_floor:
                objects.append((pickup.pos.distance_squared_to(self.player.pos), "pickup", pickup))
        for stair in self.stairs:
            if stair.floor == self.current_floor:
                objects.append((stair.pos.distance_squared_to(self.player.pos), "stair", stair))
        for missile in self.missiles:
            if missile.floor == self.current_floor:
                objects.append((missile.pos.distance_squared_to(self.player.pos), "missile", missile))
        for explosion in self.explosions:
            if explosion.floor == self.current_floor:
                objects.append((explosion.pos.distance_squared_to(self.player.pos), "explosion", explosion))
        objects.sort(key=lambda item: item[0], reverse=True)
        bob = pygame.Vector2(1.0, 0.0).rotate(self.walk_clock).y * 2.0
        for _, kind, obj in objects:
            projected = self.project_point(obj.pos)
            if projected is None:
                continue
            screen_x, depth = projected
            if kind == "enemy":
                scale = ENEMY_DATA[obj.kind]["scale"]
                height = clamp(int(VIEW_H * scale / depth), 4, VIEW_H * 3)
                width_factor = 0.82 if obj.kind in ("bruto", "rastejante") else 0.60
                width = max(3, int(height * width_factor))
                top = int(horizon - height * (0.43 if obj.kind == "rastejante" else 0.55))
                left = screen_x - width // 2
                surface = self.make_enemy_surface(width, height, obj)
                visible_runs = self.blit_occluded_sprite(surface, left, top, depth)
                if visible_runs and height >= 12:
                    bar_y = max(1, top - 5)
                    bar_surface = pygame.Surface((width, 4))
                    bar_surface.fill((14, 10, 13))
                    hp_width = int(width * obj.hp / obj.max_hp)
                    hp_color = (80, 224, 105) if obj.hp > obj.max_hp / 2 else (237, 69, 56)
                    pygame.draw.rect(bar_surface, hp_color, (1, 1, max(0, hp_width - 2), 2))
                    for run_start, run_end in visible_runs:
                        source_x = run_start - left
                        self.view.blit(bar_surface, (run_start, bar_y), (source_x, 0, run_end - run_start, 4))
            elif kind == "pickup":
                scale = 0.34 if obj.kind == "medkit" else 0.29
                height = clamp(int(VIEW_H * scale / depth), 4, VIEW_H)
                width = max(4, int(height * 0.95))
                top = int(horizon + VIEW_H * 0.38 / depth - height + bob * 0.12)
                left = screen_x - width // 2
                self.blit_occluded_sprite(self.make_pickup_surface(width, height, obj), left, top, depth)
            elif kind == "stair":
                height = clamp(int(VIEW_H * 0.48 / depth), 5, VIEW_H)
                width = max(5, int(height * 0.8))
                top = int(horizon + VIEW_H * 0.40 / depth - height + bob * 0.08)
                left = screen_x - width // 2
                self.blit_occluded_sprite(self.make_stair_surface(width, height, obj), left, top, depth)
            elif kind == "missile":
                height = clamp(int(VIEW_H * 0.18 / depth), 3, VIEW_H)
                left = screen_x - height // 2
                self.blit_occluded_sprite(self.make_missile_surface(height, height), left, horizon - height // 2, depth)
            else:
                progress = obj.age / obj.duration
                scale = 0.3 + progress * 1.3
                height = clamp(int(VIEW_H * scale / depth), 5, VIEW_H * 3)
                left = screen_x - height // 2
                self.blit_occluded_sprite(self.make_explosion_surface(height, height, obj), left, horizon - height // 2, depth)

    def draw_weapon(self):
        wave = pygame.Vector2(1.0, 0.0).rotate(self.walk_clock).y
        bob_x = int(wave * 4.0 * self.walk_amount)
        bob_y = int(abs(wave) * 3.0 * self.walk_amount)
        recoil_y = int(self.recoil * 10.0)
        center_x = VIEW_W // 2 + bob_x
        base_y = VIEW_H + bob_y + recoil_y
        pygame.draw.polygon(self.view, (80, 52, 44), ((center_x - 57, VIEW_H), (center_x - 29, base_y - 39), (center_x - 14, base_y - 25), (center_x - 31, VIEW_H)))
        pygame.draw.polygon(self.view, (80, 52, 44), ((center_x + 57, VIEW_H), (center_x + 29, base_y - 39), (center_x + 14, base_y - 25), (center_x + 31, VIEW_H)))
        gun_color = (58, 68, 80) if self.power_timers["rapid"] <= 0.0 else (119, 48, 39)
        pygame.draw.polygon(self.view, (29, 34, 42), ((center_x - 25, base_y), (center_x - 18, base_y - 56), (center_x + 18, base_y - 56), (center_x + 25, base_y)))
        pygame.draw.rect(self.view, gun_color, (center_x - 13, base_y - 73, 26, 27), border_radius=3)
        pygame.draw.rect(self.view, (15, 18, 23), (center_x - 7, base_y - 79, 14, 12), border_radius=2)
        pygame.draw.line(self.view, (141, 158, 171), (center_x - 10, base_y - 68), (center_x + 10, base_y - 68), 2)
        if self.muzzle_timer > 0.0:
            tip_y = base_y - 82
            pygame.draw.polygon(self.view, (255, 219, 67), ((center_x, tip_y - 23), (center_x - 7, tip_y - 5), (center_x - 18, tip_y - 12), (center_x - 7, tip_y + 1), (center_x, tip_y + 7), (center_x + 7, tip_y + 1), (center_x + 18, tip_y - 12), (center_x + 7, tip_y - 5)))
            pygame.draw.circle(self.view, (255, 251, 205), (center_x, tip_y - 5), 5)

    def draw_world(self):
        horizon = clamp(VIEW_H // 2 + int(self.pitch / 2.0), 24, VIEW_H - 24)
        self.draw_background(horizon)
        self.draw_walls(horizon)
        self.draw_sprites(horizon)
        self.draw_weapon()
        pygame.transform.scale(self.view, (SCREEN_W, SCREEN_H), self.screen)

    # ------------------------------------------------------------------
    # Atmosfera, HUD, mapa e telas
    # ------------------------------------------------------------------
    def draw_text(self, text, font, color, position, center=False):
        shadow = font.render(text, True, (0, 0, 0))
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        self.screen.blit(shadow, rect.move(2, 2))
        self.screen.blit(image, rect)
        return rect

    def draw_bar(self, rect, value, maximum, color, background=(28, 21, 26)):
        pygame.draw.rect(self.screen, background, rect, border_radius=5)
        pygame.draw.rect(self.screen, (190, 190, 196), rect, 2, border_radius=5)
        inner = rect.inflate(-6, -6)
        fraction = clamp(value / maximum if maximum else 0.0, 0.0, 1.0)
        fill = pygame.Rect(inner.x, inner.y, int(inner.width * fraction), inner.height)
        if fill.width > 0:
            pygame.draw.rect(self.screen, color, fill, border_radius=3)

    def nearest_visible_enemy_distance(self):
        distances = [
            enemy.pos.distance_to(self.player.pos)
            for enemy in self.enemies
            if enemy.alive and not enemy.hidden and enemy.alerted
            and enemy.floor == self.current_floor
        ]
        return min(distances) if distances else 99.0

    def draw_atmosphere(self):
        threat = self.nearest_visible_enemy_distance()
        darkness_alpha = 42 + self.current_floor * 8 + self.light_flicker
        if self.blackout_timer > 0.0:
            darkness_alpha = 175
        veil = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        veil.fill((0, 0, 5, darkness_alpha))
        center = (SCREEN_W // 2, SCREEN_H // 2 - 20)
        pygame.draw.circle(veil, (0, 0, 0, max(0, darkness_alpha - 37)), center, 280)
        pygame.draw.circle(veil, (0, 0, 0, max(0, darkness_alpha - 61)), center, 185)
        pygame.draw.circle(veil, (0, 0, 0, 0), center, 95)
        self.screen.blit(veil, (0, 0))

        vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for index in range(7):
            alpha = 12 + index * 6
            inset = index * 12
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (inset, inset, SCREEN_W - inset * 2, SCREEN_H - inset * 2), 12)
        if threat < 4.4:
            red_alpha = int(clamp((4.4 - threat) * 18, 8, 62))
            pygame.draw.rect(vignette, (126, 0, 0, red_alpha), (0, 0, SCREEN_W, SCREEN_H), 34)
        self.screen.blit(vignette, (0, 0))

        if self.scare_timer > 0.0:
            intensity = clamp(self.scare_timer / 0.9, 0.0, 1.0)
            static = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.rect(static, (145, 0, 0, int(45 * intensity)), (0, 0, SCREEN_W, SCREEN_H), 25)
            seed = pygame.time.get_ticks() // 20
            for line in range(12):
                y = (seed * 37 + line * 53) % SCREEN_H
                length = 45 + ((seed * 19 + line * 71) % 240)
                x = (seed * 23 + line * 97) % max(1, SCREEN_W - length)
                pygame.draw.rect(static, (230, 232, 238, int(35 * intensity)), (x, y, length, 2))
            self.screen.blit(static, (0, 0))

    def draw_crosshair(self):
        center = (SCREEN_W // 2, SCREEN_H // 2)
        color = (255, 255, 255) if self.hit_marker_timer <= 0.0 else (255, 70, 58)
        gap = 7
        size = 8
        pygame.draw.line(self.screen, color, (center[0] - gap - size, center[1]), (center[0] - gap, center[1]), 2)
        pygame.draw.line(self.screen, color, (center[0] + gap, center[1]), (center[0] + gap + size, center[1]), 2)
        pygame.draw.line(self.screen, color, (center[0], center[1] - gap - size), (center[0], center[1] - gap), 2)
        pygame.draw.line(self.screen, color, (center[0], center[1] + gap), (center[0], center[1] + gap + size), 2)
        if self.hit_marker_timer > 0.0:
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                pygame.draw.line(self.screen, color, (center[0] + sx * 5, center[1] + sy * 5), (center[0] + sx * 12, center[1] + sy * 12), 2)

    def cell_map_color(self, cell):
        if cell == ".":
            return (19, 23, 28)
        if cell == "B" and self.keys_owned["blue"]:
            return (18, 31, 45)
        if cell == "R" and self.keys_owned["red"]:
            return (42, 21, 21)
        return shade(WALL_COLORS.get(cell, (80, 80, 80)), 0.76)

    def draw_minimap(self):
        cell_size = 5
        map_width = MAP_W * cell_size
        map_height = MAP_H * cell_size
        start_x = SCREEN_W - map_width - 18
        start_y = 64
        panel = pygame.Surface((map_width + 8, map_height + 8), pygame.SRCALPHA)
        panel.fill((3, 5, 8, 225))
        self.screen.blit(panel, (start_x - 4, start_y - 4))
        floor_map = MAPS[self.current_floor]
        for y, row in enumerate(floor_map):
            for x, cell in enumerate(row):
                pygame.draw.rect(self.screen, self.cell_map_color(cell), (start_x + x * cell_size, start_y + y * cell_size, cell_size - 1, cell_size - 1))
        for stair in self.stairs:
            if stair.floor == self.current_floor:
                pygame.draw.circle(self.screen, (137, 207, 255), (start_x + int(stair.pos.x * cell_size), start_y + int(stair.pos.y * cell_size)), 2)
        for enemy in self.enemies:
            if enemy.alive and not enemy.hidden and enemy.floor == self.current_floor:
                color = ENEMY_DATA[enemy.kind]["color"]
                pygame.draw.circle(self.screen, color, (start_x + int(enemy.pos.x * cell_size), start_y + int(enemy.pos.y * cell_size)), 2)
        for pickup in self.pickups:
            if pickup.active and pickup.floor == self.current_floor:
                pygame.draw.circle(self.screen, self.pickup_color(pickup.kind), (start_x + int(pickup.pos.x * cell_size), start_y + int(pickup.pos.y * cell_size)), 2)
        player_point = (start_x + int(self.player.pos.x * cell_size), start_y + int(self.player.pos.y * cell_size))
        pygame.draw.circle(self.screen, (245, 245, 255), player_point, 3)
        direction_end = (player_point[0] + int(self.player.direction.x * 8), player_point[1] + int(self.player.direction.y * 8))
        pygame.draw.line(self.screen, (245, 245, 255), player_point, direction_end, 2)
        self.draw_text("MAPA " + str(self.current_floor + 1) + "/3", self.font_tiny, (210, 216, 222), (start_x, start_y + map_height + 5))

    def objective_text(self):
        if not self.keys_owned["blue"]:
            return "ENCONTRE O CARTAO AZUL NO NIVEL 1"
        if self.current_floor == 0:
            return "ELIMINE AS AMEACAS E USE [E] PARA SUBIR"
        if not self.keys_owned["red"]:
            return "ENCONTRE O CARTAO VERMELHO NO NIVEL 2"
        if self.current_floor == 1:
            return "ELIMINE AS AMEACAS E USE [E] PARA SUBIR"
        if self.living_enemies() > 0:
            return "ELIMINE TODOS: " + str(self.living_enemies()) + " RESTANTES"
        if self.current_floor != 2:
            return "VOLTE AO NIVEL 3 E ENCONTRE A SAIDA"
        return "ALCANCE A PORTA DOURADA"

    def draw_hud(self):
        panel_h = 96
        panel = pygame.Surface((SCREEN_W, panel_h), pygame.SRCALPHA)
        panel.fill((6, 7, 11, 220))
        self.screen.blit(panel, (0, SCREEN_H - panel_h))
        pygame.draw.line(self.screen, (77, 83, 92), (0, SCREEN_H - panel_h), (SCREEN_W, SCREEN_H - panel_h), 2)
        health_color = (62, 215, 101) if self.player.health > 35 else (238, 62, 51)
        self.draw_text("VIDA", self.font_small, (220, 230, 235), (22, SCREEN_H - 80))
        self.draw_bar(pygame.Rect(22, SCREEN_H - 55, 220, 27), self.player.health, self.player.max_health, health_color)
        self.draw_text(str(self.player.health) + " / " + str(self.player.max_health), self.font_small, (255, 255, 255), (132, SCREEN_H - 42), center=True)
        infinite = self.power_timers["infinite"] > 0.0
        ammo_text = "INFINITA" if infinite else ("RECARGA" if self.reload_timer > 0.0 else str(self.ammo) + " / INF")
        ammo_color = (255, 211, 65) if infinite or self.ammo <= 4 else (235, 238, 240)
        self.draw_text("MUNICAO", self.font_small, (166, 177, 188), (278, SCREEN_H - 80))
        self.draw_text(ammo_text, self.font_medium, ammo_color, (278, SCREEN_H - 57))
        plasma_text = "PRONTO" if self.missile_timer <= 0.0 else str(round(self.missile_timer, 1)) + " s"
        plasma_color = (72, 213, 255) if self.missile_timer <= 0.0 else (112, 123, 134)
        self.draw_text("PLASMA [DIREITO]", self.font_tiny, (166, 177, 188), (435, SCREEN_H - 80))
        self.draw_text(plasma_text, self.font_medium, plasma_color, (435, SCREEN_H - 57))
        current_count = self.living_enemies(self.current_floor)
        self.draw_text("AMEACAS", self.font_tiny, (166, 177, 188), (650, SCREEN_H - 80))
        self.draw_text(str(current_count) + " AQUI  /  " + str(self.living_enemies()) + " TOTAL", self.font_small, (239, 91, 72), (650, SCREEN_H - 57))
        blue_color = (73, 158, 255) if self.keys_owned["blue"] else (74, 79, 87)
        red_color = (255, 73, 60) if self.keys_owned["red"] else (74, 79, 87)
        self.draw_text("AZUL", self.font_tiny, blue_color, (650, SCREEN_H - 31))
        self.draw_text("VERMELHO", self.font_tiny, red_color, (706, SCREEN_H - 31))
        self.draw_text("NIVEL " + str(self.current_floor + 1) + "/3", self.font_small, (224, 207, 164), (843, SCREEN_H - 65))
        self.draw_crosshair()

        self.draw_text("OBJETIVO: " + self.objective_text(), self.font_small, (222, 224, 228), (17, 14))
        power_y = 43
        for kind in ("infinite", "rapid", "speed"):
            timer = self.power_timers[kind]
            if timer > 0.0:
                title, color, _ = POWER_INFO[kind]
                self.draw_text(title + "  " + str(round(timer, 1)) + "s", self.font_tiny, color, (18, power_y))
                power_y += 20
        stair = self.nearby_stair()
        if stair is not None:
            text = "[E]  " + stair.direction + " PARA O NIVEL " + str(stair.target_floor + 1)
            box = pygame.Surface((390, 42), pygame.SRCALPHA)
            box.fill((4, 8, 13, 215))
            self.screen.blit(box, (SCREEN_W // 2 - 195, SCREEN_H - 153))
            self.draw_text(text, self.font_medium, (162, 222, 255), (SCREEN_W // 2, SCREEN_H - 132), center=True)
        elif self.near_exit():
            if self.exit_unlocked:
                text = "[E]  ABRIR A SAIDA E ESCAPAR"
                color = (255, 220, 86)
            else:
                text = "[E]  SAIDA EM CONTENCAO"
                color = (227, 78, 61)
            box = pygame.Surface((390, 42), pygame.SRCALPHA)
            box.fill((4, 8, 13, 215))
            self.screen.blit(box, (SCREEN_W // 2 - 195, SCREEN_H - 153))
            self.draw_text(text, self.font_medium, color, (SCREEN_W // 2, SCREEN_H - 132), center=True)
        if self.message_timer > 0.0:
            text_surface = self.font_medium.render(self.message, True, (255, 229, 157))
            box = text_surface.get_rect(center=(SCREEN_W // 2, 73)).inflate(24, 12)
            background = pygame.Surface(box.size, pygame.SRCALPHA)
            background.fill((4, 6, 9, 215))
            self.screen.blit(background, box)
            self.screen.blit(text_surface, text_surface.get_rect(center=box.center))
        if self.show_map:
            self.draw_minimap()

    def draw_overlay(self, title, lines, title_color=(235, 238, 240)):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((2, 3, 7, 225))
        self.screen.blit(overlay, (0, 0))
        title_font = self.font_title if len(title) < 21 else self.font_large
        self.draw_text(title, title_font, title_color, (SCREEN_W // 2, 104), center=True)
        y = 184
        for text, color, size in lines:
            font = self.font_medium if size == "medium" else self.font_small
            self.draw_text(text, font, color, (SCREEN_W // 2, y), center=True)
            y += 42 if size == "medium" else 29

    def render(self):
        self.draw_world()
        self.draw_atmosphere()
        if self.state != "intro":
            self.draw_hud()
        if self.damage_flash > 0.0:
            alpha = int(125 * self.damage_flash / 0.24)
            flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash.fill((205, 14, 12, alpha))
            self.screen.blit(flash, (0, 0))
        if self.floor_banner_timer > 0.0:
            alpha = int(210 * clamp(self.floor_banner_timer / 0.7, 0.0, 1.0))
            banner = pygame.Surface((SCREEN_W, 54), pygame.SRCALPHA)
            banner.fill((3, 5, 8, alpha))
            self.screen.blit(banner, (0, 126))
            self.draw_text(FLOOR_NAMES[self.current_floor], self.font_medium, (219, 223, 228), (SCREEN_W // 2, 153), center=True)

        if self.state == "intro":
            lines = (
                ("TRES ANDARES. VINTE E QUATRO AMEACAS. NENHUMA LUZ SEGURA.", (225, 86, 68), "medium"),
                ("WASD mover   |   MOUSE olhar   |   E usar escadas", (227, 230, 234), "small"),
                ("ESQUERDO atirar   |   DIREITO missil de plasma", (227, 230, 234), "small"),
                ("R recarregar   |   M mapa   |   ESC pausar", (227, 230, 234), "small"),
                ("Powerups: municao infinita, cadencia automatica e velocidade", (116, 211, 255), "small"),
                ("Encontre os cartoes, elimine TODOS e escape pela porta dourada.", (255, 211, 72), "small"),
                ("Durante CADENCIA MAXIMA, SEGURE O BOTAO ESQUERDO.", (255, 114, 83), "small"),
                ("CLIQUE OU PRESSIONE ENTER PARA DESCER", (255, 255, 255), "medium"),
            )
            self.draw_overlay("SETOR OMEGA", lines, (231, 61, 54))
        elif self.state == "paused":
            lines = (
                ("O mouse foi liberado.", (205, 211, 216), "medium"),
                ("Clique, ENTER ou ESC para continuar", (255, 219, 93), "small"),
            )
            self.draw_overlay("PAUSADO", lines, (106, 205, 255))
        elif self.state == "dead":
            lines = (
                ("Algo encontrou voce no escuro.", (225, 225, 230), "medium"),
                ("Eliminacoes: " + str(self.total_kills) + " / " + str(len(self.enemies)), (255, 180, 70), "small"),
                ("PRESSIONE ENTER PARA REINICIAR", (255, 255, 255), "medium"),
                ("ESC para sair", (170, 176, 184), "small"),
            )
            self.draw_overlay("VOCE MORREU", lines, (238, 55, 48))
        elif self.state == "won":
            lines = (
                ("Todos os sinais biologicos desapareceram.", (219, 232, 237), "medium"),
                ("Os tres niveis foram limpos. Voce escapou.", (255, 211, 65), "small"),
                ("Eliminacoes: " + str(self.total_kills), (255, 180, 70), "small"),
                ("PRESSIONE ENTER PARA JOGAR NOVAMENTE", (255, 255, 255), "medium"),
                ("ESC para sair", (170, 176, 184), "small"),
            )
            self.draw_overlay("MISSAO CUMPRIDA", lines, (74, 230, 125))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.process_events()
            self.update(dt)
            self.render()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
