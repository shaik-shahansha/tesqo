import openpyxl
from pathlib import Path


def load_excel(filepath: str, sheet: str = None) -> list:
    """
    Read an Excel file and return a list of row dicts keyed by header names.

    Args:
        filepath: Path to the .xlsx file (relative to project root).
        sheet:    Sheet name to read. If None, reads the active/first sheet.

    Returns:
        List of dicts, one per non-blank data row.

    Example:
        rows = load_excel("data/test_data.xlsx", sheet="Login")
        # rows = [{"username": "alice", "password": "pass1", ...}, ...]
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {filepath}\n"
            "Create it or copy data/test_data.xlsx.example → data/test_data.xlsx"
        )

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet] if sheet else wb.active

    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(next(rows_iter))]

    result = []
    for row in rows_iter:
        if any(cell is not None for cell in row):       # skip completely blank rows
            result.append(dict(zip(headers, row)))

    return result
