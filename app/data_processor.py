import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.df = None
        self.brand_pivot = None
        self.marketplace_pivot = None

    def load_data(self, file_path: str) -> None:
        """Load and preprocess the data."""
        try:
            self.df = pd.read_excel(file_path)
            self.df['action_date'] = pd.to_datetime(self.df['action_date'])
            self._create_pivot_tables()
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _create_pivot_tables(self) -> None:
        """Create pivot tables for analysis."""
        try:
            self.brand_pivot = pd.pivot_table(
                self.df,
                values='count',
                index='protected_brand_name',
                columns='Week',
                aggfunc='sum',
                fill_value=0
            )

            self.marketplace_pivot = pd.pivot_table(
                self.df,
                values='count',
                index='marketplace_id',
                columns='Week',
                aggfunc='sum',
                fill_value=0
            )
        except Exception as e:
            logger.error(f"Error creating pivot tables: {str(e)}")
            raise

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'total_suppressions': self.df['count'].sum(),
            'total_brands': self.df['protected_brand_name'].nunique(),
            'total_marketplaces': self.df['marketplace_id'].nunique(),
            'date_range': (self.df['action_date'].min(), self.df['action_date'].max())
        }

    def filter_data(self, weeks=None, brands=None, marketplaces=None) -> pd.DataFrame:
        """Filter data based on selected criteria."""
        filtered_df = self.df.copy()
        
        if weeks:
            filtered_df = filtered_df[filtered_df['Week'].isin(weeks)]
        if brands:
            filtered_df = filtered_df[filtered_df['protected_brand_name'].isin(brands)]
        if marketplaces:
            filtered_df = filtered_df[filtered_df['marketplace_id'].isin(marketplaces)]
            
        return filtered_df
