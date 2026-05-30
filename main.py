#!/usr/bin/env python3
"""Script per scaricare la lista dei monitor da Uptime Kuma (v1.23.x) via Socket.IO API."""

import json
import sys
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


def main() -> None:
    config = load_config()
    host = config["host"]
    username = config["username"]
    password = config["password"]

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

    # Salva anche su file
    output_path = Path("monitors.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(monitors, f, indent=2, ensure_ascii=False)
    print(f"\nLista monitor salvata in: {output_path.resolve()}")


if __name__ == "__main__":
    main()
