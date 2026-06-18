# Istruzioni per la generazione di endpoint con `genera_model.py`


## Modello Pydantic generato
Lo script genera un modello pydantic in models a partire dalla query:


## Query SQL

```sql
SELECT
    id,
    nome,
    data_creazione AS data_creazione,
    valore_decimale AS decimale
FROM {{#comment|TABLE: ordini}}
{{/comment}}


Lo script genera una classe con campi `Optional[...] = None`, per compatibilità con il pattern del progetto.

Esempio generato:

```python
class MioRisultato(BaseModel):
    id: Optional[int] = None
    nome: Optional[str] = None
    data: Optional[datetime] = None
```

Attenzione:
- `time` viene mappato a `str`
- `Decimal` viene mappato a `float`
- se la query non restituisce righe, tutti i campi diventano `Optional[Any]`
- se il tipo non è riconosciuto, viene usato `Any`

Se serve, aggiungi manualmente in `models/models.py` gli import:

```python
from datetime import date
from datetime import datetime
```

