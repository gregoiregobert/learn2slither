
from src.environment.board import (
    Board,
    GREEN_APPLE,
    RED_APPLE,
)

from src.environment.snake import Snake

from src.training.rewards import (
    GREEN_APPLE_REWARD,
    RED_APPLE_REWARD,
    STEP_REWARD,
    DEATH_REWARD,
)


class Game:
    """Gère le déroulement d'une partie de Snake."""

    def __init__(self, width=10, height=10):
        """
        Initialise une nouvelle partie.

        Le serpent est créé avant les pommes afin que celles-ci
        ne puissent pas bloquer sa position initiale.

        Args:
            width (int): largeur du plateau.
            height (int): hauteur du plateau.
        """
        self.board = Board(width, height)
        self.snake = Snake(self.board)

        self.board.initialize_apples(
            blocked_positions=self.snake.body
        )

        self.direction = self._get_initial_direction()

        self.game_over = False
        self.steps = 0
        self.max_length = self.snake.length

    def step(self, direction):
        """
        Exécute un déplacement et applique ses conséquences.

        Les collisions sont vérifiées avant de modifier le serpent.

        Args:
            direction (str): direction du déplacement.

        Returns:
            tuple: récompense obtenue et état de fin de partie.
        """
        if self.game_over:
            return 0, True

        new_head = self.snake.get_next_head(direction)

        # Une collision avec un mur termine immédiatement la partie.
        if not self.board.is_inside(new_head):
            return self._end_game()

        green_apple = new_head in self.board.green_apples
        red_apple = new_head == self.board.red_apple

        # La queue libère une ou plusieurs cases selon le déplacement.
        if green_apple:
            occupied = self.snake.body

        elif red_apple:
            occupied = self.snake.body[:-2]

        else:
            occupied = self.snake.body[:-1]

        # Une collision avec le corps termine la partie.
        if new_head in occupied:
            return self._end_game()

        self.direction = direction

        if green_apple:
            reward = self._eat_green_apple(new_head)

        elif red_apple:
            reward = self._eat_red_apple(new_head)

        else:
            self.snake.move(direction)
            reward = STEP_REWARD

        self.steps += 1

        self.max_length = max(
            self.max_length,
            self.snake.length
        )

        return reward, self.game_over

    def _eat_green_apple(self, new_head):
        """
        Fait manger une pomme verte au serpent.

        Le serpent grandit d'un segment et une nouvelle pomme verte
        est placée sur une case disponible.

        Args:
            new_head (tuple): position de la pomme consommée.

        Returns:
            float: récompense associée à la pomme verte.
        """
        self.snake.grow(new_head)

        self.board.green_apples.remove(new_head)
        self.board.remove_apple(new_head)

        new_apple = self.board.place_apple(
            GREEN_APPLE,
            self.snake.body
        )

        if new_apple is not None:
            self.board.green_apples.append(new_apple)

        return GREEN_APPLE_REWARD

    def _eat_red_apple(self, new_head):
        """
        Fait manger une pomme rouge au serpent.

        Le serpent perd un segment net : il avance d'une case,
        mais deux segments sont retirés à la fin.

        Args:
            new_head (tuple): position de la pomme consommée.

        Returns:
            float: récompense associée à la pomme rouge.
        """
        self.snake.shrink(new_head)

        self.board.remove_apple(new_head)
        self.board.red_apple = None

        # Une pomme rouge est replacée si une case est disponible.
        self.board.red_apple = self.board.place_apple(
            RED_APPLE,
            self.snake.body
        )

        if self.snake.length <= 0:
            self.game_over = True
            return RED_APPLE_REWARD + DEATH_REWARD

        return RED_APPLE_REWARD

    def _end_game(self):
        """
        Termine la partie à la suite d'une collision.

        Returns:
            tuple: récompense de mort et état terminal.
        """
        self.game_over = True

        return DEATH_REWARD, True

    def get_results(self):
        """
        Retourne les statistiques de la partie.

        Returns:
            dict: longueur maximale, nombre de déplacements et état final.
        """
        return {
            "max_length": self.max_length,
            "steps": self.steps,
            "game_over": self.game_over,
        }

    def _get_initial_direction(self):
        """
        Détermine la direction initiale à partir de la tête et du cou.

        Returns:
            str: direction initiale du serpent.
        """
        head_x, head_y = self.snake.head
        neck_x, neck_y = self.snake.body[1]

        dx = head_x - neck_x
        dy = head_y - neck_y

        directions = {
            (0, -1): "UP",
            (0, 1): "DOWN",
            (-1, 0): "LEFT",
            (1, 0): "RIGHT",
        }

        return directions[(dx, dy)]
