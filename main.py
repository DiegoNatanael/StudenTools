# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
import json
from typing import List, Optional

# Import your generator functions
from diagram_generator import generate_graphviz_dot, render_diagram_to_bytes
from doc_generator import create_document_docx # New import
from ppt_generator import create_presentation_pptx # New import

app = FastAPI(title="StudenTools Backend Services")

# --- Diagram Generator Models (from previous steps) ---
class NodeModel(BaseModel):
    id: str
    name: str
    type: str
    has_local_db: Optional[bool] = False

class ConnectionModel(BaseModel):
    source_id: str
    target_id: str
    label: str
    type: str
    direction: str

class DiagramData(BaseModel):
    company_name: str
    nodes: List[NodeModel]
    connections: List[ConnectionModel]
    general_network_description: str

# --- DOCX Generator Models ---
class DocxTableDataRow(BaseModel):
    # Flexible table row, can be a list of strings/numbers
    # For simplicity, assuming a fixed 3 columns as per example
    col1: str
    col2: str
    col3: str

class DocxData(BaseModel):
    title: str = "Documento Generado"
    introduction: str = "Este es un documento de ejemplo generado por StudenTools."
    bullet_points: List[str] = ["Punto A", "Punto B", "Punto C"]
    table_rows: List[DocxTableDataRow] = [] # List of Pydantic models for table rows

# --- PPTX Generator Models ---
class PptxData(BaseModel):
    title: str = "Presentación Generada"
    subtitle: str = "Un ejemplo de pptx con StudenTools"
    agenda_items: List[str] = ["Introducción", "Contenido", "Conclusión"]
    features_items: List[str] = ["Feature 1", "Feature 2"]

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Welcome to StudenTools Backend! Use /docs for API documentation."}

# Diagram Generator Endpoint
@app.post("/generate-diagram/", response_class=Response, summary="Generate Graphviz Diagram")
async def generate_diagram_endpoint(data: DiagramData):
    """
    Receives diagram data in JSON, generates a Graphviz diagram (PNG),
    and returns the image bytes.
    """
    try:
        diagram_data_dict = data.dict()
        dot_script = generate_graphviz_dot(diagram_data_dict)
        image_bytes = render_diagram_to_bytes(dot_script, format="png")
        return Response(content=image_bytes, media_type="image/png")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Graphviz 'dot' command not found on server.")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Graphviz rendering failed. Stderr: {e.stderr.decode('utf-8', errors='ignore')}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# DOCX Generator Endpoint
@app.post("/generate-docx/", response_class=Response, summary="Generate Word Document (.docx)")
async def generate_docx_endpoint(data: DocxData):
    """
    Receives data in JSON, generates a .docx document,
    and returns the document bytes.
    """
    try:
        # Convert table_rows Pydantic models to list of lists for doc_generator
        table_rows_list = [[row.col1, row.col2, row.col3] for row in data.table_rows]

        docx_bytes = create_document_docx(
            title_text=data.title,
            intro_text=data.introduction,
            items=data.bullet_points,
            table_data=table_rows_list
        )
        # Set Content-Disposition header to suggest a filename
        headers = {
            "Content-Disposition": "attachment; filename=generated_document.docx"
        }
        return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating DOCX: {e}")

# PPTX Generator Endpoint
@app.post("/generate-pptx/", response_class=Response, summary="Generate PowerPoint Presentation (.pptx)")
async def generate_pptx_endpoint(data: PptxData):
    """
    Receives data in JSON, generates a .pptx presentation,
    and returns the presentation bytes.
    """
    try:
        pptx_bytes = create_presentation_pptx(
            title_text=data.title,
            subtitle_text=data.subtitle,
            agenda_items=data.agenda_items,
            features_items=data.features_items
        )
        headers = {
            "Content-Disposition": "attachment; filename=generated_presentation.pptx"
        }
        return Response(content=pptx_bytes, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PPTX: {e}")

# --- Example of how to structure the input data for testing DOCX ---
@app.get("/example-docx-data")
async def get_example_docx_data():
    """
    Returns an example JSON structure for DOCX generation.
    """
    return DocxData(
        title="Mi Documento Personalizado",
        introduction="Aquí va la introducción personalizada del documento, que puede ser más larga.",
        bullet_points=["Punto de interés uno", "Otro punto importante", "Un tercer detalle relevante"],
        table_rows=[
            DocxTableDataRow(col1="Dato 1", col2="Valor X", col3="Nota"),
            DocxTableDataRow(col1="Dato 2", col2="Valor Y", col3="Detalle")
        ]
    )

# --- Example of how to structure the input data for testing PPTX ---
@app.get("/example-pptx-data")
async def get_example_pptx_data():
    """
    Returns an example JSON structure for PPTX generation.
    """
    return PptxData(
        title="Mi Presentación Dinámica",
        subtitle="Un subtítulo creativo para mi proyecto",
        agenda_items=["Primer Tema", "Segundo Tema", "Tercer Tema con Más Info"],
        features_items=["Función A", "Función B", "Función C, la mejor de todas"]
    )
