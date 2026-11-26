
import os

from src.agent.q_learning import QLearningAgent
from src.training.trainer import Trainer
from src.utils.arguments import parse_arguments


def main():
    """Point d'entrée du programme."""
    args = parse_arguments()

    agent = QLearningAgent()

    trainer = Trainer(
        agent=agent,
        width=args.width,
        height=args.height
    )

    if args.evaluate > 0:
        agent.load(args.model)

        print(f"Loaded model: {args.model}")
        print(f"Evaluating over {args.evaluate} games...")

        results = trainer.evaluate(args.evaluate)

        print("\n===== EVALUATION RESULTS =====")
        print(f"Games: {results['episodes']}")
        print(
            f"Average maximum length: "
            f"{results['average_length']:.2f}"
        )
        print(f"Best length: {results['best_length']}")
        print(
            f"Average steps: "
            f"{results['average_steps']:.2f}"
        )
        print(
            f"Games reaching length 10: "
            f"{results['successful_games']}"
        )
        print(
            f"Success rate: "
            f"{results['success_rate']:.2f}%"
        )
        print(
            f"Q-table states before: "
            f"{results['initial_states']}"
        )
        print(
            f"Q-table states after: "
            f"{results['final_states']}"
        )
        print(
            f"Model unchanged: "
            f"{results['model_unchanged']}"
        )

        return

    if args.dontlearn:
        agent.load(args.model)

        if not args.quiet:
            print(f"Loaded model: {args.model}")

        if args.gui:
            from src.visualization.interface import GameInterface

            interface = GameInterface(
                agent=agent,
                width=args.width,
                height=args.height,
                speed=args.speed
            )

            interface.run()
            return

        if not args.quiet:
            print("Playing without learning...")

        results = trainer.play()

        print("\n===== GAME RESULTS =====")
        print(f"Maximum length: {results['max_length']}")
        print(f"Steps: {results['steps']}")
        print(f"Game over: {results['game_over']}")

        return

    history = trainer.train(
        episodes=args.episodes,
        quiet=args.quiet
    )

    model_path = args.model

    if model_path is None:
        model_path = os.path.join(
            "models",
            f"model_{args.episodes}.json"
        )

    agent.save(model_path)

    maximum_length = max(
        result["max_length"]
        for result in history
    )

    average_length = sum(
        result["max_length"]
        for result in history
    ) / len(history)

    print("\n===== TRAINING RESULTS =====")
    print(f"Episodes: {args.episodes}")
    print(f"Maximum length reached: {maximum_length}")
    print(f"Average maximum length: {average_length:.2f}")
    print(f"States learned: {len(agent.q_table)}")
    print(f"Model saved: {model_path}")


if __name__ == "__main__":
    main()
