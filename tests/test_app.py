import pytest
import pandas as pd
from app.data_processor import DataProcessor
from app.visualization import Visualizer
from app.chatbot import AnalysisChatbot

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'count': [1, 2, 3],
        'protected_brand_name': ['Brand1', 'Brand2', 'Brand1'],
        'marketplace_id': ['US', 'UK', 'US'],
        'Week': [1, 1, 2],
        'action_date': ['2024-01-01', '2024-01-02', '2024-01-03']
    })

def test_data_processor_load(sample_data):
    processor = DataProcessor()
    processor.df = sample_data
    processor._create_pivot_tables()
    assert processor.brand_pivot is not None
    assert processor.marketplace_pivot is not None

def test_chatbot_response(sample_data):
    chatbot = AnalysisChatbot(sample_data)
    response = chatbot.process_query("top brands")
    assert "Brand1" in response
    assert "Brand2" in response
