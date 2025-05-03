import pygame
import time
import random
pygame.font.init()

# Window dimensions and setup
WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Hurdles in Space")

# Assets and scaling
BG = pygame.transform.scale(pygame.image.load("bg.jpeg"), (WIDTH, HEIGHT))

# Player and game settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 80
PLAYER_VEL = 5

STAR_WIDTH = 25
STAR_HEIGHT = 50
STAR_VEL = 3

POWER_UP_WIDTH = 30
POWER_UP_HEIGHT = 30
POWER_UP_DURATION = 5  # Seconds

FONT = pygame.font.SysFont("comicsans", 30)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_COLORS = [RED, BLUE, GREEN, YELLOW]  # Available colors

# Draw menu
def draw_menu(selected_color_index):
    WIN.fill(WHITE)
    title_text = FONT.render("Dodge Hurdles in Space", 1, (0, 0, 0))
    play_text = FONT.render("Press ENTER to Start", 1, (0, 0, 0))
    customize_text = FONT.render("Customize Your Appearance:", 1, (0, 0, 0))

    WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 50))
    WIN.blit(play_text, (WIDTH/2 - play_text.get_width()/2, HEIGHT - 100))
    WIN.blit(customize_text, (WIDTH/2 - customize_text.get_width()/2, 150))

    # Display color options
    for i, color in enumerate(PLAYER_COLORS):
        rect = pygame.Rect(WIDTH/2 - 150 + i * 80, 200, 60, 80)
        pygame.draw.rect(WIN, color, rect)
        if i == selected_color_index:
            pygame.draw.rect(WIN, (0, 0, 0), rect, 3)  # Highlight selected

    pygame.display.update()

# Draw game elements
def draw(player, elapsed_time, stars, power_ups, level, score, shield_active):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, WHITE)
    level_text = FONT.render(f"Level: {level}", 1, WHITE)
    score_text = FONT.render(f"Score: {score}", 1, WHITE)
    shield_text = FONT.render("Shield: ON" if shield_active else "Shield: OFF", 1, GREEN if shield_active else RED)

    WIN.blit(time_text, (10, 10))
    WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
    WIN.blit(score_text, (10, 40))
    WIN.blit(shield_text, (10, 70))

    pygame.draw.rect(WIN, player['color'], player['rect'])

    for star in stars:
        pygame.draw.rect(WIN, WHITE, star)

    for power_up in power_ups:
        pygame.draw.ellipse(WIN, GREEN, power_up)

    pygame.display.update()

# Main menu
def menu():
    selected_color_index = 0
    run = True
    while run:
        draw_menu(selected_color_index)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and selected_color_index > 0:
                    selected_color_index -= 1
                if event.key == pygame.K_RIGHT and selected_color_index < len(PLAYER_COLORS) - 1:
                    selected_color_index += 1
                if event.key == pygame.K_RETURN:
                    run = False
    return PLAYER_COLORS[selected_color_index]

# Main game
def main(player_color):
    run = True
    clock = pygame.time.Clock()

    # Player and game state
    player = {'rect': pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT), 'color': player_color}
    start_time = time.time()
    elapsed_time = 0
    score = 0

    # Level and difficulty parameters
    level = 1
    star_velocity = STAR_VEL
    star_add_increment = 2000
    star_count = 0

    # Stars and power-ups
    stars = []
    power_ups = []
    power_up_timer = 0

    # Shield state
    shield_active = False

    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # Level progression
        if int(elapsed_time) % 10 == 0 and elapsed_time > 0:
            level = int(elapsed_time) // 10 + 1
            star_velocity = STAR_VEL + (level - 1)
            star_add_increment = max(500, 2000 - (level * 100))

        # Add stars
        if star_count > star_add_increment:
            for _ in range(3 + level // 2):  # Increase stars as levels progress
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)
            star_count = 0

        # Add power-ups occasionally
        if random.randint(1, 300) == 1:  # Random chance to spawn a power-up
            power_up_x = random.randint(0, WIDTH - POWER_UP_WIDTH)
            power_up = pygame.Rect(power_up_x, -POWER_UP_HEIGHT, POWER_UP_WIDTH, POWER_UP_HEIGHT)
            power_ups.append(power_up)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player['rect'].x - PLAYER_VEL >= 0:
            player['rect'].x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player['rect'].x + PLAYER_VEL + player['rect'].width <= WIDTH:
            player['rect'].x += PLAYER_VEL

        # Update stars
        for star in stars[:]:
            star.y += star_velocity
            if star.y > HEIGHT:
                stars.remove(star)
                score += 1  # Increase score for dodged stars
            elif star.y + star.height >= player['rect'].y and star.colliderect(player['rect']):
                if shield_active:
                    stars.remove(star)  # Destroy star if shield is active
                else:
                    lost_text = FONT.render("You Lost!", 1, WHITE)
                    WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
                    pygame.display.update()
                    pygame.time.delay(4000)
                    run = False
                    break

        # Update power-ups
        for power_up in power_ups[:]:
            power_up.y += 3
            if power_up.y > HEIGHT:
                power_ups.remove(power_up)
            elif power_up.colliderect(player['rect']):
                power_ups.remove(power_up)
                shield_active = True
                power_up_timer = time.time()

        # Deactivate shield after duration
        if shield_active and time.time() - power_up_timer > POWER_UP_DURATION:
            shield_active = False

        # Draw all elements
        draw(player, elapsed_time, stars, power_ups, level, score, shield_active)

    pygame.quit()

if __name__ == "__main__":
    selected_color = menu()
    main(selected_color)
