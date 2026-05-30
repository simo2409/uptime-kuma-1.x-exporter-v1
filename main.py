#!/usr/bin/env python3
"""Script per scaricare la lista dei monitor da Uptime Kuma (v1.23.x) via Socket.IO API."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

from uptime_kuma_api import UptimeKumaApi


def load_config(path: Path = Path("config.json")) -> dict:
    """Carica la configurazione dal file JSON specificato."""
    if not path.exists():
        print(f"Errore: file di configurazione non trovato: {path.resolve()}", file=sys.stderr)
        sys.exit(1)

    try:
        with path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Errore: il file {path} non è un JSON valido: {exc}", file=sys.stderr)
        sys.exit(1)

    required_keys = {"host", "username", "password"}
    missing = required_keys - config.keys()
    if missing:
        print(
            f"Errore: chiavi mancanti in {path}: {', '.join(sorted(missing))}",
            file=sys.stderr,
        )
        print(
            "Nota: Uptime Kuma v1.x non espone l'elenco monitor via REST API. "
            "Serve username e password per l'autenticazione Socket.IO.",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


def sanitize_filename(name: str) -> str:
    """Rende una stringa sicura da usare come nome file."""
    safe = re.sub(r'[\\/*?:"<>| ]+', "_", name)
    safe = safe.strip("._")
    return safe[:100]


def fetch_monitors(host: str, username: str, password: str) -> list[dict]:
    """Recupera la lista di tutti i monitor (attivi e non) dall'API Socket.IO di Uptime Kuma."""
    try:
        with UptimeKumaApi(host, ssl_verify=True) as api:
            login_resp = api.login(username, password)
            if not login_resp or not login_resp.get("token"):
                print("Errore: login fallito, token non ricevuto.", file=sys.stderr)
                sys.exit(1)
            monitors = api.get_monitors()
    except Exception as exc:
        print(f"Errore di connessione all'API: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(monitors, list):
        print("Errore: formato inatteso per la lista dei monitor", file=sys.stderr)
        sys.exit(1)

    return monitors


def monitor_summary(monitor: dict) -> dict:
    """Estrae i campi essenziali di un monitor (senza i settings completi)."""
    return {
        "id": monitor.get("id"),
        "name": monitor.get("name"),
        "type": str(monitor.get("type", "")),
        "active": monitor.get("active"),
        "url": monitor.get("url"),
        "parent": monitor.get("parent"),
        "childrenIDs": monitor.get("childrenIDs", []),
    }


def save_monitors(monitors: list[dict], output_dir: Path) -> None:
    """Salva la lista monitor e i singoli file per ciascun monitor."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. File principale con la lista light (solo id, nome, tipo, attivo, url, gruppo)
    list_path = output_dir / f"{today}_monitors.json"
    with list_path.open("w", encoding="utf-8") as f:
        json.dump(
            [monitor_summary(m) for m in monitors],
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    print(f"Lista monitor salvata in: {list_path.resolve()}")

    # 2. Cartella con i singoli monitor
    monitors_dir = output_dir / "monitors"
    monitors_dir.mkdir(parents=True, exist_ok=True)

    seen_names: set[str] = set()
    for monitor in monitors:
        name = monitor.get("name", "unknown")
        safe_name = sanitize_filename(name)

        # Gestione nomi duplicati
        file_name = f"{today}_{safe_name}.json"
        if file_name in seen_names:
            monitor_id = monitor.get("id", "unknown")
            file_name = f"{today}_{safe_name}_{monitor_id}.json"
        seen_names.add(file_name)

        file_path = monitors_dir / file_name
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(monitor, f, indent=2, ensure_ascii=False, default=str)

    print(f"Singoli monitor salvati in: {monitors_dir.resolve()} ({len(monitors)} file)")


def main() -> None:
    config = load_config()
    host = config["host"]
    username = config["username"]
    password = config["password"]
    output_dir = Path(config.get("output_dir", "."))

    print(f"Connessione a Uptime Kuma: {host} ...")
    monitors = fetch_monitors(host, username, password)

    print(f"Trovati {len(monitors)} monitor:\n")
    for monitor in monitors:
        monitor_id = monitor.get("id", "N/D")
        name = monitor.get("name", "N/D")
        monitor_type = monitor.get("type", "N/D")
        active = "Sì" if monitor.get("active") else "No"
        url = monitor.get("url", "N/D")
        print(f"  ID: {monitor_id}")
        print(f"  Nome: {name}")
        print(f"  Tipo: {monitor_type}")
        print(f"  Attivo: {active}")
        print(f"  URL: {url}")
        print("-" * 40)

    save_monitors(monitors, output_dir)


if __name__ == "__main__":
    main()
