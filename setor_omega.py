import pygame


# ================================================================
# SETOR OMEGA - FPS pseudo-3D em um unico arquivo
# Nenhuma imagem, som, fonte, mapa ou outro arquivo externo e usado.
# ================================================================

SCREEN_W = 960
SCREEN_H = 600
VIEW_W = 320
VIEW_H = 200
FPS = 60

MAP_DATA = (
    "1111111111111111",
    "1..............1",
    "1..11....11....1",
    "1..1......1....1",
    "1..1..22..1....1",
    "1.....2...1....1",
    "1.111.2........1",
    "1.....222.111..1",
    "1..........1...1",
    "1.3333....11...1",
    "1.3..........3.1",
    "1.3..1111....3.1",
    "1.3..........3.1",
    "1.3333..111.33.1",
    "1.............D1",
    "1111111111111111",
)

MAP_W = len(MAP_DATA[0])
MAP_H = len(MAP_DATA)

WALL_COLORS = {
    "1": (54, 112, 142),
    "2": (144, 55, 48),
    "3": (88, 55, 130),
    "D": (190, 142, 35),
}

ENEMY_DATA = {
    "sentinela": {
        "name": "SENTINELA",
        "hp": 50,
        "speed": 1.15,
        "damage": 8,
        "attack_delay": 0.85,
        "color": (71, 196, 100),
        "eye": (250, 255, 120),
        "scale": 0.76,
    },
    "demonio": {
        "name": "DEMONIO",
        "hp": 100,
        "speed": 0.88,
        "damage": 12,
        "attack_delay": 1.0,
        "color": (201, 58, 55),
        "eye": (255, 218, 60),
        "scale": 0.9,
    },
    "bruto": {
        "name": "BRUTAMONTES",
        "hp": 175,
        "speed": 0.58,
        "damage": 18,
        "attack_delay": 1.25,
        "color": (132, 69, 171),
        "eye": (255, 102, 67),
        "scale": 1.08,
    },
}


def clamp(value, low, high):
    return max(low, min(high, value))


def shade(color, factor):
    return tuple(clamp(int(channel * factor), 0, 255) for channel in color)


class Player:
    def __init__(self):
        self.pos = pygame.Vector2(1.55, 1.55)
        self.direction = pygame.Vector2(1.0, 0.0)
        self.plane = pygame.Vector2(0.0, 0.66)
        self.radius = 0.20
        self.speed = 2.7
        self.health = 100
        self.max_health = 100


class Enemy:
    def __init__(self, x, y, kind):
        data = ENEMY_DATA[kind]
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.radius = 0.25 if kind != "bruto" else 0.32
        self.attack_timer = 0.0
        self.hit_flash = 0.0
        self.alerted = False
        self.path_target = None
        self.path_timer = 0.0

    @property
    def alive(self):
        return self.hp > 0


class Pickup:
    def __init__(self, x, y, kind):
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        self.active = True


class Missile:
    def __init__(self, pos, direction):
        self.pos = pygame.Vector2(pos)
        self.direction = pygame.Vector2(direction).normalize()
        self.speed = 5.4
        self.age = 0.0
        self.alive = True


