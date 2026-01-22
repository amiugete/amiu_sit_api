# models.py

from pydantic import BaseModel,ConfigDict
from typing import Optional,Any


# 1. Definisci una classe base con la configurazione desiderata
class MyBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class Percorso(MyBaseModel):
    idpercorso: int
    descrizione: str


class Piazzola(MyBaseModel):
    id_piazzola: int
    id_via: int
    via: str
    comune: str
    municipio: Optional[str]
    quartiere: Optional[str]
    numero_civico: Any
    riferimento: Optional[str]
    note: Optional[str]
    elementi: str
    pap: int  # 0 o 1
    num_elementi: int
    num_elementi_privati: int
    lat: float
    lon: float
