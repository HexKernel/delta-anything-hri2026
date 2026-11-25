# Delta-Anything: agentic guidance foundation

Owner: HexKernel. Work packages AG-01, AG-03, AG-04, AG-08 (partial); AG-02 transcript interface. Python 3.10+, standard library. No physical device drivers.

Run from this directory:

    python -m unittest discover -s tests -v
    python -m delta_agent --model YOUR_INSTALLED_MODEL

The CLI uses typed transcripts and a user-operated OpenAI-compatible local model server. /enable arms the simulation, /stop disarms, /quit exits. No hardware movement takes place. The mock logs semantic guidance requests, not actual strokes. A live model has not been validated. The target tool rejects requests until tracking is available.

The original local foundation passed 12 scripted tests; rerun against this repository revision. Do not interpret offline tests as proof of live model reliability or hardware safety.

See docs/architecture.md for the proposed controller contract. Do not attach motors: an independently validated controller, physical enable and stop, calibration, safety limits and watchdog are required. This synchronous CLI is not a real-time controller or physical emergency stop.

Development takes place on HexKernel's fork. Upstream remains unchanged until reviewed.
