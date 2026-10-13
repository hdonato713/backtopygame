import pygame


# ============================================================================
# ARENA PROTOCOL
# FPS pseudo-3D completo em um unico arquivo. Todo o visual e gerado com
# primitivas do pygame: nenhum som, imagem, fonte, mapa ou outro asset externo.
# ============================================================================

SCREEN_W = 1100
SCREEN_H = 680
VIEW_W = 440
VIEW_H = 272
FPS = 60
MAP_W = 26
MAP_H = 26
TAU_DEGREES = 360.0


def clamp(value, low, high):
    return max(low, min(high, value))


def shade(color, factor):
    return tuple(clamp(int(channel * factor), 0, 255) for channel in color)


def mix(a, b, amount):
    return tuple(int(a[i] + (b[i] - a[i]) * amount) for i in range(3))


def wave(degrees):
    return pygame.Vector2(1.0, 0.0).rotate(degrees).y


class RNG:
    """Gerador deterministico proprio para manter a regra de um unico import."""

    def __init__(self, seed=0xA81E51):
        self.state = seed & 0xFFFFFFFF

    def random(self):
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state / 4294967296.0

    def range(self, low, high):
        return low + (high - low) * self.random()

    def integer(self, low, high):
        return low + int(self.random() * (high - low + 1))

    def choice(self, values):
        return values[int(self.random() * len(values)) % len(values)]


def empty_grid():
    grid = []
    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            row.append("1" if x in (0, MAP_W - 1) or y in (0, MAP_H - 1) else ".")
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


def block(grid, x1, y1, x2, y2, material="1"):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            grid[y][x] = material


def build_snow_map():
    g = empty_grid()
    # Complexo cientifico ao redor de uma arena aberta de neve.
    wall_h(g, 6, 1, 10, "2", (4, 8))
    wall_v(g, 10, 1, 10, "2", (3, 8))
    wall_h(g, 10, 1, 10, "2", (3, 7))
    wall_v(g, 5, 10, 21, "3", (13, 18))
    wall_h(g, 21, 1, 11, "3", (3, 8))
    wall_h(g, 5, 15, 24, "2", (18, 22))
    wall_v(g, 15, 1, 10, "2", (4, 8))
    wall_v(g, 20, 10, 24, "3", (13, 18, 22))
    wall_h(g, 15, 8, 20, "4", (11, 16))
    block(g, 11, 2, 13, 3, "4")
    block(g, 11, 22, 14, 23, "4")
    block(g, 2, 13, 3, 15, "4")
    block(g, 22, 10, 23, 12, "4")
    return tuple("".join(row) for row in g)


def build_desert_map():
    g = empty_grid()
    # Rua principal de velho oeste com saloon, banco e becos laterais.
    block(g, 2, 2, 7, 6, "2")
    block(g, 2, 9, 6, 14, "3")
    block(g, 2, 18, 8, 23, "2")
    block(g, 18, 2, 23, 7, "3")
    block(g, 19, 11, 23, 16, "2")
    block(g, 17, 20, 23, 23, "3")
    # Entradas nos predios e passagens internas.
    for x, y in ((7, 4), (6, 11), (8, 21), (18, 5), (19, 13), (17, 21)):
        g[y][x] = "."
    wall_h(g, 8, 9, 16, "4", (12,))
    wall_h(g, 17, 9, 17, "4", (13,))
    block(g, 11, 11, 13, 13, "4")
    block(g, 14, 21, 15, 23, "4")
    block(g, 10, 2, 11, 4, "4")
    return tuple("".join(row) for row in g)


def build_ship_map():
    g = empty_grid()
    # Patio de carga: corredores assimetricos feitos por conteineres.
    block(g, 2, 2, 6, 4, "2")
    block(g, 9, 2, 14, 4, "3")
    block(g, 18, 2, 23, 5, "4")
    block(g, 3, 8, 8, 10, "4")
    block(g, 12, 7, 15, 12, "2")
    block(g, 19, 9, 23, 11, "3")
    block(g, 2, 14, 5, 20, "3")
    block(g, 8, 15, 13, 18, "4")
    block(g, 17, 14, 22, 17, "2")
    block(g, 7, 22, 12, 24, "2")
    block(g, 16, 21, 23, 23, "3")
    wall_h(g, 20, 1, 6, "4", (3,))
    wall_v(g, 15, 13, 20, "4", (17,))
    return tuple("".join(row) for row in g)


def build_mansion_map():
    g = empty_grid()
    # Solar simetrico com salao central, quartos, biblioteca e jardim interno.
    wall_v(g, 7, 1, 24, "2", (4, 12, 21))
    wall_v(g, 18, 1, 24, "2", (4, 12, 21))
    wall_h(g, 7, 1, 24, "3", (4, 12, 13, 21))
    wall_h(g, 18, 1, 24, "3", (4, 12, 13, 21))
    wall_h(g, 12, 7, 18, "4", (12, 13))
    wall_v(g, 12, 7, 12, "4", (9,))
    wall_v(g, 13, 12, 18, "4", (15,))
    block(g, 2, 2, 3, 3, "4")
    block(g, 22, 2, 23, 3, "4")
    block(g, 2, 22, 3, 23, "4")
    block(g, 22, 22, 23, 23, "4")
    block(g, 10, 9, 11, 10, "2")
    block(g, 14, 14, 15, 15, "2")
    # Os moveis ficam junto das portas, mas sem selar as duas alas internas.
    g[9][11] = "."
    g[15][14] = "."
    return tuple("".join(row) for row in g)


MAPS = (build_snow_map(), build_desert_map(), build_ship_map(), build_mansion_map())

MAP_INFO = (
    {
        "name": "BASE BOREAL",
        "subtitle": "NEVE / INSTALACAO POLAR",
        "sky": (62, 91, 124),
        "horizon": (151, 190, 216),
        "floor": (196, 217, 226),
        "fog": (183, 211, 226),
        "walls": {"1": (89, 117, 140), "2": (168, 197, 211), "3": (54, 101, 139), "4": (118, 147, 161)},
        "accent": (119, 222, 255),
    },
    {
        "name": "FRONTEIRA CINZA",
        "subtitle": "DESERTO / VELHO OESTE",
        "sky": (167, 88, 51),
        "horizon": (244, 173, 96),
        "floor": (143, 91, 52),
        "fog": (209, 143, 78),
        "walls": {"1": (122, 73, 42), "2": (155, 96, 50), "3": (105, 61, 39), "4": (190, 139, 75)},
        "accent": (255, 191, 77),
    },
    {
        "name": "CARGUEIRO 09",
        "subtitle": "NAVIO / CONTEINERES",
        "sky": (34, 50, 64),
        "horizon": (78, 108, 122),
        "floor": (40, 51, 55),
        "fog": (76, 102, 107),
        "walls": {"1": (52, 69, 76), "2": (177, 59, 43), "3": (38, 104, 142), "4": (190, 142, 35)},
        "accent": (82, 229, 225),
    },
    {
        "name": "SOLAR NOCTURNO",
        "subtitle": "MANSAO / CORREDORES",
        "sky": (28, 24, 43),
        "horizon": (73, 61, 91),
        "floor": (52, 38, 43),
        "fog": (72, 58, 79),
        "walls": {"1": (67, 49, 69), "2": (107, 73, 78), "3": (75, 54, 48), "4": (130, 112, 83)},
        "accent": (207, 121, 255),
    },
)

SPAWNS = (
    ((2.5, 2.5), (8.5, 3.5), (13.5, 8.5), (18.5, 8.5), (23.0, 3.0), (3.0, 12.5), (10.5, 13.0), (23.0, 19.5), (7.0, 23.0), (16.0, 22.5), (13.0, 18.5), (22.5, 23.0)),
    ((9.5, 6.5), (16.5, 3.5), (8.5, 10.5), (17.5, 9.5), (8.0, 16.0), (18.5, 18.5), (10.0, 23.0), (15.0, 15.0), (23.5, 18.0), (1.5, 16.0), (13.0, 6.0), (16.5, 24.5)),
    ((7.5, 5.5), (16.0, 3.0), (2.0, 6.5), (10.0, 10.0), (17.0, 8.0), (7.0, 13.0), (16.5, 12.5), (23.0, 13.0), (6.5, 21.5), (14.0, 23.0), (23.0, 19.0), (2.0, 23.0)),
    ((4.5, 4.5), (12.5, 3.5), (21.5, 4.5), (4.5, 10.0), (10.0, 5.0), (16.0, 10.0), (21.5, 14.0), (4.0, 20.0), (10.0, 21.0), (15.0, 22.0), (21.0, 22.0), (12.5, 16.0)),
)

WEAPONS = {
    "shotgun": {
        "name": "DEVASTADORA 12",
        "role": "ESPINGARDA",
        "damage": 22,
        "mag": 5,
        "delay": 0.82,
        "reload": 2.75,
        "pellets": 7,
        "spread": 7.8,
        "automatic": False,
        "color": (224, 137, 54),
        "special": "ONDA CINETICA",
        "special_desc": "Explosao curta que repele e destroi",
        "special_cd": 10.0,
    },
    "smg": {
        "name": "VESPA-9",
        "role": "SUBMETRALHADORA",
        "damage": 11,
        "mag": 38,
        "delay": 0.078,
        "reload": 1.48,
        "pellets": 1,
        "spread": 2.8,
        "automatic": True,
        "color": (67, 211, 224),
        "special": "SUPERALIMENTACAO",
        "special_desc": "5s de cadencia extrema e pente infinito",
        "special_cd": 16.0,
    },
    "rifle": {
        "name": "AR-4 VANGUARDA",
        "role": "FUZIL",
        "damage": 27,
        "mag": 22,
        "delay": 0.235,
        "reload": 1.90,
        "pellets": 1,
        "spread": 1.15,
        "automatic": True,
        "color": (115, 226, 117),
        "special": "PROJETIL FANTASMA",
        "special_desc": "Disparo perfurante que atravessa paredes",
        "special_cd": 9.0,
    },
}

