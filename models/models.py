
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_geojson import LineStringModel
from typing import Optional, Any, TypeVar, Generic
from datetime import datetime
from shapely import wkb
import json
from zoneinfo import ZoneInfo

T = TypeVar('T')

class PaginatedGeoJSONResponse(BaseModel):
    total: Optional[int] = None  # Numero totale di feature
    page: Optional[int] = None   # Pagina corrente
    size: Optional[int] = None   # Dimensione della pagina
    pages: Optional[int] = None  # Numero totale di pagine
    content: Optional[GeoJSNONModel] = None  # Oggetto GeoJSON paginato

class PaginatedResponse(BaseModel, Generic[T]):
    total: Optional[int] = None # length of all items
    page: Optional[int] = None #current page -> OFFSET = (page - 1) * size = ?
    size: Optional[int] = None # limit
    pages: Optional[int] = None #toltal pages total/size
    content: list[T] = []

class Percorso(BaseModel):
    idpercorso: int
    descrizione: str


class Piazzola(BaseModel):
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


class Via(BaseModel):
    id_via: int
    nome: str
    id_comune: int
    total_count: Optional[int] = None

class Comune(BaseModel):
    id_comune: int
    descr_comune: str
    descr_provincia: str
    prefisso_utenti: str
    id_ambito: int
    cod_istat: str


class Civico(BaseModel):
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


class Quartiere(BaseModel):
    id_quartiere: int
    id_municipio: Optional[int] = None
    id_comune: int
    descrizione: str

class Municipio(BaseModel):
    id_municipio: int
    id_comune: int
    descrizione: str


class Ambito(BaseModel):
    id_ambito: int
    descr_ambito: str


class PointOfInterest(BaseModel):
    id: int
    via: str
    numero_civico: Optional[str] = None
    riferimento: Optional[str] = None
    note: Optional[str] = None
    lat: float
    lon: float
    tipo: str 


class User(BaseModel):
    id_user: int
    name: str
    role_name: str 
    email: Optional[str] = None
    

class Mappa(BaseModel):
    titolo: str
    descrizione: str

class Utenza(BaseModel):
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


class Bilaterali_albero(BaseModel):
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

class MezzoEkovision(BaseModel):
    id_scheda_ekovision: Optional[int] = None
    data_esecuzione_prevista: Optional[str] = None
    orario_esecuzione: Optional[str] = None
    fascia_turno: Optional[str] = None
    sportello: Optional[str] = None
    total_count: Optional[int] = None

class MacroCategoria(BaseModel):
    classificazione: Optional[str] = None
    categoria: Optional[int] = None
    descr_categoria: Optional[str] = None
    utilizzo: Optional[int] = None
    descr_utilizzo: Optional[str] = None

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

class ElementoAmiu(BaseModel):
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

class Deposito(BaseModel):
    id_ut: int
    descrizione: str
    long: float
    lat: float
    raggio: int
    data_inizio: str
    data_fine: Optional[str] = None
    data_ultima_modifica: str
    total_count: Optional[int] = None


class Point2Area(BaseModel):
    id_ambito: int
    ambito: str
    id_comune: int
    comune: str
    id_zona: int
    zona: str
    id_ut: int
    ut: str
    id_municicio: Optional[str] = None
    municipio: Optional[str] = None
    id_quartiere: Optional[int] = None
    quartiere: Optional[str] = None

class FasceEtaCivico(BaseModel):
    cod_civico: Optional[str] = None
    cod_via: Optional[int] = None
    n0_10: Optional[int] = None
    n11_20: Optional[int] = None
    n21_30: Optional[int] = None
    n31_40: Optional[int] = None
    n41_50: Optional[int] = None
    n51_60: Optional[int] = None
    n60_70: Optional[int] = None
    n70_80: Optional[int] = None
    npiu80: Optional[int] = None
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


class GeoJSNONModel(BaseModel):
    type: str = 'FeatureCollection'
    features: list[MyFutureModel] = []
    total: Optional[int] = None
    page: Optional[int] = None
    size: Optional[int] = None
    pages: Optional[int] = None


class MyFutureModel(BaseModel):
    type: str = 'Feature'
    properties: Optional[T] = None
    geometry: Optional[Geometry] = None
    @field_validator("geometry", mode="before")
    @classmethod
    def parse_geometry(cls, v):
        if v is None:
            return None
        # il dato arriva già in formato LineString
        elif isinstance(v, str):
            v = v.strip()
            # Se è una stringa JSON GeoJSON
            if v.startswith('{'):
                geojson = json.loads(v)
                if geojson.get("type") == "LineString" and "coordinates" in geojson:
                        coords = [[x, y] for x, y in geojson["coordinates"]]
                        return Geometry(type="LineString", coordinates=coords)
                else:
                    raise ValueError("GeoJSON non valido")
            else:
                # Altrimenti si assume sia esadecimale WKB
                geom = wkb.loads(bytes.fromhex(v))
                coords = [[x, y] for x, y in geom.coords]
                return Geometry(type="LineString", coordinates=coords)
        else:
            raise ValueError("Formato geometry non supportato")


class Geometry(BaseModel):
        type: str
        coordinates: list[list[float]]


class SecurityLog(BaseModel):
    ip_address: str
    attempts: int
    ban_count: int
    last_failure: Optional[datetime] = None
    blocked_until: Optional[datetime] = None
    last_access: Optional[datetime] = None
    count_access: Optional[int] = None

class SecurityLogUser(BaseModel):
    user: str
    attempts: int
    ban_count: int
    last_failure: Optional[datetime] = None
    blocked_until: Optional[datetime] = None
    last_access: Optional[datetime] = None
    count_access: Optional[int] = None


class UserRoles(BaseModel):
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


class LayerFilterResponse(BaseModel):
    url: str
    repository: str
    project: str
    bbox: str
    crs: str
    filter: str







