
from collections import Counter, deque

from src.environment.game import Game

from src.agent.actions import ACTIONS
from src.agent.state import (
    get_vision,
    encode_state,
    WALL,
    BODY,
)


# Pénalité appliquée lorsqu'une décision identique est répétée.
LOOP_PENALTY = -2.0

# Nombre de dernières décisions conservées pour détecter les boucles.
LOOP_HISTORY_SIZE = 40

# Nombre d'apparitions précédentes avant de considérer une répétition.
LOOP_REPEAT_LIMIT = 2


class Trainer:
    """Gère l'entraînement, les parties et l'évaluation de l'agent."""

    def __init__(
        self,
        agent,
        width=10,
        height=10,
        max_steps=None
    ):
        """
        Initialise le gestionnaire d'entraînement.

        Args:
            agent: agent utilisant le Q-learning.
            width (int): largeur du plateau.
            height (int): hauteur du plateau.
            max_steps (int): nombre maximal de déplacements par partie.
        """
        self.agent = agent
        self.width = width
        self.height = height

        if max_steps is None:
            max_steps = width * height * 10

        self.max_steps = max_steps

    def get_available_actions(self, game, vision):
        """
        Identifie les actions qui évitent une collision immédiate.

        Le demi-tour est interdit. La case de la queue est toutefois
        considérée comme accessible si elle se libère pendant le tour.

        Args:
            game (Game): partie actuelle.
            vision (dict): vision du serpent dans les quatre directions.

        Returns:
            list: actions considérées comme sûres.
        """
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
        }

        available = []

        for action in ACTIONS:

            if action == opposite[game.direction]:
                continue

            first_cell = vision[action][0]

            if first_cell == WALL:
                continue

            if first_cell == BODY:
                target = game.snake.get_next_head(action)

                # La queue quitte sa position lors d'un déplacement normal.
                if target != game.snake.tail:
                    continue

            available.append(action)

        if not available:
            return ACTIONS

        return available

    def run_episode(self, training=True):
        """
        Exécute une partie complète.

        Les répétitions d'une même paire état-action sont détectées.
        En entraînement, elles entraînent une pénalité afin de décourager
        les comportements cycliques.

        Args:
            training (bool): indique si l'agent apprend pendant la partie.

        Returns:
            dict: résultats de la partie.
        """
        game = Game(self.width, self.height)

        vision = get_vision(game)
        state = encode_state(vision, game.direction)

        episode_steps = 0
        loop_repetitions = 0

        recent_pairs = deque()
        pair_counts = Counter()

        while not game.game_over:

            available_actions = self.get_available_actions(
                game,
                vision
            )

            action = self.agent.choose_action(
                state,
                training=training,
                available_actions=available_actions
            )

            # Une paire représente une situation et l'action choisie.
            state_action = (state, action)

            # On vérifie si cette même décision a déjà été répétée.
            if pair_counts[state_action] >= LOOP_REPEAT_LIMIT:

                loop_repetitions += 1

            # On conserve uniquement les dernières décisions.
            if len(recent_pairs) >= LOOP_HISTORY_SIZE:
                oldest_pair = recent_pairs.popleft()
                pair_counts[oldest_pair] -= 1

                if pair_counts[oldest_pair] == 0:
                    del pair_counts[oldest_pair]

            recent_pairs.append(state_action)
            pair_counts[state_action] += 1

            reward, done = game.step(action)

            # La pénalité est appliquée uniquement pendant l'entraînement.
            if training and pair_counts[state_action] > LOOP_REPEAT_LIMIT:
                reward += LOOP_PENALTY

            episode_steps += 1

            # Cette limite empêche une partie de tourner indéfiniment.
            if episode_steps >= self.max_steps:
                game.game_over = True
                done = True

            if done:
                next_state = state
                next_actions = None

            else:
                next_vision = get_vision(game)

                next_state = encode_state(
                    next_vision,
                    game.direction
                )

                next_actions = self.get_available_actions(
                    game,
                    next_vision
                )

            # En mode évaluation, aucune mise à jour du Q-table n'est faite.
            if training:
                self.agent.update(
                    state,
                    action,
                    reward,
                    next_state,
                    done,
                    next_actions
                )

            state = next_state

            if not done:
                vision = next_vision

            if done:
                break

        if training:
            self.agent.decay_epsilon()

        results = game.get_results()
        results["steps"] = episode_steps
        results["epsilon"] = self.agent.epsilon
        results["loop_repetitions"] = loop_repetitions

        return results

    def train(self, episodes, quiet=False):
        """
        Entraîne l'agent sur plusieurs parties.

        Args:
            episodes (int): nombre de parties d'entraînement.
            quiet (bool): désactive l'affichage des résultats.

        Returns:
            list: résultats de chaque partie.
        """
        history = []

        for episode in range(episodes):

            results = self.run_episode(training=True)
            history.append(results)

            if not quiet:
                print(
                    f"Episode {episode + 1}/{episodes} | "
                    f"Max length: {results['max_length']} | "
                    f"Steps: {results['steps']} | "
                    f"Loops: {results['loop_repetitions']} | "
                    f"Epsilon: {results['epsilon']:.4f}"
                )

        return history

    def play(self):
        """Lance une partie sans modifier le modèle."""
        return self.run_episode(training=False)

    def evaluate(self, episodes=100):
        """
        Évalue l'agent sans lui permettre d'apprendre.

        Args:
            episodes (int): nombre de parties à exécuter.

        Returns:
            dict: statistiques globales de l'évaluation.
        """
        if episodes < 1:
            raise ValueError(
                "Evaluation episodes must be at least 1."
            )

        initial_states = len(self.agent.q_table)

        history = []

        for _ in range(episodes):
            history.append(
                self.run_episode(training=False)
            )

        lengths = [
            result["max_length"]
            for result in history
        ]

        steps = [
            result["steps"]
            for result in history
        ]

        loop_repetitions = sum(
            result["loop_repetitions"]
            for result in history
        )

        successful_games = sum(
            length >= 10
            for length in lengths
        )

        final_states = len(self.agent.q_table)

        return {
            "episodes": episodes,
            "average_length": sum(lengths) / episodes,
            "best_length": max(lengths),
            "average_steps": sum(steps) / episodes,
            "successful_games": successful_games,
            "success_rate": successful_games / episodes * 100,
            "loop_repetitions": loop_repetitions,
            "average_loop_repetitions": (
                loop_repetitions / episodes
            ),
            "initial_states": initial_states,
            "final_states": final_states,
            "model_unchanged": initial_states == final_states,
        }
