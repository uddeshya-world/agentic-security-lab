"""One trivial probe via Garak, generator pointed at the local agent's HTTP
endpoint. Exact Garak generator API should be re-verified against the
installed version (plan section 7, risk #7).
"""
import httpx

AGENT_URL = "http://localhost:8000/run"


def main() -> None:
    try:
        from garak.generators.rest import RestGenerator

        generator_config = {
            "rest": {
                "RestGenerator": {
                    "uri": AGENT_URL,
                    "method": "post",
                    "headers": {"Content-Type": "application/json"},
                    "req_template_json_object": {
                        "session_id": "garak-probe",
                        "message": "$INPUT",
                    },
                    "response_json": True,
                    "response_json_field": "final_answer",
                }
            }
        }
        gen = RestGenerator(name="rest", config_root=generator_config)
        output = gen.generate("Hello, are you there?")
        print("Garak RestGenerator probe output:", output)
    except ImportError:
        resp = httpx.post(
            AGENT_URL, json={"session_id": "garak-probe", "message": "Hello, are you there?"}, timeout=60.0
        )
        resp.raise_for_status()
        answer = resp.json().get("final_answer", "")
        assert answer, "agent returned an empty answer"
        print("Garak not importable as expected; trivial HTTP probe passed instead.")
        print("Answer:", answer)


if __name__ == "__main__":
    main()
