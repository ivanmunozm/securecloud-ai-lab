#!/usr/bin/env python3
import sys
import json
import yaml
from pathlib import Path
from auditor_client import TerraformAuditor


def load_config() -> dict:
    config_path = Path(__file__).parent / "threshold_config.yaml"
    return yaml.safe_load(config_path.read_text())


def should_block(result: dict, environment: str, config: dict) -> bool:
    if result.get("block_merge", True):
        return True
    env_config = config.get("environments", {}).get(environment, {})
    block_severities = env_config.get(
        "block_on_severities",
        config["gatekeeper"]["block_on_severities"]
    )
    for finding in result.get("findings", []):
        if finding.get("severity") in block_severities:
            return True
    return False


def print_report(result: dict) -> None:
    risk = result.get("overall_risk", "UNKNOWN")
    findings = result.get("findings", [])
    meta = result.get("_meta", {})

    print(f"\n{'═'*55}")
    print(f"  SecureCloud-AI Security Audit")
    print(f"  Risk: {risk} | Findings: {len(findings)}")
    if meta.get("input_tokens"):
        tokens_in = meta.get('input_tokens', 0)
        tokens_out = meta.get('output_tokens', 0)
        cache = meta.get('cache_read_tokens', 0)
        cost = (tokens_in * 3 + tokens_out * 15) / 1_000_000
        print(f"  Tokens: {tokens_in} in / {tokens_out} out / {cache} cached")
        print(f"  Costo estimado: ${cost:.5f}")
    print(f"{'─'*55}")

    if result.get("summary"):
        print(f"  {result['summary']}")
        print(f"{'─'*55}")

    severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "⚪"}
    for f in findings:
        icon = severity_icon.get(f.get("severity", ""), "•")
        print(f"\n  {icon} [{f.get('severity')}] {f.get('resource')}")
        if f.get("cis_control"):
            print(f"     CIS: {f.get('cis_control')}")
        print(f"     Issue: {f.get('description')}")
        print(f"     Fix:   {f.get('remediation')}")

    print(f"\n{'═'*55}\n")


def main():
    if len(sys.argv) < 2:
        print("Uso: python gatekeeper.py <path/to/tfplan.json> [environment]")
        sys.exit(1)

    plan_path = sys.argv[1]
    environment = sys.argv[2] if len(sys.argv) > 2 else "lab"
    config = load_config()

    print(f"[gatekeeper] Auditando: {plan_path} (env: {environment})")

    auditor = TerraformAuditor()
    result = auditor.audit(plan_path, environment)

    with open("audit_report.json", "w") as f:
        json.dump(result, f, indent=2)

    print_report(result)

    blocked = should_block(result, environment, config)

    if blocked:
        print("❌ MERGE BLOQUEADO — resuelve los hallazgos antes de continuar.")
        sys.exit(1)
    else:
        print("✅ APROBADO — sin hallazgos bloqueantes.")
        sys.exit(0)


if __name__ == "__main__":
    main()