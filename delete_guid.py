"""
IFC GUID Batch Deletion Utility
Reads a list of target Global IDs (GUIDs) from an Excel sheet and 
removes the corresponding elements (including child components) from an IFC model.
"""

import argparse
import sys
import ifcopenshell
import ifcopenshell.api as api
import pandas as pd

def get_guids_from_excel(file_path, sheet_name=0):
    """Reads GUIDs from a column named 'GUID' (case-insensitive) in the first 50 columns."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Locate 'GUID' column index/name in the first 50 columns
    search_limit = min(len(df.columns), 50)
    guid_col = None
    guid_col_idx = None
    
    for idx in range(search_limit):
        col_name = df.columns[idx]
        if str(col_name).strip().upper() == "GUID":
            guid_col = col_name
            guid_col_idx = idx
            break
            
    if guid_col is None:
        raise ValueError(
            f"Could not find a 'GUID' column in the first 50 columns. Checked: {list(df.columns[:search_limit])}"
        )
    
    # Convert index to Excel column letter
    col_letter = (
        chr(ord('A') + guid_col_idx) if guid_col_idx < 26 
        else chr(ord('A') + (guid_col_idx // 26) - 1) + chr(ord('A') + (guid_col_idx % 26))
    )
    print(f"Found 'GUID' column at index {guid_col_idx} (Column {col_letter}).")
    
    return df[guid_col].dropna().astype(str).tolist()

def batch_remove_elements(input_path, output_path, guids_to_remove):
    """Recursively removes elements matching GUIDs from an IFC model."""
    model = ifcopenshell.open(input_path)
    guids_set = set(guids_to_remove)
    
    # Identify target elements
    elements_to_remove = set()
    initial_elements = []
    
    for guid in guids_set:
        try:
            element = model.by_guid(guid)
            if element:
                initial_elements.append(element)
        except Exception as e:
            print(f"Warning: GUID {guid} not found in model: {e}")
            
    queue = list(initial_elements)
    elements_to_remove.update(initial_elements)
    
    # Recursively traverse decomposition/nesting relationships (e.g. IfcElementAssembly)
    while queue:
        current = queue.pop(0)
        # Collect child elements from IfcRelAggregates and IfcRelNests
        for rel in getattr(current, "IsDecomposedBy", []) or []:
            for child in rel.RelatedObjects:
                if child not in elements_to_remove:
                    elements_to_remove.add(child)
                    queue.append(child)
                    
        for rel in getattr(current, "IsNestedBy", []) or []:
            for child in rel.RelatedObjects:
                if child not in elements_to_remove:
                    elements_to_remove.add(child)
                    queue.append(child)
                    
    print(f"Initial targets: {len(initial_elements)}. Expanded to {len(elements_to_remove)} elements.")
    
    # Remove elements using official IfcOpenShell API to clean up relationships and geometry
    removed_count = 0
    for element in elements_to_remove:
        try:
            model.by_id(element.id())  # Verify validity
        except Exception:
            continue
            
        print(f"Removing: {element.is_a()} - {element.GlobalId}")
        try:
            if element.is_a("IfcProduct") or element.is_a("IfcTypeProduct"):
                api.run("root.remove_product", model, product=element)
            else:
                model.remove(element)
            removed_count += 1
        except Exception as e:
            print(f"Error removing {element.GlobalId}: {e}")
        
    model.write(output_path)
    print(f"---\nProcessed. Total {removed_count} elements removed.")

def main():
    parser = argparse.ArgumentParser(description="IFC GUID Batch Deletion CLI")
    parser.add_argument("--excel", required=True, help="Path to Excel sheet (.xlsx)")
    parser.add_argument("--ifc-in", required=True, help="Path to source IFC file")
    parser.add_argument("--ifc-out", required=True, help="Path to output modified IFC file")
    parser.add_argument("--sheet", required=True, help="Name or index (0-based) of the sheet")
    
    args = parser.parse_args()
    sheet_val = int(args.sheet) if args.sheet.isdigit() else args.sheet
        
    try:
        print(f"Loading Excel: {args.excel} (Sheet: {sheet_val})...")
        my_guids = get_guids_from_excel(args.excel, sheet_name=sheet_val)
        
        print(f"Processing IFC. Input: {args.ifc_in}, Output: {args.ifc_out}...")
        batch_remove_elements(args.ifc_in, args.ifc_out, my_guids)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
