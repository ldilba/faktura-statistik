import plotly.graph_objects as go


def empty_figure():
    return go.Figure(
        layout={
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": "Noch keine Daten geladen",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 18},
                }
            ],
        }
    )
