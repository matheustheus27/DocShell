#!/usr/bin/env python3
"""
DocShell Core - Datadog Telemetry & Performance Reporter
Analyzes Datadog JSONL logs, generates audit summaries, latency breakdowns, and exports Markdown/JSON reports.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
LOGS_DIR = ROOT_DIR / "dist" / "logs"
TELEMETRY_FILE = LOGS_DIR / "datadog_telemetry.jsonl"
REPORTS_DIR = ROOT_DIR / "dist" / "reports"


def load_telemetry_entries() -> List[Dict[str, Any]]:
    """Loads all telemetry entries from disk."""
    if not TELEMETRY_FILE.exists():
        return []
    entries = []
    with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    return entries


def generate_report(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes aggregated metrics from logs."""
    total_events = len(entries)
    event_types: Dict[str, int] = {}
    latencies: Dict[str, List[float]] = {}
    errors_count = 0
    locales_requested: Dict[str, int] = {}

    for e in entries:
        ev = e.get("event") or e.get("logger") or "unknown"
        event_types[ev] = event_types.get(ev, 0) + 1
        
        if e.get("level") == "ERROR":
            errors_count += 1

        dur = e.get("duration_ms")
        if dur is not None and isinstance(dur, (int, float)):
            latencies.setdefault(ev, []).append(dur)

        details = e.get("details", {})
        if isinstance(details, dict) and "locale" in details:
            loc = details["locale"]
            locales_requested[loc] = locales_requested.get(loc, 0) + 1

    latency_summary = {}
    for ev, vals in latencies.items():
        if vals:
            latency_summary[ev] = {
                "count": len(vals),
                "avg_ms": round(sum(vals) / len(vals), 2),
                "min_ms": round(min(vals), 2),
                "max_ms": round(max(vals), 2)
            }

    from scripts.core.cache_manager import cache_manager
    cache_stats = cache_manager.get_stats()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": total_events,
        "error_count": errors_count,
        "event_breakdown": event_types,
        "latencies": latency_summary,
        "locales_requested": locales_requested,
        "cache_stats": cache_stats
    }


def format_markdown_report(report: Dict[str, Any]) -> str:
    """Renders a formatted Markdown report."""
    md = [
        "# 📊 DocShell - Relatório de Telemetria e Desempenho (Datadog)",
        "",
        f"> **Gerado em:** `{report['generated_at']}`  ",
        f"> **Total de Eventos Registrados:** `{report['total_events']}` | **Erros:** `{report['error_count']}`",
        "",
        "---",
        "",
        "## ⚡ 1. Desempenho e Latência das Operações",
        "",
        "| Operação | Execuções | Média (ms) | Mínimo (ms) | Máximo (ms) |",
        "|---|---|---|---|---|"
    ]
    
    for op, data in report.get("latencies", {}).items():
        md.append(f"| `{op}` | {data['count']} | **{data['avg_ms']} ms** | {data['min_ms']} ms | {data['max_ms']} ms |")

    md.extend([
        "",
        "---",
        "",
        "## 💾 2. Estatísticas do Cache (Redis / Fallback)",
        "",
        f"- **Mecanismo de Cache Ativo:** `{report['cache_stats'].get('engine', 'disk').upper()}`",
        f"- **Conectado ao Redis:** `{'Sim ✅' if report['cache_stats'].get('redis_connected') else 'Não (Usando Cache em Disco) ⚠️'}`",
        f"- **Cache Hits:** `{report['cache_stats'].get('hits', 0)}`",
        f"- **Cache Misses:** `{report['cache_stats'].get('misses', 0)}`",
        f"- **Taxa de Acerto (Hit Ratio):** `{report['cache_stats'].get('hit_ratio_percent', 0.0)}%`",
        "",
        "---",
        "",
        "## 🌐 3. Requisições por Idioma / Localidade",
        "",
        "| Idioma | Requisições |",
        "|---|---|"
    ])

    for loc, count in report.get("locales_requested", {}).items():
        md.append(f"| `{loc}` | {count} |")

    md.extend([
        "",
        "---",
        "",
        "## 📈 4. Distribuição Total de Eventos",
        "",
        "| Tipo de Evento | Ocorrências |",
        "|---|---|"
    ])

    for ev, count in report.get("event_breakdown", {}).items():
        md.append(f"| `{ev}` | {count} |")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="DocShell Datadog Telemetry & Reporter")
    parser.add_argument("--summary", action="store_true", help="Print summary in console")
    parser.add_argument("--export", default="markdown", choices=["markdown", "json"], help="Export format")
    parser.add_argument("--output", default=None, help="Output file path")
    args = parser.parse_args()

    entries = load_telemetry_entries()
    report = generate_report(entries)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.export == "json":
        out_file = Path(args.output) if args.output else REPORTS_DIR / "datadog_report.json"
        out_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[DocShell Datadog] Relatório JSON exportado para: {out_file}")
    else:
        out_file = Path(args.output) if args.output else REPORTS_DIR / "datadog_report.md"
        md_content = format_markdown_report(report)
        out_file.write_text(md_content, encoding="utf-8")
        print(f"[DocShell Datadog] Relatório Markdown exportado para: {out_file}")

    if args.summary:
        print("\n=================================================================")
        print("          DOCSHELL - RESUMO DE TELEMETRIA (DATADOG)             ")
        print("=================================================================")
        print(f"Total de Eventos: {report['total_events']} | Erros: {report['error_count']}")
        print(f"Cache Engine:     {report['cache_stats']['engine'].upper()} (Hits: {report['cache_stats']['hits']}, Misses: {report['cache_stats']['misses']})")
        print("Latências:")
        for op, data in report.get("latencies", {}).items():
            print(f"  - {op:<28}: avg={data['avg_ms']}ms, count={data['count']}")
        print("=================================================================\n")


if __name__ == "__main__":
    main()
