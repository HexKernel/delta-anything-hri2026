# AG-10–12: Evaluation and research plan

## Software validation
Run all tests using python -m unittest discover -s tests -v. Run python -m delta_agent.demo --benchmark for synthetic target reach. Log success, steps, path length, final error, and simulated time. Test invalid target, stale tracking, cancellation, and timeout. The synthetic ideal hand is not human evidence.

## Live agent and voice validation
Create a preregistered set of natural commands (direction, target, ambiguity, unsupported, stop) and compare expected versus actual tool selection, clarification and no-actuation decisions. Record model, temperature, prompt revision, STT model, transcript error, tool accuracy and end-to-end latency. Include a direct command parser baseline. Measure repeated trials, report uncertainty and failures. No live-model or STT results yet.

## Physical and participant stages
Obtain controller API, calibrated geometry, workspace/force/velocity bounds, independent watchdog and physical stop. Validate bench behavior before on-body use. Obtain applicable ethics approval. Compare direct Delta guidance vs agentic Delta guidance with matched information and audio/vibrotactile conditions where relevant; use counterbalanced within-subject design, prespecified primary outcome and pilot-informed sample size. Record task success, time, path deviation, workload (NASA-TLX), clarification and stop performance. Blindfolded participants do not replace blind-user validation.

## Publication
Report architecture, interface, failure modes, baseline choice, statistical method and limitations. Verify novelty against wearable skin-stretch and LLM-driven HRI literature before making priority claims. Do not report simulation results as human performance or imply physical safety.
