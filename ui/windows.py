import pygame
from config import *
from ui.components import Button

class EndBattleWindow:
    def __init__(self, screen):
        self.screen = screen
        self.button = Button(SCREEN_WIDTH - 160, 10, 150, 45, "投降", RED)

    def handle_click(self, pos, game):
        if self.button.is_clicked(pos):
            game.game_over = True
            game.winner = game.p2
            game.log_panel.add("你投降了！")
            return True
        return False

    def draw(self):
        self.button.draw(self.screen)

class VictoryWindow:
    def __init__(self, screen):
        self.screen = screen

    def draw_victory_screen(self, game):
        if not game.game_over:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        if game.winner == game.p1:
            text = FONT_BIG.render("你胜利了！", True, YELLOW)
        else:
            text = FONT_BIG.render("你输了！", True, RED)
        self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