class Explosion:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.age = 0.0
        self.duration = 0.52


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Setor Omega - FPS em um unico arquivo")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.view = pygame.Surface((VIEW_W, VIEW_H)).convert()
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 34)
        self.font_large = pygame.font.Font(None, 72)
        self.font_title = pygame.font.Font(None, 92)

        self.running = True
        self.mouse_captured = False
        self.show_map = False
        self.first_mouse_motion = True
        self.reset_game(show_intro=True)

    # ------------------------------------------------------------
    # Estado geral
    # ------------------------------------------------------------
    def reset_game(self, show_intro=False):
        self.player = Player()
        self.enemies = [
            Enemy(6.5, 1.5, "sentinela"),
            Enemy(13.5, 1.5, "demonio"),
            Enemy(5.5, 5.5, "sentinela"),
            Enemy(9.5, 8.5, "demonio"),
            Enemy(5.5, 10.5, "bruto"),
            Enemy(11.5, 12.5, "bruto"),
        ]
        self.pickups = [
            Pickup(8.5, 4.5, "medkit"),
            Pickup(1.5, 10.5, "medkit"),
            Pickup(11.5, 13.5, "key"),
        ]
        self.missiles = []
        self.explosions = []

        self.state = "intro" if show_intro else "playing"
        self.ammo = 12
        self.magazine_size = 12
        self.reload_timer = 0.0
        self.fire_timer = 0.0
        self.missile_timer = 0.0
        self.muzzle_timer = 0.0
        self.hit_marker_timer = 0.0
        self.damage_flash = 0.0
        self.recoil = 0.0
        self.pitch = 0.0
        self.enemy_grace_timer = 1.2
        self.walk_clock = 0.0
        self.walk_amount = 0.0
        self.has_key = False
        self.exit_unlocked = False
        self.message = ""
        self.message_timer = 0.0
        self.total_kills = 0
        self.z_buffer = [1000.0] * VIEW_W
        self.show_map = False

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

    def living_enemies(self):
        return sum(1 for enemy in self.enemies if enemy.alive)

    # ------------------------------------------------------------
    # Mapa, colisao e raios
    # ------------------------------------------------------------
    def map_cell(self, x, y):
        ix = int(x)
        iy = int(y)
        if ix < 0 or iy < 0 or ix >= MAP_W or iy >= MAP_H:
            return "1"
        return MAP_DATA[iy][ix]

    def is_wall_cell(self, cell):
        if cell == ".":
            return False
        if cell == "D" and self.exit_unlocked:
            return False
        return True

    def is_blocked(self, x, y, radius=0.18):
        points = (
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius),
        )
        return any(self.is_wall_cell(self.map_cell(px, py)) for px, py in points)

    def move_with_collision(self, pos, movement, radius):
        new_x = pos.x + movement.x
        if not self.is_blocked(new_x, pos.y, radius):
            pos.x = new_x
        new_y = pos.y + movement.y
        if not self.is_blocked(pos.x, new_y, radius):
            pos.y = new_y

    def player_position_clear(self, x, y):
        if self.is_blocked(x, y, self.player.radius):
            return False
        candidate = pygame.Vector2(x, y)
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            minimum = (self.player.radius + enemy.radius) * 0.88
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

    def next_path_step(self, start_position, goal_position):
        """BFS curto no mapa 16x16; devolve o centro da proxima celula."""
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
                if self.is_wall_cell(self.map_cell(neighbor[0], neighbor[1])):
                    continue
                parents[neighbor] = current
                queue.append(neighbor)

        if goal not in parents:
            return None

        step = goal
        while parents[step] is not None and parents[step] != start:
            step = parents[step]
        return pygame.Vector2(step[0] + 0.5, step[1] + 0.5)

    def cast_ray(self, origin, ray_direction, maximum_steps=64):
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

            hit_cell = self.map_cell(map_x, map_y)
            if self.is_wall_cell(hit_cell):
                break

        distance = max(0.0001, distance)
        if side == 0:
            wall_position = origin.y + distance * ray_y
        else:
            wall_position = origin.x + distance * ray_x
        wall_position -= int(wall_position)
        return distance, side, hit_cell, wall_position

    def has_line_of_sight(self, start, end):
        offset = end - start
        distance = offset.length()
        if distance <= 0.001:
            return True
        ray_distance, _, _, _ = self.cast_ray(start, offset / distance)
        return ray_distance + 0.06 >= distance

    # ------------------------------------------------------------
    # Entrada e controles
    # ------------------------------------------------------------
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
                    if self.state == "intro":
                        self.start_playing()
                    elif self.state == "paused":
                        self.start_playing()
                    elif self.state in ("dead", "won"):
                        self.reset_game(show_intro=False)

                elif event.key == pygame.K_r and self.state == "playing":
                    self.start_reload()

                elif event.key == pygame.K_m:
                    self.show_map = not self.show_map

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "intro":
                    self.start_playing()
                elif self.state == "paused":
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

    def start_reload(self):
        if self.reload_timer > 0.0:
            return
        if self.ammo >= self.magazine_size:
            self.notify("O PENTE JA ESTA CHEIO", 1.0)
            return
        self.reload_timer = 1.3
        self.notify("RECARREGANDO...", 1.3)

    def shoot(self):
        if self.fire_timer > 0.0 or self.reload_timer > 0.0:
            return
        if self.ammo <= 0:
            self.notify("SEM BALAS NO PENTE - PRESSIONE R", 1.5)
            return

        self.ammo -= 1
        self.fire_timer = 0.22
        self.muzzle_timer = 0.075
        self.recoil = 1.0

        wall_distance, _, _, _ = self.cast_ray(
            self.player.pos, self.player.direction
        )
        target = None
        target_distance = 1000.0

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            to_enemy = enemy.pos - self.player.pos
            along = to_enemy.dot(self.player.direction)
            if along <= 0.0:
                continue
            lateral_squared = max(0.0, to_enemy.length_squared() - along * along)
            hit_radius = enemy.radius + 0.02
            if lateral_squared > hit_radius * hit_radius:
                continue
            half_chord = (hit_radius * hit_radius - lateral_squared) ** 0.5
            entry_distance = along - half_chord
            if entry_distance >= wall_distance - 0.001:
                continue

            # O raycaster simula olhar para cima/baixo deslocando o horizonte.
            # A checagem vertical faz o tiro acompanhar a mira visivel, em vez
            # de acertar um monstro quando a mira esta acima ou abaixo dele.
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
            crosshair_y = VIEW_H // 2
            if not sprite_top - 2 <= crosshair_y <= sprite_bottom + 2:
                continue

            if along < target_distance:
                target = enemy
                target_distance = along

        if target is not None:
            was_alive = target.alive
            target.hp = max(0, target.hp - 25)
            target.hit_flash = 0.13
            target.alerted = True
            self.hit_marker_timer = 0.12
            if was_alive and not target.alive:
                self.total_kills += 1
                self.notify(ENEMY_DATA[target.kind]["name"] + " ELIMINADO", 1.1)

    def launch_missile(self):
        if self.missile_timer > 0.0:
            self.notify("PLASMA RECARREGANDO", 0.7)
            return
        start = self.player.pos + self.player.direction * 0.36
        if self.is_blocked(start.x, start.y, 0.08):
            self.notify("SEM ESPACO PARA LANCAR", 0.8)
            return
        self.missiles.append(Missile(start, self.player.direction))
        self.missile_timer = 2.5
        self.recoil = 1.4
        self.notify("MISSIL DE PLASMA", 0.65)

    # ------------------------------------------------------------
    # Atualizacao da partida
    # ------------------------------------------------------------
    def update(self, dt):
        dt = min(dt, 0.05)
        if self.state != "playing":
            return

        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.missile_timer = max(0.0, self.missile_timer - dt)
        self.muzzle_timer = max(0.0, self.muzzle_timer - dt)
        self.hit_marker_timer = max(0.0, self.hit_marker_timer - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)
        self.recoil = max(0.0, self.recoil - dt * 7.5)
        self.message_timer = max(0.0, self.message_timer - dt)
        self.enemy_grace_timer = max(0.0, self.enemy_grace_timer - dt)

        if self.reload_timer > 0.0:
            self.reload_timer -= dt
            if self.reload_timer <= 0.0:
                self.reload_timer = 0.0
                self.ammo = self.magazine_size
                self.notify("ARMA CARREGADA", 0.8)

        self.update_player(dt)
        self.update_enemies(dt)
        if self.state != "playing":
            return
        self.update_missiles(dt)
        self.update_pickups()
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
            movement = movement.normalize() * self.player.speed * dt
            self.move_player_with_collision(movement)
            self.walk_clock = (self.walk_clock + dt * 300.0) % 360.0
            self.walk_amount = min(1.0, self.walk_amount + dt * 8.0)
        else:
            self.walk_amount = max(0.0, self.walk_amount - dt * 8.0)

    def update_enemies(self, dt):
        # Efeitos visuais e cooldowns continuam correndo durante a breve
        # protecao inicial; apenas a perseguicao fica bloqueada.
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy.attack_timer = max(0.0, enemy.attack_timer - dt)
            enemy.hit_flash = max(0.0, enemy.hit_flash - dt)
            enemy.path_timer = max(0.0, enemy.path_timer - dt)

        if self.enemy_grace_timer > 0.0:
            return

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            to_player = self.player.pos - enemy.pos
            distance_squared = to_player.length_squared()

            can_see = distance_squared < 100.0 and self.has_line_of_sight(
                enemy.pos, self.player.pos
            )
            if can_see:
                enemy.alerted = True

            if not enemy.alerted or distance_squared <= 0.0001:
                continue

            distance = distance_squared ** 0.5
            data = ENEMY_DATA[enemy.kind]

            if can_see:
                direction = to_player / distance
                enemy.path_target = None
                enemy.path_timer = 0.0
            else:
                if (
                    enemy.path_target is None
                    or enemy.path_timer <= 0.0
                    or enemy.pos.distance_squared_to(enemy.path_target) < 0.035
                ):
                    enemy.path_target = self.next_path_step(
                        enemy.pos, self.player.pos
                    )
                    enemy.path_timer = 0.32
                if enemy.path_target is None:
                    continue
                path_vector = enemy.path_target - enemy.pos
                if path_vector.length_squared() <= 0.0001:
                    continue
                direction = path_vector.normalize()

            if distance > 0.73:
                movement = direction * data["speed"] * dt
                old_position = pygame.Vector2(enemy.pos)
                self.move_with_collision(enemy.pos, movement, enemy.radius)

                # Evita que varios monstros ocupem exatamente o mesmo lugar.
                overlaps = any(
                    other is not enemy
                    and other.alive
                    and enemy.pos.distance_squared_to(other.pos)
                    < (enemy.radius + other.radius) ** 2 * 0.72
                    for other in self.enemies
                )
                if overlaps:
                    enemy.pos = pygame.Vector2(old_position)

                # Se uma quina travar a perseguicao, tenta deslizar pelo outro eixo.
                if enemy.pos.distance_squared_to(old_position) < 0.00000001:
                    alternate = pygame.Vector2(-direction.y, direction.x)
                    if int((enemy.pos.x + enemy.pos.y) * 10) % 2:
                        alternate *= -1
                    self.move_with_collision(
                        enemy.pos, alternate * data["speed"] * dt * 0.7, enemy.radius
                    )
                    overlaps = any(
                        other is not enemy
                        and other.alive
                        and enemy.pos.distance_squared_to(other.pos)
                        < (enemy.radius + other.radius) ** 2 * 0.72
                        for other in self.enemies
                    )
                    if overlaps:
                        enemy.pos = pygame.Vector2(old_position)
            elif can_see and enemy.attack_timer <= 0.0:
                self.player.health = max(0, self.player.health - data["damage"])
                enemy.attack_timer = data["attack_delay"]
                self.damage_flash = 0.22
                self.notify("VOCE FOI ATINGIDO!", 0.7)
                if self.player.health <= 0:
                    self.state = "dead"
                    self.set_mouse_capture(False)
                    return

    def update_pickups(self):
        for pickup in self.pickups:
            if not pickup.active:
                continue
            if pickup.pos.distance_squared_to(self.player.pos) > 0.26:
                continue

            if pickup.kind == "medkit":
                if self.player.health >= self.player.max_health:
                    continue
                healed = min(30, self.player.max_health - self.player.health)
                self.player.health += healed
                pickup.active = False
                self.notify("KIT MEDICO  +" + str(healed) + " HP", 1.4)
            elif pickup.kind == "key":
                pickup.active = False
                self.has_key = True
                self.notify("CARTAO AMARELO COLETADO", 1.8)

    def explode(self, position):
        self.explosions.append(Explosion(position))
        blast_radius = 2.0
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            distance = enemy.pos.distance_to(position)
            if distance > blast_radius:
                continue
            if not self.has_line_of_sight(position, enemy.pos):
                continue
            damage = max(20, int(78 * (1.0 - distance / blast_radius)))
            was_alive = enemy.alive
            enemy.hp = max(0, enemy.hp - damage)
            enemy.hit_flash = 0.18
            enemy.alerted = True
            if was_alive and not enemy.alive:
                self.total_kills += 1
                self.notify(ENEMY_DATA[enemy.kind]["name"] + " EXPLODIU", 1.1)

    def update_missiles(self, dt):
        for missile in self.missiles:
            if not missile.alive:
                continue
            missile.age += dt
            step_distance = missile.speed * dt / 4.0

            for _ in range(4):
                next_pos = missile.pos + missile.direction * step_distance
                if self.is_blocked(next_pos.x, next_pos.y, 0.08):
                    missile.alive = False
                    self.explode(missile.pos)
                    break

                missile.pos = next_pos
                hit_enemy = False
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                    radius = enemy.radius + 0.12
                    if enemy.pos.distance_squared_to(missile.pos) <= radius * radius:
                        missile.alive = False
                        self.explode(missile.pos)
                        hit_enemy = True
                        break
                if hit_enemy:
                    break

            if missile.age > 4.0 and missile.alive:
                missile.alive = False
                self.explode(missile.pos)

        self.missiles = [missile for missile in self.missiles if missile.alive]

    def update_explosions(self, dt):
        for explosion in self.explosions:
            explosion.age += dt
        self.explosions = [
            explosion
            for explosion in self.explosions
            if explosion.age < explosion.duration
        ]

    def update_objective(self):
        should_unlock = self.has_key and self.living_enemies() == 0
        if should_unlock and not self.exit_unlocked:
            self.exit_unlocked = True
            self.notify("SAIDA DESTRANCADA - ENCONTRE A PORTA", 2.4)

        if self.exit_unlocked and self.map_cell(
            self.player.pos.x, self.player.pos.y
        ) == "D":
            self.state = "won"
            self.set_mouse_capture(False)

    # ------------------------------------------------------------
    # Renderizacao 3D
    # ------------------------------------------------------------
    def draw_background(self, horizon):
        self.view.fill((13, 16, 25))

        top = clamp(horizon, 0, VIEW_H)
        for y in range(0, top, 4):
            factor = y / max(1, top)
            color = (
                int(12 + 15 * factor),
                int(17 + 18 * factor),
                int(29 + 25 * factor),
            )
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 4))

        for y in range(top, VIEW_H, 4):
            factor = (y - top) / max(1, VIEW_H - top)
            color = (
                int(42 - 22 * factor),
                int(39 - 20 * factor),
                int(43 - 19 * factor),
            )
            pygame.draw.rect(self.view, color, (0, y, VIEW_W, 4))

        pygame.draw.line(self.view, (54, 48, 55), (0, top), (VIEW_W, top))

    def draw_walls(self, horizon):
        for x in range(VIEW_W):
            camera_x = 2.0 * x / VIEW_W - 1.0
            ray_direction = self.player.direction + self.player.plane * camera_x
            distance, side, cell, wall_position = self.cast_ray(
                self.player.pos, ray_direction
            )
            self.z_buffer[x] = distance

            wall_height = min(VIEW_H * 4, int(VIEW_H / distance))
            draw_start = horizon - wall_height // 2
            draw_end = horizon + wall_height // 2

            base_color = WALL_COLORS.get(cell, (90, 90, 90))
            face_factor = 0.73 if side else 1.0
            fog_factor = clamp(1.08 - distance / 17.0, 0.20, 1.0)
            stripe = int(wall_position * 8.0) % 2
            stripe_factor = 0.88 if stripe else 1.0
            color = shade(base_color, face_factor * fog_factor * stripe_factor)

            pygame.draw.line(
                self.view,
                color,
                (x, max(0, draw_start)),
                (x, min(VIEW_H - 1, draw_end)),
            )

            if draw_start >= 0:
                edge = shade(color, 1.25)
                self.view.set_at((x, draw_start), edge)

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
        width = max(3, width)
        height = max(4, height)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        data = ENEMY_DATA[enemy.kind]
        body = (245, 245, 245) if enemy.hit_flash > 0.0 else data["color"]
        dark = shade(body, 0.55)

        # Chifres e silhueta diferentes deixam os tipos reconheciveis.
        if enemy.kind != "sentinela":
            pygame.draw.polygon(
                surface,
                dark,
                ((width // 5, height // 4), (0, 0), (width // 2, height // 5)),
            )
            pygame.draw.polygon(
                surface,
                dark,
                (
                    (width - width // 5, height // 4),
                    (width - 1, 0),
                    (width // 2, height // 5),
                ),
            )

        pygame.draw.ellipse(
            surface,
            dark,
            (width // 8, height // 7, width * 3 // 4, height * 4 // 5),
        )
        pygame.draw.ellipse(
            surface,
            body,
            (width // 6, height // 8, width * 2 // 3, height * 3 // 5),
        )

        eye_y = height * 3 // 10
        eye_radius = max(1, width // 13)
        pygame.draw.circle(surface, data["eye"], (width * 2 // 5, eye_y), eye_radius)
        pygame.draw.circle(surface, data["eye"], (width * 3 // 5, eye_y), eye_radius)

        mouth_y = height // 2
        pygame.draw.line(
            surface,
            (34, 18, 23),
            (width * 2 // 5, mouth_y),
            (width * 3 // 5, mouth_y),
            max(1, width // 20),
        )

        leg_w = max(1, width // 5)
        pygame.draw.rect(
            surface, dark, (width // 4, height * 3 // 4, leg_w, height // 4)
        )
        pygame.draw.rect(
            surface,
            dark,
            (width * 3 // 4 - leg_w, height * 3 // 4, leg_w, height // 4),
        )
        return surface

    def make_pickup_surface(self, width, height, pickup):
        surface = pygame.Surface((max(3, width), max(3, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        if pickup.kind == "medkit":
            pygame.draw.rect(
                surface,
                (31, 68, 46),
                (width // 10, height // 4, width * 4 // 5, height * 3 // 5),
                border_radius=max(1, width // 10),
            )
            pygame.draw.rect(
                surface,
                (86, 231, 124),
                (width // 8, height // 5, width * 3 // 4, height * 3 // 5),
                max(1, width // 16),
                border_radius=max(1, width // 10),
            )
            cross = (225, 255, 232)
            pygame.draw.rect(
                surface, cross, (width * 2 // 5, height // 3, width // 5, height // 3)
            )
            pygame.draw.rect(
                surface, cross, (width // 3, height * 2 // 5, width // 3, height // 6)
            )
        else:
            gold = (255, 205, 54)
            pygame.draw.circle(
                surface, gold, (width // 3, height // 2), max(2, width // 4), max(1, width // 10)
            )
            pygame.draw.line(
                surface,
                gold,
                (width // 2, height // 2),
                (width - 2, height // 2),
                max(2, height // 7),
            )
            pygame.draw.line(
                surface,
                gold,
                (width * 3 // 4, height // 2),
                (width * 3 // 4, height * 3 // 4),
                max(1, height // 8),
            )
        return surface

    def make_missile_surface(self, width, height):
        surface = pygame.Surface((max(3, width), max(3, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        pygame.draw.circle(
            surface,
            (58, 159, 255, 100),
            (width // 2, height // 2),
            max(1, min(width, height) // 2),
        )
        pygame.draw.circle(
            surface,
            (115, 232, 255),
            (width // 2, height // 2),
            max(1, min(width, height) // 3),
        )
        pygame.draw.circle(
            surface,
            (235, 255, 255),
            (width // 2, height // 2),
            max(1, min(width, height) // 7),
        )
        return surface

    def make_explosion_surface(self, width, height, explosion):
        surface = pygame.Surface((max(4, width), max(4, height)), pygame.SRCALPHA)
        width, height = surface.get_size()
        progress = clamp(explosion.age / explosion.duration, 0.0, 1.0)
        radius = max(2, int(min(width, height) * (0.22 + progress * 0.28)))
        alpha = int(255 * (1.0 - progress))
        pygame.draw.circle(
            surface,
            (255, 73, 26, alpha // 2),
            (width // 2, height // 2),
            max(2, radius),
        )
        pygame.draw.circle(
            surface,
            (255, 191, 48, alpha),
            (width // 2, height // 2),
            max(1, int(radius * 0.68)),
        )
        pygame.draw.circle(
            surface,
            (255, 250, 205, alpha),
            (width // 2, height // 2),
            max(1, int(radius * 0.28)),
        )
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
            self.view.blit(
                surface,
                (start, top),
                (source_x, 0, end - start, height),
            )
        return visible_runs

    def draw_sprites(self, horizon):
        objects = []
        for enemy in self.enemies:
            if enemy.alive:
                objects.append(
                    (enemy.pos.distance_squared_to(self.player.pos), "enemy", enemy)
                )
        for pickup in self.pickups:
            if pickup.active:
                objects.append(
                    (pickup.pos.distance_squared_to(self.player.pos), "pickup", pickup)
                )
        for missile in self.missiles:
            objects.append(
                (missile.pos.distance_squared_to(self.player.pos), "missile", missile)
            )
        for explosion in self.explosions:
            objects.append(
                (
                    explosion.pos.distance_squared_to(self.player.pos),
                    "explosion",
                    explosion,
                )
            )
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
                width = max(3, int(height * 0.62))
                top = int(horizon - height * 0.55)
                left = screen_x - width // 2
                surface = self.make_enemy_surface(width, height, obj)
                visible_runs = self.blit_occluded_sprite(surface, left, top, depth)

                if visible_runs and height >= 12:
                    bar_y = max(1, top - 5)
                    bar_surface = pygame.Surface((width, 4))
                    bar_surface.fill((17, 13, 17))
                    hp_width = int(width * obj.hp / obj.max_hp)
                    hp_color = (
                        (80, 224, 105)
                        if obj.hp > obj.max_hp / 2
                        else (237, 69, 56)
                    )
                    pygame.draw.rect(
                        bar_surface,
                        hp_color,
                        (1, 1, max(0, hp_width - 2), 2),
                    )
                    for run_start, run_end in visible_runs:
                        source_x = run_start - left
                        self.view.blit(
                            bar_surface,
                            (run_start, bar_y),
                            (source_x, 0, run_end - run_start, 4),
                        )

            elif kind == "pickup":
                scale = 0.34 if obj.kind == "medkit" else 0.27
                height = clamp(int(VIEW_H * scale / depth), 3, VIEW_H)
                width = max(3, int(height * (0.9 if obj.kind == "medkit" else 1.2)))
                top = int(horizon + VIEW_H * 0.38 / depth - height + bob * 0.12)
                left = screen_x - width // 2
                surface = self.make_pickup_surface(width, height, obj)
                self.blit_occluded_sprite(surface, left, top, depth)

            elif kind == "missile":
                height = clamp(int(VIEW_H * 0.18 / depth), 3, VIEW_H)
                width = height
                top = horizon - height // 2
                left = screen_x - width // 2
                surface = self.make_missile_surface(width, height)
                self.blit_occluded_sprite(surface, left, top, depth)

            else:
                progress = obj.age / obj.duration
                scale = 0.3 + progress * 1.3
                height = clamp(int(VIEW_H * scale / depth), 5, VIEW_H * 3)
                width = height
                top = horizon - height // 2
                left = screen_x - width // 2
                surface = self.make_explosion_surface(width, height, obj)
                self.blit_occluded_sprite(surface, left, top, depth)

    def draw_weapon(self):
        wave = pygame.Vector2(1.0, 0.0).rotate(self.walk_clock).y
        bob_x = int(wave * 4.0 * self.walk_amount)
        bob_y = int(abs(wave) * 3.0 * self.walk_amount)
        recoil_y = int(self.recoil * 10.0)
        center_x = VIEW_W // 2 + bob_x
        base_y = VIEW_H + bob_y + recoil_y

        # Bracos
        pygame.draw.polygon(
            self.view,
            (96, 63, 48),
            (
                (center_x - 57, VIEW_H),
                (center_x - 29, base_y - 39),
                (center_x - 14, base_y - 25),
                (center_x - 31, VIEW_H),
            ),
        )
        pygame.draw.polygon(
            self.view,
            (96, 63, 48),
            (
                (center_x + 57, VIEW_H),
                (center_x + 29, base_y - 39),
                (center_x + 14, base_y - 25),
                (center_x + 31, VIEW_H),
            ),
        )

        # Arma desenhada inteiramente com formas.
        pygame.draw.polygon(
            self.view,
            (38, 44, 53),
            (
                (center_x - 25, base_y),
                (center_x - 18, base_y - 56),
                (center_x + 18, base_y - 56),
                (center_x + 25, base_y),
            ),
        )
        pygame.draw.rect(
            self.view,
            (88, 99, 112),
            (center_x - 13, base_y - 73, 26, 27),
            border_radius=3,
        )
        pygame.draw.rect(
            self.view,
            (21, 25, 31),
            (center_x - 7, base_y - 79, 14, 12),
            border_radius=2,
        )
        pygame.draw.line(
            self.view,
            (134, 151, 164),
            (center_x - 10, base_y - 68),
            (center_x + 10, base_y - 68),
            2,
        )

        if self.muzzle_timer > 0.0:
            tip_y = base_y - 82
            pygame.draw.polygon(
                self.view,
                (255, 222, 71),
                (
                    (center_x, tip_y - 23),
                    (center_x - 7, tip_y - 5),
                    (center_x - 18, tip_y - 12),
                    (center_x - 7, tip_y + 1),
                    (center_x, tip_y + 7),
                    (center_x + 7, tip_y + 1),
                    (center_x + 18, tip_y - 12),
                    (center_x + 7, tip_y - 5),
                ),
            )
            pygame.draw.circle(self.view, (255, 251, 205), (center_x, tip_y - 5), 5)

    def draw_world(self):
        horizon = VIEW_H // 2 + int(self.pitch / 2.0)
        horizon = clamp(horizon, 24, VIEW_H - 24)
        self.draw_background(horizon)
        self.draw_walls(horizon)
        self.draw_sprites(horizon)
        self.draw_weapon()
        pygame.transform.scale(self.view, (SCREEN_W, SCREEN_H), self.screen)

    # ------------------------------------------------------------
    # HUD e telas
    # ------------------------------------------------------------
    def draw_text(self, text, font, color, position, center=False):
        shadow = font.render(text, True, (0, 0, 0))
        image = font.render(text, True, color)
        rect = image.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
        shadow_rect = rect.move(2, 2)
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(image, rect)
        return rect

    def draw_bar(self, rect, value, maximum, color, background=(32, 26, 31)):
        pygame.draw.rect(self.screen, background, rect, border_radius=5)
        pygame.draw.rect(self.screen, (220, 220, 220), rect, 2, border_radius=5)
        inner = rect.inflate(-6, -6)
        fraction = clamp(value / maximum if maximum else 0.0, 0.0, 1.0)
        fill = pygame.Rect(inner.x, inner.y, int(inner.width * fraction), inner.height)
        if fill.width > 0:
            pygame.draw.rect(self.screen, color, fill, border_radius=3)

    def draw_crosshair(self):
        center = (SCREEN_W // 2, SCREEN_H // 2)
        color = (255, 255, 255) if self.hit_marker_timer <= 0.0 else (255, 75, 61)
        gap = 7
        size = 8
        pygame.draw.line(
            self.screen, color, (center[0] - gap - size, center[1]), (center[0] - gap, center[1]), 2
        )
        pygame.draw.line(
            self.screen, color, (center[0] + gap, center[1]), (center[0] + gap + size, center[1]), 2
        )
        pygame.draw.line(
            self.screen, color, (center[0], center[1] - gap - size), (center[0], center[1] - gap), 2
        )
        pygame.draw.line(
            self.screen, color, (center[0], center[1] + gap), (center[0], center[1] + gap + size), 2
        )
        if self.hit_marker_timer > 0.0:
            for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                pygame.draw.line(
                    self.screen,
                    color,
                    (center[0] + sx * 5, center[1] + sy * 5),
                    (center[0] + sx * 12, center[1] + sy * 12),
                    2,
                )

    def draw_minimap(self):
        cell_size = 7
        map_width = MAP_W * cell_size
        map_height = MAP_H * cell_size
        start_x = SCREEN_W - map_width - 18
        start_y = 68

        panel = pygame.Surface((map_width + 8, map_height + 8), pygame.SRCALPHA)
        panel.fill((4, 6, 10, 205))
        self.screen.blit(panel, (start_x - 4, start_y - 4))

        for y, row in enumerate(MAP_DATA):
            for x, cell in enumerate(row):
                if cell == "." or (cell == "D" and self.exit_unlocked):
                    color = (24, 28, 34)
                elif cell == "D":
                    color = (230, 180, 45)
                else:
                    color = shade(WALL_COLORS.get(cell, (90, 90, 90)), 0.75)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (start_x + x * cell_size, start_y + y * cell_size, cell_size - 1, cell_size - 1),
                )

        for enemy in self.enemies:
            if enemy.alive:
                pygame.draw.circle(
                    self.screen,
                    ENEMY_DATA[enemy.kind]["color"],
                    (
                        start_x + int(enemy.pos.x * cell_size),
                        start_y + int(enemy.pos.y * cell_size),
                    ),
                    2,
                )

        for pickup in self.pickups:
            if pickup.active:
                color = (65, 230, 117) if pickup.kind == "medkit" else (255, 207, 55)
                pygame.draw.circle(
                    self.screen,
                    color,
                    (
                        start_x + int(pickup.pos.x * cell_size),
                        start_y + int(pickup.pos.y * cell_size),
                    ),
                    2,
                )

        player_point = (
            start_x + int(self.player.pos.x * cell_size),
            start_y + int(self.player.pos.y * cell_size),
        )
        pygame.draw.circle(self.screen, (245, 245, 255), player_point, 3)
        direction_end = (
            player_point[0] + int(self.player.direction.x * 8),
            player_point[1] + int(self.player.direction.y * 8),
        )
        pygame.draw.line(self.screen, (245, 245, 255), player_point, direction_end, 2)

    def draw_hud(self):
        panel = pygame.Surface((SCREEN_W, 92), pygame.SRCALPHA)
        panel.fill((8, 9, 13, 205))
        self.screen.blit(panel, (0, SCREEN_H - 92))
        pygame.draw.line(
            self.screen, (91, 106, 122), (0, SCREEN_H - 92), (SCREEN_W, SCREEN_H - 92), 2
        )

        health_color = (62, 215, 101) if self.player.health > 35 else (238, 62, 51)
        self.draw_text("VIDA", self.font_small, (220, 230, 235), (25, SCREEN_H - 76))
        self.draw_bar(
            pygame.Rect(25, SCREEN_H - 52, 245, 27),
            self.player.health,
            self.player.max_health,
            health_color,
        )
        self.draw_text(
            str(self.player.health) + " / " + str(self.player.max_health),
            self.font_small,
            (255, 255, 255),
            (147, SCREEN_H - 39),
            center=True,
        )

        ammo_text = "RECARGA" if self.reload_timer > 0.0 else str(self.ammo) + " / INF"
        ammo_color = (255, 190, 55) if self.ammo <= 3 else (235, 238, 240)
        self.draw_text("MUNICAO", self.font_small, (170, 181, 191), (330, SCREEN_H - 76))
        self.draw_text(ammo_text, self.font_medium, ammo_color, (330, SCREEN_H - 53))

        plasma_ready = self.missile_timer <= 0.0
        plasma_text = "PRONTO" if plasma_ready else str(round(self.missile_timer, 1)) + " s"
        plasma_color = (72, 213, 255) if plasma_ready else (126, 139, 151)
        self.draw_text("PLASMA [DIREITO]", self.font_small, (170, 181, 191), (505, SCREEN_H - 76))
        self.draw_text(plasma_text, self.font_medium, plasma_color, (505, SCREEN_H - 53))

        self.draw_text(
            "INIMIGOS  " + str(self.living_enemies()),
            self.font_small,
            (238, 100, 79),
            (745, SCREEN_H - 75),
        )
        key_text = "CARTAO  SIM" if self.has_key else "CARTAO  NAO"
        key_color = (255, 210, 65) if self.has_key else (130, 135, 142)
        self.draw_text(key_text, self.font_small, key_color, (745, SCREEN_H - 45))

        self.draw_crosshair()

        if self.message_timer > 0.0:
            text_surface = self.font_medium.render(self.message, True, (255, 236, 163))
            padding = 12
            box = text_surface.get_rect(center=(SCREEN_W // 2, 68)).inflate(padding * 2, padding)
            background = pygame.Surface(box.size, pygame.SRCALPHA)
            background.fill((7, 9, 13, 205))
            self.screen.blit(background, box)
            self.screen.blit(text_surface, text_surface.get_rect(center=box.center))

        objective = "OBJETIVO: "
        if self.living_enemies() > 0:
            objective += "elimine os monstros"
        elif not self.has_key:
            objective += "encontre o cartao amarelo"
        elif not self.exit_unlocked:
            objective += "aguarde a porta destrancar"
        else:
            objective += "alcance a porta dourada"
        self.draw_text(objective, self.font_small, (210, 215, 220), (18, 16))

        if self.show_map:
            self.draw_minimap()

    def draw_overlay(self, title, lines, title_color=(235, 238, 240)):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((3, 5, 9, 220))
        self.screen.blit(overlay, (0, 0))

        self.draw_text(
            title,
            self.font_title if len(title) < 14 else self.font_large,
            title_color,
            (SCREEN_W // 2, 132),
            center=True,
        )
        y = 220
        for text, color, size in lines:
            font = self.font_medium if size == "medium" else self.font_small
            self.draw_text(text, font, color, (SCREEN_W // 2, y), center=True)
            y += 44 if size == "medium" else 31

    def render(self):
        self.draw_world()

        if self.state != "intro":
            self.draw_hud()

        if self.damage_flash > 0.0:
            alpha = int(120 * self.damage_flash / 0.22)
            flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash.fill((210, 20, 16, alpha))
            self.screen.blit(flash, (0, 0))

        if self.state == "intro":
            lines = (
                ("FPS PSEUDO-3D FEITO APENAS COM PYGAME", (115, 220, 255), "medium"),
                ("WASD  mover    |    MOUSE  olhar", (230, 232, 235), "small"),
                ("ESQUERDO  atirar    |    DIREITO  missil de plasma", (230, 232, 235), "small"),
                ("R  recarregar    |    M  mapa    |    ESC  pausar", (230, 232, 235), "small"),
                ("Elimine 6 monstros, pegue o cartao e encontre a saida.", (255, 207, 73), "small"),
                ("CLIQUE OU PRESSIONE ENTER PARA COMECAR", (255, 255, 255), "medium"),
            )
            self.draw_overlay("SETOR OMEGA", lines, (238, 74, 63))

        elif self.state == "paused":
            lines = (
                ("O mouse foi liberado.", (205, 211, 216), "medium"),
                ("Clique, ENTER ou ESC para continuar", (255, 219, 93), "small"),
            )
            self.draw_overlay("PAUSADO", lines, (106, 205, 255))

        elif self.state == "dead":
            lines = (
                ("O Setor Omega venceu desta vez.", (225, 225, 230), "medium"),
                ("Eliminacoes: " + str(self.total_kills), (255, 185, 74), "small"),
                ("PRESSIONE ENTER PARA REINICIAR", (255, 255, 255), "medium"),
                ("ESC para sair", (170, 176, 184), "small"),
            )
            self.draw_overlay("VOCE MORREU", lines, (238, 63, 55))

        elif self.state == "won":
            lines = (
                ("Todos os monstros foram eliminados.", (219, 232, 237), "medium"),
                ("Cartao recuperado. Saida alcancada.", (255, 211, 65), "small"),
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
