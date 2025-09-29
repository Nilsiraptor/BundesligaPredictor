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
    attack: float = 0.0
    defense: float = 0.0

    def __str__(self):
        return f"{self.name} ({self.attack:.0f}/{self.defense:.0f})"

    def match(self, other, home, away):
        home_goals = np.log2(1 + 2**(beta_home*(self.attack - other.defense))) * home
        away_goals = np.log2(1 + 2**(beta_away*(other.attack - self.defense))) * away
        return home_goals, away_goals

    def update(self, other, historic, result, k=k):
        expectation = self.match(other, *historic)

        home_goal_diff = k * (result[0] - expectation[0])
        away_goal_diff = k * (result[1] - expectation[1])

        self.attack += home_goal_diff
        self.defense -= away_goal_diff

        other.attack += away_goal_diff
        other.defense -= home_goal_diff

    def show_probability_distribution(self, other, home_advantage, away_advantage, max_goals=4, save=False):
        # Calculate the expected goals for each team
        expected_home_goals, expected_away_goals = self.match(
            other, home=home_advantage, away=away_advantage
        )

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

        expected_home_goals, expected_away_goals = self.match(
            other, home=home_advantage, away=away_advantage
        )

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
