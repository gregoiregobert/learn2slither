import pygame

from src.environment.board import (
    GREEN_APPLE,
    RED_APPLE,
)


class Renderer:
    """Dessine le plateau et les informations de la partie."""

    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800

    BACKGROUND = (24, 27, 34)
    PANEL = (34, 39, 48)
    GRID = (55, 62, 73)
    EMPTY_CELL = (43, 49, 59)
    SNAKE = (65, 190, 115)
    SNAKE_HEAD = (105, 225, 145)
    GREEN = (80, 220, 100)
    RED = (235, 75, 75)
    TEXT = (235, 238, 242)
    MUTED = (165, 173, 185)
    ACCENT = (100, 165, 245)

    def __init__(self, screen, width, height):
        """
        Prépare les dimensions et les polices de l'affichage.

        Args:
            screen: fenêtre Pygame.
            width (int): largeur du plateau.
            height (int): hauteur du plateau.
        """
        self.screen = screen
        self.width = width
        self.height = height

        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 38)

        self.cell_size = min(
            680 // width,
            680 // height
        )

        self.board_width = self.cell_size * width
        self.board_height = self.cell_size * height

        self.board_x = 30
        self.board_y = 75

    def draw(
        self,
        game,
        speed,
        paused,
        step_mode=False,
        history_index=0,
        history_length=1
    ):
        """
        Dessine une image complète de la partie.

        Args:
            game: partie actuelle.
            speed (int): vitesse en déplacements par seconde.
            paused (bool): indique si la partie est en pause.
            step_mode (bool): conservé pour compatibilité.
            history_index (int): position actuelle dans l'historique.
            history_length (int): nombre total d'états enregistrés.
        """
        self.screen.fill(self.BACKGROUND)

        self._draw_header()
        self._draw_board(game)

        self._draw_panel(
            game,
            speed,
            paused,
            history_index,
            history_length
        )

        pygame.display.flip()

    def _draw_header(self):
        """Affiche le titre de la fenêtre."""
        title = self.title_font.render(
            "Learn2Slither",
            True,
            self.TEXT
        )

        self.screen.blit(title, (30, 25))

    def _draw_board(self, game):
        """Dessine les cases, les pommes et le serpent."""
        board_rect = pygame.Rect(
            self.board_x,
            self.board_y,
            self.board_width,
            self.board_height
        )

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            board_rect,
            border_radius=8
        )

        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    self.board_x + x * self.cell_size,
                    self.board_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                pygame.draw.rect(
                    self.screen,
                    self.EMPTY_CELL,
                    rect
                )

                pygame.draw.rect(
                    self.screen,
                    self.GRID,
                    rect,
                    width=1
                )

                value = game.board.grid[y][x]

                if value == GREEN_APPLE:
                    self._draw_apple(rect, self.GREEN)

                elif value == RED_APPLE:
                    self._draw_apple(rect, self.RED)

        # La tête est dessinée avec la couleur la plus claire.
        self._draw_snake_segment(
            game.snake.head,
            self.SNAKE_HEAD
        )

        # Le dégradé suit l'ordre réel du corps jusqu'à la queue.
        for index, position in enumerate(game.snake.body[1:], start=1):
            color = self._get_snake_color(
                index,
                game.snake.length
            )

            self._draw_snake_segment(position, color)

    def _get_snake_color(self, index, length):
        """
        Calcule la couleur d'un segment selon sa position.

        La couleur évolue progressivement du vert clair au vert foncé.

        Args:
            index (int): position du segment dans le corps.
            length (int): longueur totale du serpent.

        Returns:
            tuple: couleur RGB du segment.
        """
        start_color = (65, 190, 115)
        end_color = (25, 85, 65)

        progress = index / max(1, length - 1)

        return tuple(
            int(
                start + (end - start) * progress
            )
            for start, end in zip(start_color, end_color)
        )

    def _draw_apple(self, rect, color):
        """Dessine une pomme au centre d'une case."""
        center = rect.center
        radius = max(4, self.cell_size // 3)

        pygame.draw.circle(
            self.screen,
            color,
            center,
            radius
        )

    def _draw_snake_segment(self, position, color):
        """Dessine un segment du serpent."""
        x, y = position

        rect = pygame.Rect(
            self.board_x + x * self.cell_size,
            self.board_y + y * self.cell_size,
            self.cell_size,
            self.cell_size
        )

        margin = max(2, self.cell_size // 10)
        rect.inflate_ip(
            -margin * 2,
            -margin * 2
        )

        pygame.draw.rect(
            self.screen,
            color,
            rect,
            border_radius=max(3, self.cell_size // 5)
        )

    def _draw_panel(
        self,
        game,
        speed,
        paused,
        history_index,
        history_length
    ):
        """Affiche les statistiques et les commandes."""
        panel_x = 745
        panel_y = 75
        panel_width = 225
        panel_height = 680

        pygame.draw.rect(
            self.screen,
            self.PANEL,
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=10
        )

        x = panel_x + 20
        y = panel_y + 25

        self._draw_text(
            "STATISTIQUES",
            x,
            y,
            self.ACCENT
        )
        y += 45

        self._draw_text(
            f"Longueur : {game.snake.length}",
            x,
            y
        )
        y += 35

        self._draw_text(
            f"Record : {game.max_length}",
            x,
            y
        )
        y += 35

        self._draw_text(
            f"Déplacements : {game.steps}",
            x,
            y
        )
        y += 35

        self._draw_text(
            f"Historique : {history_index}/{history_length - 1}",
            x,
            y,
            self.MUTED,
            small=True
        )
        y += 50

        self._draw_text(
            "CONTROLES",
            x,
            y,
            self.ACCENT
        )
        y += 40

        controls = [
            "ESPACE : pause / reprise",
            "DROITE : avancer (pause)",
            "GAUCHE : reculer (pause)",
            "+ / - : vitesse",
            "R : nouvelle partie",
            "ECHAP : quitter",
        ]

        for control in controls:
            self._draw_text(
                control,
                x,
                y,
                self.MUTED,
                small=True
            )
            y += 29

        y += 30

        self._draw_text(
            "VITESSE",
            x,
            y,
            self.ACCENT
        )
        y += 35

        self._draw_text(
            f"{speed} déplacement(s) / sec.",
            x,
            y
        )
        y += 55

        if game.game_over:
            status = "PARTIE TERMINEE"
            color = self.RED
        elif paused:
            status = "EN PAUSE"
            color = self.ACCENT
        else:
            status = "EN COURS"
            color = self.GREEN

        self._draw_text(
            status,
            x,
            y,
            color
        )

        if paused:
            y += 35
            self._draw_text(
                "Navigation dans l'historique",
                x,
                y,
                self.MUTED,
                small=True
            )

    def _draw_text(
        self,
        content,
        x,
        y,
        color=None,
        small=False
    ):
        """Affiche une ligne de texte."""
        if color is None:
            color = self.TEXT

        font = self.small_font if small else self.font

        surface = font.render(
            content,
            True,
            color
        )

        self.screen.blit(
            surface,
            (x, y)
        )
