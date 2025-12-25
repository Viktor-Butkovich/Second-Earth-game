import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.callbacks import BaseCallback
from collections import Counter
import itertools
import numpy as np
import multiprocessing
import os
import matplotlib.pyplot as plt

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class RewardTrackingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_counts = []
        self.current_rewards = 0
        self.episode_num = 0

    def _on_step(self) -> bool:
        # Check if episode is done
        dones = self.locals.get("dones")
        rewards = self.locals.get("rewards")
        if rewards is not None:
            self.current_rewards += (
                rewards[0] if isinstance(rewards, (list, np.ndarray)) else rewards
            )
        if dones is not None and dones[0]:
            self.episode_rewards.append(self.current_rewards)
            self.episode_counts.append(self.episode_num)
            self.current_rewards = 0
            self.episode_num += 1
        return True


def plot_rewards(rewards, filename):
    plt.figure(figsize=(10, 5))
    window = 50
    if len(rewards) > window:
        moving_avg = np.convolve(rewards, np.ones(window) / window, mode="valid")
        plt.plot(
            range(window - 1, len(rewards)),
            moving_avg,
            label=f"{window}-episode moving avg",
        )
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title("Average Reward per Episode")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


class DiceGameEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        super().__init__()
        # Observation: [phase, possible points, dice remaining, score1..score5]
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(8,), dtype=np.float32
        )
        # Actions: 0=Cash in, 1=Roll, 2-6=Score 1-5 dice
        self.action_space = spaces.Discrete(7)

        self.phase = 0
        self.possible_points = 0
        self.dice_remaining = 6
        self.scoring_values = np.zeros(5)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.phase = 0
        self.possible_points = 0
        self.dice_remaining = 6
        self.scoring_values = np.zeros(5)
        self.last_roll = None
        self.last_action_desc = "Game reset."
        return self._get_obs(), {"action_mask": self._get_action_mask()}

    def step(self, action):
        reward = 0
        terminated = False
        truncated = False
        self.last_action_desc = ""

        if self.phase == 0:  # State 1
            if action == 0:  # Cash in
                reward = self.possible_points  # raw reward
                terminated = True
                self.last_action_desc = f"\tCash in: Collected {reward} points."
                self.possible_points = 0
                self.dice_remaining = 6
                self.phase = 0

            elif action == 1:  # Roll
                dice = np.random.randint(1, 7, size=self.dice_remaining)
                self.last_roll = dice.copy()
                self.scoring_values = scoring_values_for_roll(dice)  # raw scores
                self.last_action_desc = (
                    f"Rolled {self.dice_remaining} dice: {dice.tolist()}."
                )

                # Special cases
                if np.all(self.scoring_values == 0):
                    terminated = True
                    self.last_action_desc += (
                        " No scoring dice, lost all possible points."
                    )
                    self.phase = 0
                    self.possible_points = 0
                    self.dice_remaining = 6
                elif all_dice_are_scoring(dice):
                    points = score_dice(dice)
                    self.last_action_desc += f" All dice scored! Gained possible {points} points, rolling all 6 dice again."
                    self.possible_points += points
                    self.dice_remaining = 6
                    self.phase = 0
                else:
                    self.last_action_desc += " Choose how many dice to score."
                    self.phase = 1

        else:  # State 2
            if 2 <= action <= 6:
                k = action - 1
                points = self.scoring_values[k - 1]
                self.possible_points += points
                self.last_action_desc = (
                    f"\tSpent {k} dice for {points} possible points. "
                    f"\t{max(1, self.dice_remaining - k)} dice remain."
                )
                self.dice_remaining = max(1, self.dice_remaining - k)
                self.phase = 0
            else:
                reward = -1000  # Penalty for attempting invalid action during training
                #   While invalid actions are masked and replaced by random valid actions during evaluation, it helps
                #   training to discourage attempting them
                terminated = True
                # raise ValueError(f"Invalid action {action} in scoring phase.")

        info = {"action_mask": self._get_action_mask()}
        return self._get_obs(), reward, terminated, truncated, info

    def _get_obs(self):
        return np.array(
            [
                self.phase,
                self.possible_points / 4000.0,  # normalized
                self.dice_remaining / 6.0,
                *list(self.scoring_values / 4000.0),  # normalized
            ],
            dtype=np.float32,
        )

    def _get_action_mask(self):
        mask = np.zeros(7, dtype=np.int32)
        if self.phase == 0:
            if self.possible_points > 0 and self.dice_remaining <= 5:
                mask[0] = (
                    1  # Cash in only allowed if points available and at least 1 die scored
                )
                #   Even though cashing in with 6 dice remaining is allowed, and very occasionally optimal if there are many possible points, it is a rare enough event to be worth deciding deterministically
            mask[1] = 1  # Roll
        else:
            dice = self.last_roll if self.last_roll is not None else []
            for k in range(1, 6):
                if len(dice) >= k:
                    # Only allow if there is a subset of k dice that achieves the best score for k
                    best = 0
                    for subset in itertools.combinations(dice, k):
                        score = score_dice(subset)
                        if score == self.scoring_values[k - 1] and score > 0:
                            best = 1
                            break
                    if best:
                        mask[1 + k] = 1  # actions 2-6
        return mask

    def render(self, mode="human", verbose=True):
        if verbose:
            print(
                f"Phase={self.phase}, Points={self.possible_points}, Dice={self.dice_remaining}, "
                f"Scores={self.scoring_values} (normalized: {self.scoring_values/4000.0})"
            )
        if self.last_action_desc:
            print(self.last_action_desc)


