"""
IFC GUID Batch Deletion Utility

This script reads a list of target Global IDs (GUIDs) from an Excel sheet and 
removes the corresponding elements from an IFC model. 

It handles hierarchical components (like IfcElementAssembly) recursively to ensure 
that all sub-elements (geometry, plates, fasteners) are deleted, preventing 
dangling geometry in IFC viewers. It also uses the official IfcOpenShell API 
to safely prune relationship pointers.
"""

import ifcopenshell
import ifcopenshell.api as api
import pandas as pd

def get_guids_from_excel(file_path, sheet_name=0):
    """
    Reads GlobalIds (GUIDs) from column D of an Excel file.
    
    Parameters:
    - file_path: Path to the Excel spreadsheet (.xlsx).
    - sheet_name: The sheet to read (defaults to the first sheet).
    
    Excel Row Mapping details:
    - skiprows=1: Skips row 1 (header), meaning the script starts reading data 
      from Row 2.
    - usecols="D": Reads column D which contains the GUID string list.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1, usecols="D")
    # Extract column values, drop empty rows, convert to string list, and return
    return df.iloc[:, 0].dropna().astype(str).tolist()

def batch_remove_elements(input_path, output_path, guids_to_remove):
    """
    Removes a list of elements by their GUIDs from an IFC model and writes a new model.
    
    Parameters:
    - input_path: Path to the source IFC model.
    - output_path: Path where the modified IFC model will be written.
    - guids_to_remove: List or set of GUID strings to delete.
    """
    # Open the IFC model
    model = ifcopenshell.open(input_path)
    
    # Convert GUIDs list to set for O(1) checks during lookups
    guids_set = set(guids_to_remove)
    
    # ---------------------------------------------------------
    # Step 1: Identify targets and resolve child sub-components
    # ---------------------------------------------------------
    elements_to_remove = set()
    initial_elements = []
    
    # Fetch initial elements present in the model matching the target GUIDs
    for guid in guids_set:
        element = model.by_guid(guid)
        if element:
            initial_elements.append(element)
            
    queue = list(initial_elements)
    elements_to_remove.update(initial_elements)
    
    # Recursively traverse decomposition/nesting relationships.
    # This is critical for IfcElementAssembly objects: deleting the assembly object 
    # itself only removes the logical group, leaving the actual physical geometry 
    # (nested IfcBeams, IfcPlates, IfcFasteners) visible. Recurse to delete them all.
    while queue:
        current = queue.pop(0)
        
        # Collect child elements aggregated under the current element (via IfcRelAggregates)
        for rel in getattr(current, "IsDecomposedBy", []) or []:
            for child in rel.RelatedObjects:
                if child not in elements_to_remove:
                    elements_to_remove.add(child)
                    queue.append(child)
                    
        # Collect child elements nested under the current element (via IfcRelNests)
        for rel in getattr(current, "IsNestedBy", []) or []:
            for child in rel.RelatedObjects:
                if child not in elements_to_remove:
                    elements_to_remove.add(child)
                    queue.append(child)
                    
    print(f"Found {len(initial_elements)} initial elements matching Excel GUIDs.")
    print(f"Expanded to {len(elements_to_remove)} total elements (including child components).")
    
    # ---------------------------------------------------------
    # Step 2: Remove elements from the model
    # ---------------------------------------------------------
    removed_count = 0
    for element in elements_to_remove:
        # Check if the element is still valid inside the model.
        # This is a safety guard because removing a parent element or relationship 
        # may have already removed/cleaned up its sub-components internally.
        try:
            model.by_id(element.id())
        except Exception:
            # Skip if the element has already been cleaned up or deleted
            continue
            
        print(f"Removing: {element.is_a()} - {element.GlobalId}")
        try:
            # Use the official IfcOpenShell API to safely remove Products/TypeProducts.
            # This API automatically handles the removal of associated materials, 
            # placements, geometry, and clears empty structural relationships.
            # Directly calling model.remove() on relationships can corrupt the model or crash the program.
            if element.is_a("IfcProduct") or element.is_a("IfcTypeProduct"):
                api.run("root.remove_product", model, product=element)
            else:
                model.remove(element)
            removed_count += 1
        except Exception as e:
            print(f"Error removing element {element.GlobalId}: {e}")
        
    # Write the modified model to the output path
    model.write(output_path)
    print(f"---")
    print(f"Successfully processed. {removed_count} elements removed in total.")


if __name__ == "__main__":
    # Define local file paths
    EXCEL_PATH = r"C:\Users\User\Downloads\UKH GUIDS ALL.xlsx"
    INPUT_IFC_PATH = r"C:\Users\User\Downloads\260511_CP_Produktion.ifc"
    OUTPUT_IFC_PATH = "test.ifc"
    
    # 1. Fetch target GUID list from the Excel spreadsheet
    my_guids = get_guids_from_excel(EXCEL_PATH)
    
    # 2. Perform the batch removal and save the resulting IFC file
    batch_remove_elements(
        INPUT_IFC_PATH,
        OUTPUT_IFC_PATH,
        my_guids
    )