WEAPON_ORDER = ("shotgun", "smg", "rifle")
BOT_NAMES = ("NOVA", "REX", "VIPER", "KIRA", "GHOST", "MACK", "ZERO", "SABLE", "TORO")
TEAM_COLORS = ((66, 157, 255), (245, 75, 70))


class Combatant:
    def __init__(self, actor_id, name, team, human=False):
        self.actor_id = actor_id
        self.name = name
        self.team = team
        self.human = human
        self.pos = pygame.Vector2(2.5, 2.5)
        self.direction = pygame.Vector2(1.0, 0.0)
        self.radius = 0.20 if human else 0.24
        self.max_hp = 100
        self.hp = 100
        self.alive = True
        self.respawn_timer = 0.0
        self.invulnerable = 0.0
        self.kills = 0
        self.deaths = 0
        self.weapon = "rifle"
        self.ammo = WEAPONS[self.weapon]["mag"]
        self.fire_timer = 0.0
        self.reload_timer = 0.0
        self.special_timer = 0.0
        self.overdrive = 0.0
        self.hit_flash = 0.0
        self.target_id = -1
        self.think_timer = 0.0
        self.path_timer = 0.0
        self.path_point = None
        self.wander_timer = 0.0
        self.strafe_sign = 1
        self.muzzle = 0.0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Arena Protocol - FPS Pseudo-3D")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.view = pygame.Surface((VIEW_W, VIEW_H)).convert()
        self.clock = pygame.time.Clock()
        self.font_tiny = pygame.font.Font(None, 18)
        self.view_font = pygame.font.Font(None, 10)
        self.font_small = pygame.font.Font(None, 24)
        self.font = pygame.font.Font(None, 31)
        self.font_big = pygame.font.Font(None, 58)
        self.font_huge = pygame.font.Font(None, 88)
        self.running = True
        self.rng = RNG(pygame.time.get_ticks() ^ 0xC0FFEE)
        self.state = "map_menu"
        self.menu_index = 0
        self.map_index = 0
        self.weapon_key = "rifle"
        self.mode = "ffa"
        self.mouse_captured = False
        self.first_mouse = True
        self.paused_from = "playing"
        self.z_buffer = [999.0] * VIEW_W
        self.show_map = False
        self.reset_match()

    def reset_match(self):
        self.player = Combatant(0, "VOCE", 0, True)
        self.player.weapon = self.weapon_key
        self.player.ammo = WEAPONS[self.weapon_key]["mag"]
        self.bots = []
        for index, name in enumerate(BOT_NAMES):
            team = (index + 1) % 2
            bot = Combatant(index + 1, name, team)
            bot.weapon = WEAPON_ORDER[index % len(WEAPON_ORDER)]
            bot.ammo = WEAPONS[bot.weapon]["mag"]
            bot.strafe_sign = -1 if index % 2 else 1
            self.bots.append(bot)
        self.actors = [self.player] + self.bots
        self.team_scores = [0, 0]
        self.pitch = 0.0
        self.camera_z = 0.0
        self.vertical_velocity = 0.0
        self.on_ground = True
        self.walk_phase = 0.0
        self.walk_amount = 0.0
        self.damage_flash = 0.0
        self.hit_marker = 0.0
        self.kill_flash = 0.0
        self.recoil = 0.0
        self.message = ""
        self.message_timer = 0.0
        self.match_time = 0.0
        self.winner_text = ""
        self.kill_feed = []
        self.tracers = []
        self.special_effect = 0.0
        self.respawn_all()

    def set_mouse_capture(self, captured):
        self.mouse_captured = captured
        pygame.event.set_grab(captured)
        pygame.mouse.set_visible(not captured)
        pygame.mouse.get_rel()
        self.first_mouse = True

    def notify(self, text, duration=1.4):
        self.message = text
        self.message_timer = duration

    def map_cell(self, x, y):
        ix = int(x)
        iy = int(y)
        if ix < 0 or iy < 0 or ix >= MAP_W or iy >= MAP_H:
            return "1"
        return MAPS[self.map_index][iy][ix]

    def is_blocked(self, x, y, radius=0.18):
        for px, py in ((x-radius, y-radius), (x+radius, y-radius), (x-radius, y+radius), (x+radius, y+radius)):
            if self.map_cell(px, py) != ".":
                return True
        return False

    def actor_position_clear(self, actor, x, y):
        if self.is_blocked(x, y, actor.radius):
            return False
        candidate = pygame.Vector2(x, y)
        for other in self.actors:
            if other is actor or not other.alive:
                continue
            minimum = (actor.radius + other.radius) * 0.72
            if candidate.distance_squared_to(other.pos) < minimum * minimum:
                return False
        return True

    def move_actor(self, actor, movement):
        nx = actor.pos.x + movement.x
        if self.actor_position_clear(actor, nx, actor.pos.y):
            actor.pos.x = nx
        ny = actor.pos.y + movement.y
        if self.actor_position_clear(actor, actor.pos.x, ny):
            actor.pos.y = ny

    def spawn_actor(self, actor, initial=False):
        all_candidates = list(SPAWNS[self.map_index])
        candidates = all_candidates
        if self.mode == "tdm":
            ordered = sorted(candidates, key=lambda point: point[0])
            candidates = ordered[:7] if actor.team == 0 else ordered[-7:]
        others = [other for other in self.actors if other is not actor and other.alive]
        enemies = [other for other in others if not self.same_side(actor, other)]
        ranked = []
        # Primeiro tenta a zona do time; se estiver lotada, amplia para o mapa.
        for candidate_group in (candidates, all_candidates):
            ranked = []
            for spawn in candidate_group:
                point = pygame.Vector2(spawn)
                if self.is_blocked(point.x, point.y, actor.radius):
                    continue
                occupied = any(
                    point.distance_squared_to(other.pos)
                    < (actor.radius + other.radius + 0.12) ** 2
                    for other in others
                )
                if occupied:
                    continue
                clearance = min((point.distance_to(other.pos) for other in enemies), default=99.0)
                exposed = any(
                    point.distance_squared_to(other.pos) < 9.0 * 9.0
                    and self.has_line_of_sight(point, other.pos)
                    for other in enemies
                )
                safety = clearance - (4.0 if exposed else 0.0) + self.rng.range(0.0, 0.12)
                ranked.append((safety, spawn))
            if ranked:
                break
        if not ranked:
            for spawn in all_candidates:
                point = pygame.Vector2(spawn)
                if not self.is_blocked(point.x, point.y, actor.radius):
                    clearance = min((point.distance_to(other.pos) for other in others), default=99.0)
                    ranked.append((clearance, spawn))
        ranked.sort(key=lambda item: item[0], reverse=True)
        safe_pool = [spawn for _, spawn in ranked[:min(4, len(ranked))]]
        best = self.rng.choice(safe_pool) if safe_pool else (2.5, 2.5)
        actor.pos = pygame.Vector2(best)
        actor.direction = pygame.Vector2(1.0, 0.0).rotate(self.rng.range(0.0, 360.0))
        actor.hp = actor.max_hp
        actor.alive = True
        actor.respawn_timer = 0.0
        actor.invulnerable = 1.35 if not initial else 1.8
        actor.fire_timer = 0.35
        actor.reload_timer = 0.0
        actor.ammo = WEAPONS[actor.weapon]["mag"]
        actor.target_id = -1
        actor.path_point = None
        actor.muzzle = 0.0
        actor.hit_flash = 0.0
        actor.overdrive = 0.0
        if actor.human:
            self.camera_z = 0.0
            self.vertical_velocity = 0.0
            self.on_ground = True
            self.pitch = 0.0
            self.recoil = 0.0
            self.hit_marker = 0.0

    def respawn_all(self):
        # No modo de equipes, cada lado comeca numa metade diferente da arena.
        ordered = sorted(SPAWNS[self.map_index], key=lambda point: point[0])
        team_pools = (ordered[:6], ordered[-6:])
        team_indices = [0, 0]
        for index, actor in enumerate(self.actors):
            if self.mode == "tdm":
                pool = team_pools[actor.team]
                spawn = pool[team_indices[actor.team] % len(pool)]
                team_indices[actor.team] += 1
            else:
                spawn = SPAWNS[self.map_index][index % len(SPAWNS[self.map_index])]
            actor.pos = pygame.Vector2(spawn)
            if self.is_blocked(actor.pos.x, actor.pos.y, actor.radius):
                for candidate in SPAWNS[self.map_index]:
                    if not self.is_blocked(candidate[0], candidate[1], actor.radius):
                        actor.pos = pygame.Vector2(candidate)
                        break
            actor.direction = pygame.Vector2(1.0, 0.0).rotate(index * 137.5)
            actor.hp = actor.max_hp
            actor.alive = True
            actor.invulnerable = 1.6
            actor.respawn_timer = 0.0
            actor.ammo = WEAPONS[actor.weapon]["mag"]
            actor.kills = 0
            actor.deaths = 0

    def start_match(self):
        self.reset_match()
        self.state = "playing"
        self.set_mouse_capture(True)
        self.notify("COMBATE INICIADO", 2.0)

    def same_side(self, first, second):
        return self.mode == "tdm" and first.team == second.team

    def actor_by_id(self, actor_id):
        for actor in self.actors:
            if actor.actor_id == actor_id:
                return actor
        return None

    # ------------------------------------------------------------------
    # Entrada, menus e fluxo da partida
    # ------------------------------------------------------------------
    def menu_count(self):
        if self.state == "map_menu":
            return 4
        if self.state == "weapon_menu":
            return 3
        if self.state == "mode_menu":
            return 2
        return 1

    def confirm_menu(self):
        if self.state == "map_menu":
            self.map_index = self.menu_index
            self.state = "weapon_menu"
            self.menu_index = 0
        elif self.state == "weapon_menu":
            self.weapon_key = WEAPON_ORDER[self.menu_index]
            self.state = "mode_menu"
            self.menu_index = 0
        elif self.state == "mode_menu":
            self.mode = "ffa" if self.menu_index == 0 else "tdm"
            self.reset_match()
            self.state = "countdown"
            self.countdown = 3.5
            self.set_mouse_capture(True)

    def back_menu(self):
        if self.state == "weapon_menu":
            self.state = "map_menu"
            self.menu_index = self.map_index
        elif self.state == "mode_menu":
            self.state = "weapon_menu"
            self.menu_index = WEAPON_ORDER.index(self.weapon_key)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == getattr(pygame, "WINDOWFOCUSLOST", -999):
                if self.state in ("playing", "countdown"):
                    self.paused_from = self.state
                    self.state = "paused"
                    self.set_mouse_capture(False)
            elif event.type == pygame.KEYDOWN:
                if self.state in ("map_menu", "weapon_menu", "mode_menu"):
                    if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                        self.menu_index = (self.menu_index - 1) % self.menu_count()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                        self.menu_index = (self.menu_index + 1) % self.menu_count()
                    elif pygame.K_1 <= event.key <= pygame.K_4:
                        choice = event.key - pygame.K_1
                        if choice < self.menu_count():
                            self.menu_index = choice
                            self.confirm_menu()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.confirm_menu()
                    elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        if self.state == "map_menu":
                            self.running = False
                        else:
                            self.back_menu()
                elif event.key == pygame.K_ESCAPE:
                    if self.state in ("playing", "countdown"):
                        self.paused_from = self.state
                        self.state = "paused"
                        self.set_mouse_capture(False)
                    elif self.state == "paused":
                        self.state = self.paused_from
                        self.set_mouse_capture(True)
                    elif self.state == "finished":
                        self.state = "map_menu"
                        self.menu_index = self.map_index
                    else:
                        self.running = False
                elif self.state == "paused":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = self.paused_from
                        self.set_mouse_capture(True)
                    elif event.key == pygame.K_q:
                        self.state = "map_menu"
                        self.menu_index = self.map_index
                elif self.state == "finished":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = "countdown"
                        self.countdown = 3.5
                        self.reset_match()
                        self.set_mouse_capture(True)
                    elif event.key == pygame.K_q:
                        self.state = "map_menu"
                        self.menu_index = self.map_index
                elif self.state in ("playing", "countdown"):
                    if event.key == pygame.K_r and self.player.alive:
                        self.start_reload(self.player)
                    elif event.key == pygame.K_SPACE and self.player.alive and self.on_ground:
                        self.vertical_velocity = 3.25
                        self.on_ground = False
                    elif event.key == pygame.K_m:
                        self.show_map = not self.show_map
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "playing" and self.player.alive:
                    if event.button == 1:
                        self.player_fire()
                    elif event.button == 3:
                        self.use_special()
                elif self.state == "paused":
                    self.state = self.paused_from
                    self.set_mouse_capture(True)
            elif event.type == pygame.MOUSEMOTION and self.state in ("playing", "countdown"):
                if self.first_mouse:
                    self.first_mouse = False
                    continue
                horizontal = event.rel[0] * 0.095
                self.player.direction.rotate_ip(horizontal)
                self.pitch = clamp(self.pitch - event.rel[1] * 0.095, -92.0, 92.0)

    # ------------------------------------------------------------------
    # Colisao, caminhos, visibilidade e projecao
    # ------------------------------------------------------------------
    def cast_ray(self, origin, ray_direction, maximum_steps=90):
        map_x = int(origin.x)
        map_y = int(origin.y)
        rx, ry = ray_direction.x, ray_direction.y
        delta_x = abs(1.0 / rx) if abs(rx) > 0.000001 else 1000000.0
        delta_y = abs(1.0 / ry) if abs(ry) > 0.000001 else 1000000.0
        if rx < 0.0:
            step_x = -1
            side_x = (origin.x - map_x) * delta_x
        else:
            step_x = 1
            side_x = (map_x + 1.0 - origin.x) * delta_x
        if ry < 0.0:
            step_y = -1
            side_y = (origin.y - map_y) * delta_y
        else:
            step_y = 1
            side_y = (map_y + 1.0 - origin.y) * delta_y
        side = 0
        cell = "1"
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
            cell = self.map_cell(map_x, map_y)
            if cell != ".":
                break
        distance = max(0.0001, distance)
        position = origin.y + distance * ry if side == 0 else origin.x + distance * rx
        position -= int(position)
        return distance, side, cell, position

    def has_line_of_sight(self, start, end):
        offset = end - start
        distance = offset.length()
        if distance < 0.001:
            return True
        wall_distance, _, _, _ = self.cast_ray(start, offset / distance)
        return wall_distance + 0.08 >= distance

    def project_point(self, point):
        relative = point - self.player.pos
        right = pygame.Vector2(-self.player.direction.y, self.player.direction.x)
        depth = relative.dot(self.player.direction)
        side = relative.dot(right)
        if depth <= 0.035:
            return None
        screen_x = VIEW_W * 0.5 + side / (depth * 0.66) * VIEW_W * 0.5
        return screen_x, depth

    def next_path_step(self, start_position, goal_position):
        start = (int(start_position.x), int(start_position.y))
        goal = (int(goal_position.x), int(goal_position.y))
        if start == goal:
            return pygame.Vector2(goal[0] + 0.5, goal[1] + 0.5)
        queue = [start]
        parents = {start: None}
        cursor = 0
        while cursor < len(queue) and cursor < MAP_W * MAP_H:
            current = queue[cursor]
            cursor += 1
            if current == goal:
                break
            x, y = current
            for neighbor in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if neighbor in parents:
                    continue
                nx, ny = neighbor
                if nx < 0 or ny < 0 or nx >= MAP_W or ny >= MAP_H:
                    continue
                if self.map_cell(nx, ny) != ".":
                    continue
                parents[neighbor] = current
                queue.append(neighbor)
        if goal not in parents:
            return None
        step = goal
        while parents[step] is not None and parents[step] != start:
            step = parents[step]
        return pygame.Vector2(step[0] + 0.5, step[1] + 0.5)

    # ------------------------------------------------------------------
    # Armas, dano, especiais, mortes e placar
    # ------------------------------------------------------------------
    def start_reload(self, actor):
        data = WEAPONS[actor.weapon]
        if not actor.alive or actor.reload_timer > 0.0 or actor.ammo >= data["mag"]:
            return
        actor.reload_timer = data["reload"]
        actor.fire_timer = max(actor.fire_timer, 0.12)
        if actor.human:
            self.notify("RECARREGANDO " + data["name"], data["reload"])

    def valid_target(self, attacker, target):
        return target.alive and target is not attacker and not self.same_side(attacker, target)

    def damage_actor(self, target, amount, attacker):
        if self.state == "finished" or not target.alive or target.invulnerable > 0.0:
            return False
        target.hp = max(0, target.hp - max(0, int(amount)))
        target.hit_flash = 0.13
        if target.human:
            self.damage_flash = 0.24
        if target.hp <= 0:
            self.kill_actor(target, attacker)
            return True
        return False

    def kill_actor(self, victim, killer):
        if not victim.alive:
            return
        victim.alive = False
        victim.hp = 0
        victim.deaths += 1
        victim.respawn_timer = 3.0
        victim.reload_timer = 0.0
        victim.fire_timer = 0.0
        victim.overdrive = 0.0
        victim.target_id = -1
        if killer is not None and killer is not victim:
            killer.kills += 1
            if self.mode == "tdm":
                self.team_scores[killer.team] += 1
            if killer.human:
                self.kill_flash = 0.55
                self.notify("ELIMINOU " + victim.name, 1.2)
        killer_name = killer.name if killer is not None else "ARENA"
        self.kill_feed.insert(0, [killer_name + "  >  " + victim.name, 4.2, killer.team if killer else -1])
        self.kill_feed = self.kill_feed[:5]
        if victim.human:
            self.notify("ELIMINADO POR " + killer_name, 1.6)
        self.check_winner()

    def check_winner(self):
        if self.state == "finished":
            return
        if self.mode == "ffa":
            leader = max(self.actors, key=lambda actor: actor.kills)
            if leader.kills >= 50:
                self.winner_text = "VITORIA" if leader.human else leader.name + " VENCEU"
                self.state = "finished"
                self.set_mouse_capture(False)
        else:
            for team in (0, 1):
                if self.team_scores[team] >= 100:
                    self.winner_text = "VITORIA DA SUA EQUIPE" if team == self.player.team else "DERROTA - EQUIPE INIMIGA VENCEU"
                    self.state = "finished"
                    self.set_mouse_capture(False)

    def cancel_spawn_protection(self, actor):
        actor.invulnerable = 0.0

    def fire_ray(self, attacker, direction, damage, vertical_jitter=0.0, pierce=False):
        wall_distance = 999.0 if pierce else self.cast_ray(attacker.pos, direction)[0]
        targets = []
        for target in self.actors:
            if not self.valid_target(attacker, target):
                continue
            offset = target.pos - attacker.pos
            along = offset.dot(direction)
            if along <= 0.0 or along > wall_distance + 0.02:
                continue
            lateral_sq = max(0.0, offset.length_squared() - along * along)
            radius = target.radius + (0.09 if pierce else 0.025)
            if lateral_sq > radius * radius:
                continue
            if attacker.human:
                projected = self.project_point(target.pos)
                if projected is None:
                    continue
                _, depth = projected
                top, bottom = self.actor_vertical_bounds(depth)
                shot_y = VIEW_H // 2 + vertical_jitter
                if shot_y < top or shot_y > bottom:
                    continue
            targets.append((along, target))
        targets.sort(key=lambda item: item[0])
        hit_any = False
        maximum = 3 if pierce else 1
        for _, target in targets[:maximum]:
            self.damage_actor(target, damage, attacker)
            hit_any = True
            if attacker.human:
                self.hit_marker = 0.13
        return hit_any

    def player_fire(self):
        actor = self.player
        if self.state != "playing" or not actor.alive or actor.fire_timer > 0.0 or actor.reload_timer > 0.0:
            return False
        data = WEAPONS[actor.weapon]
        free_ammo = actor.weapon == "smg" and actor.overdrive > 0.0
        if actor.ammo <= 0 and not free_ammo:
            self.start_reload(actor)
            return False
        if not free_ammo:
            actor.ammo -= 1
        speed_factor = 0.52 if actor.weapon == "smg" and actor.overdrive > 0.0 else 1.0
        shot_delay = data["delay"] * speed_factor
        actor.fire_timer = actor.fire_timer + shot_delay if actor.fire_timer < 0.0 else shot_delay
        actor.muzzle = 0.07
        actor.invulnerable = 0.0
        spread = data["spread"] * (0.55 if self.on_ground and self.walk_amount < 0.2 else 1.0)
        any_hit = False
        for _ in range(data["pellets"]):
            angle = self.rng.range(-spread, spread)
            direction = actor.direction.rotate(angle)
            vertical = self.rng.range(-spread, spread) * 0.62
            if self.fire_ray(actor, direction, data["damage"], vertical):
                any_hit = True
        self.recoil = min(2.0, self.recoil + (1.25 if actor.weapon == "shotgun" else 0.32))
        self.tracers.append([actor.weapon, 0.10, self.rng.range(-1.0, 1.0)])
        if actor.ammo <= 0 and not free_ammo:
            self.notify("PENTE VAZIO - R PARA RECARREGAR", 1.0)
        return True

    def use_special(self):
        actor = self.player
        if not actor.alive or actor.special_timer > 0.0 or actor.reload_timer > 0.0:
            if actor.special_timer > 0.0:
                self.notify("HABILIDADE EM RECARGA  " + str(int(actor.special_timer + 0.9)) + "s", 0.8)
            return False
        data = WEAPONS[actor.weapon]
        actor.special_timer = data["special_cd"]
        actor.invulnerable = 0.0
        self.special_effect = 0.55
        if actor.weapon == "shotgun":
            hit = 0
            for target in self.actors:
                if not self.valid_target(actor, target):
                    continue
                offset = target.pos - actor.pos
                distance = offset.length()
                if distance <= 0.05 or distance > 4.4:
                    continue
                direction = offset / distance
                if direction.dot(actor.direction) < 0.36 or not self.has_line_of_sight(actor.pos, target.pos):
                    continue
                damage = int(82 - distance * 9)
                self.damage_actor(target, damage, actor)
                self.move_actor(target, direction * max(0.2, 1.4 - distance * 0.18))
                hit += 1
            # O recuo da onda tambem funciona como um pequeno blast-jump.
            if self.on_ground:
                self.vertical_velocity = 3.0
                self.on_ground = False
            self.recoil = 2.0
            self.notify("ONDA CINETICA  " + str(hit) + " ALVOS", 1.0)
        elif actor.weapon == "smg":
            actor.overdrive = 5.0
            actor.ammo = max(actor.ammo, 1)
            self.notify("SUPERALIMENTACAO: PENTE INFINITO", 1.5)
        else:
            direction = actor.direction
            self.fire_ray(actor, direction, 88, 0.0, True)
            self.tracers.append(["rail", 0.35, 0.0])
            self.recoil = 1.8
            self.notify("PROJETIL FANTASMA DISPARADO", 1.0)
        return True

    # ------------------------------------------------------------------
    # Simulacao do jogador e dos nove bots
    # ------------------------------------------------------------------
    def world_horizon(self):
        return int(VIEW_H * 0.5 + self.pitch)

    def update(self, dt):
        dt = min(max(dt, 0.0), 0.05)
        if self.state == "countdown":
            self.countdown -= dt
            if self.countdown <= 0.0:
                self.countdown = 0.0
                self.state = "playing"
                self.notify("LUTE!", 1.0)
            return
        if self.state != "playing":
            return
        self.match_time += dt
        self.message_timer = max(0.0, self.message_timer - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)
        self.hit_marker = max(0.0, self.hit_marker - dt)
        self.kill_flash = max(0.0, self.kill_flash - dt)
        self.recoil = max(0.0, self.recoil - dt * 6.8)
        self.special_effect = max(0.0, self.special_effect - dt)
        for tracer in self.tracers:
            tracer[1] -= dt
        self.tracers = [tracer for tracer in self.tracers if tracer[1] > 0.0]
        for feed in self.kill_feed:
            feed[1] -= dt
        self.kill_feed = [feed for feed in self.kill_feed if feed[1] > 0.0]

        automatic_held = (
            self.player.alive and WEAPONS[self.player.weapon]["automatic"]
            and pygame.mouse.get_pressed(3)[0]
        )
        for actor in self.actors:
            if actor is self.player and automatic_held:
                actor.fire_timer = max(-0.20, actor.fire_timer - dt)
            else:
                actor.fire_timer = max(0.0, actor.fire_timer - dt)
            actor.special_timer = max(0.0, actor.special_timer - dt)
            actor.overdrive = max(0.0, actor.overdrive - dt)
            actor.hit_flash = max(0.0, actor.hit_flash - dt)
            actor.muzzle = max(0.0, actor.muzzle - dt)
            actor.invulnerable = max(0.0, actor.invulnerable - dt)
            if actor.reload_timer > 0.0:
                actor.reload_timer -= dt
                if actor.reload_timer <= 0.0:
                    actor.reload_timer = 0.0
                    actor.ammo = WEAPONS[actor.weapon]["mag"]
                    if actor.human:
                        self.notify("ARMA PRONTA", 0.7)
            if not actor.alive:
                actor.respawn_timer -= dt
                if actor.respawn_timer <= 0.0:
                    self.spawn_actor(actor)
                    if actor.human:
                        self.notify("RESPAWN - PROTECAO TEMPORARIA", 1.4)

        if self.player.alive:
            self.update_player(dt)
            data = WEAPONS[self.player.weapon]
            if data["automatic"] and automatic_held:
                # Limite por quadro evita rajadas infinitas depois de um engasgo.
                shots = 0
                while self.player.fire_timer <= 0.0 and shots < 3:
                    if not self.player_fire():
                        break
                    shots += 1
        else:
            self.walk_amount = max(0.0, self.walk_amount - dt * 8.0)
            self.camera_z = max(0.0, self.camera_z - dt * 2.0)
        self.update_bots(dt)

    def update_player(self, dt):
        keys = pygame.key.get_pressed()
        forward = int(keys[pygame.K_w]) - int(keys[pygame.K_s])
        strafe = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        movement = pygame.Vector2()
        if forward:
            movement += self.player.direction * forward
        if strafe:
            movement += pygame.Vector2(-self.player.direction.y, self.player.direction.x) * strafe
        moving = movement.length_squared() > 0.0001
        if moving:
            movement = movement.normalize() * 3.15 * dt
            self.move_actor(self.player, movement)
            self.walk_phase = (self.walk_phase + dt * 470.0) % 360.0
            self.walk_amount = min(1.0, self.walk_amount + dt * 8.0)
        else:
            self.walk_amount = max(0.0, self.walk_amount - dt * 8.0)

        # Integracao vertical dt-safe. O jogador so pode saltar novamente no chao.
        if not self.on_ground:
            self.vertical_velocity -= 13.2 * dt
            self.camera_z += self.vertical_velocity * dt
            if self.camera_z <= 0.0:
                self.camera_z = 0.0
                self.vertical_velocity = 0.0
                self.on_ground = True
        else:
            self.camera_z = 0.0

    def choose_bot_target(self, bot):
        candidates = [actor for actor in self.actors if self.valid_target(bot, actor)]
        if not candidates:
            bot.target_id = -1
            return None
        target = min(candidates, key=lambda actor: bot.pos.distance_squared_to(actor.pos))
        bot.target_id = target.actor_id
        return target

    def bot_shoot(self, bot, target, distance):
        data = WEAPONS[bot.weapon]
        if bot.fire_timer > 0.0 or bot.reload_timer > 0.0 or not bot.alive:
            return
        if bot.ammo <= 0:
            self.start_reload(bot)
            return
        bot.ammo -= 1
        bot.fire_timer = data["delay"] * self.rng.range(0.90, 1.18)
        bot.muzzle = 0.07
        bot.invulnerable = 0.0
        accuracy = clamp(0.93 - distance * 0.055, 0.24, 0.84)
        if bot.weapon == "shotgun":
            accuracy = clamp(1.02 - distance * 0.11, 0.16, 0.92)
            damage = data["damage"] * self.rng.integer(2, 5)
        else:
            damage = data["damage"]
        if target.human and not self.on_ground:
            accuracy *= 0.68
        if self.rng.random() < accuracy:
            self.damage_actor(target, damage, bot)
        if bot.ammo <= 0:
            self.start_reload(bot)

    def update_bots(self, dt):
        for bot in self.bots:
            if not bot.alive:
                continue
            bot.think_timer -= dt
            bot.path_timer -= dt
            bot.wander_timer -= dt
            target = self.actor_by_id(bot.target_id)
            if target is None or not self.valid_target(bot, target) or bot.think_timer <= 0.0:
                target = self.choose_bot_target(bot)
                bot.think_timer = self.rng.range(0.18, 0.34)
            if target is None:
                if bot.wander_timer <= 0.0:
                    bot.direction.rotate_ip(self.rng.range(-125.0, 125.0))
                    bot.wander_timer = self.rng.range(0.8, 2.0)
                self.move_actor(bot, bot.direction * 1.1 * dt)
                continue

            offset = target.pos - bot.pos
            distance_sq = offset.length_squared()
            if distance_sq < 0.0001:
                continue
            distance = distance_sq ** 0.5
            direct = offset / distance
            can_see = distance < 13.5 and self.has_line_of_sight(bot.pos, target.pos)

            # Giro gradual torna o bot legivel e impede tiros instantaneos para tras.
            angle = bot.direction.angle_to(direct)
            bot.direction.rotate_ip(clamp(angle, -210.0 * dt, 210.0 * dt))
            if bot.direction.length_squared() > 0.001:
                bot.direction = bot.direction.normalize()

            weapon_range = 5.2 if bot.weapon == "shotgun" else 10.5
            facing = bot.direction.dot(direct)
            if can_see and distance < weapon_range and facing > 0.93:
                self.bot_shoot(bot, target, distance)

            desired = 2.4 if bot.weapon == "shotgun" else (4.5 if bot.weapon == "smg" else 6.2)
            if can_see:
                if distance > desired + 0.8:
                    move_direction = direct
                elif distance < desired - 0.8:
                    move_direction = -direct
                else:
                    move_direction = pygame.Vector2(-direct.y, direct.x) * bot.strafe_sign
                    if self.rng.random() < dt * 0.35:
                        bot.strafe_sign *= -1
            else:
                if bot.path_point is None or bot.path_timer <= 0.0 or bot.pos.distance_squared_to(bot.path_point) < 0.10:
                    bot.path_point = self.next_path_step(bot.pos, target.pos)
                    bot.path_timer = self.rng.range(0.32, 0.55)
                if bot.path_point is not None:
                    route = bot.path_point - bot.pos
                    move_direction = route.normalize() if route.length_squared() > 0.001 else direct
                else:
                    move_direction = direct
            speed = 2.05 if bot.weapon == "smg" else 1.88
            old = pygame.Vector2(bot.pos)
            self.move_actor(bot, move_direction * speed * dt)
            if bot.pos.distance_squared_to(old) < 0.000001:
                side = pygame.Vector2(-move_direction.y, move_direction.x) * bot.strafe_sign
                self.move_actor(bot, side * speed * dt)

    # ------------------------------------------------------------------
    # Renderizacao pseudo-3D procedural
    # ------------------------------------------------------------------
    def eye_height(self):
        bob = wave(self.walk_phase * 2.0) * 0.012 * self.walk_amount if self.on_ground else 0.0
        return 0.56 + self.camera_z + bob

    def draw_background(self):
        theme = MAP_INFO[self.map_index]
        horizon = self.world_horizon()
        eye = self.eye_height()
        self.view.fill(theme["sky"])
        sky_end = clamp(horizon, 0, VIEW_H)
        for y in range(0, sky_end, 4):
            amount = y / max(1, sky_end)
            color = mix(shade(theme["sky"], 0.55), theme["horizon"], amount)
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 4))
        floor_start = clamp(horizon, 0, VIEW_H)
        for y in range(floor_start, VIEW_H, 3):
            amount = (y - floor_start) / max(1, VIEW_H - floor_start)
            color = mix(theme["floor"], shade(theme["floor"], 0.38), amount)
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 3))
        # Linhas de perspectiva no piso reforcam altura, salto e inclinacao.
        for step in range(1, 13):
            y = int(horizon + eye * VIEW_H / (step * 0.62))
            if 0 <= y < VIEW_H:
                pygame.draw.line(self.view, shade(theme["floor"], 0.70), (0, y), (VIEW_W, y))
        if self.map_index == 0:
            # Neve procedural caindo ao longe.
            tick = pygame.time.get_ticks() // 18
            for index in range(38):
                x = (index * 73 + tick * (1 + index % 3)) % VIEW_W
                y = (index * 41 + tick * 2) % max(1, sky_end + 40) - 20
                pygame.draw.circle(self.view, (224, 241, 249), (x, y), 1)
        elif self.map_index == 3:
            moon_x, moon_y = VIEW_W - 62, clamp(horizon - 69, 20, 92)
            pygame.draw.circle(self.view, (192, 186, 211), (moon_x, moon_y), 14)
            pygame.draw.circle(self.view, theme["sky"], (moon_x + 6, moon_y - 3), 13)

    def draw_walls(self):
        theme = MAP_INFO[self.map_index]
        horizon = self.world_horizon()
        eye = self.eye_height()
        projection = VIEW_H
        right = pygame.Vector2(-self.player.direction.y, self.player.direction.x)
        for x in range(VIEW_W):
            camera_x = 2.0 * x / VIEW_W - 1.0
            ray = self.player.direction + right * (camera_x * 0.66)
            distance, side, cell, position = self.cast_ray(self.player.pos, ray)
            corrected = max(0.001, distance)
            self.z_buffer[x] = corrected
            top = int(horizon - (1.0 - eye) * projection / corrected)
            bottom = int(horizon + eye * projection / corrected)
            if bottom < 0 or top >= VIEW_H:
                continue
            base = theme["walls"].get(cell, (100, 100, 100))
            fog = clamp(1.08 - corrected / 18.5, 0.20, 1.0)
            face = 0.72 if side else 1.0
            stripe = 0.80 if int(position * 12) % 3 == 0 else 1.0
            color = mix(theme["fog"], shade(base, face * stripe), fog)
            pygame.draw.line(self.view, color, (x, max(-20, top)), (x, min(VIEW_H + 20, bottom)))
            if int(position * 16) in (0, 15):
                seam = shade(color, 0.62)
                pygame.draw.line(self.view, seam, (x, max(0, top)), (x, min(VIEW_H - 1, bottom)))
            # Filete superior ajuda a leitura das salas ao olhar verticalmente.
            if 0 <= top < VIEW_H and x % 2 == 0:
                self.view.set_at((x, top), shade(color, 1.25))

    def actor_vertical_bounds(self, depth):
        horizon = self.world_horizon()
        eye = self.eye_height()
        top = horizon - (0.88 - eye) * VIEW_H / depth
        bottom = horizon + eye * VIEW_H / depth
        return int(top), int(bottom)

    def make_actor_sprite(self, actor, width, height):
        width = max(5, width)
        height = max(9, height)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        team = TEAM_COLORS[actor.team]
        armor = (232, 232, 228) if actor.hit_flash <= 0.0 else (255, 255, 255)
        dark = shade(team, 0.35)
        cx = width // 2
        head_r = max(2, width // 5)
        head_y = max(head_r + 1, int(height * 0.20))
        # Sombra, pernas, torso blindado, ombreiras e capacete.
        pygame.draw.ellipse(surface, (0, 0, 0, 80), (width//8, int(height*0.90), width*3//4, max(2, height//12)))
        pygame.draw.polygon(surface, dark, ((cx-1, int(height*.58)), (cx-width//3, int(height*.91)), (cx-width//10, int(height*.94)), (cx+1, int(height*.65))))
        pygame.draw.polygon(surface, dark, ((cx+1, int(height*.58)), (cx+width//3, int(height*.91)), (cx+width//10, int(height*.94)), (cx-1, int(height*.65))))
        pygame.draw.polygon(surface, team, ((cx-width//3, int(height*.35)), (cx+width//3, int(height*.35)), (cx+width//4, int(height*.69)), (cx-width//4, int(height*.69))))
        pygame.draw.rect(surface, armor, (cx-width//5, int(height*.38), max(2, width*2//5), max(2, int(height*.20))))
        pygame.draw.circle(surface, team, (cx-width//3, int(height*.42)), max(1, width//7))
        pygame.draw.circle(surface, team, (cx+width//3, int(height*.42)), max(1, width//7))
        pygame.draw.circle(surface, armor, (cx, head_y), head_r)
        pygame.draw.rect(surface, (25, 38, 45), (cx-head_r, head_y, head_r*2, max(1, head_r//2)))
        pygame.draw.line(surface, (18, 23, 27), (cx, int(height*.49)), (width-1, int(height*.59)), max(1, width//10))
        if actor.muzzle > 0.0:
            pygame.draw.circle(surface, (255, 215, 93), (width-2, int(height*.59)), max(1, width//8))
        if actor.invulnerable > 0.0:
            pygame.draw.ellipse(surface, (*team, 110), (1, 1, width-2, height-2), max(1, width//14))
        return surface

    def blit_occluded_actor(self, surface, left, top, depth):
        width, height = surface.get_size()
        start_x = max(0, left)
        end_x = min(VIEW_W, left + width)
        visible_runs = []
        run_start = None
        for screen_x in range(start_x, end_x):
            visible = depth < self.z_buffer[screen_x] + 0.08
            if visible and run_start is None:
                run_start = screen_x
            elif not visible and run_start is not None:
                visible_runs.append((run_start, screen_x))
                run_start = None
        if run_start is not None:
            visible_runs.append((run_start, end_x))
        for run_start, run_end in visible_runs:
            source_x = run_start - left
            self.view.blit(surface, (run_start, top), (source_x, 0, run_end-run_start, height))
        return visible_runs

    def draw_actors(self):
        visible = []
        for actor in self.actors:
            if actor is self.player or not actor.alive:
                continue
            projected = self.project_point(actor.pos)
            if projected is None:
                continue
            screen_x, depth = projected
            top, bottom = self.actor_vertical_bounds(depth)
            height = clamp(bottom - top, 9, VIEW_H * 3)
            top = bottom - height
            width = clamp(int(height * 0.43), 5, VIEW_W * 2)
            left = int(screen_x - width / 2)
            if left > VIEW_W or left + width < 0 or bottom < 0 or top > VIEW_H:
                continue
            visible.append((depth, actor, left, top, width, height, screen_x))
        visible.sort(key=lambda item: item[0], reverse=True)
        for depth, actor, left, top, width, height, screen_x in visible:
            sprite = self.make_actor_sprite(actor, width, height)
            visible_runs = self.blit_occluded_actor(sprite, left, top, depth)
            if not visible_runs:
                continue
            # Nome e vida aparecem somente numa distancia util.
            if depth < 9.5 and height > 13:
                bar_w = clamp(width + 4, 12, 48)
                bar_x = int(screen_x - bar_w / 2)
                bar_y = top - 7
                pygame.draw.rect(self.view, (17, 17, 20), (bar_x, bar_y, bar_w, 3))
                pygame.draw.rect(self.view, TEAM_COLORS[actor.team], (bar_x+1, bar_y+1, int((bar_w-2)*actor.hp/actor.max_hp), 1))
                label = self.view_font.render(actor.name, True, (244, 244, 244))
                self.view.blit(label, (int(screen_x-label.get_width()/2), bar_y-label.get_height()))

    def draw_weapon(self):
        data = WEAPONS[self.player.weapon]
        recoil_y = int(self.recoil * 7)
        bob_x = int(wave(self.walk_phase) * 5 * self.walk_amount)
        bob_y = int(abs(wave(self.walk_phase * 2)) * 3 * self.walk_amount)
        cx = VIEW_W // 2 + bob_x
        base_y = VIEW_H + 17 + recoil_y + bob_y
        color = data["color"]
        dark = shade(color, 0.30)
        if not self.player.alive:
            return
        if self.player.weapon == "shotgun":
            pygame.draw.polygon(self.view, dark, ((cx-55, base_y), (cx-35, base_y-70), (cx+18, base_y-74), (cx+50, base_y)))
            pygame.draw.rect(self.view, (74, 62, 52), (cx-28, base_y-82, 22, 64), border_radius=3)
            pygame.draw.rect(self.view, color, (cx-22, base_y-91, 42, 18), border_radius=3)
            pygame.draw.rect(self.view, (35, 39, 42), (cx+8, base_y-106, 12, 35))
        elif self.player.weapon == "smg":
            pygame.draw.polygon(self.view, dark, ((cx-52, base_y), (cx-34, base_y-61), (cx+42, base_y-57), (cx+59, base_y)))
            pygame.draw.rect(self.view, color, (cx-27, base_y-75, 60, 28), border_radius=5)
            pygame.draw.rect(self.view, (30, 38, 44), (cx+20, base_y-82, 40, 10))
            pygame.draw.rect(self.view, (40, 45, 48), (cx-6, base_y-49, 17, 44))
            if self.player.overdrive > 0.0:
                pygame.draw.line(self.view, (103, 247, 255), (cx-40, base_y-84), (cx+57, base_y-66), 2)
        else:
            pygame.draw.polygon(self.view, dark, ((cx-60, base_y), (cx-37, base_y-65), (cx+44, base_y-61), (cx+61, base_y)))
            pygame.draw.rect(self.view, color, (cx-35, base_y-80, 76, 28), border_radius=3)
            pygame.draw.polygon(self.view, (34, 42, 38), ((cx-5, base_y-54), (cx+17, base_y-54), (cx+9, base_y-8), (cx-12, base_y-9)))
            pygame.draw.rect(self.view, (27, 33, 31), (cx+33, base_y-87, 58, 10))
            pygame.draw.rect(self.view, (23, 30, 27), (cx-13, base_y-92, 30, 12), border_radius=4)
        if self.player.muzzle > 0.0:
            pygame.draw.polygon(self.view, (255, 221, 92), ((cx+88, base_y-82), (cx+110, base_y-91), (cx+94, base_y-75), (cx+113, base_y-63), (cx+88, base_y-69)))

    def draw_world(self):
        self.draw_background()
        self.draw_walls()
        self.draw_actors()
        # Tracers sao efeitos de tela curtos; o rail se destaca em magenta.
        for kind, _, jitter in self.tracers:
            if kind == "rail":
                pygame.draw.line(self.view, (236, 92, 255), (VIEW_W//2, VIEW_H//2), (VIEW_W-1, VIEW_H//2), 3)
                pygame.draw.line(self.view, (255, 235, 255), (VIEW_W//2, VIEW_H//2), (VIEW_W-1, VIEW_H//2), 1)
            else:
                pygame.draw.line(self.view, (255, 217, 118), (VIEW_W//2+22, VIEW_H-43), (VIEW_W//2+int(jitter*15), VIEW_H//2), 1)
        self.draw_weapon()
        pygame.transform.scale(self.view, (SCREEN_W, SCREEN_H), self.screen)

    # ------------------------------------------------------------------
    # HUD, placares, minimapa e menus
    # ------------------------------------------------------------------
    def text(self, value, font, color, position, center=False, shadow=True):
        surface = font.render(str(value), True, color)
        rect = surface.get_rect()
        rect.center = position if center else rect.center
        if not center:
            rect.topleft = position
        if shadow:
            shadow_surface = font.render(str(value), True, (0, 0, 0))
            shadow_rect = rect.move(2, 2)
            self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(surface, rect)
        return rect

    def panel(self, rect, color=(11, 15, 20), alpha=205, border=(78, 94, 111)):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (*color, alpha), surface.get_rect(), border_radius=8)
        pygame.draw.rect(surface, (*border, min(255, alpha+25)), surface.get_rect(), 1, border_radius=8)
        self.screen.blit(surface, rect.topleft)

    def draw_crosshair(self):
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        gap = 7 + int(self.recoil * 7)
        color = (255, 255, 255) if self.hit_marker <= 0.0 else (255, 82, 74)
        pygame.draw.line(self.screen, (0, 0, 0), (cx-gap-8, cy+1), (cx-gap+1, cy+1), 4)
        pygame.draw.line(self.screen, color, (cx-gap-8, cy), (cx-gap, cy), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (cx+gap, cy+1), (cx+gap+9, cy+1), 4)
        pygame.draw.line(self.screen, color, (cx+gap, cy), (cx+gap+8, cy), 2)
        pygame.draw.line(self.screen, color, (cx, cy-gap-8), (cx, cy-gap), 2)
        pygame.draw.line(self.screen, color, (cx, cy+gap), (cx, cy+gap+8), 2)
        if self.hit_marker > 0.0:
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                pygame.draw.line(self.screen, (255, 76, 69), (cx+sx*5, cy+sy*5), (cx+sx*11, cy+sy*11), 3)

    def draw_minimap(self):
        scale = 5
        width = MAP_W * scale
        height = MAP_H * scale
        x0, y0 = 18, 72
        self.panel(pygame.Rect(x0-8, y0-8, width+16, height+16), alpha=220)
        theme = MAP_INFO[self.map_index]
        for y in range(MAP_H):
            for x in range(MAP_W):
                cell = MAPS[self.map_index][y][x]
                color = (20, 25, 29) if cell == "." else shade(theme["walls"].get(cell, (80,80,80)), 0.68)
                pygame.draw.rect(self.screen, color, (x0+x*scale, y0+y*scale, scale, scale))
        for actor in self.actors:
            if not actor.alive:
                continue
            color = (255, 255, 255) if actor.human else TEAM_COLORS[actor.team]
            px = x0 + int(actor.pos.x * scale)
            py = y0 + int(actor.pos.y * scale)
            pygame.draw.circle(self.screen, color, (px, py), 3 if actor.human else 2)
        end = pygame.Vector2(x0 + self.player.pos.x*scale, y0+self.player.pos.y*scale) + self.player.direction*9
        pygame.draw.line(self.screen, (255,255,255), (x0+self.player.pos.x*scale, y0+self.player.pos.y*scale), end, 2)

    def draw_top_five(self):
        ranking = sorted(self.actors, key=lambda actor: (-actor.kills, actor.deaths, actor.actor_id))[:5]
        rect = pygame.Rect(SCREEN_W-242, 70, 222, 174)
        self.panel(rect, alpha=188)
        self.text("TOP 5  /  50 KILLS", self.font_small, (231, 236, 241), (rect.x+14, rect.y+10))
        for index, actor in enumerate(ranking):
            y = rect.y + 42 + index*24
            color = (255, 220, 91) if actor.human else (220, 225, 230)
            self.text(str(index+1), self.font_tiny, (122, 136, 149), (rect.x+13, y+2), shadow=False)
            self.text(actor.name, self.font_tiny, color, (rect.x+35, y+2), shadow=False)
            self.text(str(actor.kills), self.font_small, color, (rect.right-38, y-1), center=True, shadow=False)

    def draw_team_score(self):
        rect = pygame.Rect(SCREEN_W//2-151, 18, 302, 56)
        self.panel(rect, alpha=205)
        self.text(str(self.team_scores[0]), self.font, TEAM_COLORS[0], (rect.x+48, rect.y+14), center=True)
        self.text("AZUL", self.font_tiny, (197,213,229), (rect.x+88, rect.y+11), shadow=False)
        self.text("100", self.font_small, (240,240,240), (SCREEN_W//2, rect.y+17), center=True)
        self.text("VERMELHO", self.font_tiny, (229,201,201), (rect.right-91, rect.y+11), shadow=False)
        self.text(str(self.team_scores[1]), self.font, TEAM_COLORS[1], (rect.right-47, rect.y+14), center=True)
        total = max(1, self.team_scores[0] + self.team_scores[1])
        pygame.draw.rect(self.screen, TEAM_COLORS[0], (rect.x+12, rect.bottom-10, int((rect.width-24)*self.team_scores[0]/total), 4))
        pygame.draw.rect(self.screen, TEAM_COLORS[1], (rect.right-12-int((rect.width-24)*self.team_scores[1]/total), rect.bottom-10, int((rect.width-24)*self.team_scores[1]/total), 4))

    def draw_kill_feed(self):
        y = 268
        for text_value, timer, team in self.kill_feed:
            surface = self.font_tiny.render(text_value, True, (238, 241, 244))
            rect = pygame.Rect(SCREEN_W-surface.get_width()-35, y, surface.get_width()+20, 22)
            color = TEAM_COLORS[team] if team in (0, 1) else (112,112,112)
            pygame.draw.rect(self.screen, (*shade(color, 0.25), 210), rect, border_radius=4)
            pygame.draw.rect(self.screen, color, (rect.x, rect.y, 3, rect.height), border_radius=2)
            self.screen.blit(surface, (rect.x+10, rect.y+3))
            y += 25

    def draw_hud(self):
        self.draw_crosshair()
        data = WEAPONS[self.player.weapon]
        # Vida e identificacao no canto inferior esquerdo.
        hp_rect = pygame.Rect(20, SCREEN_H-104, 276, 82)
        self.panel(hp_rect, alpha=218, border=TEAM_COLORS[self.player.team])
        hp_color = (74, 222, 121) if self.player.hp > 55 else ((245, 180, 55) if self.player.hp > 25 else (244, 68, 61))
        self.text("VIDA", self.font_tiny, (180,190,199), (hp_rect.x+15, hp_rect.y+12), shadow=False)
        self.text(str(self.player.hp if self.player.alive else 0), self.font_big, hp_color, (hp_rect.x+57, hp_rect.y+48), center=True)
        pygame.draw.rect(self.screen, (31,36,40), (hp_rect.x+103, hp_rect.y+23, 155, 13), border_radius=5)
        pygame.draw.rect(self.screen, hp_color, (hp_rect.x+105, hp_rect.y+25, int(151*self.player.hp/100), 9), border_radius=4)
        self.text("K " + str(self.player.kills) + "   D " + str(self.player.deaths), self.font_small, (227,230,232), (hp_rect.x+104, hp_rect.y+47), shadow=False)

        # Arma, pente e habilidade no canto inferior direito.
        gun_rect = pygame.Rect(SCREEN_W-352, SCREEN_H-114, 332, 92)
        self.panel(gun_rect, alpha=218, border=data["color"])
        self.text(data["name"], self.font_small, data["color"], (gun_rect.x+15, gun_rect.y+9), shadow=False)
        ammo_text = "∞" if self.player.weapon == "smg" and self.player.overdrive > 0.0 else str(self.player.ammo)
        self.text(ammo_text, self.font_big, (247,247,240), (gun_rect.right-57, gun_rect.y+40), center=True)
        self.text("/ " + str(data["mag"]), self.font_tiny, (154,164,172), (gun_rect.right-36, gun_rect.y+49), shadow=False)
        special_ready = self.player.special_timer <= 0.0
        special_color = data["color"] if special_ready else (107,114,122)
        special_text = data["special"] if special_ready else data["special"] + "  " + str(int(self.player.special_timer+0.9)) + "s"
        self.text("RMB  " + special_text, self.font_tiny, special_color, (gun_rect.x+15, gun_rect.y+43), shadow=False)
        pygame.draw.rect(self.screen, (32,36,41), (gun_rect.x+15, gun_rect.y+68, 210, 8), border_radius=4)
        ready_fraction = 1.0 if special_ready else 1.0 - self.player.special_timer/data["special_cd"]
        pygame.draw.rect(self.screen, special_color, (gun_rect.x+16, gun_rect.y+69, int(208*ready_fraction), 6), border_radius=3)
        if self.player.reload_timer > 0.0:
            fraction = 1.0 - self.player.reload_timer/data["reload"]
            self.text("RECARREGANDO", self.font_small, (255,207,87), (SCREEN_W//2, SCREEN_H-82), center=True)
            pygame.draw.rect(self.screen, (22,24,28), (SCREEN_W//2-100, SCREEN_H-59, 200, 9), border_radius=4)
            pygame.draw.rect(self.screen, (255,207,87), (SCREEN_W//2-98, SCREEN_H-57, int(196*fraction), 5), border_radius=3)

        self.text(MAP_INFO[self.map_index]["name"], self.font_tiny, (220,225,229), (20, 20), shadow=False)
        mode_title = "CADA UM POR SI" if self.mode == "ffa" else "BATALHA DE TIMES"
        self.text(mode_title, self.font_tiny, (168,180,190), (20, 40), shadow=False)
        if self.mode == "ffa":
            self.draw_top_five()
        else:
            self.draw_team_score()
        self.draw_kill_feed()
        if self.show_map:
            self.draw_minimap()
        if self.player.invulnerable > 0.0 and self.player.alive:
            self.text("PROTECAO DE RESPAWN  " + str(round(self.player.invulnerable, 1)) + "s", self.font_small, (116,218,255), (SCREEN_W//2, 92), center=True)
        if self.message_timer > 0.0:
            self.text(self.message, self.font, (255,238,191), (SCREEN_W//2, SCREEN_H-142), center=True)
        if not self.player.alive:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((75, 0, 0, 70))
            self.screen.blit(overlay, (0,0))
            self.text("ELIMINADO", self.font_big, (255,95,83), (SCREEN_W//2, 120), center=True)
            self.text("RESPAWN EM " + str(max(1, int(self.player.respawn_timer+0.99))), self.font, (240,240,240), (SCREEN_W//2, 166), center=True)

        if self.damage_flash > 0.0:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 24, 16, int(110*self.damage_flash/0.24)), overlay.get_rect(), width=25)
            self.screen.blit(overlay, (0,0))
        if self.kill_flash > 0.0:
            self.text("ELIMINACAO", self.font, (255,221,83), (SCREEN_W//2, SCREEN_H//2+64), center=True)

    def draw_scoreboard(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((4, 7, 11, 225))
        self.screen.blit(overlay, (0, 0))
        title = "PLACAR - CADA UM POR SI" if self.mode == "ffa" else "PLACAR - BATALHA DE TIMES"
        self.text(title, self.font_big, (242,245,247), (SCREEN_W//2, 64), center=True)
        ranking = sorted(self.actors, key=lambda actor: (-actor.kills, actor.deaths, actor.actor_id))
        x, y, width = SCREEN_W//2-350, 116, 700
        self.panel(pygame.Rect(x, y, width, 424), alpha=225)
        self.text("#", self.font_small, (130,143,154), (x+25,y+17), shadow=False)
        self.text("JOGADOR", self.font_small, (130,143,154), (x+65,y+17), shadow=False)
        self.text("ARMA", self.font_small, (130,143,154), (x+300,y+17), shadow=False)
        self.text("KILLS", self.font_small, (130,143,154), (x+510,y+17), shadow=False)
        self.text("MORTES", self.font_small, (130,143,154), (x+600,y+17), shadow=False)
        for index, actor in enumerate(ranking):
            ry = y + 54 + index*35
            if actor.human:
                pygame.draw.rect(self.screen, (255,255,255,25), (x+10,ry-5,width-20,31), border_radius=4)
            color = (255,224,108) if actor.human else TEAM_COLORS[actor.team]
            self.text(index+1, self.font_small, color, (x+27,ry+8), center=True, shadow=False)
            self.text(actor.name, self.font_small, color, (x+65,ry), shadow=False)
            self.text(WEAPONS[actor.weapon]["role"], self.font_tiny, (190,199,206), (x+300,ry+3), shadow=False)
            self.text(actor.kills, self.font_small, (242,242,242), (x+535,ry+8), center=True, shadow=False)
            self.text(actor.deaths, self.font_small, (185,190,195), (x+635,ry+8), center=True, shadow=False)
        self.text("SEGURE TAB PARA VER O PLACAR", self.font_tiny, (151,161,170), (SCREEN_W//2, 571), center=True)

    def draw_menu_background(self):
        self.screen.fill((7, 11, 17))
        for y in range(0, SCREEN_H, 5):
            amount = y / SCREEN_H
            pygame.draw.rect(self.screen, mix((10,20,30), (18,9,25), amount), (0,y,SCREEN_W,5))
        tick = pygame.time.get_ticks() * 0.025
        for index in range(22):
            x = int((index * 137 + tick * (1 + index % 3)) % (SCREEN_W + 160) - 80)
            pygame.draw.line(self.screen, (20,36,48), (x,0), (x-230,SCREEN_H), 1)
        for y in range(90, SCREEN_H, 54):
            pygame.draw.line(self.screen, (19,28,38), (0,y), (SCREEN_W,y), 1)
        self.text("ARENA", self.font_huge, (232,238,243), (54,25), shadow=True)
        self.text("PROTOCOL", self.font_huge, (74,211,229), (305,25), shadow=True)
        self.text("SIMULACAO DE COMBATE // 10 OPERADORES", self.font_tiny, (118,139,156), (60,105), shadow=False)
        steps = (("01", "MAPA"), ("02", "ARMA"), ("03", "MODO"))
        active = {"map_menu":0,"weapon_menu":1,"mode_menu":2}.get(self.state,0)
        for index, (number, label) in enumerate(steps):
            x = SCREEN_W-330 + index*98
            color = (79,221,232) if index == active else ((152,173,184) if index < active else (60,72,82))
            pygame.draw.circle(self.screen, color, (x,65), 16, 2)
            self.text(number, self.font_tiny, color, (x,65), center=True, shadow=False)
            self.text(label, self.font_tiny, color, (x,91), center=True, shadow=False)

    def draw_map_preview(self, map_index, rect):
        grid = MAPS[map_index]
        theme = MAP_INFO[map_index]
        preview = pygame.Rect(rect.x+15, rect.y+14, 128, rect.height-28)
        pygame.draw.rect(self.screen, shade(theme["sky"],0.35), preview, border_radius=5)
        cell_w = preview.width / MAP_W
        cell_h = preview.height / MAP_H
        for y in range(MAP_H):
            for x in range(MAP_W):
                cell = grid[y][x]
                if cell != ".":
                    color = theme["walls"].get(cell,(100,100,100))
                    pygame.draw.rect(self.screen, color, (int(preview.x+x*cell_w), int(preview.y+y*cell_h), max(1,int(cell_w+1)), max(1,int(cell_h+1))))
        pygame.draw.rect(self.screen, theme["accent"], preview, 1, border_radius=5)

    def draw_map_menu(self):
        self.draw_menu_background()
        self.text("ESCOLHA A ARENA", self.font_big, (241,244,246), (60,138))
        self.text("Cada mapa muda corredores, distancias e linhas de tiro.", self.font_small, (145,160,171), (62,184), shadow=False)
        card_w, card_h = 465, 184
        positions = ((60,225),(575,225),(60,429),(575,429))
        for index, position in enumerate(positions):
            selected = index == self.menu_index
            theme = MAP_INFO[index]
            rect = pygame.Rect(position[0],position[1],card_w,card_h)
            self.panel(rect, color=(15,21,28), alpha=235 if selected else 195, border=theme["accent"] if selected else (48,61,72))
            self.draw_map_preview(index,rect)
            self.text(str(index+1).zfill(2), self.font_tiny, theme["accent"], (rect.x+164,rect.y+22), shadow=False)
            self.text(theme["name"], self.font, (246,247,248) if selected else (190,199,205), (rect.x+164,rect.y+47), shadow=False)
            self.text(theme["subtitle"], self.font_tiny, (141,156,167), (rect.x+164,rect.y+84), shadow=False)
            tags = ("MEDIO ALCANCE", "ROTAS LATERAIS") if index == 0 else (("LONGO ALCANCE", "RUA CENTRAL") if index == 1 else (("CURTO ALCANCE", "LABIRINTO") if index == 2 else ("SALAS FECHADAS", "EMBOSCADAS")))
            for tag_index, tag in enumerate(tags):
                tag_rect = pygame.Rect(rect.x+164,rect.y+112+tag_index*25,150,20)
                pygame.draw.rect(self.screen, shade(theme["accent"],0.20), tag_rect, border_radius=4)
                self.text(tag,self.font_tiny,theme["accent"],(tag_rect.x+7,tag_rect.y+2),shadow=False)
            if selected:
                pygame.draw.polygon(self.screen, theme["accent"], ((rect.right-22,rect.y+14),(rect.right-10,rect.y+14),(rect.right-10,rect.y+26)))
        self.text("SETAS / WASD PARA ESCOLHER     ENTER PARA CONFIRMAR", self.font_tiny, (150,163,174), (SCREEN_W//2,649), center=True, shadow=False)

    def draw_weapon_icon(self, key, center, color):
        x,y = center
        if key == "shotgun":
            pygame.draw.rect(self.screen,color,(x-80,y-9,135,20),border_radius=4)
            pygame.draw.rect(self.screen,(39,45,49),(x+45,y-5,75,10))
            pygame.draw.polygon(self.screen,(91,64,42),((x-52,y+8),(x-5,y+8),(x-20,y+49),(x-53,y+45)))
        elif key == "smg":
            pygame.draw.rect(self.screen,color,(x-69,y-16,102,32),border_radius=7)
            pygame.draw.rect(self.screen,(39,45,49),(x+24,y-7,70,14))
            pygame.draw.rect(self.screen,(47,54,59),(x-11,y+11,23,51),border_radius=3)
        else:
            pygame.draw.rect(self.screen,color,(x-80,y-13,132,27),border_radius=4)
            pygame.draw.rect(self.screen,(35,42,39),(x+40,y-6,82,12))
            pygame.draw.polygon(self.screen,(42,50,45),((x-20,y+12),(x+12,y+12),(x+1,y+57),(x-28,y+52)))
            pygame.draw.rect(self.screen,(28,34,31),(x-25,y-28,43,15),border_radius=6)

    def stat_bar(self, x, y, label, amount, color):
        self.text(label,self.font_tiny,(151,162,171),(x,y),shadow=False)
        pygame.draw.rect(self.screen,(31,38,44),(x,y+19,190,8),border_radius=4)
        pygame.draw.rect(self.screen,color,(x+1,y+20,int(188*amount),6),border_radius=3)

    def draw_weapon_menu(self):
        self.draw_menu_background()
        self.text("ESCOLHA SEU ARMAMENTO", self.font_big, (241,244,246), (60,138))
        self.text("A reserva e infinita. O pente, a cadencia e o risco nao.",self.font_small,(145,160,171),(62,184),shadow=False)
        positions = (45,390,735)
        stats = {"shotgun":(1.0,0.25,0.30),"smg":(0.32,1.0,0.62),"rifle":(0.68,0.62,0.72)}
        for index,key in enumerate(WEAPON_ORDER):
            data=WEAPONS[key]
            selected=index==self.menu_index
            rect=pygame.Rect(positions[index],225,320,382)
            self.panel(rect,color=(15,21,28),alpha=238 if selected else 195,border=data["color"] if selected else (49,61,70))
            self.text(str(index+1).zfill(2),self.font_tiny,data["color"],(rect.x+18,rect.y+15),shadow=False)
            self.text(data["role"],self.font,(245,247,248) if selected else (187,196,202),(rect.centerx,rect.y+45),center=True,shadow=False)
            self.draw_weapon_icon(key,(rect.centerx,rect.y+114),data["color"])
            self.text(data["name"],self.font_small,data["color"],(rect.centerx,rect.y+184),center=True,shadow=False)
            power,rate,control=stats[key]
            self.stat_bar(rect.x+64,rect.y+215,"DANO",power,data["color"])
            self.stat_bar(rect.x+64,rect.y+254,"CADENCIA",rate,data["color"])
            self.stat_bar(rect.x+64,rect.y+293,"CONTROLE",control,data["color"])
            special_rect=pygame.Rect(rect.x+15,rect.bottom-48,rect.width-30,34)
            pygame.draw.rect(self.screen,shade(data["color"],0.18),special_rect,border_radius=5)
            self.text("RMB  "+data["special"],self.font_tiny,data["color"],(special_rect.centerx,special_rect.y+8),center=True,shadow=False)
        self.text("ESC VOLTA     SETAS / WASD ESCOLHEM     ENTER CONFIRMA",self.font_tiny,(150,163,174),(SCREEN_W//2,649),center=True,shadow=False)

    def draw_mode_menu(self):
        self.draw_menu_background()
        self.text("DEFINA AS REGRAS",self.font_big,(241,244,246),(60,138))
        self.text("Nove bots combatem, pontuam, morrem e voltam a arena com voce.",self.font_small,(145,160,171),(62,184),shadow=False)
        modes=(("CADA UM POR SI","FREE FOR ALL","10 JOGADORES","PRIMEIRO A 50 KILLS",(236,179,66)),("BATALHA DE TIMES","5 CONTRA 5","AZUL x VERMELHO","PRIMEIRO TIME A 100",(79,167,255)))
        for index,values in enumerate(modes):
            title,english,line1,line2,color=values
            selected=index==self.menu_index
            rect=pygame.Rect(90+index*505,242,415,302)
            self.panel(rect,color=(15,21,28),alpha=240 if selected else 195,border=color if selected else (49,61,70))
            pygame.draw.circle(self.screen,shade(color,0.22),(rect.centerx,rect.y+75),48)
            if index==0:
                for angle in range(0,360,45):
                    p=pygame.Vector2(33,0).rotate(angle)
                    pygame.draw.circle(self.screen,color,(int(rect.centerx+p.x),int(rect.y+75+p.y)),5)
            else:
                pygame.draw.circle(self.screen,TEAM_COLORS[0],(rect.centerx-22,rect.y+75),20)
                pygame.draw.circle(self.screen,TEAM_COLORS[1],(rect.centerx+22,rect.y+75),20)
                self.text("VS",self.font_tiny,(255,255,255),(rect.centerx,rect.y+75),center=True)
            self.text(title,self.font,(245,247,248),(rect.centerx,rect.y+147),center=True,shadow=False)
            self.text(english,self.font_tiny,color,(rect.centerx,rect.y+177),center=True,shadow=False)
            self.text(line1,self.font_small,(187,198,206),(rect.centerx,rect.y+219),center=True,shadow=False)
            self.text(line2,self.font_small,color,(rect.centerx,rect.y+252),center=True,shadow=False)
        self.text("ESC VOLTA     SETAS / WASD ESCOLHEM     ENTER INICIA",self.font_tiny,(150,163,174),(SCREEN_W//2,610),center=True,shadow=False)
        self.text(MAP_INFO[self.map_index]["name"]+"  //  "+WEAPONS[self.weapon_key]["name"],self.font_tiny,(91,211,224),(SCREEN_W//2,649),center=True,shadow=False)

    def draw_pause(self):
        overlay=pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
        overlay.fill((3,6,10,205))
        self.screen.blit(overlay,(0,0))
        self.text("PAUSADO",self.font_huge,(239,243,246),(SCREEN_W//2,185),center=True)
        self.text("ENTER / CLIQUE / ESC  -  CONTINUAR",self.font_small,(180,194,204),(SCREEN_W//2,284),center=True)
        self.text("Q  -  VOLTAR AO MENU",self.font_small,(180,194,204),(SCREEN_W//2,325),center=True)
        self.text("WASD MOVER  |  ESPACO PULAR  |  M MINIMAPA  |  TAB PLACAR",self.font_tiny,(114,134,149),(SCREEN_W//2,410),center=True,shadow=False)

    def draw_finished(self):
        self.draw_scoreboard()
        won=(self.mode=="ffa" and self.player.kills>=50) or (self.mode=="tdm" and self.team_scores[self.player.team]>=100)
        color=(103,229,150) if won else (244,98,83)
        banner=pygame.Surface((SCREEN_W,105),pygame.SRCALPHA)
        banner.fill((3,7,12,242))
        self.screen.blit(banner,(0,0))
        self.text(self.winner_text,self.font_big,color,(SCREEN_W//2,42),center=True)
        self.text("PARTIDA ENCERRADA",self.font_tiny,(173,187,197),(SCREEN_W//2,82),center=True)
        self.text("ENTER - REVANCHE     Q / ESC - SELECAO",self.font_small,(245,224,130),(SCREEN_W//2,620),center=True)

    def render(self):
        if self.state == "map_menu":
            self.draw_map_menu()
        elif self.state == "weapon_menu":
            self.draw_weapon_menu()
        elif self.state == "mode_menu":
            self.draw_mode_menu()
        else:
            self.draw_world()
            self.draw_hud()
            if self.state == "countdown":
                number=max(1,int(self.countdown+0.99))
                self.text(number,self.font_huge,(255,238,127),(SCREEN_W//2,SCREEN_H//2-20),center=True)
                self.text("PREPARE-SE",self.font,(240,244,247),(SCREEN_W//2,SCREEN_H//2+52),center=True)
                self.text("WASD MOVER  |  MOUSE MIRAR  |  ESPACO PULAR  |  LMB ATIRAR  |  RMB ESPECIAL  |  R RECARREGAR",self.font_tiny,(215,222,228),(SCREEN_W//2,SCREEN_H-30),center=True,shadow=False)
            elif self.state == "paused":
                self.draw_pause()
            elif self.state == "finished":
                self.draw_finished()
            elif pygame.key.get_pressed()[pygame.K_TAB]:
                self.draw_scoreboard()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt=self.clock.tick(FPS)/1000.0
            self.process_events()
            self.update(dt)
            self.render()
        self.set_mouse_capture(False)
        pygame.quit()


if __name__ == "__main__":
    Game().run()





