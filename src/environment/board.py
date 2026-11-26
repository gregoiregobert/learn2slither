
import random


EMPTY = 0
GREEN_APPLE = 2
RED_APPLE = 3


class Board:
    """Représente le plateau de jeu et gère les pommes."""

    def __init__(self, width=10, height=10):
        """
        Initialise un plateau vide.

        Args:
            width (int): largeur du plateau.
            height (int): hauteur du plateau.
        """
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("Board dimensions must be integers.")

        if width < 3 or height < 3:
            raise ValueError("Board dimensions must be at least 3.")

        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        """Réinitialise le plateau et supprime toutes les pommes."""
        self.grid = [
            [EMPTY for _ in range(self.width)]
            for _ in range(self.height)
        ]

        self.green_apples = []
        self.red_apple = None

    def is_inside(self, position):
        """
        Vérifie si une position appartient au plateau.

        Args:
            position (tuple): coordonnées (x, y).

        Returns:
            bool: True si la position est dans les limites.
        """
        x, y = position

        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )

    def is_empty(self, position):
        """
        Vérifie si une case est vide.

        Une case occupée par le serpent reste considérée comme vide
        dans la grille : le corps du serpent est géré séparément.

        Args:
            position (tuple): coordonnées (x, y).

        Returns:
            bool: True si la case est disponible dans la grille.
        """
        if not self.is_inside(position):
            return False

        x, y = position

        return self.grid[y][x] == EMPTY

    def get_empty_cells(self, blocked_positions=None):
        """
        Retourne les cases disponibles, hors positions bloquées.

        Args:
            blocked_positions (iterable): positions à exclure,
                notamment celles occupées par le serpent.

        Returns:
            list: liste des coordonnées disponibles.
        """
        blocked_positions = set(blocked_positions or [])
        cells = []

        for y in range(self.height):
            for x in range(self.width):
                position = (x, y)

                if (
                    self.is_empty(position)
                    and position not in blocked_positions
                ):
                    cells.append(position)

        return cells

    def place_apple(self, apple_type, blocked_positions=None):
        """
        Place une pomme sur une case disponible.

        Args:
            apple_type (int): type de pomme (GREEN_APPLE ou RED_APPLE).
            blocked_positions (iterable): positions à éviter.

        Returns:
            tuple | None: position de la pomme, ou None si
            aucune case n'est disponible.
        """
        if apple_type not in (GREEN_APPLE, RED_APPLE):
            raise ValueError("Invalid apple type.")

        empty_cells = self.get_empty_cells(blocked_positions)

        if not empty_cells:
            return None

        position = random.choice(empty_cells)
        x, y = position

        self.grid[y][x] = apple_type

        return position

    def remove_apple(self, position):
        """
        Retire une pomme du plateau.

        Args:
            position (tuple): coordonnées de la pomme.

        Raises:
            ValueError: si la position est invalide ou ne contient
                aucune pomme.
        """
        if not self.is_inside(position):
            raise ValueError("Position is outside the board.")

        x, y = position

        if self.grid[y][x] not in (GREEN_APPLE, RED_APPLE):
            raise ValueError("No apple at this position.")

        self.grid[y][x] = EMPTY

    def initialize_apples(self, blocked_positions=None):
        """
        Place les deux pommes vertes et la pomme rouge initiales.

        Le plateau est réinitialisé avant le placement.

        Args:
            blocked_positions (iterable): positions à ne pas utiliser,
                notamment le corps initial du serpent.
        """
        self.reset()

        for _ in range(2):
            position = self.place_apple(
                GREEN_APPLE,
                blocked_positions
            )

            if position is not None:
                self.green_apples.append(position)

        self.red_apple = self.place_apple(
            RED_APPLE,
            blocked_positions
        )
