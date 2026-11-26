
import copy

import pygame

from src.environment.game import Game
from src.agent.state import get_vision, encode_state
from src.training.trainer import Trainer
from src.visualization.renderer import Renderer


class GameInterface:
    """Gère la fenêtre et l'exécution visuelle d'une partie."""

    MIN_SPEED = 1
    MAX_SPEED = 30

    def __init__(
        self,
        agent,
        width=10,
        height=10,
        speed=8
    ):
        """Initialise l'interface graphique."""
        self.agent = agent
        self.width = width
        self.height = height

        self.speed = max(
            self.MIN_SPEED,
            min(self.MAX_SPEED, speed)
        )

        self.trainer = Trainer(
            agent=agent,
            width=width,
            height=height
        )

        self.game = Game(width, height)

        self.paused = False
        self.step_requested = False

        self.history = [copy.deepcopy(self.game)]
        self.history_index = 0

        self.clock = None
        self.screen = None
        self.renderer = None

    def run(self):
        """Lance la boucle principale de l'interface."""
        pygame.init()

        pygame.display.set_caption("Learn2Slither")

        self.screen = pygame.display.set_mode(
            (
                Renderer.WINDOW_WIDTH,
                Renderer.WINDOW_HEIGHT
            )
        )

        self.clock = pygame.time.Clock()

        self.renderer = Renderer(
            self.screen,
            self.width,
            self.height
        )

        last_move = pygame.time.get_ticks()
        running = True

        while running:
            running = self._handle_events()

            current_time = pygame.time.get_ticks()
            interval = 1000 / self.speed

            if self._can_move(current_time, last_move, interval):
                self._play_step()
                last_move = current_time

            self.renderer.draw(
                self.game,
                self.speed,
                self.paused,
                True,
                self.history_index,
                len(self.history)
            )

            self.clock.tick(60)

        pygame.quit()

    def _handle_events(self):
        """Traite les événements clavier et ceux de la fenêtre."""
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return False

            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
                self.step_requested = False

            elif event.key == pygame.K_RIGHT:
                if self.paused:
                    self.step_requested = True

            elif event.key == pygame.K_LEFT:
                if self.paused:
                    self._go_back()

            elif event.key in (
                pygame.K_PLUS,
                pygame.K_KP_PLUS,
                pygame.K_EQUALS
            ):
                self.speed = min(
                    self.MAX_SPEED,
                    self.speed + 1
                )

            elif event.key in (
                pygame.K_MINUS,
                pygame.K_KP_MINUS
            ):
                self.speed = max(
                    self.MIN_SPEED,
                    self.speed - 1
                )

            elif event.key == pygame.K_r:
                self._new_game()

        return True

    def _can_move(self, current_time, last_move, interval):
        """Détermine si un déplacement doit être exécuté."""
        if self.paused:
            return self.step_requested

        if self.game.game_over:
            return False

        return current_time - last_move >= interval

    def _play_step(self):
        """Avance d'un déplacement ou restaure l'état suivant."""
        self.step_requested = False

        if self.history_index < len(self.history) - 1:
            self.history_index += 1

            self.game = copy.deepcopy(
                self.history[self.history_index]
            )

        elif not self.game.game_over:
            vision = get_vision(self.game)

            state = encode_state(
                vision,
                self.game.direction
            )

            available_actions = self.trainer.get_available_actions(
                self.game,
                vision
            )

            action = self.agent.choose_action(
                state,
                training=False,
                available_actions=available_actions
            )

            self.game.step(action)

            self.history = self.history[:self.history_index + 1]

            self.history.append(
                copy.deepcopy(self.game)
            )

            self.history_index += 1

    def _go_back(self):
        """Restaure l'état précédent de la partie."""
        if self.history_index <= 0:
            return

        self.history_index -= 1

        self.game = copy.deepcopy(
            self.history[self.history_index]
        )

        self.step_requested = False

    def _new_game(self):
        """Démarre une nouvelle partie et réinitialise l'historique."""
        self.game = Game(
            self.width,
            self.height
        )

        self.history = [copy.deepcopy(self.game)]
        self.history_index = 0

        self.step_requested = False
