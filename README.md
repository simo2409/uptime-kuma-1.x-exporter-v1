# uptime-kuma-1-x-exporter-v1

Script Python per esportare la lista dei monitor da un'istanza **Uptime Kuma v1.23.17** (o compatibile v1.x) tramite le API REST ufficiali.

## Cosa fa

- Si autentica all'API di Uptime Kuma usando una **API Key**.
- Scarica l'elenco completo dei monitor (attivi e non).
- Stampa i dettagli a schermo e salva il JSON grezzo in `monitors.json`.

## Requisiti

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (consigliato per gestire dipendenze e virtualenv)

## Configurazione

1. Copia il file di configurazione di esempio:
   ```bash
   cp config.json.default config.json
   ```

2. Modifica `config.json` inserendo i tuoi dati:
   ```json
   {
     "host": "https://uptime.tuo-dominio.com",
     "api_key": "uk1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   }
   ```

## Esecuzione

```bash
uv sync
uv run python main.py
```

## Output

Oltre alla stampa a schermo, viene generato il file `monitors.json` contenente l'array completo dei monitor recuperato dall'API.
