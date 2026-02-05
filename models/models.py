

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Any, TypeVar, Generic
from datetime import datetime

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
    total_count: Optional[int] = None


class Via(MyBaseModel):
    id_via: int
    nome: str
    id_comune: int
    total_count: Optional[int] = None

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
    total_count: Optional[int] = None


class Quartiere(MyBaseModel):
    id_quartiere: int
    id_municipio: Optional[int] = None
    id_comune: int
    descrizione: str

class Municipio(BaseModel):
    id_municipio: int
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

class Mappa(MyBaseModel):
    titolo: str
    descrizione: str

class Utenza(MyBaseModel):
    id_utenza: str
    codice_immobile: Optional[int] = None
    cod_interno: Optional[str] = None
    cod_civico: Optional[str] = None
    tipo_utenza: Optional[str] = None
    categoria: Optional[int] = None
    nominativo: Optional[str] = None
    cfisc_pariva: Optional[str] = None
    cod_via: Optional[int] = None
    descr_via: Optional[str] = None
    civico: Optional[int] = None
    lettera_civico: Optional[str] = None
    colore_civico: Optional[str] = None
    scala: Optional[str] = None
    interno: Optional[str] = None
    lettera_interno: Optional[str] = None
    zona_municipio: Optional[str] = None
    subzona_quartiere: Optional[str] = None
    data_cessazione: Optional[datetime] = None
    totale_record: Optional[int] = None


class Bilaterali_albero(MyBaseModel):
    id_area: Optional[int] = None
    descrizione : Optional[str] = None
    id_padre:Optional[int] = None


class Bilaterali(BaseModel):
    id_padre: Optional[int]
    ut_responsabile: Optional[str]
    id_tipo_rifiuto: Optional[int]
    tipi_rifiuto: Optional[str]
    desc_turno: Optional[str]
    id_percorso: Optional[str]
    cod_percorso: Optional[str]
    desc_percorso: Optional[str]
    frequenza: Optional[str]

class PosterioriPercorso(BaseModel):
    cod_percorso: Optional[str] = None
    descrizione: Optional[str] = None
    servizio: Optional[str] = None
    id_ut: Optional[int] = None
    ut_rimessa: Optional[str] = None
    freq_testata: Optional[int] = None
    freq: Optional[str] = None
    id_turno: Optional[int] = None
    turno: Optional[str] = None
    codice_cer: Optional[str] = None
    data_inizio_validita: Optional[str] = None
    data_fine_validita: Optional[str] = None
    data_ultima_modifica: Optional[str] = None
    versione_testata: Optional[int] = None
    periodicita: Optional[str] = None
    doppia_antenna: Optional[int] = None
    total_count: Optional[int] = None

class PiazzolaAmiu(BaseModel):
    id_piazzola: Optional[int] = None
    via: Optional[str] = None
    numero_civico: Optional[int] = None
    riferimento: Optional[str] = None
    note: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    data_inserimento: Optional[str] = None
    data_eliminazione: Optional[str] = None
    data_ultima_modifica: Optional[str] = None
    total_count: Optional[int] = None

class ElementoAmiu(MyBaseModel):
    id_elemento: int
    id_piazzola: Optional[int]
    id_tipo_elemento: Optional[int]
    tipo_elemento: Optional[str]
    rifiuto: Optional[str]
    volume_litri: Optional[float]
    matricola: Optional[str]
    tag: Optional[str]
    serratura: Optional[int]
    matricola_serratura: Optional[str]
    data_inserimento: Optional[str]
    data_eliminazione: Optional[str] = None
    data_ultima_modifica: Optional[str] = None
    total_count: Optional[int] = None

class ItinerarioPercorsoPsteriore(BaseModel):
        cod_percorso: Optional[str] = None
        ordine: Optional[int] = None
        id_elemento: Optional[int] = None
        id_frequenza: Optional[int] = None
        descrizione_long: Optional[str] = None
        data_inizio: Optional[str] = None
        data_fine: Optional[str] = None
        id_asta_percorso: Optional[int] = None
        ripasso: Optional[int] = None
        periodicita: Optional[str] = None
        data_ultima_modifica: Optional[str] = None
        total_count: Optional[int] = None

class PercorsoDettaglio(BaseModel):
    seq: Optional[int]
    id_piazzola: Optional[int]
    via: Optional[str]
    civ: Optional[str]
    riferimento: Optional[str]
    note_piazzola: Optional[str]
    tipo_elem: Optional[str]
    num: Optional[int]

class UserRoles(MyBaseModel):
    id_user: int
    utenze: Optional[bool] = None
    amministratore: Optional[bool] = None

    def get_active_roles(self) -> list[str]:
        """Restituisce una lista dei ruoli attivi per l'utente."""
        roles = []
        for field in type(self).model_fields.keys():
            if field != "id_user":
                value = getattr(self, field, None)
                if value:
                    roles.append(field)
        return roles




