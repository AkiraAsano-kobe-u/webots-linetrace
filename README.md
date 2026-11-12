# webots-linetrace

A small harness that lets a coding agent improve a [Webots](https://cyberbotics.com) line-following controller by
itself: run a trial → read the score → edit the controller → keep the change if the score went up, revert if not.

It ships with a working task (`examples/smoke/`: an e-puck on an oval track, score = laps completed in 60 simulated
seconds), so a fork runs as is.

## Quick start

Requirements: Webots **R2025a**, Python 3, git. No Python packages.

```sh
git clone https://github.com/<you>/webots-linetrace && cd webots-linetrace
bin/run-trial --note baseline
```

The first run downloads the robot models referenced by the world, so it needs internet access and takes longer.
After that a trial takes about 5 seconds and prints one JSON line:

```json
{"status": "ok", "result": {"score": 1.2613, "laps": 1.2613, "mean_abs_error_m": 0.00096, "off_line_s": 0.0, "end": "time_up"}, ...}
```

Then start a coding agent (Claude Code, Codex, Hermes, …) in the repository and tell it to follow `AGENTS.md`.
The loop rules, what the agent may edit, and when it stops are all in that file.

| Platform | State |
|---|---|
| macOS (Apple Silicon), Webots R2025a from the official dmg | verified by hand |
| Linux, `cyberbotics/webots:R2025a-ubuntu22.04` under `xvfb-run` | verified by CI (`.github/workflows/trial.yml`) |
| Windows | not tested |

Webots is found in this order: `$WEBOTS_BIN`, `/Applications/Webots.app`, `webots` on `PATH`, `$WEBOTS_HOME/webots`.
On a machine without a display run it as `xvfb-run -a bin/run-trial`.
Scores are deterministic on one machine; they can differ between platforms, so take your own baseline.

## Commands

| Command | What |
|---|---|
| `bin/run-trial [--note TEXT]` | one trial in fast mode; the result is printed and appended to `runs/results.jsonl` |
| `bin/stream start\|stop\|status` | live view of the current controller in a browser (realtime, Webots w3d stream) |

`bin/stream start` prints a local URL (`http://127.0.0.1:1236/index.html`). Open it and press Connect.
To watch from another machine, expose that port privately, for example with Tailscale:
`tailscale serve --bg --http=1234 http://127.0.0.1:1236`, then open `http://<host>.<tailnet>.ts.net:1234/index.html`
and set "Connect to" to `ws://<host>.<tailnet>.ts.net:1234`. Webots listens on 1236 and not 1234 on purpose:
tailscale serve holds `<tailnet ip>:1234`, so Webots could not bind it and would silently move to another port.

## Using your own track or robot

`project.json` defines the task:

| Key | Meaning |
|---|---|
| `world` | the `.wbt` file to run |
| `controller` | the only path the agent may edit |
| `frozen` | paths that define the task (evaluator, world, textures); `bin/run-trial` refuses to run if they differ from `HEAD` |
| `sim_seconds`, `wall_timeout_s` | simulated length of a trial, and the real-time limit after which it is killed |

The world needs a supervisor robot whose controller measures the run, writes a JSON object with a `score` field
(higher is better) to the path in `$TRIAL_RESULT`, and quits Webots. `$TRIAL_SIM_SECONDS` carries the trial length.
`examples/smoke/controllers/evaluator/evaluator.py` is a 60-line example; `examples/smoke/tools/make_track.py`
generates the floor texture.

## macOS notes

- Install Webots from the official dmg into `/Applications` (the Homebrew cask is disabled).
- Do not pass `--no-rendering`: it segfaults R2025a on Apple Silicon. The scripts use `--minimize` instead.
- After a killed run macOS can show a modal "reopen windows?" alert that blocks every later start. The scripts delete
  the saved window state before each start; `defaults write com.cyberbotics.webots ApplePersistenceIgnoreState -bool YES`
  turns the alert off for good.

## License

MIT. Webots itself is Apache-2.0 and is not included.
