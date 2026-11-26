
import random


class Snake:
    """Représente le serpent et gère son corps et ses déplacements."""

    def __init__(self, board, length=3):
        """
        Initialise le serpent sur une position aléatoire.

        Args:
            board (Board): plateau sur lequel apparaît le serpent.
            length (int): longueur initiale du serpent.
        """
        if not isinstance(length, int) or length < 2:
            raise ValueError("Snake length must be at least 2.")

        if length > max(board.width, board.height):
            raise ValueError(
                "Snake length exceeds the board dimensions."
            )

        self.board = board
        self.body = self._generate_body(length)

    @property
    def length(self):
        """Retourne la longueur actuelle du serpent."""
        return len(self.body)

    @property
    def head(self):
        """Retourne la position de la tête du serpent."""
        return self.body[0]

    @property
    def tail(self):
        """Retourne la position de la queue du serpent."""
        return self.body[-1]

    def _generate_body(self, length):
        """
        Génère une position initiale aléatoire pour le serpent.

        Le serpent apparaît horizontalement ou verticalement,
        avec sa tête à l'avant de son corps.

        Args:
            length (int): longueur souhaitée.

        Returns:
            list: positions successives du serpent.
        """
        candidates = []

        # Génération des positions horizontales possibles.
        if length <= self.board.width:
            for y in range(self.board.height):
                for x in range(length - 1, self.board.width):
                    body = [
                        (x - i, y)
                        for i in range(length)
                    ]
                    candidates.append(body)

        # Génération des positions verticales possibles.
        if length <= self.board.height:
            for x in range(self.board.width):
                for y in range(length - 1, self.board.height):
                    body = [
                        (x, y - i)
                        for i in range(length)
                    ]
                    candidates.append(body)

        random.shuffle(candidates)

        for body in candidates:
            if all(
                self.board.is_empty(position)
                for position in body
            ):
                return body

        raise ValueError(
            "No valid position available for the snake."
        )

    def get_next_head(self, direction):
        """
        Calcule la prochaine position de la tête.

        Args:
            direction (str): direction parmi UP, DOWN, LEFT, RIGHT.

        Returns:
            tuple: coordonnées de la prochaine tête.
        """
        movements = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0),
        }

        if direction not in movements:
            raise ValueError("Invalid direction.")

        x, y = self.head
        dx, dy = movements[direction]

        return x + dx, y + dy

    def move(self, direction):
        """
        Déplace le serpent d'une case sans modifier sa longueur.

        La vérification des collisions doit être effectuée par Game
        avant d'appeler cette méthode.

        Args:
            direction (str): direction du déplacement.
        """
        new_head = self.get_next_head(direction)

        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self, new_head):
        """
        Déplace le serpent en conservant son ancienne queue.

        Args:
            new_head (tuple): nouvelle position de la tête.
        """
        self.body.insert(0, new_head)

    def shrink(self, new_head, amount=1):
        """
        Déplace le serpent et retire des segments à sa queue.

        Args:
            new_head (tuple): nouvelle position de la tête.
            amount (int): nombre de segments supplémentaires à retirer.

        Raises:
            ValueError: si le nombre de segments à retirer est invalide.
        """
        if amount < 1:
            raise ValueError("Shrink amount must be positive.")

        self.body.insert(0, new_head)

        for _ in range(amount + 1):
            if self.body:
                self.body.pop()
