# IFC Batch Element Deletion Utility

This utility reads a list of target Global IDs (GUIDs) from an Excel spreadsheet and removes the corresponding elements (and their child components) from an IFC model.

---

## Features

- **Safe API Deletion:** Utilizes the official `ifcopenshell.api.run("root.remove_product", ...)` to delete elements instead of basic low-level deletions. This automatically cleans up:
  - Spatially nested objects
  - Geometry and representation definitions
  - Material mappings
  - Empty parent relationships
- **Recursive Decomposition:** Automatically traverses hierarchical structures (like `IfcElementAssembly`). Removing an assembly will recursively find and delete its sub-components (such as beams, columns, plates, and fasteners) to ensure no ghost geometry is left behind in BIM viewers.

---

## Requirements

The utility requires **Python 3** and is configured to run with `uv`.

The dependencies are:
- `ifcopenshell` (IFC parsing library)
- `pandas` (Excel reading)
- `openpyxl` (Engine dependency for Pandas to read `.xlsx` files)

---

## Usage

You can run the utility directly via `uv run` without manually managing a virtual environment or installing packages.

### Run the Utility

Open your terminal, navigate to the repository directory, and run the script with the required CLI arguments:

```powershell
uv run delete-guid --excel "C:\path\to\your\file.xlsx" --ifc-in "C:\path\to\input.ifc" --ifc-out "C:\path\to\output.ifc" --sheet 0
```

### Command-Line Arguments

All parameters are required:
- `--excel`: Path to the Excel spreadsheet (`.xlsx`) containing target GUIDs.
- `--ifc-in`: Path to the source input IFC model file.
- `--ifc-out`: Path where the modified output IFC model will be saved.
- `--sheet`: Name or index (0-based) of the Excel sheet to read.

