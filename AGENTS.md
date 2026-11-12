# webots-linetrace — agent self-improvement loop

Goal: an agent improves the Webots line-trace controller by itself: run → measure → edit → keep or revert.
Setup and commands: `README.md`.

## Loop (one iteration)
1. Read `runs/results.jsonl` (history) and the controller named in `project.json` → `controller`.
2. Make ONE change with a stated hypothesis.
3. `bin/run-trial --note "<hypothesis>"` (about 5 s). It prints the score and appends to `runs/results.jsonl`.
4. Score higher than the best committed score → `git commit` the controller and results (message: score before → after, why).
   Not higher → `git checkout -- <controller>`; still commit `runs/results.jsonl` so failed ideas are not retried.
5. Repeat. Stop and report when 10 consecutive iterations bring no improvement, or the user says stop.

## Rules
- Score = `result.score` in the JSON (higher is better). `status != "ok"` counts as a failure, never as a score.
- Only edit the path in `project.json` → `controller`. Paths in `frozen` (evaluator, world, textures) define the task;
  `bin/run-trial` refuses to run if they differ from HEAD. Changing the task is the user's decision.
- The simulation is deterministic: the same code gives the same score, so do not re-run to "confirm".
- Do not pass `--no-rendering` to Webots (segfaults on Apple Silicon, R2025a).
- An empty `runs/results.jsonl` means no baseline yet: run one trial with `--note baseline` before changing anything.
- Do not push unless asked. Do not leave `bin/stream` running after the user is done watching.
