import pandas as pd
from io import StringIO
from typing import Optional, Dict, Any, Tuple
import plotly.graph_objects as go


def deserialize_dataframe(json_data: Optional[str]) -> Optional[pd.DataFrame]:
    """
    Deserialize JSON string to pandas DataFrame.

    Args:
        json_data: JSON string representation of DataFrame

    Returns:
        DataFrame or None if data is empty/invalid
    """
    if not json_data:
        return None
    try:
        return pd.read_json(StringIO(json_data))
    except Exception:
        return None


def deserialize_store_data(
    data_all: Optional[Dict[str, Any]], key: str
) -> Optional[pd.DataFrame]:
    """
    Extract and deserialize specific DataFrame from data store.

    Args:
        data_all: Dictionary containing multiple serialized DataFrames
        key: Key to extract from data_all

    Returns:
        DataFrame or None if data is missing/invalid
    """
    if not data_all or key not in data_all:
        return None
    return deserialize_dataframe(data_all[key])


def standard_chart_config(
    displaylogo: bool = False, static_plot: bool = False
) -> Dict[str, Any]:
    """
    Get standard configuration for plotly charts.

    Args:
        displaylogo: Whether to show plotly logo
        static_plot: Whether chart should be static (no interactivity)

    Returns:
        Configuration dictionary for plotly charts
    """
    config = {"displaylogo": displaylogo}
    if static_plot:
        config["staticPlot"] = True
    return config


def apply_transparent_background(fig: go.Figure) -> go.Figure:
    """
    Apply transparent background to plotly figure.

    Args:
        fig: Plotly figure object

    Returns:
        Modified figure with transparent background
    """
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0)"
    )
    return fig


def standard_layout_margins() -> Dict[str, int]:
    """
    Get standard margin settings for charts.

    Returns:
        Dictionary with margin values
    """
    return STANDARD_MARGINS


def create_error_response(message: str) -> Tuple[None, Dict[str, Any], str]:
    """
    Create standardized error response for callbacks.

    Args:
        message: Error message to display

    Returns:
        Tuple of (None, toast_data, error_message)
    """
    return None, {"message": message, "is_open": True}, ""


def validate_required_columns(
    df: pd.DataFrame, required_columns: list
) -> Optional[str]:
    """
    Validate that DataFrame contains all required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        Error message if validation fails, None if successful
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return f"Fehlende Spalten in der Datei: {', '.join(missing_columns)}"
    return None


# Import constants
from common.constants import (
    HOURS_PER_PT,
    DEFAULT_GAUGE_HEIGHT,
    DEFAULT_BAR_HEIGHT,
    STANDARD_MARGINS,
)
