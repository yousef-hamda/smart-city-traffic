# RL Signal Optimizer

Reinforcement-learning traffic-signal control, trained on a custom Gymnasium
environment and **benchmarked honestly against classical controllers**. Serves
signal-timing recommendations over REST.

## Environment (`env.py`)

A `gymnasium.Env` over a cluster of signalised intersections:

- **Observation** — per approach: normalized queue length; per intersection:
  current-phase one-hot + time-in-phase. Concatenated across the cluster.
- **Action** — `MultiDiscrete`, one phase per intersection (joint control).
- **Reward** — negative change in total delay each step (dense, aligned with
  the real objective) minus a small switching penalty to discourage flicker.

The default backend is a fast, deterministic pure-Python queue simulator
(`intersection.py`) so everything trains and tests with no native deps. A
SUMO/`traci` backend (`SumoTrafficEnv`) is documented for when the SUMO binary
is available — same observation/action/reward contract, so policies transfer.

## Controllers

| Controller   | Type                | Notes                                                      |
| ------------ | ------------------- | ---------------------------------------------------------- |
| Fixed-time   | baseline            | round-robin, demand-blind                                  |
| Webster      | baseline            | demand-proportional split, capped cycle                    |
| Max-pressure | baseline (adaptive) | serves the busiest phase; provably stable                  |
| **DQN**      | RL                  | off-policy value learning (Discrete via a flatten wrapper) |
| **PPO**      | RL                  | on-policy policy gradient (native MultiDiscrete)           |

See [`docs/rl.md`](../../docs/rl.md) for the full comparison table and an honest
discussion of where RL wins and where max-pressure is hard to beat.

## Usage

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,train]"          # train extra pulls SB3/torch

# train + benchmark vs all baselines
python -m rl_optimizer.train --algo ppo --timesteps 150000 --compare
python -m rl_optimizer.train --algo dqn --timesteps 150000 --compare

# serve recommendations
uvicorn rl_optimizer.main:app --port 8084
```

`POST /recommend/signal-timing` takes the current per-approach queues and
returns a recommended phase + green seconds per intersection. Offline it uses
the tuning-free max-pressure + Webster combination (a safe, strong default);
a trained RL policy is preferred when present.

## Tests & quality

```bash
pytest -q                 # fast suite (env, baselines, recommend, API)
pytest -q -m slow         # adds short DQN/PPO training smoke tests
ruff check src tests && mypy src
```

`OMP_NUM_THREADS=1` is set in the training path to avoid torch thread
oversubscription on many-core CPUs (which otherwise makes tiny trainings crawl).
