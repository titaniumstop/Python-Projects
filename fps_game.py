import pygame
import math
import random
import asyncio
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, x, y, character='soldier'):
        self.x = x
        self.y = y
        self.angle = 0  # Viewing angle in radians
        self.character = character
        
        # Character stats
        self.stats = {
            'soldier': {'health': 100, 'speed': 3, 'color': BLUE, 'damage': 25},
            'commando': {'health': 75, 'speed': 4, 'color': GREEN, 'damage': 20},
            'tank': {'health': 150, 'speed': 2, 'color': (128, 0, 128), 'damage': 30},
            'assassin': {'health': 80, 'speed': 3.5, 'color': (255, 140, 0), 'damage': 35}
        }
        
        self.health = self.stats[self.character]['health']
        self.max_health = self.health
        self.ammo = 30
        self.speed = self.stats[self.character]['speed']
        self.width = 20
        self.height = 20
        self.color = self.stats[self.character]['color']
        
    def move(self, keys, map_data):
        old_x, old_y = self.x, self.y
        
        # Calculate movement based on angle
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.x -= math.cos(self.angle) * self.speed
            self.y -= math.sin(self.angle) * self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x += math.cos(self.angle - math.pi/2) * self.speed
            self.y += math.sin(self.angle - math.pi/2) * self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += math.cos(self.angle + math.pi/2) * self.speed
            self.y += math.sin(self.angle + math.pi/2) * self.speed
            
        # Check for wall collision
        grid_x = int(self.x / 64)
        grid_y = int(self.y / 64)
        if 0 <= grid_x < len(map_data[0]) and 0 <= grid_y < len(map_data):
            if map_data[grid_y][grid_x] == 1:
                self.x, self.y = old_x, old_y
            else:
                # Keep player in bounds
                self.x = max(self.width, min(SCREEN_WIDTH - self.width, self.x))
                self.y = max(self.height, min(SCREEN_HEIGHT - self.height, self.y))
                
    def rotate(self, mouse_movement):
        # Improved sensitivity for better aiming
        sensitivity = 0.006
        self.angle += mouse_movement * sensitivity
        
    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return True
        return False

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = 50
        self.speed = 2.0  # Increased from 1.5
        self.width = 20
        self.height = 20
        self.cooldown = 60
        self.cooldown_timer = 0
        self.dist = 0  # Cache distance to avoid recalculation
        
    def update(self, player):
        # Simple AI: move towards player (optimized)
        dx = player.x - self.x
        dy = player.y - self.y
        self.dist = math.sqrt(dx*dx + dy*dy) if dx*dx + dy*dy > 0 else 1
        
        # Use cached distance
        if self.dist > 0:
            self.x += (dx / self.dist) * self.speed
            self.y += (dy / self.dist) * self.speed
            self.angle = math.atan2(dy, dx)
            
        # Update cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            
    def can_shoot(self):
        return self.cooldown_timer == 0
        
    def shoot(self):
        if self.can_shoot():
            self.cooldown_timer = self.cooldown
            return True
        return False

