# diagram_generator.py

import subprocess
import os
import json # Ensure json is imported for potential future uses, though not directly used here

OUTPUT_DOT_FILENAME = "temp_diagram.dot" # Temporary DOT file
OUTPUT_IMAGE_FILENAME = "temp_diagram.png" # Temporary PNG file

def generate_graphviz_dot(data: dict) -> str:
    """
    Generates a Graphviz DOT script from the parsed diagram data,
    with flexible styling based on node and connection types.
    """
    dot_commands = ["digraph G {", "  charset=\"UTF-8\";"]
    dot_commands.append("  rankdir=TB;") # Top to bottom layout
    dot_commands.append("  node [style=filled, fontname=\"Helvetica\", fontsize=10];")
    dot_commands.append("  edge [fontname=\"Helvetica\", fontsize=8];")

    # Main Graph Title at the Top
    company_name_title = data.get("company_name", "Diagrama de Arquitectura")
    dot_commands.append(f'  labeljust="c";') # Center the title
    dot_commands.append(f'  labelloc="t";')
    dot_commands.append(f'  label="{company_name_title}";')
    dot_commands.append(f'  fontsize=20;')

    # Define nodes
    node_id_map = {}
    for node in data["nodes"]:
        graphviz_id = node["id"].replace(" ", "_").replace("-", "_")
        node_id_map[node["id"]] = graphviz_id

        label = node['name']
        shape = "box" # Default shape
        fillcolor = "white" # Default fill color
        fontcolor = "black" # Default font color

        # --- Dynamic Styling based on node type ---
        if node["type"] == "server":
            shape = "ellipse" # Representing cloud with ellipse
            fillcolor = "lightskyblue"
        elif node["type"] == "branch":
            shape = "box"
            fillcolor = "coral"
        elif node["type"] == "headquarters":
            shape = "box"
            fillcolor = "darkgray"
            fontcolor = "white"
        elif node["type"] == "db_management":
            shape = "oval"
            fillcolor = "lightsteelblue"
        elif node["type"] == "database":
            shape = "ellipse" # Representing cloud with ellipse
            fillcolor = "plum"
            label = "BD" # Ensure label is just "BD"

        dot_commands.append(f'  "{graphviz_id}" [label="{label}", shape="{shape}", fillcolor="{fillcolor}", fontcolor="{fontcolor}"];')

    # Define connections
    for conn in data["connections"]:
        source_graphviz_id = node_id_map.get(conn["source_id"])
        target_graphviz_id = node_id_map.get(conn["target_id"])

        if not source_graphviz_id or not target_graphviz_id:
            print(f"Warning: Node ID not found for connection between '{conn['source_id']}' and '{conn['target_id']}'.")
            continue

        edge_label = conn["label"]
        arrowhead = "normal"
        color = "darkgreen" # Default edge color (from original image)
        style = "solid"
        dir_attr = "dir=forward"

        # --- Dynamic Styling based on connection type ---
        if conn["type"] == "sales_report":
            color = "darkgreen"
            edge_label = "Ventas"
        elif conn["type"] == "inventory_report":
            color = "darkred"
            edge_label = "Inventario"
        elif conn["type"] == "master_data_replication":
            color = "blue"
            style = "dashed"
            edge_label = "Datos Maestros"
        elif conn["type"] == "network": # For "IP" connections
            color = "darkgreen"
            edge_label = "IP"
        elif conn["type"] == "local_db_access": # For branch to BD connections
            color = "darkgreen"
            edge_label = "" # No label for these in the original image
        elif conn["type"] == "management_link": # For Yucatan to Gestion BD
            color = "darkgreen"
            edge_label = "" # No label for this in the original image


        dot_commands.append(f'  "{source_graphviz_id}" -> "{target_graphviz_id}" [label="{edge_label}", arrowhead="{arrowhead}", color="{color}", style="{style}" {dir_attr}];')

    # Add the descriptive text at the very bottom, wrapping it within a separate node.
    footer_text = data.get("general_network_description", "").replace('"', '\\"')
    dot_commands.append(f'  footer_description [shape=box, style="filled", fillcolor="lavenderblush", '
                        f'color="purple", fontcolor="black", fontsize=10, '
                        f'label=<'
                        f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">'
                        f'<TR><TD ALIGN="LEFT" WIDTH="500">{footer_text}</TD></TR>' # WIDTH attribute helps with wrapping
                        f'</TABLE>>];')

    # Force the footer_description node to the bottom rank
    dot_commands.append(f'  {{ rank=sink; footer_description; }}')
    # Add an invisible edge to establish ordering from a bottom node to the footer.
    # This helps ensure the footer is placed after all other nodes.
    # We'll use a generic existing node from the bottom row for this.
    # For robust placement, it might be good to ensure at least one node is placed before it.
    # For this diagram, "Yucatan_HQ" is a good candidate to connect invisibly.
    dot_commands.append(f'  Yucatan_HQ -> footer_description [style=invis];')


    dot_commands.append("}")
    return "\n".join(dot_commands)

def render_diagram_to_bytes(dot_script: str, format: str = "png") -> bytes:
    """
    Renders the Graphviz DOT script to an image format and returns the bytes.
    Does not write to a file directly.
    """
    print(f"Attempting to render diagram using Graphviz (format: {format})...")
    try:
        # Use subprocess.run to execute 'dot' command
        result = subprocess.run(
            ["dot", f"-T{format}"],
            input=dot_script.encode("utf-8"), # Pass DOT script via stdin
            capture_output=True,
            check=True,
            text=False # Crucial: set to False to get bytes output
        )
        print("Diagram rendered successfully!")
        return result.stdout
    except FileNotFoundError:
        print("Error: 'dot' command not found. Ensure Graphviz is installed and in PATH.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Error rendering diagram with Graphviz: {e}")
        print("Graphviz stdout:", e.stdout.decode("utf-8", errors='ignore')) # Decode for printing
        print("Graphviz stderr:", e.stderr.decode("utf-8", errors='ignore')) # Decode for printing
        raise
    except Exception as e:
        print(f"An unexpected error occurred during diagram rendering: {e}")
        raise
