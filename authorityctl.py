from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from agents.anchor_contract import canonical_json
from agents.authority_runtime import evaluate_authority_case, render_decision_markdown


def _read_packet(path: Path) -> dict:
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read authority packet {path}: {exc}") from exc
    if not isinstance(packet, dict):
        raise ValueError("authority packet root must be an object")
    return packet


def _select_case(packet: dict, case_id: str) -> dict:
    cases = packet.get("cases")
    if not isinstance(cases, list):
        raise ValueError("authority packet has no typed cases list")
    matches = [case for case in cases if isinstance(case, dict) and case.get("id") == case_id]
    if len(matches) != 1:
        raise ValueError(f"expected one case named {case_id!r}; found {len(matches)}")
    return matches[0]


def _write_receipt(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def audit(args: argparse.Namespace) -> int:
    packet = _read_packet(args.packet)
    case = _select_case(packet, args.case_id)
    result = evaluate_authority_case(case, packet)
    markdown = render_decision_markdown(result)
    json_receipt = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

    if args.json_out:
        _write_receipt(args.json_out, json_receipt)
    if args.markdown_out:
        _write_receipt(args.markdown_out, markdown)

    if args.format == "json":
        print(json_receipt, end="")
    elif args.format == "canonical-json":
        print(canonical_json(result))
    else:
        print(markdown, end="")
    return result["exit_code"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="authorityctl",
        description="Audit one proposed action against receipt-bound current authority. Dry-run only.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit", help="evaluate one frozen authority packet case")
    audit_parser.add_argument("packet", type=Path, help="path to an Authority Runtime v0 JSON packet")
    audit_parser.add_argument("--case", dest="case_id", required=True, help="case ID inside the packet")
    audit_parser.add_argument("--json-out", type=Path, help="write the JSON decision receipt")
    audit_parser.add_argument("--markdown-out", type=Path, help="write the Markdown decision receipt")
    audit_parser.add_argument(
        "--format",
        choices=("markdown", "json", "canonical-json"),
        default="markdown",
        help="stdout rendering (default: markdown)",
    )
    audit_parser.set_defaults(handler=audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except ValueError as exc:
        print(f"authorityctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
