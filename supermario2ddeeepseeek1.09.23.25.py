import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# === UPDATED CONSTANTS ===
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Colors
SKY_BLUE = (107, 140, 255)
GREEN = (76, 175, 80)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

class Fireball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.radius = 5
        self.direction = direction
        self.speed = 7
        self.bounce_count = 0
        self.max_bounces = 3

    def update(self, platforms):
        self.x += self.speed * self.direction
        
        # Apply gravity
        self.y += 3
        
        # Check for platform collisions
        fireball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                                   self.radius * 2, self.radius * 2)
        for platform in platforms:
            if platform.broken:
                continue
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if fireball_rect.colliderect(plat_rect):
                # Bounce off platform
                self.y = platform.y - self.radius
                self.bounce_count += 1
                if self.bounce_count >= self.max_bounces:
                    return False
        
        # Check if out of bounds
        if self.x < -20 or self.x > SCREEN_WIDTH + 20 or self.y > SCREEN_HEIGHT + 20:
            return False
            
        return True

    def check_collision(self, enemy):
        fireball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                                   self.radius * 2, self.radius * 2)
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
        return fireball_rect.colliderect(enemy_rect)

    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 2)

class Platform:
    def __init__(self, x, y, width, height, breakable=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.breakable = breakable
        self.broken = False
        self.bounce_timer = 0

    def draw(self, screen):
        if self.broken:
            return
            
        if self.breakable:
            color = (150, 75, 0)  # Brown for breakable blocks
        else:
            color = GREEN
            
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)

