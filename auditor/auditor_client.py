import os
import json
import jsonschema
from pathlib import Path
import anthropic
from anonymizer import TerraformPlanAnonymizer


class TerraformAuditor:

    MODEL = "claude-sonnet-4-5"
    MAX_TOKENS = 1500

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no está definida en el entorno")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.anonymizer = TerraformPlanAnonymizer()

        base = Path(__file__).parent
        self.system_prompt = (base / "system_prompt.txt").read_text()
        self.schema = json.loads((base / "audit_schema.json").read_text())

    def audit(self, plan_path: str, environment: str = "lab") -> dict:
        with open(plan_path) as f:
            raw_plan = json.load(f)

        anon_plan, mapping = self.anonymizer.anonymize(raw_plan)
        delta = self.anonymizer.extract_risk_delta(anon_plan)

        with open("anonymization_mapping.json", "w") as f:
            json.dump(mapping, f, indent=2)

        print(f"[auditor] Cambios a auditar: {delta['change_summary']}")
        print(f"[auditor] Valores anonimizados: {len(mapping)}")

        user_msg = f"""
Environment: {environment}

Terraform plan delta (anonymized — REDACTED values are expected):

{json.dumps(delta, indent=2)}

Audit this plan. Respond only with JSON.
"""

        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=[{
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{"role": "user", "content": user_msg}],
                timeout=45,
            )

            raw_output = response.content[0].text.strip()

            if raw_output.startswith("```"):
                raw_output = raw_output.split("```")[1]
                if raw_output.startswith("json"):
                    raw_output = raw_output[4:]

            result = json.loads(raw_output)
            jsonschema.validate(result, self.schema)

            result["_meta"] = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
                "model": self.MODEL,
                "environment": environment,
                "changes_analyzed": delta["change_summary"],
            }

            return result

        except (json.JSONDecodeError, jsonschema.ValidationError) as e:
            return {
                "overall_risk": "ERROR",
                "block_merge": True,
                "summary": f"Auditor response validation failed: {str(e)[:200]}",
                "findings": [],
                "_meta": {"error": str(e)}
            }
        except Exception as e:
            return {
                "overall_risk": "ERROR",
                "block_merge": True,
                "summary": f"Auditor unavailable: {str(e)[:200]}",
                "findings": [],
                "_meta": {"error": str(e)}
            }