# controller/callbacks.py
from __future__ import annotations

from dash import Input, Output, dash_table, html
import plotly.express as px

from model.finance_model import FinanceTrendsModel


def register_callbacks(app, model: FinanceTrendsModel) -> None:
    """Registra todos os callbacks da aplicação Dash."""

    # --- Gráfico 1: média de nota por produto ---
    @app.callback(
        Output("graph-preferences", "figure"),
        [
            Input("gender-dropdown", "value"),
            Input("age-group-dropdown", "value"),
            Input("duration-dropdown", "value"),
        ],
    )
    def update_preferences_graph(gender, age_group, duration):
        df = model.preferences_summary(
            gender=gender,
            age_group=age_group,
            duration=duration,
        )

        if df.empty:
            return px.bar(title="Sem dados para os filtros selecionados.")

        fig = px.bar(
            df,
            x="Instrument",
            y="Score",
            title="Preferência média por produto de investimento",
            labels={"Instrument": "Produto", "Score": "Nota média (1–7)"},
        )
        fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        return fig

    # --- Gráfico 2: distribuição de fatores (Risk/Returns/Locking Period) ---
    @app.callback(
        Output("graph-factor", "figure"),
        [
            Input("gender-dropdown", "value"),
            Input("age-group-dropdown", "value"),
            Input("duration-dropdown", "value"),
        ],
    )
    def update_factor_graph(gender, age_group, duration):
        df = model.factor_distribution(
            gender=gender,
            age_group=age_group,
            duration=duration,
        )

        if df.empty:
            return px.pie(title="Fator principal não disponível para estes filtros.")

        fig = px.pie(
            df,
            names="Factor",
            values="Count",
            title="Fator principal na escolha do investimento",
        )
        return fig

    # --- Gráfico 3: heatmap produto × duração ---
    @app.callback(
        Output("graph-heatmap", "figure"),
        [
            Input("gender-dropdown", "value"),
            Input("age-group-dropdown", "value"),
        ],
    )
    def update_heatmap(gender, age_group):
        df = model.heatmap_preferences_by_duration(
            gender=gender,
            age_group=age_group,
        )

        if df.empty:
            return px.imshow(
                [[0]],
                labels=dict(x="Produto", y="Duração", color="Score"),
                title="Sem dados suficientes para o heatmap.",
            )

        fig = px.density_heatmap(
            df,
            x="Instrument",
            y="Duration",
            z="Score",
            title="Nota média por produto × duração",
            nbinsx=len(df["Instrument"].unique()),
            nbinsy=len(df["Duration"].unique()),
        )
        return fig

    # --- Tabela de dados filtrados ---
    @app.callback(
        Output("table-container", "children"),
        [
            Input("gender-dropdown", "value"),
            Input("age-group-dropdown", "value"),
            Input("duration-dropdown", "value"),
        ],
    )
    def update_table(gender, age_group, duration):
        df = model.filter_data(
            gender=gender,
            age_group=age_group,
            duration=duration,
        )

        if df.empty:
            return html.P("Nenhum dado para os filtros selecionados.")

        # Limitar para não ficar gigante em aula
        df_small = df.head(200)

        return dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in df_small.columns],
            data=df_small.to_dict("records"),
            page_size=20,
            style_table={"overflowX": "auto"},
        )
