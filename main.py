import pygame
import random
import json
import os
import math
import sqlite3
import sys
from pathlib import Path
# Flappy Bird - skolni projekt v Pythonu
# Spusteni: pip install -r requirements.txt
#           python main.py

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
GROUND_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Python projekt")
clock = pygame.time.Clock()

# Barvy
SKY = (118, 198, 238)
SKY_LIGHT = (175, 225, 247)
WHITE = (255, 255, 255)
DARK = (35, 52, 76)
GREEN = (72, 190, 95)
GREEN_DARK = (38, 145, 67)
YELLOW = (255, 211, 65)
ORANGE = (255, 145, 40)
GROUND = (222, 190, 124)
GROUND_DARK = (190, 151, 89)

FONT = pygame.font.SysFont("arial", 28, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 56, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20, bold=True)

SAVE_FILE = "best_score.json"


def load_best_score():
    """Nacte nejlepsi skore ze souboru, pokud existuje."""
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return int(data.get("best_score", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_best_score(score):
    """Ulozi nejlepsi skore do JSON souboru."""
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump({"best_score": score}, file)
    except OSError:
        pass
def save_score_to_database(user_id, score):
    """Ulozi vysledek hrace do SQLite databaze."""
    if user_id is None:
        return

    database_path = Path(__file__).parent / "database" / "game.db"

    connection = sqlite3.connect(database_path)

    connection.execute(
        "INSERT INTO scores (user_id, score) VALUES (?, ?)",
        (user_id, score)
    )

    connection.commit()
    connection.close()

def draw_text(surface, text, font, color, center):
    """Vykresli text doprostred zadane pozice."""
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    # Stin pro lepsi citelnost
    shadow = font.render(text, True, (35, 52, 76))
    shadow_rect = shadow.get_rect(center=(center[0] + 2, center[1] + 3))
    surface.blit(shadow, shadow_rect)
    surface.blit(image, rect)


def draw_background(surface, scroll):
    surface.fill(SKY)

    # Jemny svetly pruh v horni casti oblohy
    pygame.draw.rect(surface, SKY_LIGHT, (0, 0, WIDTH, 150))

    # Oblaky
    cloud_positions = [(120, 115), (420, 75), (690, 160), (300, 220)]
    for x, y in cloud_positions:
        cx = (x - scroll * 0.25) % (WIDTH + 180) - 90
        pygame.draw.circle(surface, WHITE, (int(cx), y), 25)
        pygame.draw.circle(surface, WHITE, (int(cx + 28), y - 10), 32)
        pygame.draw.circle(surface, WHITE, (int(cx + 58), y), 24)
        pygame.draw.rect(surface, WHITE, (int(cx - 5), y, 65, 20))

    # Vzdalene kopce
    for i in range(4):
        x = int((i * 260 - scroll * 0.45) % (WIDTH + 260) - 130)
        pygame.draw.ellipse(surface, (113, 190, 151), (x, HEIGHT - GROUND_HEIGHT - 95, 310, 150))


def draw_ground(surface, scroll):
    y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(surface, GROUND, (0, y, WIDTH, GROUND_HEIGHT))
    pygame.draw.rect(surface, (120, 190, 90), (0, y, WIDTH, 12))
    pygame.draw.rect(surface, GROUND_DARK, (0, y + 12, WIDTH, 5))

    # Opakujici se male dlazdice
    tile_width = 48
    offset = int(scroll) % tile_width
    for x in range(-offset, WIDTH + tile_width, tile_width):
        pygame.draw.line(surface, (205, 171, 107), (x, y + 28), (x + 24, y + 48), 2)
        pygame.draw.line(surface, (205, 171, 107), (x + 24, y + 48), (x + 48, y + 28), 2)


class Bird:
    def __init__(self):
        self.x = 190
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 18
        self.rotation = 0

    def flap(self):
        self.velocity = -390

    def update(self, dt):
        self.velocity += 1150 * dt
        self.y += self.velocity * dt
        self.rotation = max(-30, min(75, self.velocity * 0.10))

    def draw(self, surface):
        # Telo ptacka
        body = pygame.Rect(0, 0, 42, 32)
        body.center = (int(self.x), int(self.y))
        pygame.draw.ellipse(surface, ORANGE, body)
        pygame.draw.ellipse(surface, YELLOW, body.inflate(-5, -5))

        # Kridlo
        wing_y = int(self.y + 4 + math.sin(pygame.time.get_ticks() * 0.018) * 3)
        pygame.draw.ellipse(surface, (245, 165, 35), (int(self.x - 15), wing_y, 20, 13))

        # Oko
        pygame.draw.circle(surface, WHITE, (int(self.x + 10), int(self.y - 6)), 8)
        pygame.draw.circle(surface, DARK, (int(self.x + 13), int(self.y - 6)), 4)

        # Zobak
        pygame.draw.polygon(surface, (245, 105, 45), [
            (int(self.x + 18), int(self.y + 1)),
            (int(self.x + 34), int(self.y + 7)),
            (int(self.x + 18), int(self.y + 12))
        ])


class Pipe:
    WIDTH = 76
    GAP = 170
    SPEED = 230

    def __init__(self, x):
        self.x = x
        margin = 95
        self.gap_y = random.randint(margin + self.GAP // 2,
                                    HEIGHT - GROUND_HEIGHT - margin - self.GAP // 2)
        self.scored = False

    def update(self, dt):
        self.x -= self.SPEED * dt

    def rects(self):
        top_height = int(self.gap_y - self.GAP // 2)
        bottom_y = int(self.gap_y + self.GAP // 2)
        ground_y = HEIGHT - GROUND_HEIGHT

        top_rect = pygame.Rect(int(self.x), 0, self.WIDTH, top_height)
        bottom_rect = pygame.Rect(int(self.x), bottom_y, self.WIDTH, ground_y - bottom_y)
        return top_rect, bottom_rect

    def draw_pipe(self, surface, rect, is_top):
        pygame.draw.rect(surface, GREEN_DARK, rect)
        inner = rect.inflate(-12, 0)
        pygame.draw.rect(surface, GREEN, inner)

        # Svetle pruhy dodavaji trubce plasticky vzhled
        pygame.draw.rect(surface, (130, 225, 125),
                        (rect.x + 13, rect.y, 8, rect.height))

        cap_height = 24
        if is_top:
            cap = pygame.Rect(rect.x - 6, rect.bottom - cap_height,
                             self.WIDTH + 12, cap_height)
        else:
            cap = pygame.Rect(rect.x - 6, rect.y,
                             self.WIDTH + 12, cap_height)
        pygame.draw.rect(surface, GREEN_DARK, cap, border_radius=5)
        pygame.draw.rect(surface, GREEN, cap.inflate(-10, -5), border_radius=4)

    def draw(self, surface):
        top, bottom = self.rects()
        self.draw_pipe(surface, top, True)
        self.draw_pipe(surface, bottom, False)


def bird_hits_pipe(bird, pipe):
    # Jednoducha kolize pomoci obdelniku kolem ptacka
    bird_rect = pygame.Rect(int(bird.x - 16), int(bird.y - 14), 32, 28)
    top, bottom = pipe.rects()
    return bird_rect.colliderect(top) or bird_rect.colliderect(bottom)


def reset_game():
    return Bird(), [], 0, 0.0


def main():
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    score_saved = False

    best_score = load_best_score()
    bird, pipes, score, pipe_timer = reset_game()
    state = "menu"  # menu, playing, game_over
    ground_scroll = 0.0
    background_scroll = 0.0

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.035)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if state == "menu" and event.key in (pygame.K_SPACE, pygame.K_UP):
                    bird, pipes, score, pipe_timer = reset_game()
                    state = "playing"
                    bird.flap()

                elif state == "playing" and event.key in (pygame.K_SPACE, pygame.K_UP):
                    bird.flap()

                elif state == "game_over" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    bird, pipes, score, pipe_timer = reset_game()
                    score_saved = False
                    state = "playing"
                    bird.flap()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    bird, pipes, score, pipe_timer = reset_game()
                    state = "playing"
                    bird.flap()
                elif state == "playing":
                    bird.flap()
                elif state == "game_over":
                    bird, pipes, score, pipe_timer = reset_game()
                    score_saved = False
                    state = "playing"
                    bird.flap()

        if state == "playing":
            bird.update(dt)
            pipe_timer += dt

            if pipe_timer >= 1.45:
                pipes.append(Pipe(WIDTH + 30))
                pipe_timer = 0

            for pipe in pipes:
                pipe.update(dt)

                if not pipe.scored and pipe.x + pipe.WIDTH < bird.x:
                    pipe.scored = True
                    score += 1
                    if score > best_score:
                        best_score = score
                        save_best_score(best_score)

                if bird_hits_pipe(bird, pipe):
                    state = "game_over"

            pipes = [pipe for pipe in pipes if pipe.x + pipe.WIDTH > -20]

            if bird.y - bird.radius < 0 or bird.y + bird.radius > HEIGHT - GROUND_HEIGHT:
                state = "game_over"

            ground_scroll += Pipe.SPEED * dt
            background_scroll += 35 * dt
        if state == "game_over" and not score_saved:
            save_score_to_database(user_id, score)
            score_saved = True
        elif state == "menu":
            # Jemne poskakovani ptacka v menu
            bird.y = HEIGHT // 2 + math.sin(pygame.time.get_ticks() * 0.004) * 12
            background_scroll += 15 * dt
            ground_scroll += 35 * dt

        draw_background(screen, background_scroll)

        for pipe in pipes:
            pipe.draw(screen)

        draw_ground(screen, ground_scroll)
        bird.draw(screen)

        if state == "menu":
            draw_text(screen, "FLAPPY BIRD", BIG_FONT, WHITE, (WIDTH // 2, 150))
            draw_text(screen, "Python projekt", SMALL_FONT, WHITE, (WIDTH // 2, 205))
            draw_text(screen, "SPACE / klik = start", FONT, WHITE, (WIDTH // 2, 410))
            draw_text(screen, f"Nejlepsi skore: {best_score}", SMALL_FONT, WHITE, (WIDTH // 2, 455))

        elif state == "playing":
            draw_text(screen, str(score), BIG_FONT, WHITE, (WIDTH // 2, 65))
            draw_text(screen, "SPACE nebo klik = skok", SMALL_FONT, WHITE, (WIDTH // 2, 115))

        elif state == "game_over":
            # Prusvitny panel
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (25, 40, 60, 150), (0, 0, WIDTH, HEIGHT))
            screen.blit(overlay, (0, 0))

            draw_text(screen, "GAME OVER", BIG_FONT, WHITE, (WIDTH // 2, 190))
            draw_text(screen, f"Skore: {score}", FONT, WHITE, (WIDTH // 2, 270))
            draw_text(screen, f"Nejlepsi: {best_score}", FONT, WHITE, (WIDTH // 2, 315))
            draw_text(screen, "SPACE / klik = hrat znovu", SMALL_FONT, WHITE, (WIDTH // 2, 390))
            draw_text(screen, "ESC = konec", SMALL_FONT, WHITE, (WIDTH // 2, 425))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
