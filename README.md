# uptime-kuma-1-x-exporter-v1

Script Python per esportare la lista dei monitor da un'istanza **Uptime Kuma v1.23.x** tramite le **API Socket.IO** (l'unica disponibile in questa versione per leggere l'elenco dei monitor).

## Cosa fa

- Si autentica all'istanza Uptime Kuma usando **username e password**.
- Scarica l'elenco completo dei monitor (attivi e non) tramite Socket.IO.
- Stampa i dettagli a schermo.
- Genera i file di output:
  1. **`YYYY-MM-DD_monitors.json`** — lista "light" di tutti i monitor (inclusi i gruppi) con solo *id, nome, tipo, attivo, url e appartenenza al gruppo*; **senza** i settings completi.
  2. Cartella **`monitors/`** — un file JSON per ogni monitor, nominato `YYYY-MM-DD_<nome-monitor>.json`.

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
     "password": "your-password",
     "output_dir": "./output"
   }
   ```

   - `output_dir` è opzionale: se omesso i file vengono scritti nella directory corrente.

## Esecuzione

```bash
uv sync
uv run python main.py
```

## Output

Supponendo `output_dir` = `./output` e data odierna `2026-05-30`:

```
output/
├── 2026-05-30_monitors.json       # lista light di tutti i monitor
└── monitors/
    ├── 2026-05-30_Google.json      # parametri completi del singolo monitor
    ├── 2026-05-30_API_Production.json
    └── ...
```
