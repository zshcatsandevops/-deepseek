import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario 2D World")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

# Game states
INTRO = 0
GAME = 1
BOSS = 2
GAME_OVER = 3
VICTORY = 4

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 36)
normal_font = pygame.font.SysFont('Arial', 24)

# Player class
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - 150
        self.vel_y = 0
        self.jump_power = 15
        self.gravity = 0.8
        self.is_jumping = False
        self.speed = 5
        self.direction = 1  # 1 for right, -1 for left
        self.lives = 3
        self.score = 0
        self.invincible = 0
        self.color = RED
        
    def jump(self):
        if not self.is_jumping:
            self.vel_y = -self.jump_power
            self.is_jumping = True
    
    def update(self, platforms):
        # Apply gravity
        self.vel_y += self.gravity
        self.y += self.vel_y
        
        # Check platform collisions
        self.is_jumping = True
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.is_jumping = False
        
        # Keep player on screen
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - 150
            self.lives -= 1
            self.invincible = 60
            
        # Update invincibility
        if self.invincible > 0:
            self.invincible -= 1
    
    def draw(self, screen):
        # Draw Mario
        if self.invincible > 0 and self.invincible % 10 < 5:
            # Flash when invincible
            return
            
        # Body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Hat
        pygame.draw.rect(screen, RED, (self.x-5, self.y, self.width+10, 15))
        # Face
        pygame.draw.circle(screen, (255, 200, 150), (self.x+self.width//2, self.y+25), 12)
        # Eyes
        pygame.draw.circle(screen, BLACK, (self.x+self.width//2+5*self.direction, self.y+22), 4)
        # Mustache
        pygame.draw.rect(screen, BLACK, (self.x+self.width//2-15, self.y+30, 30, 5))

# Platform class
class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type="goomba"):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 2
        self.direction = 1
        self.type = enemy_type
        self.is_alive = True
        
    def update(self, platforms):
        if not self.is_alive:
            return
            
        self.x += self.speed * self.direction
        
        # Change direction at edges
        on_platform = False
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                on_platform = True
                # Check if at edge of platform
                if (self.x <= platform.x and self.direction == -1) or \
                   (self.x + self.width >= platform.x + platform.width and self.direction == 1):
                    self.direction *= -1
                break
                
        if not on_platform:
            self.direction *= -1
    
    def draw(self, screen):
        if not self.is_alive:
            return
            
        if self.type == "goomba":
            # Draw Goomba
            pygame.draw.ellipse(screen, (139, 69, 19), (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, (100, 40, 0), (self.x, self.y, self.width, self.height//2))
            # Eyes
            pygame.draw.circle(screen, BLACK, (self.x+10, self.y+15), 5)
            pygame.draw.circle(screen, BLACK, (self.x+30, self.y+15), 5)
        elif self.type == "koopa":
            # Draw Koopa Troopa
            pygame.draw.ellipse(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, (0, 100, 0), (self.x, self.y, self.width, self.height//2))
            # Shell pattern
            pygame.draw.ellipse(screen, (0, 80, 0), (self.x+5, self.y+5, self.width-10, self.height-10))

# Boss class
class Boss:
    def __init__(self, boss_type, world):
        self.type = boss_type
        self.world = world
        self.width = 80
        self.height = 80
        self.x = SCREEN_WIDTH - 150
        self.y = SCREEN_HEIGHT - 200
        self.health = 5
        self.speed = 3
        self.direction = -1
        self.attack_timer = 0
        self.projectiles = []
        
    def update(self, player):
        # Move side to side
        self.x += self.speed * self.direction
        
        # Change direction at edges
        if self.x <= 50 or self.x >= SCREEN_WIDTH - 150:
            self.direction *= -1
            
        # Attack periodically
        self.attack_timer += 1
        if self.attack_timer >= 60:  # Attack every 2 seconds
            self.attack()
            self.attack_timer = 0
            
        # Update projectiles
        for proj in self.projectiles[:]:
            proj[0] += proj[2] * 5  # Move projectile
            if proj[0] < 0 or proj[0] > SCREEN_WIDTH:
                self.projectiles.remove(proj)
                
            # Check collision with player
            if (player.x < proj[0] < player.x + player.width and
                player.y < proj[1] < player.y + player.height and
                player.invincible == 0):
                player.lives -= 1
                player.invincible = 60
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
    
    def attack(self):
        # Create projectiles based on boss type
        if self.type == "kamek":
            # Kamek shoots magic projectiles
            self.projectiles.append([self.x, self.y + self.height//2, -1])
        elif self.type == "king_boo":
            # King Boo shoots ghostly projectiles
            angle = math.atan2(player.y - self.y, player.x - self.x)
            self.projectiles.append([self.x, self.y + self.height//2, math.cos(angle), math.sin(angle)])
        elif self.type == "wiggler":
            # Wiggler charges
            self.speed = 8
            pygame.time.set_timer(pygame.USEREVENT, 1000)  # Reset speed after 1 second
        elif self.type == "bowser_jr":
            # Bowser Jr. shoots fireballs
            self.projectiles.append([self.x, self.y + self.height//2, -1])
            self.projectiles.append([self.x, self.y + self.height//2, -0.7])
            self.projectiles.append([self.x, self.y + self.height//2, -1.3])
        elif self.type == "dry_bowser":
            # Dry Bowser shoots bone projectiles
            for i in range(5):
                angle = (i - 2) * 0.3
                self.projectiles.append([self.x, self.y + self.height//2, math.cos(angle), math.sin(angle)])
    
    def draw(self, screen):
        if self.type == "kamek":
            # Draw Kamek
            pygame.draw.rect(screen, (200, 0, 200), (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, (150, 0, 150), (self.x+self.width//2, self.y-10), 20)
            # Eyes
            pygame.draw.circle(screen, YELLOW, (self.x+20, self.y+20), 10)
            pygame.draw.circle(screen, YELLOW, (self.x+60, self.y+20), 10)
            pygame.draw.circle(screen, BLACK, (self.x+20, self.y+20), 5)
            pygame.draw.circle(screen, BLACK, (self.x+60, self.y+20), 5)
            # Nose
            pygame.draw.polygon(screen, (255, 150, 150), [(self.x+40, self.y+30), (self.x+30, self.y+50), (self.x+50, self.y+50)])
        elif self.type == "king_boo":
            # Draw King Boo
            pygame.draw.circle(screen, WHITE, (self.x+self.width//2, self.y+self.height//2), self.width//2)
            pygame.draw.circle(screen, (200, 200, 200), (self.x+self.width//2, self.y+self.height//2), self.width//2-5)
            # Crown
            pygame.draw.polygon(screen, YELLOW, [(self.x+20, self.y+10), (self.x+40, self.y-20), (self.x+60, self.y+10)])
            # Eyes
            pygame.draw.ellipse(screen, BLACK, (self.x+20, self.y+20, 20, 30))
            pygame.draw.ellipse(screen, BLACK, (self.x+40, self.y+20, 20, 30))
            # Mouth
            pygame.draw.arc(screen, BLACK, (self.x+20, self.y+40, 40, 20), 0, math.pi, 3)
        
        # Draw projectiles
        for proj in self.projectiles:
            if self.type == "kamek" or self.type == "bowser_jr":
                pygame.draw.circle(screen, RED, (int(proj[0]), int(proj[1])), 8)
            elif self.type == "king_boo":
                pygame.draw.circle(screen, (200, 200, 255), (int(proj[0]), int(proj[1])), 8)
            elif self.type == "dry_bowser":
                pygame.draw.ellipse(screen, WHITE, (int(proj[0]), int(proj[1]), 15, 8))

# Coin class
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 0.1) % (2 * math.pi)
        
    def draw(self, screen):
        if not self.collected:
            # Animated coin
            offset = math.sin(self.animation) * 3
            pygame.draw.circle(screen, YELLOW, (int(self.x + self.width//2), int(self.y + self.height//2 + offset)), self.width//2)
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x + self.width//2), int(self.y + self.height//2 + offset)), self.width//2 - 3)

# Flagpole class (end of level)
class Flagpole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 200
        self.flag_raised = False
        
    def draw(self, screen):
        # Pole
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
        # Flag
        if not self.flag_raised:
            pygame.draw.polygon(screen, RED, [(self.x+self.width, self.y+30), 
                                            (self.x+self.width+40, self.y+30), 
                                            (self.x+self.width+40, self.y+60), 
                                            (self.x+self.width, self.y+60)])

# Create game objects
player = Player()
platforms = []
enemies = []
coins = []
boss = None
flagpole = None

# Game state
game_state = INTRO
current_world = 1
current_level = 1
intro_timer = 0
boss_defeated = False
level_complete = False
level_timer = 0

# Boss types for each world
boss_types = ["kamek", "king_boo", "wiggler", "bowser_jr", "dry_bowser"]
boss_names = ["Kamek", "King Boo", "Wiggler", "Bowser Jr.", "Dry Bowser"]

# Create levels
def create_level(world, level):
    global platforms, enemies, coins, flagpole, boss
    
    platforms = []
    enemies = []
    coins = []
    boss = None
    flagpole = None
    
    # Ground platform
    platforms.append(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    
    # Level design based on world and level
    if level < 4:  # Regular levels
        # Add platforms
        for i in range(5):
            platforms.append(Platform(150 + i*120, SCREEN_HEIGHT - 150, 80, 20))
            
        # Add enemies
        for i in range(3):
            enemies.append(Enemy(200 + i*200, SCREEN_HEIGHT - 190, random.choice(["goomba", "koopa"])))
            
        # Add coins
        for i in range(10):
            coins.append(Coin(100 + i*70, SCREEN_HEIGHT - 200))
            
        # Add flagpole at the end
        flagpole = Flagpole(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        
    else:  # Boss level
        # Create boss
        boss = Boss(boss_types[world-1], world)
        
        # Add platforms for boss battle
        platforms.append(Platform(0, SCREEN_HEIGHT - 150, 200, 20))
        platforms.append(Platform(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150, 200, 20))
        platforms.append(Platform(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 250, 200, 20))

# Initial level creation
create_level(current_world, current_level)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == INTRO:
                    game_state = GAME
                elif game_state == GAME and not level_complete:
                    player.jump()
                elif game_state == BOSS and not boss_defeated:
                    player.jump()
                elif game_state == GAME_OVER or game_state == VICTORY:
                    # Reset game
                    player = Player()
                    current_world = 1
                    current_level = 1
                    create_level(current_world, current_level)
                    game_state = GAME
            elif event.key == pygame.K_r and (game_state == GAME_OVER or game_state == VICTORY):
                # Reset game
                player = Player()
                current_world = 1
                current_level = 1
                create_level(current_world, current_level)
                game_state = GAME
    
    # Fill background
    if current_world == 1:
        screen.fill((135, 206, 235))  # Sky blue for world 1
    elif current_world == 2:
        screen.fill((100, 100, 200))  # Evening sky for world 2
    elif current_world == 3:
        screen.fill((150, 75, 0))     # Autumn for world 3
    elif current_world == 4:
        screen.fill((70, 70, 120))    # Night for world 4
    else:
        screen.fill((30, 30, 60))     # Space for world 5
    
    # Game state handling
    if game_state == INTRO:
        # Draw intro screens
        intro_timer += 1
        
        if intro_timer < 180:  # SamSoft presents (3 seconds)
            # SamSoft logo (similar to HAL Labs style)
            pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200))
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 - 90, 280, 180))
            
            text = title_font.render("SamSoft", True, BLUE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 70))
            
            text = subtitle_font.render("presents", True, BLUE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
            
        elif intro_timer < 360:  # Nintendo co-presents (3 seconds)
            # Nintendo logo
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200))
            
            text = title_font.render("Nintendo", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 70))
            
            text = subtitle_font.render("co-presents", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
            
        else:  # Fade to game
            game_state = GAME
            
    elif game_state == GAME:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed
            player.direction = -1
        if keys[pygame.K_RIGHT]:
            player.x += player.speed
            player.direction = 1
            
        # Update game objects
        player.update(platforms)
        
        for enemy in enemies:
            enemy.update(platforms)
            
        for coin in coins:
            coin.update()
            
        # Check coin collection
        for coin in coins:
            if (not coin.collected and 
                player.x < coin.x + coin.width and 
                player.x + player.width > coin.x and
                player.y < coin.y + coin.height and 
                player.y + player.height > coin.y):
                coin.collected = True
                player.score += 100
                
        # Check enemy collisions
        for enemy in enemies[:]:
            if (enemy.is_alive and
                player.x < enemy.x + enemy.width and 
                player.x + player.width > enemy.x and
                player.y < enemy.y + enemy.height and 
                player.y + player.height > enemy.y):
                
                # Player jumps on enemy
                if player.vel_y > 0 and player.y + player.height < enemy.y + enemy.height/2:
                    enemy.is_alive = False
                    player.vel_y = -10  # Bounce
                    player.score += 200
                # Player gets hit
                elif player.invincible == 0:
                    player.lives -= 1
                    player.invincible = 60
                    
        # Check if player reached flagpole
        if flagpole and not level_complete:
            if (player.x + player.width > flagpole.x and 
                player.x < flagpole.x + flagpole.width):
                level_complete = True
                level_timer = 0
                flagpole.flag_raised = True
                
        # Handle level completion
        if level_complete:
            level_timer += 1
            if level_timer > 120:  # 2 seconds delay
                level_complete = False
                if current_level < 4:
                    current_level += 1
                else:
                    current_level = 1
                    current_world += 1
                    if current_world > 5:
                        game_state = VICTORY
                    else:
                        game_state = BOSS
                create_level(current_world, current_level)
                
        # Check for game over
        if player.lives <= 0:
            game_state = GAME_OVER
            
        # Draw game objects
        for platform in platforms:
            platform.draw(screen)
            
        for coin in coins:
            coin.draw(screen)
            
        for enemy in enemies:
            enemy.draw(screen)
            
        if flagpole:
            flagpole.draw(screen)
            
        player.draw(screen)
        
        # Draw UI
        lives_text = normal_font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (20, 20))
        
        score_text = normal_font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (20, 50))
        
        world_text = normal_font.render(f"World {current_world}-{current_level}", True, WHITE)
        screen.blit(world_text, (SCREEN_WIDTH - world_text.get_width() - 20, 20))
        
    elif game_state == BOSS:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed
            player.direction = -1
        if keys[pygame.K_RIGHT]:
            player.x += player.speed
            player.direction = 1
            
        # Update game objects
        player.update(platforms)
        boss.update(player)
        
        # Check if player hits boss
        if (boss and 
            player.x < boss.x + boss.width and 
            player.x + player.width > boss.x and
            player.y < boss.y + boss.height and 
            player.y + player.height > boss.y and
            player.invincible == 0):
            
            # Player jumps on boss
            if player.vel_y > 0 and player.y + player.height < boss.y + boss.height/2:
                boss.health -= 1
                player.vel_y = -10  # Bounce
                if boss.health <= 0:
                    boss_defeated = True
                    player.score += 1000
            # Player gets hit
            else:
                player.lives -= 1
                player.invincible = 60
                
        # Handle boss defeat
        if boss_defeated:
            level_timer += 1
            if level_timer > 120:  # 2 seconds delay
                boss_defeated = False
                game_state = GAME
                
        # Check for game over
        if player.lives <= 0:
            game_state = GAME_OVER
            
        # Draw game objects
        for platform in platforms:
            platform.draw(screen)
            
        boss.draw(screen)
        player.draw(screen)
        
        # Draw UI
        lives_text = normal_font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (20, 20))
        
        score_text = normal_font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (20, 50))
        
        boss_text = normal_font.render(f"Boss: {boss_names[current_world-1]} - HP: {boss.health}", True, WHITE)
        screen.blit(boss_text, (SCREEN_WIDTH//2 - boss_text.get_width()//2, 20))
        
        world_text = normal_font.render(f"World {current_world} Boss", True, WHITE)
        screen.blit(world_text, (SCREEN_WIDTH - world_text.get_width() - 20, 20))
        
    elif game_state == GAME_OVER:
        # Draw game over screen
        text = title_font.render("GAME OVER", True, RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        text = normal_font.render("Press SPACE to play again or R to restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
    elif game_state == VICTORY:
        # Draw victory screen
        text = title_font.render("VICTORY!", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        text = normal_font.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        text = normal_font.render("Press SPACE to play again or R to restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 70))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
