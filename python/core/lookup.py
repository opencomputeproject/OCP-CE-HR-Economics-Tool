"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2025-10-08
"""

"""
Lookup functions for heat exchanger and system data.

This module contains all data lookup functions including the main
lookup_allhx_data function ported from the Jupyter notebook.
"""

from typing import Dict, Optional, Any, Union
import pandas as pd

# Import the data module to access csv_data
from data.loader import get_csv_data, is_csv_loaded
from data.converter import universal_float_convert

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)  

def lookup_allhx_data(wha: float, T1: float, itdt: float, approach: float) -> Optional[Dict[str, Any]]:
    """
    ALLHX lookup using proper data filtering and type consistency.
    
    This function has been ported from the Interactive Analysis Tool.ipynb
    and maintains the same functionality while using the modular data access.
    
    Args:
        wha: System wha in MW
        T1: Inlet temperature in °C
        itdt: Temperature difference in °C  
        approach: Approach value
    
    Returns:
        System data dictionary with keys: F1, F2, T3, T4, hx_cost
        Returns None if not found
        
    Example:
        >>> result = lookup_allhx_data(1, 20, 10, 2)
        >>> if result:
        ...     print(f"F1={result['F1']}, F2={result['F2']}")
    """

    msg = f"lookup_allhx_data"
    logger.info(msg)
    msg = f"Input: wha: {wha}, T1: {T1}, itdt: {itdt}, approach: {approach}"
    logger.info(msg)
       
    T2 = T1 + itdt
    
    # Check if ALLHX data is loaded
    if not is_csv_loaded('ALLHX'):
        logger.error("ALLHX.csv not loaded")
        return None
    
    # Get the dataframe using the data module
    df = get_csv_data('ALLHX')
    if df is None:
        return None
    
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # print(f"ALLHX lookup: wha={wha}, T1={T1}, TempDiff={itdt}, T2={T2}, Approach={approach}")
    
    # Clean data - remove header rows
    df = df[df['wha'].astype(str).str.strip() != 'A']
    df = df[df['wha'].astype(str).str.strip() != 'wha']
    
    # Convert to consistent numeric types using universal converter
    numeric_columns = ['wha', 'T1', 'itdt', 'T2', 'TCSapp', 'F1', 'T4', 'T3', 'F2', 
                       'FWSapp', 'costHX', 'areaHX', 'Hxweight', 'CO2_Footprint']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: float(universal_float_convert(x)))
    
    # Remove invalid rows
    valid_df = df[(df['wha'] > 0) & (df['T1'] > 0) & (df['itdt'] > 0) & (df['TCSapp'] > 0)]
    
    # print(f"Valid data rows: {len(valid_df)}")
    
    if len(valid_df) == 0:
        logger.error("No valid data after conversion")
        return None
    
    # Debug: Show available combinations
    wha_values = sorted(valid_df['wha'].unique())
    T1_values = sorted(valid_df['T1'].unique()) 
    itdt_values = sorted(valid_df['itdt'].unique())
    approach_values = sorted(valid_df['TCSapp'].unique())
    
    # print("Available combinations:")
    # print(f"  wha (wha): {wha_values}")
    # print(f"  T1: {T1_values}")
    # print(f"  TempDiff (itdt): {itdt_values}")
    # print(f"  Approach (TCSapp): {approach_values}")
    
    # Find exact matches
    matches = valid_df[
        (valid_df['wha'] == wha) & 
        (valid_df['T1'] == T1) & 
        (valid_df['itdt'] == itdt) & 
        (valid_df['TCSapp'] == approach)
    ]
    
    # print(f"Exact matches found: {len(matches)}")
    
    if len(matches) == 0:
        logger.warning("No exact match found")
        return None
    
    # Use the first match
    match = matches.iloc[0]
    
    result = {
        'wha': wha,
        'F1': match['F1'],
        'F2': match['F2'], 
        'T1': match['T1'],
        'T2': match['T2'],
        'T3': match['T3'],
        'T4': match['T4'],
        'hx_cost': match['costHX'],
        'approach': approach,
        'itdt': itdt
    }
    
    msg = f"lookup_allhx_data result = {result}"
    logger.info(msg)
    
    # print(f"✅ Match found: F1={result['F1']}, F2={result['F2']}, HX_Cost=€{result['HX_cost']}")
    
    return result

def get_available_approaches() -> list:
    """
    Approach temperatures that have heat exchanger data in ALLHX.csv.

    Rows are cleaned the same way as in lookup_allhx_data, so the list matches
    what a lookup can find. Returns an empty list if ALLHX is not loaded.

    Example:
        >>> get_available_approaches()
        [2.0, 3.0, 5.0]
    """
    if not is_csv_loaded('ALLHX'):
        return []
    df = get_csv_data('ALLHX')
    if df is None:
        return []

    df = df.copy()
    df = df[df['wha'].astype(str).str.strip() != 'A']
    df = df[df['wha'].astype(str).str.strip() != 'wha']
    for col in ['wha', 'T1', 'itdt', 'TCSapp']:
        df[col] = df[col].apply(lambda x: float(universal_float_convert(x)))
    valid_df = df[(df['wha'] > 0) & (df['T1'] > 0) & (df['itdt'] > 0) & (df['TCSapp'] > 0)]
    return sorted(valid_df['TCSapp'].unique().tolist())

def get_lookup_value(csv_name: str, lookup_value: Any, col_index_lookup: int = 0, col_index_return: Union[int, str, list] = 1) -> Any:
    """
    Look up a value in a CSV file based on finding the first value 
    in col_index_lookup that is >= lookup_value, then return the 
    corresponding value from col_index_return.
    
    Parameters:
    csv_name (str): Name of the CSV file (case-insensitive)
    lookup_value: Value to look up (will be compared against col_index_lookup)
    col_index_lookup (int): Index of column to search in (default: 0)
    col_index_return (int/str/list): Index of column(s) to return value from (default: 1)
                                    Can be an integer, column name, or list of integers/names
    
    Returns:
    The value from col_index_return corresponding to the first row where
    col_index_lookup >= lookup_value, or None if not found.
    If col_index_return is a list, returns a dictionary with column names/indices as keys.
    """
    
    # Get the dataframe using the data module
    df = get_csv_data(csv_name)
    if df is None:
        return None
    
    # Convert lookup column to numeric
    lookup_col = df.iloc[:, col_index_lookup].apply(universal_float_convert)
    
    # Find first row where lookup column >= lookup_value
    matching_indices = lookup_col[lookup_col >= lookup_value].index
    
    if len(matching_indices) == 0:
        return None
    
    # Get the first matching row
    match_idx = matching_indices[0]
    matched_row = df.iloc[match_idx]
    
    # Handle different return column specifications
    if isinstance(col_index_return, (list, tuple)):
        # Return multiple columns as a dictionary
        result = {}
        for col in col_index_return:
            if isinstance(col, int):
                result[col] = matched_row.iloc[col]
            else:
                result[col] = matched_row[col]
        return result
    else:
        # Return a single column
        if isinstance(col_index_return, int):
            return matched_row.iloc[col_index_return]
        else:
            return matched_row[col_index_return]