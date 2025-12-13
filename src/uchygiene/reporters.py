"""
Reporting functionality for hygiene check results.

Formats and outputs check results in various formats.
"""

import json
from typing import Any

from .checks import CheckResult, CheckSeverity


class ConsoleReporter:
    """Outputs hygiene check results to the console."""

    SEVERITY_SYMBOLS = {
        CheckSeverity.INFO: "ℹ",
        CheckSeverity.WARNING: "⚠",
        CheckSeverity.ERROR: "✗",
    }

    def report(self, results: list[CheckResult]) -> None:
        """
        Print check results to the console.

        Args:
            results: List of CheckResult objects to report.
        """
        if not results:
            print("\n" + "=" * 60)
            print("UNITY CATALOG HYGIENE CHECK")
            print("=" * 60)
            print("\n✓ All checks passed - no issues found!\n")
            return

        # Group by severity
        by_severity = {
            CheckSeverity.ERROR: [],
            CheckSeverity.WARNING: [],
            CheckSeverity.INFO: [],
        }
        for result in results:
            by_severity[result.severity].append(result)

        print("\n" + "=" * 60)
        print("UNITY CATALOG HYGIENE CHECK")
        print("=" * 60)

        for severity in [CheckSeverity.ERROR, CheckSeverity.WARNING, CheckSeverity.INFO]:
            items = by_severity[severity]
            if not items:
                continue

            print(f"\n{severity.value.upper()} ({len(items)})")
            print("-" * 40)

            for result in items:
                symbol = self.SEVERITY_SYMBOLS[severity]
                print(f"\n{symbol} [{result.object_type}] {result.object_name}")
                print(f"  {result.message}")
                
                if result.details:
                    for key, value in result.details.items():
                        if isinstance(value, list) and len(value) > 5:
                            display = ", ".join(str(v) for v in value[:5]) + f"... (+{len(value) - 5} more)"
                        elif isinstance(value, list):
                            display = ", ".join(str(v) for v in value)
                        else:
                            display = str(value)
                        print(f"  {key}: {display}")

        # Summary
        print("\n" + "-" * 60)
        print(
            f"SUMMARY: {len(by_severity[CheckSeverity.ERROR])} errors, "
            f"{len(by_severity[CheckSeverity.WARNING])} warnings, "
            f"{len(by_severity[CheckSeverity.INFO])} info"
        )
        print("=" * 60 + "\n")


class JsonReporter:
    """Outputs hygiene check results as JSON."""

    def to_dict(self, results: list[CheckResult]) -> dict[str, Any]:
        """
        Convert check results to a dictionary.

        Args:
            results: List of CheckResult objects.

        Returns:
            A dictionary representation of the results.
        """
        by_severity = {
            "error": [r for r in results if r.severity == CheckSeverity.ERROR],
            "warning": [r for r in results if r.severity == CheckSeverity.WARNING],
            "info": [r for r in results if r.severity == CheckSeverity.INFO],
        }

        return {
            "summary": {
                "total": len(results),
                "errors": len(by_severity["error"]),
                "warnings": len(by_severity["warning"]),
                "info": len(by_severity["info"]),
            },
            "results": [
                {
                    "check_name": r.check_name,
                    "severity": r.severity.value,
                    "object_type": r.object_type,
                    "object_name": r.object_name,
                    "message": r.message,
                    "details": r.details,
                }
                for r in results
            ],
        }

    def report(self, results: list[CheckResult], indent: int = 2) -> str:
        """
        Convert check results to a JSON string.

        Args:
            results: List of CheckResult objects.
            indent: JSON indentation level.

        Returns:
            A JSON string representation of the results.
        """
        return json.dumps(self.to_dict(results), indent=indent, default=str)