class FlagPole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = 150
        self.flag_raised = False

    def draw(self, screen):
        # Draw pole
        pygame.draw.rect(screen, GRAY, (self.x, self.y, 5, self.height))
        
        # Draw flag
        if not self.flag_raised:
            flag_color = RED
            pygame.draw.polygon(screen, flag_color, [
                (self.x + 5, self.y + 10),
                (self.x + 30, self.y + 20),
                (self.x + 5, self.y + 30)
            ])

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.vel_x = 1
        self.vel_y = 0
        self.enemy_type = enemy_type
        self.alive = True
        self.bounce_timer = 0
        self.direction = -1  # Start moving left

    def update(self, platforms):
        if not self.alive and self.bounce_timer > 0:
            self.bounce_timer -= 1
            self.y -= 2  # Bounce up when defeated
            return True
            
        if not self.alive:
            return False
            
        # Move horizontally
        self.x += self.vel_x * self.direction
        
        # Apply gravity
        self.vel_y += 0.4
        self.y += self.vel_y
        
        # Check platform collisions
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            if platform.broken:
                continue
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if enemy_rect.colliderect(plat_rect):
                if self.vel_y > 0:  # Falling
                    self.y = platform.y - self.height
                    self.vel_y = 0
                elif self.vel_y < 0:  # Jumping up
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                    
                # Change direction when hitting platform edges
                if self.x + self.width > platform.x + platform.width or self.x < platform.x:
                    self.direction *= -1
        
        # Change direction at screen edges
        if self.x <= 0 or self.x + self.width >= SCREEN_WIDTH:
            self.direction *= -1
            
        return True

    def draw(self, screen):
        if not self.alive and self.bounce_timer <= 0:
            return
            
        if self.enemy_type == "goomba":
            # Draw goomba body
            body_color = (150, 75, 0)  # Brown
            pygame.draw.rect(screen, body_color, (self.x, self.y, self.width, self.height))
            
            # Draw face
            eye_color = WHITE
            pygame.draw.circle(screen, eye_color, (self.x + 4, self.y + 6), 2)
            pygame.draw.circle(screen, eye_color, (self.x + 12, self.y + 6), 2)
            
            if not self.alive:
                # Squished goomba
                pygame.draw.rect(screen, body_color, (self.x, self.y + 10, self.width, 4))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 6
        self.collected = False
        self.bounce_offset = 0
        self.bounce_direction = 1

    def update(self):
        if not self.collected:
            # Bouncing animation
            self.bounce_offset += 0.1 * self.bounce_direction
            if abs(self.bounce_offset) > 3:
                self.bounce_direction *= -1

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, YELLOW, 
                              (int(self.x), int(self.y + self.bounce_offset)), 
                              self.radius)
            pygame.draw.circle(screen, (200, 200, 0), 
                              (int(self.x), int(self.y + self.bounce_offset)), 
                              self.radius - 2)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.power_type = power_type
        self.collected = False
        self.bounce_offset = 0
        self.bounce_direction = 1

    def update(self):
        if not self.collected:
            # Bouncing animation
            self.bounce_offset += 0.05 * self.bounce_direction
            if abs(self.bounce_offset) > 2:
                self.bounce_direction *= -1

    def draw(self, screen):
        if not self.collected:
            y_pos = self.y + self.bounce_offset
            
            if self.power_type == "mushroom":
                # Red mushroom
                pygame.draw.rect(screen, RED, (self.x, y_pos, self.width, self.height))
                pygame.draw.rect(screen, WHITE, (self.x, y_pos, self.width, 4))
            elif self.power_type == "fire_flower":
                # Fire flower
                pygame.draw.rect(screen, (255, 100, 100), (self.x, y_pos, self.width, self.height))
                for i in range(4):
                    angle = i * math.pi / 2
                    px = self.x + self.width/2 + math.cos(angle) * 4
                    py = y_pos + self.height/2 + math.sin(angle) * 4
                    pygame.draw.circle(screen, YELLOW, (int(px), int(py)), 3)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 32
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -8.5
        self.gravity = 0.4
        self.speed = 2
        self.run_speed = 3.5
        self.on_ground = False
        self.direction = 1
        self.color = RED
        self.power_level = 0
        self.spin_jumping = False
        self.spin_jump_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.crouching = False
        self.carrying_item = None
        self.fireballs = []
        self.fireball_cooldown = 0

    def update(self, platforms, enemies, coins, powerups):
        # Apply gravity
        self.vel_y += self.gravity

        # Store original position for collision resolution
        orig_x, orig_y = self.x, self.y

        # Move horizontally first
        self.x += self.vel_x
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            if platform.broken:
                continue
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if player_rect.colliderect(plat_rect):
                if self.vel_x > 0:  # Moving right
                    self.x = platform.x - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.x + platform.width
                self.vel_x = 0  # Stop horizontal movement when hitting a wall

        # Then move vertically
        self.y += self.vel_y
        self.on_ground = False

        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            if platform.broken:
                continue
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if player_rect.colliderect(plat_rect):
                if self.vel_y > 0:  # Falling
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    self.y = platform.y + platform.height
                    self.vel_y = 0

        # Update cooldowns & fireballs
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        if self.spin_jump_timer > 0:
            self.spin_jump_timer -= 1
            if self.spin_jump_timer == 0:
                self.spin_jumping = False

        for fireball in self.fireballs[:]:
            if not fireball.update(platforms):
                self.fireballs.remove(fireball)
            else:
                for enemy in enemies:
                    if enemy.alive and fireball.check_collision(enemy):
                        enemy.alive = False
                        enemy.bounce_timer = 20
                        self.score += 100
                        self.fireballs.remove(fireball)
                        break

        # Screen boundaries
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.y > SCREEN_HEIGHT:
            self.respawn()

        # Invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def spin_jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power * 1.2
            self.spin_jumping = True
            self.spin_jump_timer = 30
            self.on_ground = False

    def shoot_fireball(self):
        if self.power_level == 2 and self.fireball_cooldown == 0:
            self.fireballs.append(Fireball(
                self.x + self.width // 2,
                self.y + self.height // 2,
                self.direction
            ))
            self.fireball_cooldown = 20

    def take_damage(self):
        if self.invulnerable:
            return
        if self.power_level > 0:
            self.power_level -= 1
            self.invulnerable = True
            self.invulnerable_timer = 120
            self.vel_x = -5 * self.direction
            self.vel_y = -5
            if self.power_level == 0:
                self.height = 32
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over()
            else:
                self.respawn()

    def respawn(self):
        self.x = 100
        self.y = 200
        self.vel_x = 0
        self.vel_y = 0
        self.invulnerable = True
        self.invulnerable_timer = 120
        self.carrying_item = None

    def game_over(self):
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.power_level = 0
        self.height = 32
        self.respawn()

    def draw(self, screen):
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            return

        body_color = RED if self.power_level == 0 else (BLUE if self.power_level == 2 else RED)
        body_height = self.height // 2 if self.crouching else self.height
        body_y = self.y + self.height // 2 if self.crouching else self.y
        pygame.draw.rect(screen, body_color, (self.x, body_y, self.width, body_height))

        face_y = body_y + 8 if self.crouching else self.y + 8
        pygame.draw.circle(screen, (255, 200, 150),
                          (self.x + self.width // 2 + self.direction * 3, face_y), 6)

        hat_y = body_y if self.crouching else self.y
        pygame.draw.rect(screen, RED, (self.x - 3, hat_y, self.width + 6, 6))

        if self.spin_jumping:
            for i in range(3):
                angle = pygame.time.get_ticks() / 100 + i * 2
                radius = 12
                star_x = self.x + self.width // 2 + math.cos(angle) * radius
                star_y = self.y + self.height // 2 + math.sin(angle) * radius
                pygame.draw.circle(screen, YELLOW, (int(star_x), int(star_y)), 3)

        for fireball in self.fireballs:
            fireball.draw(screen)

class Level:
    def __init__(self, level_num, world_num):
        self.level_num = level_num
        self.world_num = world_num
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.powerups = []
        self.flag_pole = None
        self.setup_level()

    def setup_level(self):
        # Ground platform
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))

        if self.level_num == 1:
            self.platforms.append(Platform(100, 300, 120, 15))
            self.platforms.append(Platform(300, 240, 100, 15))
            self.platforms.append(Platform(180, 180, 80, 15))
            self.platforms.append(Platform(250, 150, 40, 15, breakable=True))
            self.enemies.append(Enemy(220, 270, "goomba"))
            self.enemies.append(Enemy(350, 210, "goomba"))
            for i in range(5):
                self.coins.append(Coin(120 + i * 20, 270))
            for i in range(3):
                self.coins.append(Coin(320 + i * 20, 210))
            self.powerups.append(PowerUp(200, 270, "mushroom"))
            self.flag_pole = FlagPole(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)

        elif self.level_num == 2:
            self.platforms.append(Platform(120, 320, 80, 15))
            self.platforms.append(Platform(250, 260, 80, 15))
            self.platforms.append(Platform(380, 200, 80, 15))
            self.platforms.append(Platform(500, 260, 80, 15))
            self.platforms.append(Platform(280, 140, 40, 15, breakable=True))
            self.platforms.append(Platform(320, 140, 40, 15, breakable=True))
            self.enemies.append(Enemy(160, 290, "goomba"))
            self.enemies.append(Enemy(280, 230, "goomba"))
            self.enemies.append(Enemy(410, 170, "goomba"))
            for i in range(4):
                self.coins.append(Coin(135 + i * 15, 290))
            for i in range(3):
                self.coins.append(Coin(265 + i * 15, 230))
            for i in range(5):
                self.coins.append(Coin(395 + i * 15, 170))
            self.powerups.append(PowerUp(280, 230, "mushroom"))
            self.powerups.append(PowerUp(410, 120, "fire_flower"))
            self.flag_pole = FlagPole(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)

        elif self.level_num == 3:
            for i in range(7):
                x = 80 + i * 70
                y = 300 - i * 25
                self.platforms.append(Platform(x, y, 50, 15))
            self.platforms.append(Platform(200, 160, 80, 15))
            self.platforms.append(Platform(360, 130, 80, 15))
            for i in range(3):
                self.platforms.append(Platform(240 + i * 25, 100, 25, 25, breakable=True))
            self.enemies.append(Enemy(110, 270, "goomba"))
            self.enemies.append(Enemy(180, 240, "goomba"))
            self.enemies.append(Enemy(260, 170, "goomba"))
            self.enemies.append(Enemy(400, 200, "goomba"))
            for i in range(3):
                self.coins.append(Coin(95 + i * 12, 270))
            for i in range(3):
                self.coins.append(Coin(165 + i * 12, 240))
            for i in range(4):
                self.coins.append(Coin(220 + i * 15, 130))
            for i in range(4):
                self.coins.append(Coin(375 + i * 15, 100))
            self.powerups.append(PowerUp(240, 130, "mushroom"))
            self.powerups.append(PowerUp(380, 160, "fire_flower"))
            self.flag_pole = FlagPole(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)

        else:
            # Default level
            for i in range(5):
                x = 100 + i * 100
                y = 300 - i * 30
                self.platforms.append(Platform(x, y, 70, 15))
                if i % 2 == 0:
                    self.platforms.append(Platform(x + 20, y - 40, 30, 15, breakable=True))
            for i in range(3):
                self.enemies.append(Enemy(130 + i * 140, 270, "goomba"))
            for i in range(10):
                self.coins.append(Coin(110 + i * 50, 240))
            self.powerups.append(PowerUp(300, 240, "mushroom"))
            self.powerups.append(PowerUp(450, 180, "fire_flower"))
            self.flag_pole = FlagPole(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 180)