import gymnasium as gym
import numpy as np


class MaskedEnv(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)

    def step(self, action):
        # Get current mask
        mask = self.env._get_action_mask()

        if mask is not None and mask[action] == 0:
            # If chosen action is invalid, resample a valid one
            valid_actions = np.where(mask == 1)[0]
            if len(valid_actions) > 0:
                action = np.random.choice(valid_actions)
                # obs, reward, terminated, truncated, info = self.env.step(action)
            else:
                raise ValueError("No valid actions available to resample.")

        obs, reward, terminated, truncated, info = self.env.step(action)

        return obs, reward, terminated, truncated, info

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        return obs, info

    def render(self, *args, **kwargs):
        return self.env.render(*args, **kwargs)


def all_dice_are_scoring(dice):
    """Return True if every die in the roll is used in scoring."""
    full_score = score_dice(dice)
    n = len(dice)
    # If removing any die reduces the score, then all dice are needed
    for i in range(n):
        subset = np.delete(dice, i)
        if score_dice(subset) == full_score:
            return False
    return full_score > 0


def score_dice(dice):
    counts = Counter(dice)
    best = 0

    # Recursive search
    def dfs(counts, total):
        nonlocal best
        best = max(best, total)

        # Singles
        if counts[1] > 0:
            new_counts = counts.copy()
            new_counts[1] -= 1
            dfs(new_counts, total + 100)
        if counts[5] > 0:
            new_counts = counts.copy()
            new_counts[5] -= 1
            dfs(new_counts, total + 50)

        # Straights
        if all(counts[i] > 0 for i in range(1, 6)):
            new_counts = counts.copy()
            for i in range(1, 6):
                new_counts[i] -= 1
            dfs(new_counts, total + 500)
        if all(counts[i] > 0 for i in range(2, 7)):
            new_counts = counts.copy()
            for i in range(2, 7):
                new_counts[i] -= 1
            dfs(new_counts, total + 750)
        if all(counts[i] > 0 for i in range(1, 7)):
            new_counts = counts.copy()
            for i in range(1, 7):
                new_counts[i] -= 1
            dfs(new_counts, total + 1500)

        # Triples and extensions
        for face in range(1, 7):
            if counts[face] >= 3:
                base = 1000 if face == 1 else 100 * face
                extra = counts[face] - 3
                score = base * (2**extra)
                new_counts = counts.copy()
                new_counts[face] -= 3 + extra
                dfs(new_counts, total + score)

    dfs(counts, 0)
    return best


def scoring_values_for_roll(dice):
    """Return array of max scores for scoring 1..5 dice from the rolled set.
    Only count subsets where all dice are used for scoring (no 'dead' dice)."""
    values = []
    for k in range(1, 6):
        best = 0
        for subset in itertools.combinations(dice, k):
            score = score_dice(subset)
            # Only count if all dice in the subset are needed for the score
            if score > 0:
                # Remove each die and see if score drops
                all_needed = True
                for i in range(k):
                    reduced = list(subset[:i]) + list(subset[i + 1 :])
                    if score_dice(reduced) == score:
                        all_needed = False
                        break
                if all_needed:
                    best = max(best, score)
        values.append(best)
    return np.array(values)


def train() -> None:
    env = make_vec_env(
        lambda: MaskedEnv(DiceGameEnv()), n_envs=multiprocessing.cpu_count() - 1
    )

    # Define model
    policy_kwargs = dict(net_arch=[128, 128])
    model = PPO(
        "MlpPolicy",
        env,
        gamma=1.0,
        verbose=1,
        tensorboard_log="./ppo_dice_tensorboard/",
        policy_kwargs=policy_kwargs,
    )

    # Train
    callback = RewardTrackingCallback()
    n = 1_000_000
    model.learn(total_timesteps=n, callback=callback)

    # Save
    model.save(os.path.join(OUTPUT_DIR, "dice_game/ppo"))
    plot_rewards(
        callback.episode_rewards,
        filename=os.path.join(OUTPUT_DIR, "dice_game/rewards.png"),
    )

    # Evaluate
    obs = env.reset()
    for i in range(10):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        env.render()


