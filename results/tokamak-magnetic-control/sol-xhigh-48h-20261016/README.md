# Tokamak: GPT-6.1 Sol, xhigh, 48 hours

**C027 scored 0.636364: 21 successful episodes out of 33 non-void episodes.**
The original sealed evaluator attempted 35 episodes and excluded two simulator
timeouts. Policy computation was 0.1834 ms, below the 0.5 ms gate.

The [published baseline](https://github.com/sunnweiwei/science-speedrun/blob/eedb84f7c27e69194612a9b8033a6e5ebcba0507/tasks/tokamak-magnetic-control/environment/baseline/shape_vc/RESULTS.md)
scored 17/35 (0.485714) on the same suite. The observed difference is +15.06
percentage points; the baseline was not rerun alongside C027, and void counts
differ. This single comparison does not establish statistical significance.


| Setting                      | Recorded value                                              |
| ---------------------------- | ----------------------------------------------------------- |
| Agent                        | `gpt-6.1-sol`, `xhigh`, Standard; Codex CLI 0.163.0         |
| Research time                | 172,800 seconds (48 hours)                                  |
| Requested research resources | 1 H100, 64 CPUs, 128 GiB RAM                                |
| Sealed evaluation            | 0 GPUs, 40 CPUs, 48 GiB requested; approximately 66 minutes |


- [evaluation/](evaluation/): verifier outputs
- [submission/](submission/): exact evaluated controller, weights and its
original development documentation.
- [logs/](logs/): original Codex session, trajectory, preflight, stderr and
verifier logs. Plain files, Git-ignored; credential stores are excluded.

Task source commit: `eedb84f7c27e69194612a9b8033a6e5ebcba0507`.

