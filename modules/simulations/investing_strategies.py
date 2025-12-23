import numpy as np
from scipy.stats import truncnorm, lognorm
import simpy
from joblib import Parallel, delayed
import multiprocessing
from tqdm import tqdm
import time
import os
import shutil
import matplotlib.pyplot as plt
import matplotlib
from typing import List
import logging
import random

OUTPUT_DIR = "Outputs/investing_strategies"
INITIAL_MONEY = 15.0
INVESTMENT_PER_ROUND = 10.0
RANDOM_SEED = 42

matplotlib.use("Agg")


def set_global_seed(seed: int):
    np.random.seed(seed)
    random.seed(seed)


class Investor:
    def __init__(
        self,
        margin: float,
        initial_money: float,
    ) -> None:
        self.margin = max(1.01, margin)  # Ensure margin > 1
        self.money: float = initial_money
        self.previous_money: float = initial_money
        self.active: bool = True

        """
        self.variance: float = np.exp(
            self.margin - 1
        )  # Variance increases rapidly with margin
        # Quadratic scaling for standard deviation
        k = 75.0  # You can tune this value
        p = 2  # Quadratic
        sigma = k * (self.margin - 1) ** p

        # Truncated normal: mean=self.margin, std=sigma, bounded by 0.0 to inf
        lower, upper = 0.0, np.inf
        mu = self.margin
        self.rv = truncnorm(
            a=(lower - mu) / sigma, b=(upper - mu) / sigma, loc=mu, scale=sigma
        )

        self.variance = sigma**2
        """
        # Lognormal parameters: mean and standard deviation of the underlying normal
        # Set sigma to control skewness; higher sigma = more right-skewed
        sigma = 0.01 + 10.0 * (self.margin - 1.01)

        # Calculate mu so that mean = margin
        mu = np.log(self.margin) - 0.5 * sigma**2

        self.rv = lognorm(s=sigma, scale=np.exp(mu))
        self.variance = (np.exp(sigma**2) - 1) * np.exp(2 * mu + sigma**2)

    def get_return(self, investment: float) -> float:
        multiplier = self.rv.rvs()  # Materializes a single sample from the distribution
        return investment * multiplier

    def __str__(self) -> str:
        return f"Investor(margin={self.margin}, money={round(self.money, 1)}, change={round(self.money - self.previous_money, 1)}, active={self.active})"

    def plot_pdf(self, filename: str) -> None:
        num_points = 1000
        mu = self.margin  # Define mu for labeling
        x = np.linspace(0, self.margin + 4 * np.sqrt(self.variance), num_points)
        pdf = self.rv.pdf(x)

        plt.figure(figsize=(8, 4))
        plt.plot(
            x, pdf, label=f"PDF (margin=${mu}$, variance=${round(self.variance, 2)}$)"
        )
        plt.fill_between(
            x, 0, pdf, where=(x < 1.0), color="red", alpha=0.3, label="Loss (<$1.0$)"
        )
        plt.fill_between(
            x,
            0,
            pdf,
            where=(x >= 1.0),
            color="green",
            alpha=0.3,
            label=r"Profit ($\geq 1.0$)",
        )
        plt.title(f"Investor PDF (margin=${mu}$)")
        plt.xlabel("Return Multiplier")
        plt.ylabel("Probability Density")
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        plt.close()


def investing_simulation(
    env: simpy.Environment,
    investors: List[Investor],
    investment_per_round: float = INVESTMENT_PER_ROUND,
    wait_time: float = 0.5,
) -> simpy.events.Process:
    """
    The while loop represents each timestep in the simulation, with up to 20 timesteps.
    At each timestep, each active investor invests a fixed amount of money, and receives a random return based on their
        personal investment parameters.
    """
    while any(investor.active for investor in investors):
        for investor in investors:
            if investor.active and investor.money >= investment_per_round:
                investor.previous_money = investor.money
                investment_return = investor.get_return(investment_per_round)
                investor.money += investment_return - investment_per_round
                if investor.money < investment_per_round:
                    investor.active = False
        if wait_time > 0:
            time.sleep(wait_time)
        yield env.timeout(1)  # Next timestep


def single_simulation(margins: List[float]) -> None:
    investors = [Investor(margin, initial_money=INITIAL_MONEY) for margin in margins]
    env = simpy.Environment()
    env.process(
        investing_simulation(
            env, investors, investment_per_round=INVESTMENT_PER_ROUND, wait_time=0.01
        )
    )
    env.run(until=20)  # Run for 20 timesteps
    logging.info("Single simulation results:")
    for i, investor in enumerate(investors):
        logging.info(f"Final State Investor {i}: {investor}")
        investor.plot_pdf(
            filename=os.path.join(OUTPUT_DIR, f"investor_{investor.margin:.2f}.png")
        )


def parallel_simulation(margin: float, initial_money: float, seed: int = None) -> tuple:
    if seed is not None:
        set_global_seed(seed)
    investor = Investor(margin, initial_money=initial_money)
    env = simpy.Environment()
    env.process(
        investing_simulation(
            env, [investor], investment_per_round=INVESTMENT_PER_ROUND, wait_time=0.0
        )
    )
    env.run(until=20)
    return investor.money, investor.active


def monte_carlo_simulation(margins: List[float], runs: int = 1000) -> None:
    n_jobs = max(1, multiprocessing.cpu_count() - 1)
    logging.info(f"Running Monte Carlo simulations using {n_jobs} parallel jobs...")
    for margin in margins:
        # tqdm for progress visualization
        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(parallel_simulation)(
                margin, initial_money=INITIAL_MONEY, seed=RANDOM_SEED + _
            )
            for _ in tqdm(range(runs), desc=f"Margin ${margin}$")
        )
        final_money = np.mean([money for money, _ in results])
        final_active = np.mean([active for _, active in results])
        logging.info(
            f"Margin ${margin}$: Expected final money = ${final_money:.2f}$, Expected active ratio = ${final_active:.2f}$"
        )


def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler(),  # Output to console
                logging.FileHandler(
                    f"{OUTPUT_DIR}/simulation_log.txt"
                ),  # Output to file as well
            ],
        )
    set_global_seed(RANDOM_SEED)
    margins = [round(margin, 2) for margin in np.arange(1.01, 1.21, 0.01)]
    single_simulation(margins)
    monte_carlo_simulation(margins, runs=10000)


if __name__ == "__main__":
    main()
