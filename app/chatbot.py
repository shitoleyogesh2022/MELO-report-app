import pandas as pd
from typing import Dict, Any
import re

class AnalysisChatbot:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.commands = {
            'top brands': self._get_top_brands,
            'marketplace stats': self._get_marketplace_stats,
            'weekly trend': self._get_weekly_trend,
            'brand details': self._get_brand_details,
            'help': self._get_help
        }

    def process_query(self, query: str) -> str:
        """Process user query and return appropriate response."""
        query = query.lower()
        
        for command, handler in self.commands.items():
            if command in query:
                return handler(query)
        
        return self._get_help()

    def _get_top_brands(self, query: str) -> str:
        """Get top brands information."""
        n = 5  # default
        if match := re.search(r'top (\d+)', query):
            n = int(match.group(1))
        
        top_brands = self.df.groupby('protected_brand_name')['count'].sum().nlargest(n)
        return f"Top {n} brands by suppression count:\n{top_brands.to_string()}"

    def _get_marketplace_stats(self, query: str) -> str:
        """Get marketplace statistics."""
        stats = self.df.groupby('marketplace_id')['count'].sum().sort_values(ascending=False)
        return f"Marketplace statistics:\n{stats.to_string()}"

    def _get_weekly_trend(self, query: str) -> str:
        """Get weekly trend information."""
        trend = self.df.groupby('Week')['count'].sum()
        return f"Weekly trend:\n{trend.to_string()}"

    def _get_brand_details(self, query: str) -> str:
        """Get details for a specific brand."""
        brands = self.df['protected_brand_name'].unique()
        for brand in brands:
            if brand.lower() in query:
                brand_data = self.df[self.df['protected_brand_name'] == brand]
                summary = brand_data.groupby('Week')['count'].sum()
                return f"Details for {brand}:\n{summary.to_string()}"
        return "Brand not found. Please specify a valid brand name."

    def _get_help(self) -> str:
        """Get help message with available commands."""
        return """
        Available commands:
        - "top brands" or "top N brands"
        - "marketplace stats"
        - "weekly trend"
        - "brand details [brand name]"
        - "help"
        """
