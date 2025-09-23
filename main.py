# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
import json
from typing import List, Optional

# Import your diagram generation functions
from diagram_generator import generate_graphviz_dot, render_diagram_to_bytes

app = FastAPI(title="Graphviz Diagram Generator Backend")

# --- Pydantic Models for Input Data (Based on your parsed_data structure) ---
class NodeModel(BaseModel):
    id: str
    name: str
    type: str # e.g., "server", "branch", "headquarters", "db_management", "database"
    has_local_db: Optional[bool] = False # Not all nodes will have this

class ConnectionModel(BaseModel):
    source_id: str
    target_id: str
    label: str
    type: str # e.g., "network", "local_db_access", "management_link"
    direction: str # "unidirectional" or "bidirectional"

class DiagramData(BaseModel):
    company_name: str
    nodes: List[NodeModel]
    connections: List[ConnectionModel]
    general_network_description: str
    #replication_details: Optional[dict] = {} # Can add if needed later
    #style_notes: Optional[str] = "" # Can add if needed later

# --- Endpoint to Generate Diagram ---
@app.post("/generate-diagram/", response_class=Response)
async def generate_diagram(data: DiagramData):
    """
    Receives diagram data in JSON format, generates a Graphviz diagram (PNG),
    and returns the image bytes.
    """
    try:
        # Convert Pydantic model to a plain dictionary for diagram_generator
        diagram_data_dict = data.dict()

        dot_script = generate_graphviz_dot(diagram_data_dict)
        image_bytes = render_diagram_to_bytes(dot_script, format="png")

        return Response(content=image_bytes, media_type="image/png")
    except FileNotFoundError:
        raise HTTPException(
            status_code=500, detail="Graphviz 'dot' command not found on server."
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Graphviz rendering failed. Stderr: {e.stderr.decode('utf-8', errors='ignore')}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- Example of how to structure the input data for testing ---
@app.get("/example-diagram-data")
async def get_example_diagram_data():
    """
    Returns an example JSON structure for diagram generation,
    based on the original image's layout.
    """
    example_data = {
      "company_name": "Arquitectura de Sucursales Distribuidas",
      "nodes": [
        { "id": "Servidor_Central", "name": "Servidor", "type": "server" },
        { "id": "Sinaloa_Branch", "name": "Sinaloa", "type": "branch" },
        { "id": "Baja_California_Sur_Branch", "name": "Baja California Sur", "type": "branch" },
        { "id": "Veracruz_Branch", "name": "Veracruz", "type": "branch" },
        { "id": "Yucatan_HQ", "name": "Yucatán", "type": "headquarters" },
        { "id": "Gestion_BD_Yucatan", "name": "Gestión de las BD", "type": "db_management" },
        { "id": "BD_Sinaloa", "name": "BD", "type": "database" },
        { "id": "BD_BCS", "name": "BD", "type": "database" },
        { "id": "BD_Veracruz", "name": "BD", "type": "database" },
        { "id": "BD_Yucatan", "name": "BD", "type": "database" }
      ],
      "connections": [
        { "source_id": "Servidor_Central", "target_id": "Sinaloa_Branch", "label": "IP", "type": "network", "direction": "unidirectional" },
        { "source_id": "Servidor_Central", "target_id": "Baja_California_Sur_Branch", "label": "IP", "type": "network", "direction": "unidirectional" },
        { "source_id": "Servidor_Central", "target_id": "Veracruz_Branch", "label": "IP", "type": "network", "direction": "unidirectional" },
        { "source_id": "Servidor_Central", "target_id": "Yucatan_HQ", "label": "IP", "type": "network", "direction": "unidirectional" },

        { "source_id": "Sinaloa_Branch", "target_id": "BD_Sinaloa", "label": "", "type": "local_db_access", "direction": "unidirectional" },
        { "source_id": "Baja_California_Sur_Branch", "target_id": "BD_BCS", "label": "", "type": "local_db_access", "direction": "unidirectional" },
        { "source_id": "Veracruz_Branch", "target_id": "BD_Veracruz", "label": "", "type": "local_db_access", "direction": "unidirectional" },
        { "source_id": "Yucatan_HQ", "target_id": "BD_Yucatan", "label": "", "type": "local_db_access", "direction": "unidirectional" },
        { "source_id": "Yucatan_HQ", "target_id": "Gestion_BD_Yucatan", "label": "", "type": "management_link", "direction": "unidirectional" }
      ],
      "general_network_description": "Las bases de datos son homogéneas y utilizan fragmentación de datos. La sede principal (Yucatán) puede acceder a las BD de las sucursales vía IP, y usuarios con permisos de vista pueden consultar la información almacenada."
    }
    return example_data
