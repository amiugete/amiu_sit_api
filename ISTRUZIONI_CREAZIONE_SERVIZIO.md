# Istruzioni per la generazione di endpoint con `genera_servizio.py`

Questo documento spiega come usare lo script `genera_servizio.py` per generare:
- un modello Pydantic in `models/models.py`
- un file repository SQL in `repository/pst_<nome>.py`
- il guscio di un endpoint FastAPI in un router esistente o nuovo
- l’eventuale registrazione del router in `main.py`

---

## 1. Preparazione

Lo script `genera_servizio.py` lavora con:
- `config/database.py` per le connessioni DB
- `models/models.py` per i modelli Pydantic
- `repository/` per le query SQL
- file router `*_api.py` per gli endpoint
- `main.py` per la registrazione del router

È pensato per progetti dove:
- le query DB sono centralizzate in repository
- le risposte sono tipizzate con modelli Pydantic
- gli endpoint usano i helper in `business.query_helpers`
- l’autenticazione è gestita con `check_permissions`

---

## 2. Flusso principale dello script

1. Chiede il nome del modello Pydantic.
2. Chiede la connessione DB (`DbConnection`).
3. Chiede la query SQL e la esegue con un `LIMIT 1` sicuro.
4. In base ai tipi delle colonne, genera:
   - classe Pydantic in `models/models.py`
   - eventuali import mancanti (`datetime`, `date`)
5. Crea o sovrascrive il file repository `repository/pst_<nome>.py`
6. Chiede se generare anche il guscio di un endpoint

---

## 3. Generazione del modello Pydantic

Lo script genera una classe con campi `Optional[...] = None`, per compatibilità con il pattern del progetto.

Esempio generato:

```python
class MioRisultato(BaseModel):
    id: Optional[int] = None
    nome: Optional[str] = None
    data: Optional[datetime] = None