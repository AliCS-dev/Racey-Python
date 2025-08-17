import pygame
import time
import random
import os

pygame.init()

# =========================
# Config
# =========================
GAME_W, GAME_H = 1000, 1000
FPS = 60
START_LIVES = 3
OBSTACLE_BASE_SPEED = 7
OBSTACLE_MIN_SPEED = 4
OBSTACLE_MAX_SPEED = 18
OBSTACLE_START_COUNT = 3
OBSTACLE_SIZE_RANGE = (70, 140)   # min, max square size
LEVEL_UP_EVERY = 10               # every N dodges, increase difficulty
MAX_OBSTACLES = 12
POWERUP_CHANCE = 0.015            # per-frame chance to spawn a power-up
POWERUP_SIZE = 44
SLOW_EFFECT = 0.5                 # global slowdown multiplier during slow power-up
SLOW_DURATION_MS = 4500           # slowdown lasts this long
EXTRA_LIFE_CHANCE = 0.35          # probability a spawned power-up is extra-life instead of slow
ROAD_SCROLL_SPEED = 8
HIGHSCORE_FILE = "highscore.txt"

# =========================
# Window, Colors, Clock
# =========================
gameDisplay = pygame.display.set_mode((GAME_W, GAME_H))
pygame.display.set_caption("Racey+")
clock = pygame.time.Clock()

black  = (0, 0, 0)
white  = (255, 255, 255)
red    = (220, 40, 40)
green  = (20, 160, 60)
blue   = (50, 90, 220)
grey   = (120, 120, 120)
yellow = (240, 210, 60)
orange = (255, 140, 0)
purple = (150, 60, 200)
bg_grey = (200, 200, 200)

# =========================
# Helpers: Safe asset load
# =========================
def safe_load_image(path, fallback_color=None, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        if fallback_color is None:
            fallback_color = grey
        w, h = size if size else (80, 160)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_color, (0, 0, w, h), border_radius=10)
        pygame.draw.rect(surf, black, (0, 0, w, h), width=3, border_radius=10)
        return surf

def safe_load_sound(path):
    try:
        snd = pygame.mixer.Sound(path)
        return snd
    except Exception:
        return None

def safe_play_music(path, volume=0.35):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

# =========================
# Assets
# =========================
# Car skins: list of (name, surface)
CAR_SKIN_FILES = [
    ("Classic", "Racey.png", (blue,)),
    ("Red",     "Racey_red.png", (red,)),
    ("Blue",    "Racey_blue.png", (blue,)),
    ("Green",   "Racey_green.png", (green,))
]

# Will be scaled later once we know car size
CAR_SIZE = (90, 180)

car_skins = []
for label, fname, fallback in CAR_SKIN_FILES:
    img = safe_load_image(fname, fallback_color=fallback[0], size=CAR_SIZE)
    car_skins.append((label, img))

ROAD_IMG = safe_load_image("road.png", fallback_color=bg_grey, size=(GAME_W, GAME_H))
CRASH_SND = safe_load_sound("crash.wav")
POWERUP_SND = safe_load_sound("powerup.wav")
SELECT_SND = safe_load_sound("select.wav")
safe_play_music("bg_music.mp3", volume=0.28)

# =========================
# Text helpers
# =========================
def text_surface(text, size=32, color=black, bold=False):
    font = pygame.font.SysFont("freesans", size, bold=bold)
    return font.render(text, True, color)

def draw_centered_text(text, size, color, center_xy, bold=False, shadow=True):
    surf = text_surface(text, size=size, color=color, bold=bold)
    rect = surf.get_rect(center=center_xy)
    if shadow:
        sh = text_surface(text, size=size, color=(0,0,0,100))
        sh.set_alpha(120)
        sh_rect = sh.get_rect(center=(center_xy[0]+2, center_xy[1]+2))
        gameDisplay.blit(sh, sh_rect)
    gameDisplay.blit(surf, rect)

