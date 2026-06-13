# ADR 0005 — Reinforcement learning for traffic-signal control

Date: 2026-06-13
Status: Accepted

## Context

Traffic-signal timing is the platform's main _actuator_ — the one place it can
change the world rather than just observe it. We need a controller that adapts
green time to live demand across a cluster of intersections.

The options form a ladder:

- **Fixed-time** plans are simple and predictable but ignore demand entirely.
- **Webster's method** sets demand-proportional splits but is still a _fixed_
  plan that degrades as conditions drift and breaks under oversaturation.
- **Max-pressure** is adaptive and provably stabilizes queues, but it is
  greedy and myopic — it optimizes each intersection's instantaneous pressure,
  not coordinated, forward-looking flow across the cluster.
- **Reinforcement learning** can, in principle, learn coordinated,
  anticipatory policies that account for downstream effects and the rush-hour
  curve — at the cost of training, reward design, and a sim-to-real gap.

## Decision

Use RL (Stable-Baselines3 **DQN** as the discrete-control baseline and **PPO**
as the policy-gradient advanced agent) trained against a custom **Gymnasium**
environment, and **benchmark it honestly against all three classical
controllers** (fixed-time, Webster, max-pressure). The environment's
observation/action/reward contract is fixed so a policy is portable across
backends:

- **Observation:** per-approach normalized queues + current-phase one-hot +
  time-in-phase, concatenated across the cluster.
- **Action:** `MultiDiscrete` — one phase per intersection (joint control).
- **Reward:** negative change in total delay each step (dense, aligned with
  the real objective) minus a small switching penalty to prevent flicker.

The default simulator backend is a fast, deterministic pure-Python queue model
so the entire stack trains and unit-tests without native dependencies; a
**SUMO/`traci`** backend (`SumoTrafficEnv`) is documented for when the SUMO
binary is available, keeping the same contract so policies transfer.

## Consequences

- **Positive:** the comparison is the deliverable — we report throughput and
  waiting time for every controller, so the RL agent's value (or lack of it on
  a given scenario) is measured, not asserted. This is far more credible in an
  interview than "my agent beat everything."
- **Positive:** DQN-vs-PPO and RL-vs-classical are concrete talking points
  (off-policy value learning vs on-policy policy gradients; learned vs
  hand-designed control).
- **Negative / honest:** on simple, independent intersections **max-pressure
  is a very strong baseline** and hard to beat; RL's advantage grows with
  coordination complexity (correlated demand, offsets/green-waves) and training
  budget. We document where RL wins and where it doesn't.
- **Negative:** sim-to-real is real — a policy trained on the toy model would
  need SUMO (then field) validation before touching a street. The serving
  endpoint therefore defaults to the safe, tuning-free max-pressure + Webster
  recommendation and only prefers a trained policy when one is present.
- **Risk accepted:** reward shaping can induce degenerate behavior (e.g.
  flicker); the switching penalty and the dense delay signal mitigate it, and
  the evaluation harness would catch a regression.
