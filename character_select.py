import pygame
import asyncio

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class CharacterSelect:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Choose Your Character")
        self.clock = pygame.time.Clock()
        self.selected = None
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.characters = [
            {'name': 'Soldier', 'color': BLUE, 'stats': 'Balanced', 'key': 'soldier'},
            {'name': 'Commando', 'color': GREEN, 'stats': 'Fast & Agile', 'key': 'commando'},
            {'name': 'Tank', 'color': (128, 0, 128), 'stats': 'High Health', 'key': 'tank'},
            {'name': 'Assassin', 'color': (255, 140, 0), 'stats': 'High Damage', 'key': 'assassin'}
        ]
        
        self.hovered = None
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("Choose Your Character", True, GREEN)
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw character cards
        card_width = 160
        card_height = 220
        spacing = 40
        total_width = len(self.characters) * card_width + (len(self.characters) - 1) * spacing
        start_x = (self.width - total_width) // 2
        
        for i, char in enumerate(self.characters):
            x = start_x + i * (card_width + spacing)
            y = 200
            
            # Check if hovering
            mouse_x, mouse_y = pygame.mouse.get_pos()
            is_hover = (x <= mouse_x <= x + card_width and y <= mouse_y <= y + card_height)
            
            if is_hover:
                self.hovered = i
            
            # Draw card
            border_color = WHITE if is_hover else (128, 128, 128)
            pygame.draw.rect(self.screen, border_color, (x - 5, y - 5, card_width + 10, card_height + 10), 3)
            pygame.draw.rect(self.screen, (40, 40, 40), (x, y, card_width, card_height))
            
            # Draw character preview
            center_x = x + card_width // 2
            center_y = y + 60
            pygame.draw.circle(self.screen, char['color'], (center_x, center_y), 40)
            
            # Draw name
            name_surface = self.font_medium.render(char['name'], True, WHITE)
            name_rect = name_surface.get_rect(center=(x + card_width // 2, y + 120))
            self.screen.blit(name_surface, name_rect)
            
            # Draw stats
            stats_surface = self.font_small.render(char['stats'], True, (200, 200, 200))
            stats_rect = stats_surface.get_rect(center=(x + card_width // 2, y + 160))
            self.screen.blit(stats_surface, stats_rect)
            
            # Number
            num_surface = self.font_small.render(f"{i + 1}", True, WHITE)
            self.screen.blit(num_surface, (x + 10, y + 10))
        
        # Instructions
        inst = self.font_small.render("Click on a character to select or press number keys 1-4", True, WHITE)
        inst_rect = inst.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(inst, inst_rect)
        
        pygame.display.flip()
    
    async def run(self):
        running = True
        
        while running and self.selected is None:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = event.pos
                        card_width = 160
                        card_height = 220
                        spacing = 40
                        total_width = len(self.characters) * card_width + (len(self.characters) - 1) * spacing
                        start_x = (self.width - total_width) // 2
                        
                        for i, char in enumerate(self.characters):
                            x = start_x + i * (card_width + spacing)
                            y = 200
                            if x <= mouse_x <= x + card_width and y <= mouse_y <= y + card_height:
                                self.selected = char['key']
                                running = False
                                break
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected = self.characters[0]['key']
                        running = False
                    elif event.key == pygame.K_2:
                        self.selected = self.characters[1]['key']
                        running = False
                    elif event.key == pygame.K_3:
                        self.selected = self.characters[2]['key']
                        running = False
                    elif event.key == pygame.K_4:
                        self.selected = self.characters[3]['key']
                        running = False
            
            self.draw()
            await asyncio.sleep(0)
            self.clock.tick(60)
        
        pygame.quit()
        return self.selected

