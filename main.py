#!/usr/bin/env python3
"""Script per scaricare la lista dei monitor da Uptime Kuma (v1.23.17) via REST API."""

import json
import sys
from pathlib import Path

import requests


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

    required_keys = {"host", "api_key"}
    missing = required_keys - config.keys()
    if missing:
        print(f"Errore: chiavi mancanti in {path}: {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    return config


def fetch_monitors(host: str, api_key: str) -> list[dict]:
    """Recupera la lista di tutti i monitor (attivi e non) dall'API di Uptime Kuma."""
    base_url = host.rstrip("/")
    url = f"{base_url}/api/monitors"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"Errore di connessione all'API: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        print(f"Errore: risposta non valida dall'API: {exc}", file=sys.stderr)
        sys.exit(1)

    if not data.get("ok"):
        msg = data.get("msg", "Errore sconosciuto")
        print(f"Errore API Uptime Kuma: {msg}", file=sys.stderr)
        sys.exit(1)

    monitors = data.get("monitors", [])
    if not isinstance(monitors, list):
        print("Errore: formato inatteso per la lista dei monitor", file=sys.stderr)
        sys.exit(1)

    return monitors


def main() -> None:
    config = load_config()
    host = config["host"]
    api_key = config["api_key"]

    print(f"Connessione a Uptime Kuma: {host} ...")
    monitors = fetch_monitors(host, api_key)

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