def rollout_game(agent, log=True) -> tuple[str, int, int]:
    """Alternate full episodes between PPO agent and random baseline until one hits target_points."""
    env_agent = MaskedEnv(DiceGameEnv())
    env_random = MaskedEnv(DiceGameEnv())

    score_agent, score_random = 0, 0
    episode = 0
    target_points = 4000

    while score_agent < target_points and score_random < target_points:
        episode += 1
        if log:
            print(f"\n=== Round {episode} ===")
        # --- PPO agent plays one episode ---
        obs, info = env_agent.reset()
        done = False
        ep_reward = 0
        while not done:
            action, _ = agent.predict(obs)
            if log:
                env_agent.render(verbose=False)
            obs, reward, terminated, truncated, info = env_agent.step(action)
            ep_reward += reward
            done = terminated or truncated
        if log:
            env_agent.render(verbose=False)
        score_agent += ep_reward
        if log:
            print(
                f"[Round {episode}] PPO agent scored {ep_reward}, total={score_agent}"
            )
        if score_agent >= target_points:
            if log:
                print("PPO agent wins!")
            return "PPO", score_agent, score_random

        # --- Random agent plays one episode ---
        obs, info = env_random.reset()
        done = False
        ep_reward = 0
        while not done:
            mask = info["action_mask"]
            valid_actions = np.where(mask == 1)[0]
            action = np.random.choice(valid_actions)
            if log:
                env_random.render(verbose=False)
            obs, reward, terminated, truncated, info = env_random.step(action)
            ep_reward += reward
            done = terminated or truncated
        if log:
            env_random.render(verbose=False)
        score_random += ep_reward
        if log:
            print(
                f"[Round {episode}] Random agent scored {ep_reward}, total={score_random}"
            )
        if score_random >= target_points:
            if log:
                print("Random agent wins!")
            return "Random", score_agent, score_random


def main() -> None:
    env = MaskedEnv(DiceGameEnv())
    obs, info = env.reset()
    total_reward = 0
    step = 0
    while total_reward < 4000:
        step += 1
        env.render(verbose=False)
        mask = info["action_mask"]
        valid_actions = np.where(mask == 1)[0]
        action = np.random.choice(valid_actions)  # pick a valid random action
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        if terminated or truncated:
            env.render(verbose=False)
            print(f"\tTotal Reward={total_reward}\n")
            obs, info = env.reset()
    env.render(verbose=False)
    print("Starting RL training...")
    if input("Re-train RL agent? (y/n): ").lower() == "y":
        train()
    agent = PPO.load(os.path.join(OUTPUT_DIR, "dice_game/ppo"))
    if input("Single rollout game with logging? (y/n): ").lower() == "y":
        rollout_game(agent, log=True)
    total_games = 1000
    if input(f"Evaluate over {total_games} games? (y/n): ").lower() == "y":
        ppo_wins = 0
        for i in range(total_games):
            winner, _, _ = rollout_game(agent, log=False)
            if winner == "PPO":
                ppo_wins += 1
            if (i + 1) % 50 == 0:
                print(
                    f"PPO agent wins so far: {ppo_wins} out of {i + 1} games ({ppo_wins/(i+1):.2%})"
                )
        print(
            f"PPO agent won {ppo_wins} out of {total_games} games ({ppo_wins/total_games:.2%})"
        )


"""
Dice game:

State 1:
    After having some number of points available and dice remaining, the player chooses to cash in or keep rolling.
    At the start of the game, we initialize with 0 possible points and all 6 dice remaining.
    State features:
        Possible points: How many points could be cashed in if the player stops rolling
        Dice remaining: How many dice the player has left to roll: 1-6
    Actions:
        Cash in: Gain immediate reward equal to possible points, then transition to state 1 with 0 
        Roll: Roll dice equal to dice remaining, and transition to state 2 with the dice results.

State 2:
    Given some set of dice results, the player chooses how many dice to score, from 1 to 5.
    Based on the dice results, a different number of dice are valid to score.
    If 0 dice are available, automatically go to state 1 with 0 possible points and all 6 dice remaining.
    If 6 dice are available, it is always optimal to score all 6 dice and return to state 1 with the possible points and all 6 dice remaining.
        These steps are deterministic and can be handled outside of the agent when encountered.
    Upon scoring some number of dice, transition to state 1 with updated possible points and dice remaining.
    State features:
        Pre-computed values of scoring 1-5 dice
    Actions:
        Score 1-5 dice
    Rather than an action mask, we can simply give an action a value of 0 if it is not valid to score that many dice.

Cashing in is the sole means of gaining immediate reward, and we seek to maximize average reward per time step.
"""

if __name__ == "__main__":
    main()