# =========================
# Buttons
# =========================
def draw_button(label, rect, base_color, hover_color, text_color=white, action=None):
    mx, my = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mx, my)
    pygame.draw.rect(gameDisplay, hover_color if hovered else base_color, rect, border_radius=16)
    pygame.draw.rect(gameDisplay, (0,0,0,30), rect, width=3, border_radius=16)
    draw_centered_text(label, 26, text_color, rect.center, bold=True)
    clicked = False
    for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
        if event.button == 1 and hovered:
            clicked = True
    if clicked and action:
        if SELECT_SND: SELECT_SND.play()
        action()

# =========================
# Game Entities
# =========================
class Car:
    def __init__(self, img, start_x, start_y, left_key, right_key, name="P1", color_guide=blue):
        self.img = img
        self.rect = img.get_rect(topleft=(start_x, start_y))
        self.speed = 11
        self.x_delta = 0
        self.left_key = left_key
        self.right_key = right_key
        self.lives = START_LIVES
        self.score = 0
        self.name = name
        self.color_guide = color_guide
        self.alive = True

    def handle_event(self, event):
        if not self.alive: return
        if event.type == pygame.KEYDOWN:
            if event.key == self.left_key:
                self.x_delta = -self.speed
            elif event.key == self.right_key:
                self.x_delta = self.speed
        elif event.type == pygame.KEYUP:
            if event.key in (self.left_key, self.right_key):
                self.x_delta = 0

    def update(self):
        if not self.alive: return
        self.rect.x += self.x_delta
        # Keep on screen
        self.rect.x = max(0, min(GAME_W - self.rect.w, self.rect.x))

    def draw(self):
        gameDisplay.blit(self.img, self.rect.topleft)
        # small underline to tell players apart
        pygame.draw.rect(gameDisplay, self.color_guide, (self.rect.x, self.rect.bottom+2, self.rect.w, 6), border_radius=3)

    def hit(self):
        if not self.alive: return
        self.lives -= 1
        if CRASH_SND: CRASH_SND.play()
        if self.lives <= 0:
            self.alive = False

class Obstacle:
    def __init__(self):
        size = random.randint(*OBSTACLE_SIZE_RANGE)
        self.w = size
        self.h = size
        self.x = random.randint(0, GAME_W - self.w)
        self.y = random.randint(-800, -120)
        self.speed = random.uniform(OBSTACLE_MIN_SPEED, OBSTACLE_BASE_SPEED+2)
        self.color = random.choice([black, grey, purple, orange])

    def update(self, speed_scale=1.0):
        self.y += self.speed * speed_scale
        if self.y > GAME_H + 40:
            # Reposition above, count as dodged
            self.reset(top=True)

    def reset(self, top=True):
        size = random.randint(*OBSTACLE_SIZE_RANGE)
        self.w = size
        self.h = size
        self.x = random.randint(0, GAME_W - self.w)
        self.y = random.randint(-1000, -120) if top else -self.h
        self.speed = random.uniform(OBSTACLE_MIN_SPEED, OBSTACLE_MAX_SPEED)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        pygame.draw.rect(gameDisplay, self.color, (self.x, self.y, self.w, self.h), border_radius=10)
        pygame.draw.rect(gameDisplay, (0,0,0), (self.x, self.y, self.w, self.h), width=2, border_radius=10)

class PowerUp:
    def __init__(self):
        self.kind = "life" if random.random() < EXTRA_LIFE_CHANCE else "slow"
        self.size = POWERUP_SIZE
        self.x = random.randint(0, GAME_W - self.size)
        self.y = random.randint(-900, -200)
        self.speed = random.uniform(6, 10)

    def update(self, speed_scale=1.0):
        self.y += self.speed * speed_scale

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self):
        r = self.rect()
        if self.kind == "life":
            pygame.draw.rect(gameDisplay, red, r, border_radius=12)
            draw_centered_text("+1", 20, white, r.center, bold=True, shadow=False)
        else:
            pygame.draw.rect(gameDisplay, green, r, border_radius=12)
            draw_centered_text("SLOW", 18, white, r.center, bold=True, shadow=False)

