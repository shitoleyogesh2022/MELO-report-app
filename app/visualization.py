import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple, List
import pandas as pd

class Visualizer:
    @staticmethod
    def create_trend_chart(df: pd.DataFrame) -> go.Figure:
        """Create weekly trend chart."""
        weekly_trend = df.groupby('Week')['count'].sum()
        fig = px.line(
            weekly_trend,
            title='Weekly Suppression Trend',
            labels={'value': 'Suppression Count', 'Week': 'Week Number'}
        )
        return fig

    @staticmethod
    def create_brand_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Create top brands chart."""
        top_brands = df.groupby('protected_brand_name')['count'].sum().nlargest(top_n)
        fig = px.bar(
            top_brands,
            title=f'Top {top_n} Brands by Suppression Count',
            labels={'value': 'Suppression Count', 'protected_brand_name': 'Brand'}
        )
        return fig

    @staticmethod
    def create_marketplace_chart(df: pd.DataFrame) -> go.Figure:
        """Create marketplace distribution chart."""
        marketplace_data = df.groupby('marketplace_id')['count'].sum()
        fig = px.pie(
            values=marketplace_data.values,
            names=marketplace_data.index,
            title='Suppression Distribution by Marketplace'
        )
        return fig
