import pgzrun
from random import randint
from pygame import Rect

# Config.
WIDTH, HEIGHT = 1200, 700
PLAYER_START = (100, HEIGHT - 100)
GOAL_POS = (WIDTH - 100, 50)
PLATFORM_START = Rect(0, HEIGHT - 40, 200, 20)

GRAVITY = 0.8
JUMP_FORCE = -15
PLAYER_SPEED = 4

# Animações do herói.
HERO_ANIM = {
    "walk_left": [f"characters/hero/walk_left/hero_walk_left_frame_{i}"
                  for i in range(8)],
    "walk_right": [f"characters/hero/walk_right/hero_walk_right_frame_{i}"
                   for i in range(8)],
    "idle": [f"characters/hero/idle/hero_idle_frame_{i}"
             for i in range(4)]
}

# Animações do inimigo.
ENEMY_ANIM = {
    "left": [f"characters/enemy/walk_left/enemy_walk_left_frame_{i}"
             for i in range(4)],
    "right": [f"characters/enemy/walk_right/enemy_walk_right_frame_{i}"
              for i in range(4)],
    "idle": [f"characters/enemy/idle/enemy_idle_frame"]
}

# Player


class Player(Actor):
    def __init__(self, game_ref):
        super().__init__(HERO_ANIM["idle"][0], PLAYER_START)
        self.game = game_ref
        self.velocity = [0, 0]
        self.anim_frame = 0
        self.anim_timer = 0
        self.on_ground = False

    def update(self, platforms, enemies):
        self.move()          # Input
        self.physics(platforms)  # Gravidade e colisão
        self.animate()       # Animação
        self.check_enemies(enemies)  # Verifica inimigos

    def move(self):
        self.velocity[0] = 0
        if keyboard.right:
            self.velocity[0] = PLAYER_SPEED
        if keyboard.left:
            self.velocity[0] = -PLAYER_SPEED
        if (keyboard.up or keyboard.space) and self.on_ground:
            self.jump()

    def jump(self):
        self.velocity[1] = JUMP_FORCE
        self.on_ground = False
        if self.game.sound_on:
            sounds.jump.play()

    def physics(self, platforms):
        self.velocity[1] += GRAVITY
        self.x += self.velocity[0]
        for p in platforms:
            if self.colliderect(p):
                if self.velocity[0] > 0:
                    self.right = p.left
                elif self.velocity[0] < 0:
                    self.left = p.right
        self.y += self.velocity[1]
        self.on_ground = False
        for p in platforms:
            if self.colliderect(p):
                if self.velocity[1] > 0:
                    self.bottom = p.top
                    self.on_ground = True
                else:
                    self.top = p.bottom
                self.velocity[1] = 0

    def animate(self):
        if self.velocity[0] == 0:
            self.idle_anim()
        else:
            self.walk_anim()

    def idle_anim(self):
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(HERO_ANIM["idle"])
            self.image = HERO_ANIM["idle"][self.anim_frame]

    def walk_anim(self):
        self.anim_timer += 1
        if self.anim_timer >= 6:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 8
            direction = "walk_left" if self.velocity[0] < 0 else "walk_right"
            self.image = HERO_ANIM[direction][self.anim_frame]

    def check_enemies(self, enemies):
        for enemy in enemies:
            if self.colliderect(enemy):
                if self.game.sound_on:
                    sounds.hurt.play()
                self.reset_position()

    def reset_position(self):
        self.pos = PLAYER_START

# Inimigo


class Enemy(Actor):
    def __init__(self, pos, patrol_range, speed=1.5):
        super().__init__(ENEMY_ANIM["idle"][0], (pos[0], pos[1] - 30))
        self.patrol_left = pos[0] - patrol_range
        self.patrol_right = pos[0] + patrol_range
        self.speed = speed
        self.direction = 1
        self.anim_frame = 0
        self.anim_timer = 0

    def update(self):
        self.move()
        self.animate()

    def move(self):
        self.x += self.speed * self.direction
        if self.x > self.patrol_right or self.x < self.patrol_left:
            self.direction *= -1

    def animate(self):
        self.anim_timer += 1
        if self.direction != 0 and self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
            d = "left" if self.direction < 0 else "right"
            self.image = ENEMY_ANIM[d][self.anim_frame]

# Jogo


