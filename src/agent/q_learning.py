
import json
import os
import random

from src.agent.actions import ACTIONS


class QLearningAgent:

    def __init__(
        self,
        alpha=0.1,
        gamma=0.9,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.9995
    ):

        self.alpha = alpha
        self.gamma = gamma

        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.q_table = {}

    def get_q_values(self, state):

        if state not in self.q_table:
            self.q_table[state] = {
                action: 0.0
                for action in ACTIONS
            }

        return self.q_table[state]

    def choose_action(
        self,
        state,
        training=True,
        available_actions=None
    ):

        if not available_actions:
            available_actions = ACTIONS

        if training and random.random() < self.epsilon:
            return random.choice(available_actions)

        if state not in self.q_table:

            if training:
                self.get_q_values(state)
            else:
                return random.choice(available_actions)

        q_values = self.q_table[state]

        best_value = max(
            q_values[action]
            for action in available_actions
        )

        best_actions = [
            action
            for action in available_actions
            if q_values[action] == best_value
        ]

        return random.choice(best_actions)

    def update(
        self,
        state,
        action,
        reward,
        next_state,
        done,
        next_actions=None
    ):

        q_values = self.get_q_values(state)

        current_q = q_values[action]

        if done:
            future_q = 0.0

        else:
            next_q_values = self.get_q_values(next_state)

            if next_actions:
                future_q = max(
                    next_q_values[action]
                    for action in next_actions
                )
            else:
                future_q = 0.0

        target = reward + self.gamma * future_q

        q_values[action] += self.alpha * (
            target - current_q
        )

    def decay_epsilon(self):

        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )

    def save(self, filepath):

        directory = os.path.dirname(filepath)

        if directory:
            os.makedirs(directory, exist_ok=True)

        data = {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_min": self.epsilon_min,
            "epsilon_decay": self.epsilon_decay,
            "q_table": self.q_table
        }

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self, filepath):

        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.alpha = data["alpha"]
        self.gamma = data["gamma"]
        self.epsilon = data["epsilon"]
        self.epsilon_min = data["epsilon_min"]
        self.epsilon_decay = data["epsilon_decay"]

        loaded_table = data["q_table"]

        for state, values in loaded_table.items():

            if set(values) != set(ACTIONS):
                raise ValueError(
                    f"Invalid actions in saved state: {state}"
                )

        self.q_table = loaded_table
