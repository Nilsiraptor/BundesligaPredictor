from dataclasses import dataclass
import numpy as np
from scipy.special import factorial
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

k = 0.5

beta = 0.1
beta_home = beta
beta_away = beta

# Function to calculate Poisson probability
def poisson(k, l):
    return l**k / factorial(k, exact=True) * np.exp(-l)

@dataclass
class Team():
    name: str
    home_attack: float = 1.25 / beta_home
    home_defense: float = 0.0
    away_attack: float = 0.36 / beta_away
    away_defense: float = 0.0

    def __str__(self):
        return f"{self.name} ({self.home_attack:.1f}:{self.home_defense:.1f}/{self.away_attack:.1f}:{self.away_defense:.1f})"

    @property
    def score(self):
        return self.home_attack + self.home_defense + self.away_attack + self.away_defense

    def match(self, other):
        home_goals = np.log2(1 + 2**(beta_home*(self.home_attack - other.away_defense)))
        away_goals = np.log2(1 + 2**(beta_away*(other.away_attack - self.home_defense)))
        return home_goals, away_goals

    def update(self, other, result, k=k):
        expectation = self.match(other)

        home_goal_diff = k * (result[0] - expectation[0])
        away_goal_diff = k * (result[1] - expectation[1])

        self.home_attack += home_goal_diff
        self.home_defense -= away_goal_diff

        other.away_attack += away_goal_diff
        other.away_defense -= home_goal_diff

    def show_probability_distribution(self, other, home_advantage, away_advantage, max_goals=4, save=False):
        # Calculate the expected goals for each team
        expected_home_goals, expected_away_goals = self.match(other)

        # Create a grid for the probability distribution
        home_goals_range = np.arange(0, max_goals + 1)
        away_goals_range = np.arange(0, max_goals + 1)
        probabilities = np.zeros((len(home_goals_range), len(away_goals_range)))

        # Calculate the probability for each scoreline
        for i, home_goals in enumerate(home_goals_range):
            for j, away_goals in enumerate(away_goals_range):
                prob_home = poisson(home_goals, expected_home_goals)
                prob_away = poisson(away_goals, expected_away_goals)
                probabilities[i, j] = prob_home * prob_away

        # Plot the heatmap
        fig, ax = plt.subplots(figsize=(5, 4.135), layout="constrained")
        heatmap = ax.imshow(probabilities, cmap='inferno', origin="lower")

        # Add labels and a color bar
        ax.set_xticks([])
        ax.set_yticks([])
        # ax.set_xlabel(f'{other.name} Goals')
        # ax.set_ylabel(f'{self.name} Goals')
        ax.set_title(f'{self.name} vs. {other.name}')
        fig.colorbar(heatmap, label='Wahrscheinlichkeit', format=PercentFormatter(xmax=1.0))

        # Add text annotations for each cell
        for i in range(len(home_goals_range)):
            for j in range(len(away_goals_range)):
                ax.text(j, i, f'{i} : {j}', ha='center', va='center', color='g')

        if save:
            plt.savefig("match_results.png")

        plt.show()

    def calculate_win_probabilities(self, other, home_advantage, away_advantage, max_goals=100):

        expected_home_goals, expected_away_goals = self.match(other)

        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0

        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob_home = poisson(i, expected_home_goals)
                prob_away = poisson(j, expected_away_goals)

                score_prob = prob_home * prob_away

                if i > j:
                    home_win_prob += score_prob
                elif i == j:
                    draw_prob += score_prob
                else: # i < j
                    away_win_prob += score_prob

        return (home_win_prob, draw_prob, away_win_prob)

class defaultdict(dict):
    def __init__(self, factory):
        super().__init__()

        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)

        return self[key]