class Game:
    def __init__(self):
        self.state = "menu"   # menu, playing, victory, game_over
        self.sound_on = True
        self.level = 0
        self.player = Player(self)
        self.enemies = []
        self.platforms = []
        self.goal = None
        self.init_levels()
        self.reset_level()
        self.buttons = [
            {"text": "Começar o jogo", "pos": (WIDTH//2, 200),
             "action": self.start_game},
            {"text": f"Musica e Sons: {'ON' if self.sound_on else 'OFF'}",
             "pos": (WIDTH//2, 260), "action": self.toggle_sound},
            {"text": "Sair", "pos": (WIDTH//2, 320),
             "action": quit}
        ]

    def init_levels(self):
        self.levels = [
            {  # level 1
                "platforms": [
                    Rect(300, 600, 80, 20),
                    Rect(400, 500, 80, 20),
                    Rect(300, 400, 80, 20),
                    Rect(400, 300, 80, 20),
                    Rect(600, 350, 80, 20),
                    Rect(700, 230, 80, 20),
                    Rect(850, 150, 120, 20),
                ],
                "enemies": [
                ]
            },
            {
                "platforms": [
                    Rect(300, 600, 80, 20),
                    Rect(400, 500, 200, 20),
                    Rect(600, 370, 80, 20),
                    Rect(700, 250, 80, 20),
                    Rect(850, 150, 120, 20)
                ],
                "enemies": [
                    ((500, 500), 100),
                    ((900, 150), 60)
                ]
            },
            {
                "platforms": [
                    Rect(300, 600, 80, 20),
                    Rect(400, 500, 190, 20),
                    Rect(300, 400, 80, 20),
                    Rect(450, 300, 100, 20),
                    Rect(600, 350, 80, 20),
                    Rect(700, 230, 80, 20),
                    Rect(850, 150, 200, 20),
                ],
                "enemies": [
                    ((500, 500), 90),
                    ((500, 300), 40),
                    ((950, 150), 100, 3)
                ]
            },
            {
                "platforms": [
                    Rect(300, 660, 10, 20),
                    Rect(400, 560, 10, 20),
                    Rect(550, 660, 10, 20),
                    Rect(650, 560, 10, 20),
                    Rect(600, 450, 10, 20),
                    Rect(700, 380, 10, 20),
                    Rect(600, 280, 10, 20),
                    Rect(720, 180, 10, 20),
                    Rect(920, 280, 10, 20),
                    Rect(1020, 180, 10, 20),
                ],
                "enemies": [
                ]
            },
        ]

    def reset_level(self):
        lvl = self.levels[self.level]
        self.platforms = [PLATFORM_START] + lvl["platforms"]
        self.goal = Rect(*GOAL_POS, 30, 30)
        self.enemies = [Enemy(*e) for e in lvl["enemies"]]
        self.player.reset_position()

    def start_game(self):
        self.state = "playing"
        self.level = 0
        self.reset_level()
        if self.sound_on:
            music.play("bg_music")

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        music.set_volume(0.25 if self.sound_on else 0)
        self.buttons[1]["text"] = f"Musica e Sons: {'ON' if self.sound_on else 'OFF'}"

    def draw_menu(self, victory=None):
        screen.fill((30, 144, 255))  # blue
        screen.blit("bg", (0, 0))
        screen.draw.text("Platform Adventure",
                         center=(WIDTH//2, 100),
                         fontsize=72, color=(255, 51, 0))
        if victory is not None:
            txt = "Voce Venceu! :D" if victory else "Voce Perdeu! :("
            col = (0, 255, 0) if victory else (255, 50, 0)
            screen.draw.text(txt,
                             center=(WIDTH//2, 450),
                             fontsize=72, color=col)
        for btn in self.buttons:
            screen.draw.filled_rect(
                Rect(btn["pos"][0]-150,
                     btn["pos"][1]-20, 300, 40),
                (255, 51, 0))
            screen.draw.text(btn["text"],
                             center=btn["pos"],
                             color=(255, 255, 255),
                             fontsize=32)

    def draw_game(self):
        music.set_volume(0.5)
        screen.fill((135, 206, 235))  # sky
        screen.blit("bg", (0, 0))
        screen.draw.text(f"Level {self.level+1}",
                         center=(WIDTH//2, 30),
                         fontsize=48, color=(255, 51, 0))
        for p in self.platforms:
            screen.draw.filled_rect(p, (139, 69, 19))
        screen.draw.filled_rect(self.goal, (255, 215, 0))
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()
        if self.player.colliderect(self.goal):
            self.level += 1
            if self.level < len(self.levels):
                self.reset_level()
            else:
                self.state = "victory"
                if self.sound_on:
                    music.set_volume(0)
                    sounds.win.play()

    def update_game(self):
        if self.state == "playing":
            self.player.update(self.platforms, self.enemies)
            for enemy in self.enemies:
                enemy.update()
            if self.player.y > HEIGHT:
                self.state = "game_over"
                if self.sound_on:
                    music.set_volume(0)
                    sounds.lose.play()

    def click_menu(self, pos):
        for btn in self.buttons:
            if Rect(btn["pos"][0]-150,
                    btn["pos"][1]-20, 300, 40).collidepoint(pos):
                btn["action"]()


game = Game()


def update():
    game.update_game()


def draw():
    if game.state in ["menu", "victory", "game_over"]:
        game.draw_menu(
            game.state == "victory" if game.state != "menu" else None)
    else:
        game.draw_game()


def on_mouse_down(pos):
    if game.state in ["menu", "victory", "game_over"]:
        game.click_menu(pos)


def on_key_down(key):
    if keyboard.escape:
        game.state = "menu"
    if keyboard.space and game.state != "playing":
        game.start_game()


pgzrun.go()
