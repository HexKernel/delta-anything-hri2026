# AG-01 — Proposed agentic architecture (draft)

User speech → speech-to-text → LLM task reasoning → validated tool dispatcher → deterministic guidance controller → Delta skin cues → voluntary human motion → tracking feedback.

The agent handles intent, clarification, target selection and high-level task state. The controller handles spatial transforms, cue trajectories, kinematics, contact force, workspace and independent safety. Never pass raw motor commands through the LLM.

| Tool | Arguments | Behavior |
|---|---|---|
| guide_direction | direction enum, user/skin frame | locally enabled mock request |
| guide_to_target | trusted target ID | rejects without tracking |
| get_guidance_status | none | reports state |
| stop_guidance | none | clears request and disarms mock |

Eight planar directions are currently defined. User and skin frame names are semantic placeholders, not a validated mapping. Signed depth encoding is unresolved. Acknowledge requests separately from actual target completion or grasp.

## Interface dependencies

Perception provides timestamped hand, target and orientation observations with frame IDs, units and validity; control owners provide calibrated transformations, cue rendering, kinematics, validated limits and safe disengagement. The agent owner provides speech, orchestration, tool adapter and status integration. Simulation may proceed independently. Hardware owners must approve the physical interface.

A real controller must manage session IDs, deadlines, sequence numbers, observed state, stale data rejection, emergency stop, watchdog, safe retraction and fault reporting independently of the LLM. Motion requests require explicit user consent; model prompting alone is not an interlock.

## Task status

AG-01 draft pending review; AG-03 bounded tool loop and optional local transport; AG-04 mock backend; AG-08 software safeguards only; AG-02 typed input; AG-05–07 require perception and frame mapping; AG-09 hardware integration blocked until interface and safety validation; AG-10–12 demonstrations, evaluation and documentation remain in progress.

No novelty or human performance claim is established.
