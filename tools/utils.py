from typing import List, Tuple, Union
import pandas as pd

from openpyxl.utils import column_index_from_string
# 处理列索引，统一转为列索引
def col_to_colidx(df: pd.DataFrame, col_param: Union[int, str]) -> int:
    if isinstance(col_param, int):
        if 0 <= col_param < len(df.columns):
            return col_param
        else:
            raise ValueError(f"column index {col_param} out of range, should be between 0 and {len(df.columns) - 1}")
        
    elif isinstance(col_param, str):
        if col_param in df.columns:
            return df.columns.get_loc(col_param)
        elif col_param.isalpha():
            col_idx = column_index_from_string(col_param.upper()) - 1
            if col_idx >= len(df.columns) or col_idx < 0:
                raise ValueError(f"column letter {col_param} out of range, should be between 0 and {len(df.columns) - 1}")
            return col_idx
        else:
            raise ValueError(f"invalid column name: {col_param}")
    else:
        raise ValueError(f"invalid column parameter type: {type(col_param)}")

