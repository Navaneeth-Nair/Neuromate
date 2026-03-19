import math
import random
from dataclasses import dataclass

@dataclass
class MoodState:
    valence: float = 0.5
    arousal: float = 0.5

class MoodElo:
    def __init__(self, k_valence:float = 16, k_arousal:float = 16, base_valence:float = 0.5, base_arousal:float = 0.5):
        self.Kv = k_valence
        self.Ka = k_arousal
        self.base_arousal = base_arousal
        self.base_valence = base_valence
    
    @staticmethod
    def _expected_score(r_user:float , r_base:float) -> float:
        return 1/(1+math.pow(10, (r_base - r_user)/400))

    @staticmethod
    def _normalize(value:float, min_val:float, max_val:float) -> float:
        return max(min(value, max_val), min_val)
    
    def update(self, state: MoodState, sentiment: float, intensity: float) -> MoodState:
        S_valence = (sentiment + 1) / 2
        S_arousal = intensity

        E_v = self._expected_score(state.valence, self.base_valence)
        E_a = self._expected_score(state.arousal, self.base_arousal)

        new_valence = state.valence + self.Kv * (S_valence - E_v) / 1000
        new_arousal = state.arousal + self.Ka * (S_arousal - E_a) / 1000

        new_valence = self._normalize(new_valence, 0, 1)
        new_arousal = self._normalize(new_arousal, 0, 1)

        return MoodState(valence=new_valence, arousal=new_arousal)

    def simulate(self, text_sentiment: float, text_intensity: float, rounds: int = 10):
        state = MoodState()
        for i in range(rounds):
            state = self.update(state, text_sentiment, text_intensity)
            print(f"Round {i+1}: Valence={state.valence:.3f}, Arousal={state.arousal:.3f}")
        return state