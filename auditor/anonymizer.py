import re
import json
import hashlib


class TerraformPlanAnonymizer:
    """
    Reemplaza datos sensibles de un terraform plan JSON
    por placeholders antes de enviarlo al LLM.
    Mismo valor → mismo placeholder (determinista).
    """

    PATTERNS = [
        (r'\b\d{12}\b', 'ACCT'),
        (r'arn:aws[-a-z]*:[a-z0-9\-]+:[\w\-]*:\d*:[^\s"\\,]+', 'ARN'),
        (r'\b(10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)\b', 'IP_PRIV'),
        (r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b', 'IP_PUB'),
        (r'(?i)(?:"(?:password|secret|token|key|passwd|pwd)"\s*:\s*)"([^"]{6,})"', 'SECRET'),
    ]

    def __init__(self):
        self._map: dict[str, str] = {}

    def _placeholder(self, base: str, value: str) -> str:
        h = hashlib.md5(value.encode()).hexdigest()[:6].upper()
        return f"{base}_REDACTED_{h}"

    def _replace(self, base: str, match: re.Match) -> str:
        original = match.group(0)
        if original not in self._map:
            self._map[original] = self._placeholder(base, original)
        return self._map[original]

    def anonymize(self, plan: dict) -> tuple[dict, dict]:
        plan_str = json.dumps(plan)
        for regex, base in self.PATTERNS:
            plan_str = re.sub(regex, lambda m, b=base: self._replace(b, m), plan_str)
        return json.loads(plan_str), dict(self._map)

    def extract_risk_delta(self, plan: dict) -> dict:
        """
        Extrae solo los recursos que cambiarán.
        Reduce tokens hasta 80% vs enviar el plan completo.
        """
        changes = plan.get('resource_changes', [])
        real_changes = [
            rc for rc in changes
            if set(rc.get('change', {}).get('actions', [])) != {'no-op'}
        ]
        return {
            'terraform_version': plan.get('terraform_version', 'unknown'),
            'resource_changes': real_changes,
            'change_summary': {
                'total':   len(real_changes),
                'create':  sum(1 for r in real_changes if 'create' in r.get('change', {}).get('actions', [])),
                'update':  sum(1 for r in real_changes if 'update' in r.get('change', {}).get('actions', [])),
                'destroy': sum(1 for r in real_changes if 'delete' in r.get('change', {}).get('actions', [])),
            }
        }
