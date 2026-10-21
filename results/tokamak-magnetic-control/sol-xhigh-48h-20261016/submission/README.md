# Shared magnetic controller — C027

One globally fitted magnetic field/centroid reconstruction and one shared
whole-boundary/X-point/gap virtual-circuit controller serve all seven cases.
Raw magnetics and observed target descriptors produce twelve coil voltages.
Shared current PI, inductive current tracking and delayed vertical feedback
use fixed weights/normalization; integrators and missing-channel state reset.
Machine responses are conditioned on observed geometry/Ip, with no case-name
or seed dispatch to independent controllers.

The clean32 field fit reuses2,393 pooled static/dynamic frames and exact active/
passive covariance; shared gap weight8 uses1,632 local fault frames. No new
training steps in this evidence refresh. Provenance is in training.json.
NumPy plus bundled generic C99/libc/libm; no Torch/compiler/network/workspace
import or external checkpoint at inference. Conservative numeric NPZ resources
and controller settings:562,986 scalars, below1,000,000.

Completed original nonlinear development evaluations:

| Distribution | Actual successes/scored | Full horizons/attempts | Voids | Compute ms |
|---|---:|---:|---:|---:|
| Visible0–2 | 21/21 | 21/21 | 0 | 0.187422 |
| Research wider8201–3 | 14/18 | 17/21 | 3 | 0.176614 |
| Prospective wider10901–10903 reference | 16/19 | 16/21 | 2 | 0.265642 |
| Prospective wider11501–11503 reference | 9/21 | 9/21 | 0 | 0.226164 |
| Prospective wider12101–12103 reference | 17/21 | 17/21 | 0 | 0.230321 |
| Prospective wider12401–12403 reference | 11/20 | 15/21 | 1 | 0.192110 |
| Prospective wider12501–12503 reference | 18/20 | 18/21 | 1 | 0.197417 |
| Prospective wider12801–12803 reference | 9/20 | 14/21 | 1 | 0.250629 |
| Prospective wider12901–12903 reference | 14/18 | 15/21 | 3 | 0.206308 |
| Prospective wider13201–13203 reference | 11/21 | 13/21 | 0 | 0.229368 |
| Prospective wider13901–13903 reference | 16/18 | 18/21 | 3 | 0.210304 |
| Prospective wider14301–14303 reference | 13/19 | 16/21 | 2 | 0.195253 |
| Additional exposed8401–3 | 13/21 | 20/21 | 0 | 0.238088 |
| Prospective wider8501–8503 reference | 8/21 | 12/21 | 0 | 0.199819 |
| Prospective wider8601–8603 reference | 11/19 | 12/21 | 2 | 0.228895 |
| Prospective wider8701–8703 reference | 11/19 | 11/21 | 2 | 0.217446 |
| Prospective wider8801–8803 reference | 14/20 | 14/21 | 1 | 0.206546 |
| Prospective wider8901–8903 reference | 16/18 | 17/21 | 3 | 0.209227 |
| Prospective wider9001–9003 reference | 16/17 | 16/21 | 4 | 0.202974 |

Across these19 completed draws:258 actual successes,
291 full horizons and28 voids in399
attempts. Void exclusions are never credited as kept/successful episodes.

The matched C011 comparison covers only the first63 attempts:48successes and
58horizons versus43 and56, with pooled per-case nonregression. Original
publication used per-case dominance on the first42. The exposed8401 draw
alone is mixed:13successes versusC011's14, and20horizons versus19; diverted/
high-Ip holds each lose one success and vertical shift gains one. The later
draws have no matched C011 replay, so this is not a399-attempt
C011 comparison or evidence of improvement on every new plant draw.

Frozen C057 on8501 gains one success but loses earlier visible/wider cases;
its complete63-attempt comparison is40successes/47horizons versusC02743/50.
C058 ties11successes/12horizons on8601, but loses one old-wider P4 success
and horizon while gaining a kept sequence. Its complete63-attempt comparison
is45successes/50horizons versusC02746/50, so it fails the fixed rule.
C060's completed visible17successes/17horizons loses four episodes to voids,
so it cannot replace C027 under the fixed rule. Its fresh8701 result is6
successes/7horizons versusC02711/11. C063's complete63-attempt
comparison is47successes/51horizons versusC02749/52; it also fails
the fixed rule. C064 completed all63attempts with49successes/54horizons/7voids
versusC02751/55/6. Its old-wider diverted-hold case loses a success:
seed8201 inner gap1.00114cm versus.999848cm; the1cm limit is unchanged.
C067's completed visible19successes/19horizons fails its20/20 launch gate,
so its old-wider suite was not run. Its completed fresh9001 comparison gains
one success and horizon (17/17/4voids versusC02716/16/4), which does not repair
the visible regression. No rejected challenger changes this checkpoint.

The8701 reference includes six original solver-timeout entries with no recent
states, final step counts or wall times. Their control attempts remain unknown;
reported totals are lower bounds. Full per-case physical metrics, original
episodes and missing-cost counts appear in validation.json.

These wider studies use pressure-constrained profiles. The separate beta9531–3
study was invalidated by five initialization failures; it has no benchmark
score. No sealed result or sealed improvement is claimed. Further all-case
robustness research continues; optimizer state/archives stay outside this package.
