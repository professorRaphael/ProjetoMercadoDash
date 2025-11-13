# model/finance_model.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd


@dataclass
class FinanceTrendsModel:
    """Camada de acesso e transformação dos dados Finance_Trends.csv."""

    csv_path: Path

    # Colunas de "nota" (1–7) para cada produto de investimento
    INV_SCORE_COLS: Sequence[str] = (
        "Mutual_Funds",
        "Equity_Market",
        "Debentures",
        "Government_Bonds",
        "Fixed_Deposits",
        "PPF",
        "Gold",
    )

    def __post_init__(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV não encontrado em: {self.csv_path}")

        df = pd.read_csv(self.csv_path)

        # Garantir numérico para idade
        if "age" in df.columns:
            df["age"] = pd.to_numeric(df["age"], errors="coerce")

            # Faixas etárias para filtro (ajuste se quiser outras faixas)
            df["age_group"] = pd.cut(
                df["age"],
                bins=[17, 25, 30, 40],  # 18–25, 26–30, 31–40
                labels=["18-25", "26-30", "31-40"],
            )
        else:
            df["age_group"] = pd.NA

        self.df = df

    # ---------- Métodos de "consulta" para popular filtros ----------

    def get_available_genders(self) -> list[str]:
        if "gender" not in self.df.columns:
            return []
        return self.df["gender"].dropna().astype(str).sort_values().unique().tolist()

    def get_available_age_groups(self) -> list[str]:
        if "age_group" not in self.df.columns:
            return []
        series = self.df["age_group"].dropna()
        if not pd.api.types.is_categorical_dtype(series):
            # fallback se algo mudar
            return sorted(series.astype(str).unique().tolist())
        return [str(cat) for cat in series.cat.categories]

    def get_available_durations(self) -> list[str]:
        if "Duration" not in self.df.columns:
            return []
        return self.df["Duration"].dropna().astype(str).sort_values().unique().tolist()

    # ---------- Filtro base ----------

    def filter_data(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
        duration: Optional[str] = None,
    ) -> pd.DataFrame:
        df = self.df.copy()

        if gender and "gender" in df.columns:
            df = df[df["gender"] == gender]

        if age_group and "age_group" in df.columns:
            df = df[df["age_group"].astype(str) == age_group]

        if duration and "Duration" in df.columns:
            df = df[df["Duration"] == duration]

        return df

    # ---------- Agregações para os gráficos ----------

    def preferences_summary(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
        duration: Optional[str] = None,
    ) -> pd.DataFrame:
        """Média de nota (1–7) por produto de investimento."""
        df = self.filter_data(gender, age_group, duration)

        cols = [c for c in self.INV_SCORE_COLS if c in df.columns]
        if not cols:
            return pd.DataFrame()

        tidy = df[cols].melt(
            var_name="Instrument",
            value_name="Score",
        )

        grouped = (
            tidy.groupby("Instrument")["Score"]
            .mean()
            .reset_index()
            .sort_values("Score", ascending=False)
        )
        return grouped

    def factor_distribution(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
        duration: Optional[str] = None,
    ) -> pd.DataFrame:
        """Distribuição do fator principal (Risk/Returns/Locking Period)."""
        df = self.filter_data(gender, age_group, duration)
        if "Factor" not in df.columns:
            return pd.DataFrame()

        grouped = (
            df.groupby("Factor")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )
        return grouped

    def duration_distribution(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
    ) -> pd.DataFrame:
        """Distribuição das durações de investimento."""
        df = self.filter_data(gender, age_group, duration=None)
        if "Duration" not in df.columns:
            return pd.DataFrame()

        grouped = (
            df.groupby("Duration")
            .size()
            .reset_index(name="Count")
            .sort_values("Duration")
        )
        return grouped

    def source_distribution(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
        duration: Optional[str] = None,
    ) -> pd.DataFrame:
        """De onde a pessoa se informa (Source)."""
        df = self.filter_data(gender, age_group, duration)
        if "Source" not in df.columns:
            return pd.DataFrame()

        grouped = (
            df.groupby("Source")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )
        return grouped

    def heatmap_preferences_by_duration(
        self,
        gender: Optional[str] = None,
        age_group: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Média de nota por produto × duração — pronto para virar heatmap.
        """
        df = self.filter_data(gender, age_group, duration=None)
        if "Duration" not in df.columns:
            return pd.DataFrame()

        cols = [c for c in self.INV_SCORE_COLS if c in df.columns]
        if not cols:
            return pd.DataFrame()

        tidy = df[["Duration"] + list(cols)].melt(
            id_vars="Duration",
            var_name="Instrument",
            value_name="Score",
        )

        grouped = tidy.groupby(["Duration", "Instrument"])["Score"].mean().reset_index()
        return grouped
