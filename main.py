from typing import List,Optional
from fastapi import FastAPI,Query
from config.database import execute_query,generic_mapper_list
from models.models import Percorso,Piazzola
from repository.piazzoleRepo import PreparedStatementPiazzole
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"), # Scrive su file
        logging.StreamHandler()         # Scrive su console
    ]
)

logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/piazzole",response_model=List[Piazzola])
def lista_piazzole(
    cod_comune: Optional[int] = Query(None, description="Filtra per comune"),
    cod_municipio: Optional[int] = Query(None, description="Filtra per municipio"),
    id_via: Optional[int] = Query(None, description="Filtra per ID della via"),
    pap: Optional[int] = Query(None, ge=0, le=1, description="Filtra per PAP (1 = Sì, 0 = No)"),
):
    logger.info("Ricevuta richiesta GET /piazzole")
    query_select = PreparedStatementPiazzole(cod_comune,cod_municipio,id_via,pap)
    risultato = execute_query(query_select)
    if risultato is None:
        logger.error("Nessun risultato ottenuto dalla query.")
        return []
    
    piazzole = generic_mapper_list(risultato,Piazzola)
    return piazzole