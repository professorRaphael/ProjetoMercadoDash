# app.py
from __future__ import annotations

from pathlib import Path

from dash import Dash

from controller.callbacks import register_callbacks
from model.finance_model import FinanceTrendsModel
from view.layout import create_layout


def create_app() -> Dash:
    csv_path = Path("assets") / "Finance_Trends.csv"  # <- coloque o CSV aqui

    model = FinanceTrendsModel(csv_path=csv_path)

    app = Dash(
        __name__,
        title="Finance Trends – Dashboard",
    )

    app.layout = create_layout(model)
    register_callbacks(app, model)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
