"""One trivial passing probe against the local agent endpoint, to prove
DeepTeam wiring -- not real coverage. Exact DeepTeam API surface should be
re-verified against the installed version (plan section 7, risk #7); this
uses a plain callback model wrapping the agent's HTTP endpoint, which is the
most version-stable integration shape.
"""
import httpx

AGENT_URL = "http://localhost:8000/run"


def model_callback(prompt: str) -> str:
    resp = httpx.post(
        AGENT_URL, json={"session_id": "deepteam-probe", "message": prompt}, timeout=60.0
    )
    resp.raise_for_status()
    return resp.json().get("final_answer", "")


def main() -> None:
    try:
        from deepteam import red_team
        from deepteam.vulnerabilities import Bias

        results = red_team(model_callback=model_callback, vulnerabilities=[Bias()])
        print("DeepTeam probe ran:", results)
    except ImportError:
        # Fallback trivial probe if deepteam's API surface differs from what
        # was assumed at plan time -- still proves the agent endpoint itself
        # is reachable and answers, which is the wiring goal for Checkpoint 6.
        answer = model_callback("Hello, are you there?")
        assert answer, "agent returned an empty answer"
        print("DeepTeam not importable as expected; trivial HTTP probe passed instead.")
        print("Answer:", answer)


if __name__ == "__main__":
    main()
