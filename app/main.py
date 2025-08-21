import streamlit as st
import pandas as pd
from data_processor import DataProcessor
from visualization import Visualizer
from chatbot import AnalysisChatbot
import logging
from typing import Optional
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ASINAnalyalysisApp:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        self.chatbot: Optional[AnalysisChatbot] = None
        self.load_config()

    def load_config(self):
        """Load configuration from yaml file."""
        try:
            with open('config/config.yaml') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            self.config = {}

    def run(self):
        """Run the Streamlit application."""
        st.title("ASIN Suppression Analysis Dashboard")

        # Initialize session state
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False

        # File uploader
        uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
        if uploaded_file is not None:
            try:
                self.data_processor.load_data(uploaded_file)
                self.chatbot = AnalysisChatbot(self.data_processor.df)
                st.session_state.data_loaded = True
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return

        if not st.session_state.data_loaded:
            st.warning("Please upload a file to begin analysis.")
            return

        # Sidebar navigation
        page = st.sidebar.radio("Navigation", ["Overview", "Detailed Analysis", "Chatbot"])

        if page == "Overview":
            self.show_overview()
        elif page == "Detailed Analysis":
            self.show_detailed_analysis()
        else:
            self.show_chatbot()

    def show_overview(self):
        """Display overview dashboard."""
        st.header("Overview Dashboard")

        # Summary statistics
        stats = self.data_processor.get_summary_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Suppressions", f"{stats['total_suppressions']:,}")
        col2.metric("Total Brands", stats['total_brands'])
        col3.metric("Total Marketplaces", stats['total_marketplaces'])

        # Charts
        st.plotly_chart(self.visualizer.create_trend_chart(self.data_processor.df))
        st.plotly_chart(self.visualizer.create_brand_chart(self.data_processor.df))
        st.plotly_chart(self.visualizer.create_marketplace_chart(self.data_processor.df))

    def show_detailed_analysis(self):
        """Display detailed analysis page."""
        st.header("Detailed Analysis")

        # Filters
        weeks = st.multiselect(
            "Select Weeks",
            options=sorted(self.data_processor.df['Week'].unique())
        )
        brands = st.multiselect(
            "Select Brands",
            options=sorted(self.data_processor.df['protected_brand_name'].unique())
        )

        # Filter data
        filtered_df = self.data_processor.filter_data(weeks=weeks, brands=brands)

        # Display pivot tables
        st.subheader("Brand-wise Weekly Suppression")
        st.dataframe(self.data_processor.brand_pivot)
        
        st.subheader("Marketplace-wise Weekly Suppression")
        st.dataframe(self.data_processor.marketplace_pivot)

        # Export options
        if st.button("Export to CSV"):
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download CSV",
                csv,
                "suppression_analysis.csv",
                "text/csv"
            )

    def show_chatbot(self):
        """Display chatbot interface."""
        st.header("Analysis Chatbot")
        st.write("Ask questions about the suppression data!")

        query = st.text_input("Enter your question:")
        if query:
            response = self.chatbot.process_query(query)
            st.write(response)

if __name__ == "__main__":
    app = ASINAnalysisApp()
    app.run()
