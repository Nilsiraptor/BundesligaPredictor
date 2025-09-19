from dataclasses import dataclass

k = 10

beta = 0.1
beta_home = beta
beta_away = beta

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

    def update(self, other, historic, result, k):
        expectation = self.match(other, *historic)

        home_goal_diff = k * (result[0] - expectation[0])
        away_goal_diff = k * (result[1] - expectation[1])

        self.attack += home_goal_diff
        self.defense -= away_goal_diff

        other.attack += away_goal_diff
        other.defense -= home_goal_diff

class defaultdict(dict):
    def __init__(self, factory):
        super().__init__()

        self.factory = factory

    def __missing__(self, key):
        self[key] = self.factory(key)

        return self[key]
