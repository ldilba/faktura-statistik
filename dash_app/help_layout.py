from dash import html, dcc
from dash_iconify import DashIconify


def create_layout():
    """
    Create the layout for the help page.
    """
    return html.Div(
        [
            # Back button
            html.Div(
                [
                    html.A(
                        [
                            DashIconify(
                                icon="heroicons:arrow-left",
                                height=24,
                                color="#2B7FFF",
                            ),
                            html.Span("Zurück", className="ml-2"),
                        ],
                        href="/",
                        className="flex items-center p-2 bg-white rounded-md shadow-md hover:bg-slate-200 w-fit",
                    ),
                ],
                className="m-5",
            ),
            # Help content
            html.Div(
                [
                    html.H1("Hilfe", className="text-2xl font-bold mb-4"),
                    html.P("Hier kommt eine anleitung hin", className="text-lg"),
                ],
                className="m-5 p-5 bg-white rounded-xl shadow-lg",
            ),
        ],
        className="w-full bg-slate-100 min-h-screen",
    )
