from fastapi import HTTPException

def get_layer_filter_query(level: str) -> str:
    """
    Costruisce dinamicamente la query per il filtro dei layer
    in base al livello specificato.
    """
    if level == 'ambito':
        table_name = 'geo.v_ambiti'
    elif level == 'comune':
        table_name = 'geo.confini_comuni_area'
    elif level == 'municipio':
        table_name = 'geo.municipi_area'
    else:
        # La validazione principale è nel router, ma questa è una sicurezza aggiuntiva.
        raise ValueError(f"Livello '{level}' non è valido.")

    # La logica di concatenazione del filtro viene replicata dal PHP.
    # Crea una stringa di filtro come: layer_name:+"livello"+ILIKE+''nome_descrizione''+
    filter_expression = f"concat(al.layername, ':+\"{level}\"ILIKE+''', g.descrizione, '''')"

    query = f"""
        SELECT 
            'https://amiugis.amiu.genova.it/dwh/lizmap/www/index.php/view/map/' as url, 
            al.repo as repository, 
            al.qgis_project as project,
            replace(replace(replace(st_extent(st_transform(g.geoloc,3857))::text,'BOX(',''),')',''),' ',',') as bbox, 
            'EPSG:3857' as crs,
            {filter_expression} as filter 
        FROM {table_name} g, etl.api_layers al 
        WHERE al.title = :title AND g.descrizione ilike :name
        GROUP BY g.descrizione, al.repo, al.qgis_project, al.layername;
    """
    
    return query
