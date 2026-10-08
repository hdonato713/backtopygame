"""NUCLEO ZERO - jogo completo em um unico arquivo.

Requer apenas pygame: python -m pip install pygame
Execute com: python nucleo_zero.py
"""

import math
import random
import sys
from dataclasses import dataclass

import pygame


W, H = 1100, 700
FPS = 60
V2 = pygame.Vector2
BG = (8, 11, 20)
WHITE = (235, 242, 255)
CYAN = (64, 225, 255)
BLUE = (65, 115, 255)
RED = (255, 75, 92)
ORANGE = (255, 155, 55)
GREEN = (80, 235, 145)
PURPLE = (175, 95, 255)
YELLOW = (255, 225, 80)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def circle_hit(a, ar, b, br):
    return a.distance_squared_to(b) <= (ar + br) ** 2


def unit(v):
    return v.normalize() if v.length_squared() else V2(1, 0)


def text(surface, value, size, pos, color=WHITE, center=False, bold=False):
    font = pygame.font.SysFont("consolas", size, bold=bold)
    img = font.render(str(value), True, color)
    rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surface.blit(img, rect)
    return rect


def bar(surface, rect, ratio, fg, bg=(30, 37, 55), border=WHITE):
    pygame.draw.rect(surface, bg, rect, border_radius=5)
    fill = rect.copy()
    fill.width = int(rect.width * clamp(ratio, 0, 1))
    if fill.width:
        pygame.draw.rect(surface, fg, fill, border_radius=5)
    pygame.draw.rect(surface, border, rect, 2, border_radius=5)


