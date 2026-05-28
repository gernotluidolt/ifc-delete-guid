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

The utility requires **Python 3** and the following dependencies:

- `ifcopenshell` (IFC parsing library)
- `pandas` (Excel reading)
- `openpyxl` (Engine dependency for Pandas to read `.xlsx` files)

You can install the dependencies using:

```bash
pip install pandas openpyxl ifcopenshell
```

---

## Usage

### 1. Configuration

Open [deleteGuid.py](file:///c:/Users/User/source/repos/bsc_scripts/deleteGUID/deleteGuid.py) and configure the local file paths inside the `__main__` block at the bottom of the script:

```python
if __name__ == "__main__":
    # Define local file paths
    EXCEL_PATH = r"C:\Users\User\Downloads\UKH GUIDS ALL.xlsx"
    INPUT_IFC_PATH = r"C:\Users\User\Downloads\260511_CP_Produktion.ifc"
    OUTPUT_IFC_PATH = "test.ifc"
```

### 2. Custom Excel Row & Column Selection

If your Excel spreadsheet layout changes, you can modify the mapping parameters inside `get_guids_from_excel`:

```python
def get_guids_from_excel(file_path, sheet_name=0):
    # skiprows=1: Skips row 1 (header), starts reading from Row 2.
    # usecols="D": Targets column D (where GUIDs reside).
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, usecols="D")
    return df.iloc[:, 0].dropna().astype(str).tolist()
```

### 3. Run the Utility

Open your terminal or command line, navigate to the repository directory, and run the script:

```powershell
python deleteGUID\deleteGuid.py
```

Upon successful completion, a status report will print the total counts, and the processed model will be saved to your specified output path (e.g., `test.ifc`).
