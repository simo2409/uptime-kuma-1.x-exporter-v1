# uptime-kuma-1-x-exporter-v1

Script Python per esportare la lista dei monitor da un'istanza **Uptime Kuma v1.23.x** tramite le **API Socket.IO** (l'unica disponibile in questa versione per leggere l'elenco dei monitor).

## Cosa fa

- Si autentica all'istanza Uptime Kuma usando **username e password**.
- Scarica l'elenco completo dei monitor (attivi e non) tramite Socket.IO.
- Stampa i dettagli a schermo e salva il JSON grezzo in `monitors.json`.

## Requisiti

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (consigliato per gestire dipendenze e virtualenv)

## ⚠️ Nota importante

In **Uptime Kuma v1.x** l'endpoint REST `/api/monitors` **non esiste**. Le *API Key* create nelle impostazioni servono solo per endpoint read-only come `/metrics` o i badge, ma **non** per ottenere la lista dei monitor.  
Per questo lo script richiede **username** e **password** di un utente abilitato.

## Configurazione

1. Copia il file di configurazione di esempio:
   ```bash
   cp config.json.default config.json
   ```

2. Modifica `config.json` inserendo i tuoi dati:
   ```json
   {
     "host": "https://uptime.tuo-dominio.com",
     "username": "admin",
     "password": "your-password"
   }
   ```

## Esecuzione

```bash
uv sync
uv run python main.py
```

## Output

Oltre alla stampa a schermo, viene generato il file `monitors.json` contenente l'array completo dei monitor recuperato dall'API.
