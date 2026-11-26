# Learn2Slither 🐍

Un jeu Snake intelligent qui apprend à jouer de manière autonome grâce au Reinforcement Learning (Q-learning).

![Learn2Slither Demo](learn2slither.gif)

## Présentation

Learn2Slither est un projet de Reinforcement Learning dans lequel un agent apprend à jouer au Snake par essais et erreurs.

À chaque déplacement, l'agent observe son environnement, choisit une action et reçoit une récompense en fonction du résultat. Au fil des parties, il améliore progressivement sa stratégie pour collecter les pommes et éviter les collisions.

Le projet utilise le **Q-learning** avec une Q-table pour mémoriser les meilleures actions à effectuer dans chaque situation.

## Fonctionnalités

- Environnement Snake avec pommes vertes et rouges.
- Agent autonome basé sur le Q-learning.
- Vision limitée aux quatre directions autour de la tête du serpent.
- Exploration et exploitation pour apprendre progressivement.
- Détection et pénalisation des comportements répétitifs.
- Sauvegarde et chargement des modèles entraînés.
- Évaluation sans modification du modèle.
- Interface graphique avec pause, vitesse configurable et navigation dans l'historique.
- Plateaux de dimensions variables, sans réentraînement du modèle.

## Installation

Cloner le dépôt :

```bash
git clone git@github.com:gregoiregobert/learn2slither.git
cd learn2slither
```

Créer un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

Le programme propose trois modes principaux : entraînement, évaluation et exécution d'un modèle.

Les arguments disponibles dépendent du mode choisi.

### 1. Entraînement

L'entraînement permet à l'agent d'apprendre progressivement à jouer.

```bash
python main.py -episodes 5000 -model models/model_5000.json
```

**Arguments associés :**

| Argument | Rôle |
|---|---|
| `-episodes` | Nombre de parties utilisées pour entraîner l'agent. |
| `-model` | Chemin du fichier dans lequel sauvegarder le modèle entraîné. |
| `-width` | Largeur du plateau d'entraînement. |
| `-height` | Hauteur du plateau d'entraînement. |

Les arguments `-width` et `-height` sont facultatifs : sans eux, le plateau utilise ses dimensions par défaut.

**Exemples :**

Entraîner sur un plateau de 20 × 20, sur 5000 parties :

```bash
python main.py -episodes 5000 -model models/model_5000.json -width 20 -height 20
```

Chaque nouvel entraînement crée un agent et une Q-table initialement vides. Il ne reprend pas automatiquement un modèle existant.

### 2. Évaluation

L'évaluation permet de mesurer les performances d'un modèle déjà entraîné, sans modifier ses connaissances.

```bash
python main.py -evaluate 100 -model models/model_5000_anti_loop.json
```

**Arguments associés :**

| Argument | Rôle |
|---|---|
| `-evaluate` | Nombre de parties utilisées pour évaluer le modèle. |
| `-model` | Chemin du modèle à charger. |
| `-width` | Largeur du plateau d'évaluation. |
| `-height` | Hauteur du plateau d'évaluation. |

**Exemples :**

Évaluer sur 500 parties :

```bash
python main.py -evaluate 500 -model models/model_5000_anti_loop.json
```

Évaluer le même modèle sur un plateau de 20 × 20 :

```bash
python main.py -evaluate 100 -model models/model_5000_anti_loop.json -width 20 -height 20
```

L'évaluation fournit notamment :

- La longueur moyenne maximale du serpent.
- La meilleure longueur atteinte.
- Le nombre moyen de déplacements.
- Le nombre et le taux de parties atteignant une longueur de 10.

Le modèle reste inchangé pendant toute l'évaluation.

### 3. Exécution d'un modèle

L'argument `-dontlearn` permet de charger un modèle existant et de le faire jouer sans effectuer d'apprentissage.

**Arguments associés :**

| Argument | Rôle |
|---|---|
| `-dontlearn` | Désactive l'apprentissage et utilise un modèle existant. |
| `-model` | Chemin du modèle à charger. |
| `-width` | Largeur du plateau. |
| `-height` | Hauteur du plateau. |
| `-gui` | Lance l'interface graphique. |
| `-speed` | Définit la vitesse de jeu dans l'interface graphique. |

L'interface graphique est facultative : sans `-gui`, le jeu s'exécute dans le terminal.

**Exemples :**



Utiliser le modèle sur un plateau de 20 × 20, avec interface graphique sans apprentissage :

```bash
python main.py -dontlearn -model models/model_5000_anti_loop.json -gui -width 20 -height 20
```

**Commandes de l'interface graphique :**

| Touche | Action |
|---|---|
| Espace | Pause / Reprise |
| Flèche droite | Avancer d'un déplacement (en pause) |
| Flèche gauche | Reculer dans l'historique (en pause) |
| + / - | Modifier la vitesse |
| R | Nouvelle partie |
| Échap | Quitter |

### Récapitulatif des arguments

| Argument | Entraînement | Évaluation | Exécution |
|---|:---:|:---:|:---:|
| `-episodes` | ✓ | | |
| `-evaluate` | | ✓ | |
| `-dontlearn` | | | ✓ |
| `-model` | ✓ | ✓ | ✓ |
| `-width` | ✓ | ✓ | ✓ |
| `-height` | ✓ | ✓ | ✓ |
| `-gui` | | | ✓ |
| `-speed` | | | ✓ |

Les arguments `-episodes` et `-evaluate` définissent des modes différents : le premier entraîne l'agent, tandis que le second mesure les performances d'un modèle existant.

## Fonctionnement du Q-learning

Le Q-learning est un algorithme de Reinforcement Learning qui apprend à associer une valeur à chaque action possible dans une situation donnée.

L'agent utilise trois éléments principaux :

- **État :** représentation de la vision du serpent dans les quatre directions.
- **Action :** déplacement vers le haut, le bas, la gauche ou la droite.
- **Récompense :** valeur positive ou négative attribuée selon le résultat de l'action.

L'agent utilise une stratégie d'exploration et d'exploitation :

- **Exploration :** essayer de nouvelles actions pour découvrir de meilleures stratégies.
- **Exploitation :** choisir les actions qui ont déjà donné les meilleurs résultats.

La Q-table conserve les valeurs apprises pour chaque état et chaque action.

### Détection des boucles

Un mécanisme supplémentaire détecte les répétitions de situations et d'actions.

Lorsqu'un comportement répétitif est identifié pendant l'entraînement, une pénalité est appliquée pour décourager l'agent de rester bloqué dans une boucle.

## Structure du projet

```text
Learn2Slither/
├── main.py
├── models/
│   ├── model_1.json
│   ├── model_10.json
│   ├── model_100.json
│   └── model_5000_anti_loop.json
├── src/
│   ├── agent/
│   │   ├── actions.py
│   │   ├── q_learning.py
│   │   └── state.py
│   ├── environment/
│   │   ├── board.py
│   │   ├── game.py
│   │   └── snake.py
│   ├── training/
│   │   ├── rewards.py
│   │   └── trainer.py
│   ├── utils/
│   │   └── arguments.py
│   └── visualization/
│       ├── interface.py
│       └── renderer.py
└── requirements.txt
```

## Technologies

- Python
- Pygame
- Reinforcement Learning
- Q-learning
- JSON

## Auteur

Projet réalisé dans le cadre du cursus de l'École 42.