class Game:
    def __init__(self):
        global game_instance
        game_instance = self
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros")
        self.clock = pygame.time.Clock()
        
        self.player = Player(100, 200)
        self.current_level = 1
        self.level = Level(self.current_level, 1)
        self.font = pygame.font.SysFont(None, 24)
        
        self.running = True
        self.game_state = "playing"  # playing, game_over, level_complete

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_LSHIFT:
                    self.player.spin_jump()
                elif event.key == pygame.K_z:
                    self.player.shoot_fireball()
                elif event.key == pygame.K_r:
                    self.reset_level()

    def reset_level(self):
        self.level = Level(self.current_level, 1)
        self.player.respawn()

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.player.vel_x = -self.player.speed
            self.player.direction = -1
        elif keys[pygame.K_RIGHT]:
            self.player.vel_x = self.player.speed
            self.player.direction = 1
        else:
            self.player.vel_x = 0
            
        # Crouching
        self.player.crouching = keys[pygame.K_DOWN]
        
        # Update player
        self.player.update(self.level.platforms, self.level.enemies, 
                          self.level.coins, self.level.powerups)
        
        # Update enemies
        for enemy in self.level.enemies[:]:
            if not enemy.update(self.level.platforms):
                self.level.enemies.remove(enemy)
        
        # Update coins
        for coin in self.level.coins:
            coin.update()
            
        # Update powerups
        for powerup in self.level.powerups:
            powerup.update()
            
        # Check coin collisions
        player_rect = pygame.Rect(self.player.x, self.player.y, 
                                 self.player.width, self.player.height)
        for coin in self.level.coins[:]:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x - coin.radius, coin.y - coin.radius,
                                       coin.radius * 2, coin.radius * 2)
                if player_rect.colliderect(coin_rect):
                    coin.collected = True
                    self.player.coins += 1
                    self.player.score += 100
                    self.level.coins.remove(coin)
        
        # Check powerup collisions
        for powerup in self.level.powerups[:]:
            if not powerup.collected:
                powerup_rect = pygame.Rect(powerup.x, powerup.y, 
                                          powerup.width, powerup.height)
                if player_rect.colliderect(powerup_rect):
                    powerup.collected = True
                    if powerup.power_type == "mushroom":
                        if self.player.power_level < 2:
                            self.player.power_level += 1
                    elif powerup.power_type == "fire_flower":
                        self.player.power_level = 2
                    self.player.score += 1000
                    self.level.powerups.remove(powerup)
        
        # Check enemy collisions
        for enemy in self.level.enemies:
            if enemy.alive:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if player_rect.colliderect(enemy_rect):
                    # Check if player is jumping on enemy
                    if self.player.vel_y > 0 and player_rect.bottom < enemy_rect.top + 10:
                        enemy.alive = False
                        enemy.bounce_timer = 20
                        self.player.vel_y = -5  # Bounce off enemy
                        self.player.score += 100
                    else:
                        self.player.take_damage()

    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        # Draw level elements
        for platform in self.level.platforms:
            platform.draw(self.screen)
            
        for coin in self.level.coins:
            coin.draw(self.screen)
            
        for powerup in self.level.powerups:
            powerup.draw(self.screen)
            
        for enemy in self.level.enemies:
            enemy.draw(self.screen)
            
        if self.level.flag_pole:
            self.level.flag_pole.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        coins_text = self.font.render(f"Coins: {self.player.coins}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(coins_text, (10, 40))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 40))
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Global game instance
game_instance = None

# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
