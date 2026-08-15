#!/usr/bin/env python3
"""
DocShell Core - Datadog Telemetry, Container Health & SQLite Audit Reporter
Performs multi-dimensional observability audit:
1. Docker Container Stack Health & Metrics (docshell-ollama, docshell-redis, docshell-rag, docshell-web, docshell-datadog)
2. Local SQLite Audit Logs (docshell.db)
3. Datadog APM & JSONL Telemetry Tracing
4. Ollama LLM & Embedding Model Status
5. Redis & Cache Hit/Miss Telemetry
"""

import sys
import json
import shutil
import socket
import urllib.request
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

socket.setdefaulttimeout(2.0)

def _resolve_root() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        if (p / "docs").exists() or (p / "publication").exists() or (p / "scripts").exists():
            return p
    return Path("/app") if Path("/app").exists() else current.parent

ROOT_DIR = _resolve_root()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LOGS_DIR = ROOT_DIR / "dist" / "logs"
TELEMETRY_FILE = LOGS_DIR / "datadog_telemetry.jsonl"
REPORTS_DIR = ROOT_DIR / "dist" / "reports"


def load_telemetry_entries() -> List[Dict[str, Any]]:
    """Loads all telemetry entries from Datadog JSONL log stream."""
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


def get_docker_containers_info() -> List[Dict[str, Any]]:
    """Inspects all DocShell Docker containers and gathers status, ports, and memory."""
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return []

    containers = []
    try:
        cmd = [
            docker_bin, "ps", "-a",
            "--filter", "name=docshell",
            "--format", "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}|{{.State}}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.strip().splitlines():
                parts = line.split("|")
                if len(parts) >= 6:
                    containers.append({
                        "id": parts[0],
                        "name": parts[1],
                        "image": parts[2],
                        "status": parts[3],
                        "ports": parts[4],
                        "state": parts[5]
                    })
    except Exception:
        pass
    return containers


def get_ollama_models_status() -> Dict[str, Any]:
    """Queries Ollama endpoint to verify installed models and daemon status."""
    ollama_host = "http://localhost:11434"
    status = {"online": False, "models": []}
    try:
        req = urllib.request.Request(f"{ollama_host}/api/tags", headers={"User-Agent": "DocShell-Reporter"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                status["online"] = True
                status["models"] = [
                    {
                        "name": m.get("name"),
                        "size_mb": round(m.get("size", 0) / (1024 * 1024), 2),
                        "modified_at": m.get("modified_at")
                    }
                    for m in data.get("models", [])
                ]
    except Exception:
        pass
    return status


def generate_report(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes aggregated multi-dimensional metrics from logs, containers, and SQLite."""
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

    # SQLite Audit Summary
    sqlite_summary = {}
    try:
        from scripts.core.database import db
        sqlite_summary = db.get_audit_summary()
    except Exception:
        pass

    # Containers & Models
    containers = get_docker_containers_info()
    ollama_info = get_ollama_models_status()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": total_events,
        "error_count": errors_count,
        "event_breakdown": event_types,
        "latencies": latency_summary,
        "locales_requested": locales_requested,
        "cache_stats": cache_stats,
        "containers": containers,
        "ollama_info": ollama_info,
        "sqlite_audit": sqlite_summary
    }


def format_markdown_report(report: Dict[str, Any]) -> str:
    """Renders a formatted Markdown report with container cross-auditing."""
    md = [
        "# 📊 DocShell - Relatório Completo de Telemetria, Contêineres e Auditoria",
        "",
        f"> **Gerado em:** `{report['generated_at']}`  ",
        f"> **Total de Eventos Registrados:** `{report['total_events']}` | **Erros:** `{report['error_count']}`",
        "",
        "---",
        "",
        "## 🐳 1. Status e Saúde dos Contêineres Docker",
        "",
        "| Contêiner | Imagem | Estado | Portas / Mapeamentos |",
        "|---|---|---|---|"
    ]

    containers = report.get("containers", [])
    if containers:
        for c in containers:
            status_icon = "🟢" if c["state"] == "running" else "🔴"
            md.append(f"| {status_icon} **`{c['name']}`** | `{c['image']}` | `{c['status']}` | `{c['ports'] or '-'}` |")
    else:
        md.append("| ℹ️ *Nenhum contêiner DocShell detectado em execução no momento.* | - | - | - |")

    md.extend([
        "",
        "---",
        "",
        "## 🦙 2. Modelos de IA e Status do Ollama Daemon",
        "",
        f"- **Ollama Daemon Conectado:** `{'Sim 🟢' if report['ollama_info']['online'] else 'Não 🔴 (Inicie com docker compose up)'}`",
        "",
        "| Modelo Instalado | Tamanho (MB) | Última Modificação |",
        "|---|---|---|"
    ])

    models = report.get("ollama_info", {}).get("models", [])
    if models:
        for m in models:
            md.append(f"| 🧠 **`{m['name']}`** | `{m['size_mb']} MB` | `{m['modified_at']}` |")
    else:
        md.append("| ℹ️ *Nenhum modelo baixado ainda ou Ollama offline.* | - | - |")

    md.extend([
        "",
        "---",
        "",
        "## ⚡ 3. Desempenho e Latência das Operações (Datadog & APM)",
        "",
        "| Operação | Execuções | Média (ms) | Mínimo (ms) | Máximo (ms) |",
        "|---|---|---|---|---|"
    ])
    
    for op, data in report.get("latencies", {}).items():
        md.append(f"| `{op}` | {data['count']} | **{data['avg_ms']} ms** | {data['min_ms']} ms | {data['max_ms']} ms |")

    md.extend([
        "",
        "---",
        "",
        "## 🗄️ 4. Auditoria do Banco Local (SQLite `docshell.db`)",
        "",
        f"- **Total de Eventos no Banco de Auditoria:** `{report.get('sqlite_audit', {}).get('total_events', 0)}`",
        f"- **Eventos com Erro:** `{report.get('sqlite_audit', {}).get('error_events', 0)}`",
        "",
        "| Evento no SQLite | Ocorrências | Duração Média (ms) |",
        "|---|---|---|"
    ])

    for ev_agg in report.get("sqlite_audit", {}).get("event_aggregations", []):
        avg_dur = round(ev_agg.get("avg_duration") or 0.0, 2)
        md.append(f"| `{ev_agg.get('event')}` | {ev_agg.get('count')} | {avg_dur} ms |")

    md.extend([
        "",
        "---",
        "",
        "## 💾 5. Estatísticas do Cache (Redis / SQLite)",
        "",
        f"- **Mecanismo de Cache Ativo:** `{report['cache_stats'].get('engine', 'disk').upper()}`",
        f"- **Conectado ao Redis:** `{'Sim ✅' if report['cache_stats'].get('redis_connected') else 'Não (Usando Cache SQLite/Disco) ⚠️'}`",
        f"- **Cache Hits:** `{report['cache_stats'].get('hits', 0)}`",
        f"- **Cache Misses:** `{report['cache_stats'].get('misses', 0)}`",
        f"- **Taxa de Acerto (Hit Ratio):** `{report['cache_stats'].get('hit_ratio_percent', 0.0)}%`",
        "",
        "---",
        "",
        "## 🌐 6. Requisições por Idioma / Localidade",
        "",
        "| Idioma | Requisições Registradas |",
        "|---|---|"
    ])

    for loc, count in report.get("locales_requested", {}).items():
        md.append(f"| `{loc}` | {count} |")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="DocShell Datadog Telemetry, Container Health & SQLite Audit Reporter")
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

    if args.summary or True:
        print("\n=================================================================")
        print("    DOCSHELL - AUDITORIA DE SISTEMA, CONTÊINERES E DATADOG       ")
        print("=================================================================")
        print(f"Gerado em:        {report['generated_at']}")
        print(f"Total Eventos:    {report['total_events']} (Datadog) | {report.get('sqlite_audit', {}).get('total_events', 0)} (SQLite)")
        print(f"Contêineres:      {len(report.get('containers', []))} ativos")
        for c in report.get("containers", []):
            print(f"  • {c['name']:<22} [{c['state']}] -> {c['status']}")
        print(f"Ollama Daemon:    {'🟢 Online' if report['ollama_info']['online'] else '🔴 Offline'}")
        for m in report.get("ollama_info", {}).get("models", []):
            print(f"  🧠 Modelo: {m['name']} ({m['size_mb']} MB)")
        print(f"Cache Engine:     {report['cache_stats']['engine'].upper()} (Hits: {report['cache_stats']['hits']}, Misses: {report['cache_stats']['misses']})")
        print("=================================================================\n")


if __name__ == "__main__":
    main()
