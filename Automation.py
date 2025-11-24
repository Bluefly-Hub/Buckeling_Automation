"""
Buckeling Automation Logic
Handles the automation workflow for processing depth and surface weight inputs
"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from Button_Repository import Button_Repository


def run_automation_batch(
    data_list: List[Dict[str, Any]],
    status_callback: Optional[Callable[[str], None]] = None,
    result_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    stop_check: Optional[Callable[[], bool]] = None
) -> List[Dict[str, Any]]:
    """
    Execute automation for a batch of input rows.
    
    Parameters
    ----------
    data_list : List[Dict[str, Any]]
        List of input dictionaries with 'depth' and 'surface_weight' keys
    status_callback : Optional[Callable[[str], None]]
        Function to call with status updates
    result_callback : Optional[Callable[[Dict[str, Any]], None]]
        Function to call with each result as it's generated
    stop_check : Optional[Callable[[], bool]]
        Function that returns True if automation should stop
        
    Returns
    -------
    List[Dict[str, Any]]
        List of result dictionaries containing depth, surface_weight, and foe_value
    """
    results = []
    
    # Connect to application once
    if status_callback:
        status_callback("Connecting to application...")
    repo = Button_Repository()
    #time.sleep(0.5)
    
    # Click Surface Weight button once
    if status_callback:
        status_callback("Selecting Surface Weight option...")
    repo.Surface_Weight_Button()
    #time.sleep(0.5)
    
    total_rows = len(data_list)
    previous_foe = ""

    #Get surface load
    surface_load = repo.Surface_Load()
    Depth_Value_current = repo.Depth_Value_get()
    previous_foe = repo.FOE_Value()
    
    for idx, row in enumerate(data_list):
        # Check if we should stop
        if stop_check and stop_check():
            if status_callback:
                status_callback("Stopped by user")
            break
            
        depth = row.get("depth", "")
        weight = row.get("surface_weight", "")
        
        if status_callback:
            status_callback(f"Processing row {idx + 1}/{total_rows}...")
        


        if surface_load == weight and Depth_Value_current == depth :
            repo.Surface_Weight_Button_Value(float(weight) + 1000)

            #Refresh
            foe_result= repo.FOE_Value()
            repo.Refresh()
            while foe_result == previous_foe:
                time.sleep(1)
                foe_result = repo.FOE_Value()

        repo.Surface_Weight_Button_Value(weight)
        repo.Depth_Value(depth)


        # Set surface weight value
        #repo.Surface_Weight_Button_Value(weight)

        foe_result = repo.FOE_Value()


        #Refresh
        foe_result= repo.FOE_Value()
        repo.Refresh()
        while foe_result == previous_foe:
            time.sleep(1)
            foe_result = repo.FOE_Value()


        # Read FOE value
        #foe_result = repo.FOE_Value()
        
        # Create result record
        result_data = {
            "WOB Buckeling": foe_result
        }
        
        results.append(result_data)
        
        # Notify caller of new result
        if result_callback:
            result_callback(result_data)

        previous_foe = foe_result
    
    if status_callback:
        status_callback(f"Completed {len(results)} rows")
        
    return results


if __name__ == "__main__":
    # Example usage for testing
    test_data = [
        {"depth": "5374", "surface_weight": "138661.3"},
        {"depth": "5206", "surface_weight": "135469.6"},
    ]
    
    def print_status(msg: str):
        print(f"Status: {msg}")
    
    def print_result(result: Dict[str, Any]):
        print(f"Result: {result}")
    
    results = run_automation_batch(
        test_data,
        status_callback=print_status,
        result_callback=print_result
    )
    
    print(f"\nFinal results: {results}")