class Bullet:
    def __init__(self, x, y, angle, owner, damage=25):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.owner = owner  # 'player' or 'enemy'
        self.damage = damage if owner == 'player' else 10
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class FPSGame:
    def __init__(self, selected_character='soldier'):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FPS Game - WASD to move, Mouse to aim, Left Click to shoot")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create simple map (1 = wall, 0 = open space)
        self.map_data = self.create_map()
        
        # Create player with selected character
        self.player = Player(200, 200, selected_character)
        
        # Create enemies
        self.enemies = [
            Enemy(600, 300),
            Enemy(700, 500),
            Enemy(800, 200),
        ]
        
        # Bullets
        self.bullets = []
        
        # Score
        self.score = 0
        
        # Enemy spawning
        self.max_enemies = 10  # Max enemies on screen at once
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 120  # Spawn every 2 seconds (at 60 FPS)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Mouse control
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
    def create_map(self):
        # Create a simple maze-like map
        map_data = [[0 for _ in range(16)] for _ in range(12)]
        
        # Add walls around borders
        for i in range(16):
            map_data[0][i] = 1
            map_data[11][i] = 1
        for i in range(12):
            map_data[i][0] = 1
            map_data[i][15] = 1
            
        # Add some internal walls
        for i in range(5, 10):
            map_data[3][i] = 1
            map_data[8][i] = 1
            
        for i in range(4, 9):
            map_data[i][7] = 1
            map_data[i][12] = 1
            
        return map_data
        
    def draw_map(self):
        tile_size = 64
        
        # Draw map
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                if cell == 1:
                    pygame.draw.rect(self.screen, DARK_GRAY, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
                    
    def draw_player(self):
        # Draw player as a colored circle based on character
        pygame.draw.circle(self.screen, self.player.color, (int(self.player.x), int(self.player.y)), self.player.width // 2)
        pygame.draw.line(
            self.screen, self.player.color,
            (self.player.x, self.player.y),
            (self.player.x + math.cos(self.player.angle) * 30,
             self.player.y + math.sin(self.player.angle) * 30),
            3
        )
        
    def draw_enemies(self):
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, RED, (int(enemy.x), int(enemy.y)), enemy.width // 2)
            pygame.draw.line(
                self.screen, RED,
                (enemy.x, enemy.y),
                (enemy.x + math.cos(enemy.angle) * 30,
                 enemy.y + math.sin(enemy.angle) * 30),
                3
            )
                
    def draw_bullets(self):
        for bullet in self.bullets:
            color = YELLOW if bullet.owner == 'player' else RED
            pygame.draw.circle(self.screen, color, (int(bullet.x), int(bullet.y)), 5)
            
    def draw_hud(self):
        # Health bar
        bar_width = 200
        bar_height = 30
        bar_x = 10
        bar_y = 10
        health_percent = self.player.health / self.player.max_health
        
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, int(bar_width * health_percent), bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        health_text = self.small_font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (bar_x + 10, bar_y + 5))
        
        # Ammo
        ammo_text = self.small_font.render(f"Ammo: {self.player.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (10, 50))
        
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 80))
        
        # Enemies remaining
        enemies_left = sum(1 for e in self.enemies if e.health > 0)
        enemies_text = self.small_font.render(f"Enemies: {enemies_left}", True, WHITE)
        self.screen.blit(enemies_text, (10, 110))
        
        # Crosshair
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        pygame.draw.line(self.screen, WHITE, (center_x - 10, center_y), (center_x + 10, center_y), 2)
        pygame.draw.line(self.screen, WHITE, (center_x, center_y - 10), (center_x, center_y + 10), 2)
        
    def check_bullet_collisions(self):
        for bullet in self.bullets[:]:
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
                
            # Check wall collision
            grid_x = int(bullet.x / 64)
            grid_y = int(bullet.y / 64)
            if 0 <= grid_x < len(self.map_data[0]) and 0 <= grid_y < len(self.map_data):
                if self.map_data[grid_y][grid_x] == 1:
                    self.bullets.remove(bullet)
                    continue
                    
            # Check player collision
            if bullet.owner == 'enemy':
                dx = bullet.x - self.player.x
                dy = bullet.y - self.player.y
                dist_sq = dx*dx + dy*dy
                if dist_sq < self.player.width * self.player.width:
                    self.player.health -= bullet.damage
                    self.bullets.remove(bullet)
                    if self.player.health <= 0:
                        self.running = False
                    continue
                    
            # Check enemy collision
            if bullet.owner == 'player':
                for enemy in self.enemies:
                    if enemy.health > 0:
                        dx = bullet.x - enemy.x
                        dy = bullet.y - enemy.y
                        dist_sq = dx*dx + dy*dy
                        if dist_sq < enemy.width * enemy.width:
                            enemy.health -= bullet.damage
                            self.bullets.remove(bullet)
                            if enemy.health <= 0:
                                self.score += 100
                            break
                            
    def update_enemies(self):
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.health > 0]
        
        for enemy in self.enemies:
            enemy.update(self.player)
            
            # Enemy shoots at player (use cached distance)
            if enemy.can_shoot():
                if enemy.dist < 300 and random.random() < 0.02:
                    enemy.shoot()
                    self.bullets.append(Bullet(enemy.x, enemy.y, enemy.angle, 'enemy'))
                    
    def spawn_enemy(self):
        """Spawn a new enemy at a random position away from player"""
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            # Spawn at edge of map
            side = random.randint(0, 3)
            if side == 0:  # Top
                x = random.randint(64, SCREEN_WIDTH - 64)
                y = 64
            elif side == 1:  # Bottom
                x = random.randint(64, SCREEN_WIDTH - 64)
                y = SCREEN_HEIGHT - 64
            elif side == 2:  # Left
                x = 64
                y = random.randint(64, SCREEN_HEIGHT - 64)
            else:  # Right
                x = SCREEN_WIDTH - 64
                y = random.randint(64, SCREEN_HEIGHT - 64)
            
            # Check if spawn point is valid (not a wall and not too close to player)
            grid_x = int(x / 64)
            grid_y = int(y / 64)
            dist_to_player = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
            
            if (0 <= grid_x < len(self.map_data[0]) and 0 <= grid_y < len(self.map_data) and
                self.map_data[grid_y][grid_x] == 0 and dist_to_player > 200):
                self.enemies.append(Enemy(x, y))
                return
                
            attempts += 1
        
        # Fallback: spawn at fixed safe location
        self.enemies.append(Enemy(50, 50))
                
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Player movement
        self.player.move(keys, self.map_data)
        
        # Mouse look
        mouse_rel = pygame.mouse.get_rel()
        self.player.rotate(mouse_rel[0])
        
        # Shooting
        if pygame.mouse.get_pressed()[0] and self.player.ammo > 0:
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_shot_time'):
                self.last_shot_time = 0
                
            if current_time - self.last_shot_time > 200:  # Fire rate: 200ms
                self.player.shoot()
                damage = self.player.stats[self.player.character]['damage']
                self.bullets.append(Bullet(self.player.x, self.player.y, self.player.angle, 'player', damage))
                self.last_shot_time = current_time
                
        # Reload
        if keys[pygame.K_r]:
            if self.player.ammo < 30:
                self.player.ammo = 30
                
    async def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        
            # Handle input
            self.handle_input()
            
            # Update enemies
            self.update_enemies()
            
            # Spawn new enemies if needed
            alive_enemies = sum(1 for e in self.enemies if e.health > 0)
            if alive_enemies < self.max_enemies:
                self.enemy_spawn_timer += 1
                if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                    self.spawn_enemy()
                    self.enemy_spawn_timer = 0
            else:
                self.enemy_spawn_timer = 0  # Reset timer if at max
            
            # Update bullets
            for bullet in self.bullets:
                bullet.update()
                
            # Check collisions
            self.check_bullet_collisions()
                
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_map()
            self.draw_enemies()
            self.draw_player()
            self.draw_bullets()
            self.draw_hud()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
            # Yield control to browser event loop
            await asyncio.sleep(0)
            
        pygame.quit()
        
    def show_victory_screen(self):
        pygame.time.wait(1000)
        self.screen.fill(BLACK)
        victory_text = self.font.render("VICTORY!", True, GREEN)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Press ESC to exit", True, WHITE)
        
        self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

async def main():
    # Character selection
    from character_select import CharacterSelect
    select = CharacterSelect()
    selected_char = await select.run()
    
    if selected_char:
        # Start game with selected character
        game = FPSGame(selected_char)
        await game.run()

if __name__ == "__main__":
    asyncio.run(main())

