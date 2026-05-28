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
- **Robust Memory Handling:** Performs checks using `model.by_id()` before deleting, preventing duplicate deletion attempts which crash the Python/C++ interface wrapper.
- **Custom Excel Parsing:** Configured to easily adjust column and row offets.

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

### Custom Excel Row & Column Selection

If your Excel spreadsheet layout changes, you can modify the mapping parameters inside `get_guids_from_excel` in [delete_guid.py](file:///c:/Users/User/source/repos/ifc-delete-guid/delete_guid.py):

```python
def get_guids_from_excel(file_path, sheet_name=0):
    # Read the first row (header row) without headers to find the GUID column index
    header_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1, header=None)
    # Search limit is set to first 50 columns
    # ...
```