@dataclass
class Bullet:
    pos: V2
    vel: V2
    damage: float
    radius: int
    friendly: bool
    life: float = 2.0
    pierce: int = 0
    color: tuple = CYAN

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt

    def draw(self, s):
        pygame.draw.circle(s, self.color, self.pos, self.radius)
        pygame.draw.circle(s, WHITE, self.pos, max(1, self.radius // 3))


@dataclass
class Particle:
    pos: V2
    vel: V2
    color: tuple
    life: float
    size: float

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= 0.96
        self.life -= dt

    def draw(self, s):
        if self.life > 0:
            pygame.draw.circle(s, self.color, self.pos, max(1, int(self.size * self.life)))


class Enemy:
    def __init__(self, kind, pos, wave):
        self.kind, self.pos = kind, V2(pos)
        self.flash = 0
        self.shoot_cd = random.random()
        scale = 1 + wave * 0.075
        data = {
            "chaser": (28, 115, 18, RED, 10),
            "tank": (105, 48, 31, PURPLE, 25),
            "shooter": (42, 72, 22, ORANGE, 18),
            "splitter": (52, 88, 24, GREEN, 20),
            "mite": (12, 155, 10, YELLOW, 4),
            "boss": (550, 45, 60, (235, 70, 210), 250),
        }
        hp, speed, radius, color, xp = data[kind]
        self.max_hp = 5 * hp * scale
        self.hp = self.max_hp
        self.speed, self.radius, self.color, self.xp = speed, radius, color, xp
        self.contact = 14 if kind != "boss" else 28
        self.phase = random.random() * 10

    def update(self, game, dt):
        self.flash = max(0, self.flash - dt)
        self.shoot_cd -= dt
        target = game.player.pos
        to_target = target - self.pos
        dist = max(1, to_target.length())
        direction = to_target / dist
        if self.kind == "shooter":
            desired = 280
            motion = direction * (1 if dist > desired + 35 else -1 if dist < desired - 35 else 0)
            motion += V2(-direction.y, direction.x) * math.sin(game.time * 1.8 + self.phase) * .55
            self.pos += unit(motion) * self.speed * dt if motion.length_squared() else V2()
            if self.shoot_cd <= 0 and dist < 540:
                game.enemy_bullets.append(Bullet(self.pos.copy(), direction * 270, 10, 5, False, 4, color=ORANGE))
                self.shoot_cd = 1.35
        elif self.kind == "boss":
            self.pos += direction * self.speed * dt
            if self.shoot_cd <= 0:
                for i in range(12):
                    ang = i * math.tau / 12 + game.time * .35
                    game.enemy_bullets.append(Bullet(self.pos.copy(), V2(math.cos(ang), math.sin(ang))*190, 12, 6, False, 5, color=PURPLE))
                self.shoot_cd = 1.7
        else:
            self.pos += direction * self.speed * dt

        # Tambem ameacam o reator se estiver mais perto dele.
        if self.pos.distance_to(game.core) < self.radius + 48:
            game.core_hp -= self.contact * dt

    def draw(self, s):
        c = WHITE if self.flash > 0 else self.color
        p = (int(self.pos.x), int(self.pos.y))
        if self.kind in ("chaser", "mite"):
            pygame.draw.circle(s, c, p, self.radius)
            pygame.draw.circle(s, BG, p, self.radius // 2)
        elif self.kind == "tank":
            pygame.draw.rect(s, c, (p[0]-self.radius, p[1]-self.radius, self.radius*2, self.radius*2), border_radius=7)
            pygame.draw.rect(s, BG, (p[0]-10, p[1]-10, 20, 20))
        elif self.kind == "shooter":
            pts = [(p[0], p[1]-self.radius), (p[0]+self.radius, p[1]+self.radius), (p[0]-self.radius, p[1]+self.radius)]
            pygame.draw.polygon(s, c, pts)
        elif self.kind == "splitter":
            pygame.draw.polygon(s, c, [(p[0], p[1]-self.radius), (p[0]+self.radius, p[1]), (p[0], p[1]+self.radius), (p[0]-self.radius, p[1])])
        else:
            pygame.draw.circle(s, c, p, self.radius)
            pygame.draw.circle(s, BG, p, self.radius-12, 5)
            for i in range(6):
                d = V2(1, 0).rotate(i*60 + pygame.time.get_ticks()*.04)
                pygame.draw.circle(s, c, self.pos+d*(self.radius+8), 7)
        if self.hp < self.max_hp and self.kind != "mite":
            bar(s, pygame.Rect(p[0]-self.radius, p[1]-self.radius-11, self.radius*2, 5), self.hp/self.max_hp, RED, border=(60,60,75))


class Player:
    def __init__(self):
        self.pos = V2(W/2, H/2+150)
        self.radius = 16
        self.speed = 260
        self.hp = self.max_hp = 100
        self.damage = 18
        self.fire_rate = .25
        self.shot_cd = 0
        self.bullet_speed = 620
        self.multishot = 1
        self.pierce = 0
        self.dash_cd = 0
        self.dash_max = 2.2
        self.dash_time = 0
        self.invuln = 0
        self.regen = 0
        self.aim = V2(1, 0)

    def update(self, game, dt):
        keys = pygame.key.get_pressed()
        move = V2(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])
        if move.length_squared(): move.normalize_ip()
        speed = 760 if self.dash_time > 0 else self.speed
        self.pos += move * speed * dt
        self.pos.x = clamp(self.pos.x, self.radius, W-self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, H-self.radius)
        self.aim = unit(V2(pygame.mouse.get_pos()) - self.pos)
        self.shot_cd -= dt
        self.dash_cd = max(0, self.dash_cd-dt)
        self.dash_time = max(0, self.dash_time-dt)
        self.invuln = max(0, self.invuln-dt)
        self.hp = min(self.max_hp, self.hp + self.regen*dt)
        if (pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]) and self.shot_cd <= 0:
            spread = 9
            for i in range(self.multishot):
                angle = (i-(self.multishot-1)/2)*spread
                d = self.aim.rotate(angle)
                game.bullets.append(Bullet(self.pos+d*22, d*self.bullet_speed, self.damage, 5, True, 1.8, self.pierce, CYAN))
            self.shot_cd = self.fire_rate

    def dash(self, game):
        if self.dash_cd <= 0:
            self.dash_time, self.invuln, self.dash_cd = .16, .32, self.dash_max
            game.burst(self.pos, BLUE, 16, 160)

    def hurt(self, damage, game):
        if self.invuln <= 0:
            self.hp -= damage
            self.invuln = .7
            game.shake = 9
            game.burst(self.pos, RED, 12, 130)

    def draw(self, s):
        c = WHITE if self.invuln > 0 and int(self.invuln*14)%2 else BLUE
        nose = self.pos + self.aim*23
        side = V2(-self.aim.y, self.aim.x)
        pygame.draw.polygon(s, c, [nose, self.pos-self.aim*15+side*13, self.pos-self.aim*15-side*13])
        pygame.draw.circle(s, CYAN, self.pos, 6)


UPGRADES = [
    ("CALIBRE", "+35% de dano", lambda p: setattr(p, "damage", p.damage*1.35)),
    ("CADENCIA", "atira 18% mais rapido", lambda p: setattr(p, "fire_rate", max(.07, p.fire_rate*.82))),
    ("PROPULSOR", "+15% de velocidade", lambda p: setattr(p, "speed", p.speed*1.15)),
    ("BLINDAGEM", "+25 de vida maxima e cura", lambda p: (setattr(p,"max_hp",p.max_hp+25), setattr(p,"hp",min(p.max_hp,p.hp+35)))),
    ("TIRO DUPLO", "+1 projetil por disparo", lambda p: setattr(p, "multishot", min(5,p.multishot+1))),
    ("PERFURANTE", "projeteis atravessam +1 alvo", lambda p: setattr(p, "pierce", p.pierce+1)),
    ("NANORREPARO", "+1.2 de vida por segundo", lambda p: setattr(p, "regen", p.regen+1.2)),
    ("SALTO CURTO", "investida recarrega 20% antes", lambda p: setattr(p, "dash_max", max(.65,p.dash_max*.8))),
]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Nucleo Zero")
        self.clock = pygame.time.Clock()
        self.state = "title"
        self.best = 0
        self.reset()

    def reset(self):
        self.player = Player()
        self.core = V2(W/2, H/2)
        self.core_hp = self.core_max = 180
        self.enemies, self.bullets, self.enemy_bullets, self.particles = [], [], [], []
        self.wave = 0
        self.wave_left = 0
        self.spawn_cd = 0
        self.break_time = 1
        self.score = self.kills = 0
        self.xp, self.level, self.xp_need = 0, 1, 60
        self.options = []
        self.time = self.shake = 0

    def edge_spawn(self):
        side = random.randrange(4)
        if side == 0: return V2(random.randrange(W), -40)
        if side == 1: return V2(W+40, random.randrange(H))
        if side == 2: return V2(random.randrange(W), H+40)
        return V2(-40, random.randrange(H))

    def start_wave(self):
        self.wave += 1
        self.wave_left = 7 + self.wave*3
        if self.wave % 5 == 0:
            self.enemies.append(Enemy("boss", self.edge_spawn(), self.wave))
            self.wave_left = max(3, self.wave)
        self.spawn_cd = .3

    def spawn_enemy(self):
        r = random.random()
        kinds = ["chaser"]
        if self.wave >= 2: kinds += ["shooter"]
        if self.wave >= 3: kinds += ["tank"]
        if self.wave >= 4: kinds += ["splitter"]
        kind = random.choice(kinds) if r > .18 else "chaser"
        self.enemies.append(Enemy(kind, self.edge_spawn(), self.wave))

    def burst(self, pos, color, count=8, speed=100):
        for _ in range(count):
            v = V2(1,0).rotate(random.randrange(360))*random.uniform(speed*.3,speed)
            self.particles.append(Particle(V2(pos), v, color, random.uniform(.3,.8), random.uniform(2,5)))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_need:
            self.xp -= self.xp_need
            self.level += 1
            self.xp_need = int(self.xp_need*1.28)
            self.options = random.sample(UPGRADES, 3)
            self.state = "upgrade"

    def choose(self, idx):
        if 0 <= idx < len(self.options):
            self.options[idx][2](self.player)
            self.state = "playing"

    def kill(self, enemy):
        self.score += int(enemy.xp*10 + self.wave*2)
        self.kills += 1
        self.gain_xp(enemy.xp)
        self.burst(enemy.pos, enemy.color, 14 if enemy.kind=="boss" else 7, 150)
        if enemy.kind == "splitter":
            for _ in range(3):
                self.enemies.append(Enemy("mite", enemy.pos+V2(random.randint(-15,15),random.randint(-15,15)), self.wave))

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.state == "playing": self.state = "paused"
                    elif self.state == "paused": self.state = "playing"
                    elif self.state in ("title","gameover"): return False
                if self.state == "title" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset(); self.state = "playing"
                elif self.state == "gameover" and e.key == pygame.K_r:
                    self.reset(); self.state = "playing"
                elif self.state == "playing" and e.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): self.player.dash(self)
                elif self.state == "upgrade" and e.key in (pygame.K_1,pygame.K_2,pygame.K_3): self.choose(e.key-pygame.K_1)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "title": self.reset(); self.state = "playing"
                elif self.state == "gameover": self.reset(); self.state = "playing"
                elif self.state == "upgrade":
                    for i, rect in enumerate(self.upgrade_rects()):
                        if rect.collidepoint(e.pos): self.choose(i)
        return True

    def update(self, dt):
        if self.state != "playing": return
        self.time += dt
        self.player.update(self, dt)
        if self.wave_left <= 0 and not self.enemies:
            self.break_time -= dt
            if self.break_time <= 0:
                self.start_wave(); self.break_time = 2.3
                self.core_hp = min(self.core_max, self.core_hp+12)
        elif self.wave_left > 0:
            self.spawn_cd -= dt
            if self.spawn_cd <= 0:
                self.spawn_enemy(); self.wave_left -= 1
                self.spawn_cd = max(.12, .72-self.wave*.025)

        for e in self.enemies: e.update(self, dt)
        for b in self.bullets + self.enemy_bullets: b.update(dt)
        for p in self.particles: p.update(dt)

        for b in self.bullets[:]:
            hit = None
            for e in self.enemies:
                if circle_hit(b.pos,b.radius,e.pos,e.radius): hit=e; break
            if hit:
                hit.hp -= b.damage; hit.flash = .08
                self.burst(b.pos, hit.color, 3, 70)
                if hit.hp <= 0 and hit in self.enemies:
                    self.enemies.remove(hit); self.kill(hit)
                if b.pierce > 0: b.pierce -= 1; b.pos += unit(b.vel)*12
                elif b in self.bullets: self.bullets.remove(b)

        for e in self.enemies:
            if circle_hit(e.pos,e.radius,self.player.pos,self.player.radius):
                self.player.hurt(e.contact, self)
                e.pos -= unit(self.player.pos-e.pos)*18
        for b in self.enemy_bullets[:]:
            if circle_hit(b.pos,b.radius,self.player.pos,self.player.radius):
                self.player.hurt(b.damage,self); self.enemy_bullets.remove(b)

        self.bullets[:] = [b for b in self.bullets if b.life>0 and -80<b.pos.x<W+80 and -80<b.pos.y<H+80]
        self.enemy_bullets[:] = [b for b in self.enemy_bullets if b.life>0]
        self.particles[:] = [p for p in self.particles if p.life>0]
        self.shake = max(0,self.shake-25*dt)
        if self.player.hp <= 0 or self.core_hp <= 0:
            self.best = max(self.best,self.score); self.state="gameover"

    def upgrade_rects(self):
        return [pygame.Rect(145+i*285, 250, 245, 220) for i in range(3)]

    def draw_grid(self, s):
        s.fill(BG)
        off = int(self.time*18)%40
        for x in range(-40+off,W,40): pygame.draw.line(s,(16,22,36),(x,0),(x,H))
        for y in range(-40+off,H,40): pygame.draw.line(s,(16,22,36),(0,y),(W,y))

    def draw_world(self):
        world = pygame.Surface((W,H))
        self.draw_grid(world)
        pulse = 4+int(math.sin(self.time*4)*3)
        pygame.draw.circle(world,(25,45,72),self.core,52+pulse)
        pygame.draw.circle(world,CYAN,self.core,43,4)
        pygame.draw.circle(world,(22,85,105),self.core,28)
        for p in self.particles: p.draw(world)
        for b in self.bullets+self.enemy_bullets: b.draw(world)
        for e in self.enemies: e.draw(world)
        self.player.draw(world)
        offset = V2(random.uniform(-self.shake,self.shake),random.uniform(-self.shake,self.shake)) if self.shake else V2()
        self.screen.blit(world, offset)
        bar(self.screen,pygame.Rect(22,22,260,18),self.player.hp/self.player.max_hp,BLUE)
        text(self.screen,f"NAVE {max(0,int(self.player.hp))}/{int(self.player.max_hp)}",15,(28,23))
        bar(self.screen,pygame.Rect(22,50,260,14),self.core_hp/self.core_max,CYAN)
        text(self.screen,f"REATOR {max(0,int(self.core_hp))}/{self.core_max}",13,(28,50))
        bar(self.screen,pygame.Rect(22,77,260,10),self.xp/self.xp_need,PURPLE,border=(80,80,100))
        text(self.screen,f"NIVEL {self.level}",15,(22,94),PURPLE)
        text(self.screen,f"ONDA {self.wave}",25,(W-150,20),YELLOW,bold=True)
        text(self.screen,f"PONTOS {self.score}",17,(W-180,52))
        dash_ratio = 1-self.player.dash_cd/self.player.dash_max
        bar(self.screen,pygame.Rect(W-180,82,150,10),dash_ratio,BLUE,border=(80,80,100))
        text(self.screen,"SHIFT: INVESTIDA",12,(W-180,97),(150,170,210))
        if self.wave_left<=0 and not self.enemies:
            text(self.screen,"PROXIMA ONDA...",22,(W/2,70),YELLOW,True,True)

    def draw_overlay(self):
        if self.state == "title":
            self.draw_grid(self.screen)
            text(self.screen,"NUCLEO ZERO",70,(W/2,155),CYAN,True,True)
            text(self.screen,"Defenda o reator. Evolua. Sobreviva.",23,(W/2,235),WHITE,True)
            tips=["WASD  mover","MOUSE ou ESPACO  atirar","SHIFT  investida","ESC  pausar"]
            for i,t in enumerate(tips): text(self.screen,t,19,(W/2,330+i*38),(170,195,225),True)
            text(self.screen,"ENTER ou clique para comecar",21,(W/2,540),YELLOW,True,True)
        elif self.state == "paused":
            veil=pygame.Surface((W,H),pygame.SRCALPHA); veil.fill((0,0,0,175)); self.screen.blit(veil,(0,0))
            text(self.screen,"PAUSADO",55,(W/2,H/2-25),WHITE,True,True)
            text(self.screen,"ESC para continuar",19,(W/2,H/2+45),CYAN,True)
        elif self.state == "upgrade":
            veil=pygame.Surface((W,H),pygame.SRCALPHA); veil.fill((4,6,14,220)); self.screen.blit(veil,(0,0))
            text(self.screen,"ESCOLHA UMA MELHORIA",34,(W/2,145),YELLOW,True,True)
            for i,(opt,rect) in enumerate(zip(self.options,self.upgrade_rects())):
                hover=rect.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(self.screen,(36,46,70) if hover else (23,29,47),rect,border_radius=12)
                pygame.draw.rect(self.screen,CYAN if hover else (80,95,125),rect,3,border_radius=12)
                text(self.screen,str(i+1),30,(rect.centerx,rect.y+38),CYAN,True,True)
                text(self.screen,opt[0],22,(rect.centerx,rect.y+95),WHITE,True,True)
                text(self.screen,opt[1],15,(rect.centerx,rect.y+145),(175,195,225),True)
            text(self.screen,"Clique ou pressione 1, 2 ou 3",16,(W/2,515),(155,175,205),True)
        elif self.state == "gameover":
            veil=pygame.Surface((W,H),pygame.SRCALPHA); veil.fill((0,0,0,205)); self.screen.blit(veil,(0,0))
            title="REATOR DESTRUIDO" if self.core_hp<=0 else "NAVE DESTRUIDA"
            text(self.screen,title,50,(W/2,190),RED,True,True)
            text(self.screen,f"Pontuacao: {self.score}   |   Onda: {self.wave}   |   Abates: {self.kills}",22,(W/2,285),WHITE,True)
            text(self.screen,f"Recorde desta sessao: {self.best}",18,(W/2,330),YELLOW,True)
            text(self.screen,"R ou clique para tentar novamente",20,(W/2,450),CYAN,True,True)
            text(self.screen,"ESC para sair",15,(W/2,490),(150,160,180),True)

    def run(self):
        while True:
            dt=min(self.clock.tick(FPS)/1000, .035)
            if not self.handle_events(): break
            self.update(dt)
            if self.state != "title": self.draw_world()
            self.draw_overlay()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    try:
        Game().run()
    except pygame.error as exc:
        print("Erro ao iniciar o Pygame:", exc)
        print("Verifique se ha um ambiente grafico disponivel.")
        sys.exit(1)
