import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def load_and_process_data(df):
    """Process the raw data into required format"""
    required_columns = [
        'count', 'protected_brand_id', 'protected_brand_name', 'marketplace_id',
        'action_type', 'rule_id', 'template_source', 'infringing_brand',
        'action_date', 'gl_product_group_desc', 'template_sub_type', 'Week'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return None, None
            
    df['Week'] = pd.to_numeric(df['Week'])
    unique_weeks = sorted(df['Week'].unique(), reverse=True)[:4]  # Last 4 weeks only
    return df, unique_weeks

def create_summary_tables(df, unique_weeks):
    """Create summary tables with grand totals"""
    # Weekly summary
    weekly_data = []
    for week in unique_weeks:
        count = df[df['Week'] == week]['count'].sum()
        weekly_data.append({'Week': str(week), 'ASIN Count': count})
    
    weekly_df = pd.DataFrame(weekly_data)
    weekly_df.set_index('Week', inplace=True)
    
    # Add Grand Total
    total = weekly_df['ASIN Count'].sum()
    weekly_df.loc['Grand Total'] = total
    
    # Top 5 brands
    brand_totals = df[df['Week'].isin(unique_weeks)].groupby('protected_brand_name')['count'].sum()
    top_5_brands = brand_totals.nlargest(5).index
    
    brand_weekly = pd.pivot_table(
        df[df['protected_brand_name'].isin(top_5_brands)],
        values='count',
        index='protected_brand_name',
        columns='Week',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ensure correct week columns and order
    brand_weekly = brand_weekly[unique_weeks]
    brand_weekly.columns = brand_weekly.columns.astype(str)
    
    # Add Grand Total column
    brand_weekly['Grand Total'] = brand_weekly.sum(axis=1)
    brand_weekly = brand_weekly.sort_values('Grand Total', ascending=False)
    
    # Add Grand Total row
    brand_weekly.loc['Grand Total'] = brand_weekly.sum()
    
    return weekly_df, brand_weekly

def create_full_pivot_tables(df, unique_weeks):
    """Create complete brand and marketplace pivot tables"""
    # Brand-wise pivot
    brand_pivot = pd.pivot_table(
        df[df['Week'].isin(unique_weeks)],
        values='count',
        index='protected_brand_name',
        columns='Week',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ensure correct week columns and order
    brand_pivot = brand_pivot[unique_weeks]
    brand_pivot.columns = brand_pivot.columns.astype(str)
    
    # Add Grand Total column and sort
    brand_pivot['Grand Total'] = brand_pivot.sum(axis=1)
    brand_pivot = brand_pivot.sort_values('Grand Total', ascending=False)
    
    # Add Grand Total row
    brand_pivot.loc['Grand Total'] = brand_pivot.sum()
    
    # Marketplace-wise pivot
    marketplace_pivot = pd.pivot_table(
        df[df['Week'].isin(unique_weeks)],
        values='count',
        index='marketplace_id',
        columns='Week',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ensure correct week columns and order
    marketplace_pivot = marketplace_pivot[unique_weeks]
    marketplace_pivot.columns = marketplace_pivot.columns.astype(str)
    
    # Add Grand Total column and sort
    marketplace_pivot['Grand Total'] = marketplace_pivot.sum(axis=1)
    marketplace_pivot = marketplace_pivot.sort_values('Grand Total', ascending=False)
    
    # Add Grand Total row
    marketplace_pivot.loc['Grand Total'] = marketplace_pivot.sum()
    
    return brand_pivot, marketplace_pivot

def generate_brand_overview(df, latest_week, top_5_brands):
    """Generate brand overview for top 5 brands"""
    brand_overviews = {}
    
    for brand in top_5_brands[:-1]:  # Exclude Grand Total
        brand_data = df[df['protected_brand_name'] == brand]
        latest_week_data = brand_data[brand_data['Week'] == latest_week]
        
        total_count = latest_week_data['count'].sum()
        
        # Get marketplace information
        marketplace_share = (latest_week_data.groupby('marketplace_id')['count'].sum() / total_count * 100)
        top_marketplace = marketplace_share.nlargest(1)
        
        # Get category information
        category_counts = latest_week_data.groupby('gl_product_group_desc')['count'].sum()
        top_category = category_counts.nlargest(1)
        
        # Get suspect brands
        suspect_brands = latest_week_data.groupby('infringing_brand')['count'].sum().nlargest(2)
        
        brand_overviews[brand] = {
            'total_suppressions': total_count,
            'top_marketplace': top_marketplace,
            'top_category': top_category,
            'suspect_brands': suspect_brands
        }
    
    return brand_overviews

def create_visualizations(weekly_df, brand_weekly, marketplace_pivot):
    """Create all visualizations"""
    # Remove Grand Total for visualizations
    weekly_data = weekly_df.drop('Grand Total')
    brand_data = brand_weekly.drop('Grand Total')
    marketplace_data = marketplace_pivot.drop('Grand Total')
    
    # Weekly trend chart
    fig1 = px.line(
        weekly_data,
        y='ASIN Count',
        title='Weekly Suppression Trend (T4W)',
        markers=True
    )
    
    # Top brands chart
    fig2 = px.bar(
        brand_data.sort_values('Grand Total'),
        y=brand_data.index,
        x='Grand Total',
        title='Top 5 Brands by Total Suppression',
        orientation='h'
    )
    
    # Marketplace distribution
    fig3 = px.pie(
        values=marketplace_data['Grand Total'],
        names=marketplace_data.index,
        title='Suppression Distribution by Marketplace'
    )
    
    # Weekly brand trend
    trend_data = brand_data.drop(columns=['Grand Total']).T
    fig4 = px.line(
        trend_data,
        title='Weekly Brand-wise Trend',
        markers=True
    )
    
    return fig1, fig2, fig3, fig4
def main():
    st.title("ASIN Suppression Analysis Dashboard")
    
    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            # Load and process data
            df = pd.read_excel(uploaded_file)
            processed_df, unique_weeks = load_and_process_data(df)
            
            if processed_df is not None:
                latest_week = max(unique_weeks)
                
                # Create main tables
                weekly_df, brand_weekly = create_summary_tables(processed_df, unique_weeks)
                brand_pivot, marketplace_pivot = create_full_pivot_tables(processed_df, unique_weeks)
                
                # Generate brand overviews
                brand_overviews = generate_brand_overview(processed_df, latest_week, brand_weekly.index)
                
                # Create tabs
                tab1, tab2 = st.tabs(["Main Report", "Visualizations"])
                
                with tab1:
                    # Section 1
                    st.markdown("### Section - 1 : Suppression Overview")
                    current_week_count = float(weekly_df.loc[str(latest_week), 'ASIN Count'])
                    prev_week = str(latest_week - 1)
                    prev_week_count = float(weekly_df.loc[prev_week, 'ASIN Count']) if prev_week in weekly_df.index else 0
                    wow_change = current_week_count - prev_week_count
                    
                    st.markdown(f"""
                    During WK{latest_week}, overall ~{current_week_count/1000:.1f}K ASINs were suppressed, 
                    with a {'reduction' if wow_change < 0 else 'increase'} of ~{abs(wow_change)/1000:.1f}K ASINs w.r.t. previous week.
                    """)
                    
                    # Section 2
                    st.markdown("### Section - 2 : WoW Overall Suppression Trend (T4W)")
                    st.dataframe(weekly_df.style.format({'ASIN Count': '{:,.0f}'}))
                    
                    # Section 3
                    st.markdown("### Section - 3 : Top 5 Suppression Contributing brands (T4W)")
                    st.dataframe(brand_weekly.style.format('{:,.0f}'))
                    
                    # Section 4
                    st.markdown("### Section - 4 : Brand Overview")
                    
                    for i, brand in enumerate(brand_weekly.index[:-1], 1):  # Exclude Grand Total
                        data = brand_overviews.get(brand, {})
                        if data:
                            with st.expander(f"4.{i} - {brand}", expanded=True):
                                overview_text = f"""
                                Total suppressions in Week {latest_week}: ~{data['total_suppressions']/1000:.1f}K ASINs\n
                                """
                                
                                # Add marketplace information
                                for mkp, share in data['top_marketplace'].items():
                                    overview_text += f"Top contributing Marketplace: {mkp} ({share:.2f}%)\n"
                                
                                # Add category information
                                for cat, count in data['top_category'].items():
                                    overview_text += f"\nTop category: {cat} (~{count/1000:.1f}K ASINs)"
                                
                                # Add suspect brands if available
                                if not data['suspect_brands'].empty:
                                    overview_text += "\n\nTop suspect brands:"
                                    for suspect, count in data['suspect_brands'].items():
                                        overview_text += f"\n- {suspect} (~{count/1000:.1f}K ASINs)"
                                
                                st.markdown(overview_text)
                    
                    # Section 5
                    st.markdown("### Section - 5 : Appendix")
                    
                    # 5.1 Brand-wise Suppression
                    st.markdown("#### 5.1 – WoW Brand Wise Suppression Counts (T4W)")
                    st.dataframe(brand_pivot.style.format('{:,.0f}'))
                    
                    # 5.2 Marketplace-wise Suppression
                    st.markdown("#### 5.2 - Marketplace Wise Suppression Counts")
                    st.dataframe(marketplace_pivot.style.format('{:,.0f}'))
                
                with tab2:
                    st.header("Analysis Visualizations")
                    
                    # Create all visualizations
                    fig1, fig2, fig3, fig4 = create_visualizations(weekly_df, brand_weekly, marketplace_pivot)
                    
                    # Display visualizations in an organized layout
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.plotly_chart(fig1, use_container_width=True)
                        st.plotly_chart(fig3, use_container_width=True)
                    
                    with col2:
                        st.plotly_chart(fig2, use_container_width=True)
                        st.plotly_chart(fig4, use_container_width=True)
                    
                    # Add download buttons for the data
                    st.markdown("### Download Data")
                    col1, col2, col3 = st.columns(3)
                    
                    def convert_df_to_csv(df):
                        return df.to_csv().encode('utf-8')
                    
                    with col1:
                        csv_brand = convert_df_to_csv(brand_pivot)
                        st.download_button(
                            "Download Brand-wise Data",
                            csv_brand,
                            "brand_wise_data.csv",
                            "text/csv",
                            key='brand-csv'
                        )
                    
                    with col2:
                        csv_marketplace = convert_df_to_csv(marketplace_pivot)
                        st.download_button(
                            "Download Marketplace Data",
                            csv_marketplace,
                            "marketplace_data.csv",
                            "text/csv",
                            key='marketplace-csv'
                        )
                    
                    with col3:
                        csv_weekly = convert_df_to_csv(weekly_df)
                        st.download_button(
                            "Download Weekly Data",
                            csv_weekly,
                            "weekly_data.csv",
                            "text/csv",
                            key='weekly-csv'
                        )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your Excel file has the correct format")

if __name__ == "__main__":
    main()
