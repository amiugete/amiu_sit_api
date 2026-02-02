# models.py

from logging import log
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Any, TypeVar, Generic
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm

import re

T = TypeVar('T')

# 1. Definisci una classe base con la configurazione desiderata
class MyBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class PaginatedResponse(MyBaseModel, Generic[T]):
    total: Optional[int] = None # length of all items
    page: Optional[int] = None #current page -> OFFSET = (page - 1) * size = ?
    size: Optional[int] = None # limit
    pages: Optional[int] = None #toltal pages total/size
    content: list[T] = []

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


class Via(MyBaseModel):
    id_via: int
    nome: str
    id_comune: int


class Comune(MyBaseModel):
    id_comune: int
    descr_comune: str
    descr_provincia: str
    prefisso_utenti: str
    id_ambito: int
    cod_istat: str


class Civico(MyBaseModel):
    cod_civico: str
    numero: int
    lettera: Optional[str] = None
    colore: Optional[str] = None
    testo: Optional[str] = None
    cod_strada: int
    nome_via: str
    id_comune: int
    id_municipio: Optional[int] = None
    id_quartiere: Optional[int] = None
    lat: float
    lon: float
    insert_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


class Quartiere(MyBaseModel):
    id_quartiere: int
    id_municipio: Optional[int] = None
    id_comune: int
    descrizione: str


class Ambito(MyBaseModel):
    id_ambito: int
    descr_ambito: str


class PointOfInterest(MyBaseModel):
    id: int
    via: str
    numero_civico: Optional[str] = None
    riferimento: Optional[str] = None
    note: Optional[str] = None
    lat: float
    lon: float
    tipo: str    


class User(MyBaseModel):
    id_user: int
    name: str
    email: Optional[str] = None