# =========================
# Highscore
# =========================
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_highscore(score):
    hi = load_highscore()
    if score > hi:
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(score))
        except Exception:
            pass

# =========================
# HUD / Road
# =========================
def draw_hud(players, level, dodged, slow_until_ms):
    # Top bar bg
    pygame.draw.rect(gameDisplay, (245,245,245), (0,0,GAME_W,40))
    # Scores & lives
    x_off = 10
    for p in players:
        name = p.name
        txt = f"{name}  Score:{p.score}  Lives:{p.lives}"
        surf = text_surface(txt, 22, p.color_guide, bold=True)
        gameDisplay.blit(surf, (x_off, 8))
        x_off += surf.get_width() + 20

    # Level & total dodged
    right_txt = text_surface(f"Level:{level}  Dodged:{dodged}", 22, black, bold=True)
    gameDisplay.blit(right_txt, (GAME_W - right_txt.get_width() - 12, 8))

    # Slow effect indicator
    now = pygame.time.get_ticks()
    if slow_until_ms > now:
        remaining = (slow_until_ms - now) / 1000.0
        stxt = text_surface(f"SLOW x{SLOW_EFFECT:.2f} ({remaining:.1f}s)", 20, green, bold=True)
        gameDisplay.blit(stxt, (GAME_W//2 - stxt.get_width()//2, 42))

def draw_scrolling_road(scroll_y):
    # Two tiles of ROAD_IMG, looped
    y1 = scroll_y % GAME_H
    y2 = y1 - GAME_H
    gameDisplay.blit(ROAD_IMG, (0, y2))
    gameDisplay.blit(ROAD_IMG, (0, y1))

# =========================
# Screens
# =========================
def pause_menu():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False

        gameDisplay.fill((30,30,30))
        draw_centered_text("PAUSED", 80, white, (GAME_W//2, GAME_H//2-100), bold=True)
        rect_resume = pygame.Rect(GAME_W//2 - 120, GAME_H//2, 240, 60)
        rect_quit   = pygame.Rect(GAME_W//2 - 120, GAME_H//2+80, 240, 60)

        def _resume(): 
            nonlocal paused
            paused = False
        def _quit():
            pygame.quit(); raise SystemExit

        draw_button("Resume (P)", rect_resume, blue, (80,130,255), action=_resume)
        draw_button("Quit", rect_quit, red, (255,90,90), action=_quit)

        pygame.display.update()
        clock.tick(30)

def game_over_screen(players, total_dodged):
    # Determine winner (two-player) or single
    winner = None
    alive_players = [p for p in players if p.alive]
    if len(players) == 1:
        title = "Game Over!"
    else:
        # If both dead, winner is higher score
        if all(not p.alive for p in players):
            p_sorted = sorted(players, key=lambda p: p.score, reverse=True)
            if p_sorted[0].score != p_sorted[1].score:
                winner = p_sorted[0]
        title = "Match Over!"

    # Update highscore from the best individual score
    best_score = max(p.score for p in players)
    save_highscore(best_score)
    hi = load_highscore()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

        gameDisplay.fill((20,20,20))
        draw_centered_text(title, 80, white, (GAME_W//2, 160), bold=True)
        if winner:
            draw_centered_text(f"Winner: {winner.name} with {winner.score}!", 40, yellow, (GAME_W//2, 240), bold=True)
        else:
            draw_centered_text(f"Total Dodged: {total_dodged}", 36, white, (GAME_W//2, 240))

        # Scores table
        y = 320
        for p in players:
            color = p.color_guide
            draw_centered_text(f"{p.name}: Score {p.score} | Lives {max(p.lives,0)}", 32, color, (GAME_W//2, y), bold=True)
            y += 50

        draw_centered_text(f"High Score: {hi}", 28, white, (GAME_W//2, y+20))
        rect_retry = pygame.Rect(GAME_W//2 - 130, y+80, 260, 60)
        rect_menu  = pygame.Rect(GAME_W//2 - 130, y+160, 260, 60)

        clicked = {"retry": False, "menu": False}
        def _retry():
            clicked["retry"] = True
        def _menu():
            clicked["menu"] = True

        draw_button("Play Again", rect_retry, green, (60,220,120), action=_retry)
        draw_button("Main Menu", rect_menu, blue, (80,130,255), action=_menu)

        pygame.display.update()
        clock.tick(30)

        if clicked["retry"]:
            return "retry"
        if clicked["menu"]:
            return "menu"

def skin_select_screen(player_index):
    idx = 0
    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

        gameDisplay.fill((35, 35, 35))
        draw_centered_text(f"Select Car - Player {player_index}", 60, white, (GAME_W//2, 120), bold=True)

        # Display current skin preview
        name, img = car_skins[idx]
        preview = pygame.transform.smoothscale(img, (int(img.get_width()*1.1), int(img.get_height()*1.1)))
        gameDisplay.blit(preview, (GAME_W//2 - preview.get_width()//2, 220))
        draw_centered_text(name, 34, yellow, (GAME_W//2, 220 + preview.get_height() + 40), bold=True)

        rect_prev = pygame.Rect(GAME_W//2 - 300, 820, 200, 60)
        rect_next = pygame.Rect(GAME_W//2 + 100, 820, 200, 60)
        rect_ok   = pygame.Rect(GAME_W//2 - 100, 900, 200, 60)

        def _prev(): 
            nonlocal idx
            idx = (idx - 1) % len(car_skins)
        def _next(): 
            nonlocal idx
            idx = (idx + 1) % len(car_skins)
        def _ok(): 
            nonlocal selecting
            selecting = False

        draw_button("◀ Prev", rect_prev, blue, (80,130,255), action=_prev)
        draw_button("Next ▶", rect_next, blue, (80,130,255), action=_next)
        draw_button("Select", rect_ok, green, (60,220,120), action=_ok)

        pygame.display.update()
        clock.tick(30)
    return idx

def main_menu():
    hi = load_highscore()
    choice = {"mode": None}
    while choice["mode"] is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

        gameDisplay.blit(ROAD_IMG, (0,0))
        draw_centered_text("FAST AND FURIOUS", 80, white, (GAME_W//2, GAME_H//2 - 160), bold=True)
        draw_centered_text("Racey+", 46, yellow, (GAME_W//2, GAME_H//2 - 100), bold=True)
        draw_centered_text(f"High Score: {hi}", 30, white, (GAME_W//2, GAME_H//2 - 40))

        rect_sp = pygame.Rect(GAME_W//2 - 180, GAME_H//2 + 40, 360, 70)
        rect_tp = pygame.Rect(GAME_W//2 - 180, GAME_H//2 + 130, 360, 70)
        rect_quit = pygame.Rect(GAME_W//2 - 180, GAME_H//2 + 220, 360, 70)

        def _sp(): choice["mode"] = 1
        def _tp(): choice["mode"] = 2
        def _quit(): pygame.quit(); raise SystemExit

        draw_button("Single Player", rect_sp, green, (60,220,120), action=_sp)
        draw_button("Two Player", rect_tp, blue, (80,130,255), action=_tp)
        draw_button("Quit", rect_quit, red, (255,90,90), action=_quit)

        pygame.display.update()
        clock.tick(30)
    return choice["mode"]

# =========================
# Game Loop
# =========================
def game_loop(player_count=1, skin_indices=None):
    if skin_indices is None:
        skin_indices = [0] * player_count

    # Players
    players = []
    lanes = [GAME_W*0.28, GAME_W*0.58] if player_count == 2 else [GAME_W*0.32]
    keys = [(pygame.K_LEFT, pygame.K_RIGHT), (pygame.K_a, pygame.K_d)]
    names = ["P1", "P2"]
    colors = [blue, purple]

    for i in range(player_count):
        _, img = car_skins[skin_indices[i]]
        x = int(lanes[i])
        y = int(GAME_H * 0.6)
        p = Car(img, x, y, keys[i][0], keys[i][1], name=names[i], color_guide=colors[i])
        players.append(p)

    # Obstacles
    obstacles = [Obstacle() for _ in range(OBSTACLE_START_COUNT)]
    total_dodged = 0
    level = 1

    # Power-ups
    powerups = []
    slow_until_ms = 0

    # Road scroll
    scroll_y = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pause_menu()
            for p in players:
                p.handle_event(event)

        # Update speed scale (slow effect)
        speed_scale = SLOW_EFFECT if now < slow_until_ms else 1.0

        # UPDATE
        for p in players:
            p.update()

        # Road scroll
        scroll_y += ROAD_SCROLL_SPEED * speed_scale

        # Obstacles update
        for obs in obstacles:
            prev_y = obs.y
            obs.update(speed_scale=speed_scale)
            # If it went off screen this frame, count a dodge for all living players
            if prev_y <= GAME_H and obs.y > GAME_H:
                alive_any = False
                for p in players:
                    if p.alive:
                        p.score += 1
                        alive_any = True
                if alive_any:
                    total_dodged += 1

        # Spawn power-ups probabilistically
        if random.random() < POWERUP_CHANCE and len(powerups) < 3:
            powerups.append(PowerUp())

        for pu in powerups[:]:
            pu.update(speed_scale=speed_scale)
            if pu.y > GAME_H + 40:
                powerups.remove(pu)

        # COLLISIONS
        for obs in obstacles:
            r_obs = obs.rect()
            for p in players:
                if p.alive and p.rect.colliderect(r_obs):
                    p.hit()
                    # bounce obstacle up to avoid multi-hit same frame
                    obs.reset(top=True)

        for pu in powerups[:]:
            r_pu = pu.rect()
            for p in players:
                if p.alive and p.rect.colliderect(r_pu):
                    if POWERUP_SND: POWERUP_SND.play()
                    if pu.kind == "slow":
                        slow_until_ms = max(slow_until_ms, now + SLOW_DURATION_MS)
                    else:  # extra life
                        p.lives += 1
                    powerups.remove(pu)
                    break

        # LEVEL PROGRESSION
        if total_dodged > 0 and total_dodged % LEVEL_UP_EVERY == 0:
            # Increase difficulty a bit (add obstacle up to max, also slightly speed existing ones)
            if len(obstacles) < MAX_OBSTACLES:
                obstacles.append(Obstacle())
            for obs in obstacles:
                obs.speed = min(OBSTACLE_MAX_SPEED, obs.speed + 0.8)
            level = 1 + total_dodged // LEVEL_UP_EVERY

        # END CONDITIONS
        if all(not p.alive for p in players):
            # End game if all players dead
            next_action = game_over_screen(players, total_dodged)
            if next_action == "retry":
                return "retry"
            else:
                return "menu"

        # RENDER
        draw_scrolling_road(scroll_y)
        for obs in obstacles:
            obs.draw()
        for pu in powerups:
            pu.draw()
        for p in players:
            p.draw()
        draw_hud(players, level, total_dodged, slow_until_ms)

        pygame.display.update()

# =========================
# Main Flow
# =========================
def run():
    while True:
        mode = main_menu()                 # 1 or 2 players
        skin_indices = []
        # Skin selection per player
        for i in range(1, mode+1):
            idx = skin_select_screen(i)
            skin_indices.append(idx)

        result = game_loop(player_count=mode, skin_indices=skin_indices)
        if result == "menu":
            continue
        elif result == "retry":
            # replay same mode with same skins
            result2 = game_loop(player_count=mode, skin_indices=skin_indices)
            if result2 == "menu":
                continue

if __name__ == "__main__":
    try:
        run()
    except SystemExit:
        pass
    finally:
        pygame.quit()
