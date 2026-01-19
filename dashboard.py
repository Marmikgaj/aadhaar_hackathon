import streamlit as st
from src.loader import load_data, get_state_list, get_district_list
from src.plots import plot_trend, plot_bar_distribution
import plotly.express as px
import pandas as pd
from ydata_profiling import ProfileReport
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Aadhaar Insights Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

# Load Data
with st.spinner('Loading Aadhaar Datasets...'):
    data = load_data()

if data is None:
    st.error("Failed to load data. Please check raw files.")
    st.stop()



enrolment_df = data['enrolment']
demographic_df = data['demographic']
biometric_df = data['biometric']

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Enrolment Analysis", "Demographic Updates", "Biometric Updates", "Visual Analysis", "Demand Forecasting", "MBU Compliance Tracker", "Automated Profiling"])

st.sidebar.header("Global Filters")
# State Filter
state_list = ["All"] + get_state_list(enrolment_df)
selected_state = st.sidebar.selectbox("Select State", state_list)

# District Filter (Dynamic)
if selected_state != "All":
    district_list = ["All"] + get_district_list(enrolment_df, selected_state)
    selected_district = st.sidebar.selectbox("Select District", district_list)
else:
    selected_district = "All"

# Helper to filter data
def filter_data(df):
    temp_df = df.copy()
    if selected_state != "All":
        temp_df = temp_df[temp_df['state'] == selected_state]
        if selected_district != "All":
            temp_df = temp_df[temp_df['district'] == selected_district]
    return temp_df

# Main Content
if page == "Overview":
    st.title("Aadhaar Enrolment & Update Insights")
    st.markdown("### Unlocking Societal Trends in Aadhaar Enrolment and Updates")
    
    # Filter data
    filtered_enrolment = filter_data(enrolment_df)
    filtered_demographic = filter_data(demographic_df)
    filtered_biometric = filter_data(biometric_df)
    
    # 1. Key Metrics (KPIs)
    col1, col2, col3 = st.columns(3)
    total_enrolments = filtered_enrolment[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum()
    total_demographic_updates = filtered_demographic[['demo_age_5_17', 'demo_age_17_']].sum().sum()
    total_biometric_updates = filtered_biometric[['bio_age_5_17', 'bio_age_17_']].sum().sum()

    col1.metric("Total Enrolments", f"{total_enrolments:,.0f}")
    col2.metric("Demographic Updates", f"{total_demographic_updates:,.0f}")
    col3.metric("Biometric Updates", f"{total_biometric_updates:,.0f}")
    st.markdown("---")

    col_1, col_2 = st.columns(2)
    
    # 2. Total Activity Trend (Combined Line Chart)
    with col_1:
         # Aggregate by date
        enrol_trend = filtered_enrolment.groupby('date')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Enrolments')
        demo_trend = filtered_demographic.groupby('date')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='Demographic Updates')
        bio_trend = filtered_biometric.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).reset_index(name='Biometric Updates')
        
        # Merge trends
        combined_trend = pd.merge(enrol_trend, demo_trend, on='date', how='outer').merge(bio_trend, on='date', how='outer').fillna(0)
        combined_melted = combined_trend.melt(id_vars='date', var_name='Activity Type', value_name='Count')
        
        st.subheader("Total Activity Trend")
        fig_trend = plot_trend(combined_melted, 'date', 'Count', 'Daily Activity by Type', color='Activity Type')
        st.plotly_chart(fig_trend, use_container_width=True)

    # 3. Activity Composition (Donut Chart)
    with col_2:
        st.subheader("Activity Composition")
        activity_data = pd.DataFrame({
            'Activity': ['Enrolments', 'Demographic Updates', 'Biometric Updates'],
            'Count': [total_enrolments, total_demographic_updates, total_biometric_updates]
        })
        from src.plots import plot_donut
        fig_donut = plot_donut(activity_data, 'Count', 'Activity', 'Share of Total Activity')
        st.plotly_chart(fig_donut, use_container_width=True)

    col_3, col_4 = st.columns(2)

    # 4. Top States Leaderboard (Bar Chart) - Only meaningful if "All" states selected or analysing districts
    with col_3:
        if selected_state == "All":
            st.subheader("Top 10 States by Total Activity")
            # Calculate total activity per state
            e_state = enrolment_df.groupby('state')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1)
            d_state = demographic_df.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1)
            b_state = biometric_df.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1)
            
            total_state = (e_state.add(d_state, fill_value=0).add(b_state, fill_value=0)).reset_index(name='Total Activity')
            top_states = total_state.sort_values(by='Total Activity', ascending=False).head(10)
            fig_bar = plot_bar_distribution(top_states, 'state', 'Total Activity', 'Top 10 States')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.subheader("Top 10 Districts by Total Activity")
            e_dist = filtered_enrolment.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1)
            d_dist = filtered_demographic.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1)
            b_dist = filtered_biometric.groupby('district')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1)
            
            total_dist = (e_dist.add(d_dist, fill_value=0).add(b_dist, fill_value=0)).reset_index(name='Total Activity')
            top_dist = total_dist.sort_values(by='Total Activity', ascending=False).head(10)
            fig_bar = plot_bar_distribution(top_dist, 'district', 'Total Activity', 'Top 10 Districts')
            st.plotly_chart(fig_bar, use_container_width=True)

    # 5. Least Active Regions (Bar Chart)
    with col_4:
        if selected_state == "All":
            st.subheader("Bottom 10 States (Least Active)")
            bottom_states = total_state.sort_values(by='Total Activity', ascending=True).head(10)
            fig_bar_low = plot_bar_distribution(bottom_states, 'state', 'Total Activity', 'Least Active States')
            st.plotly_chart(fig_bar_low, use_container_width=True)
        else:
            st.subheader("Bottom 10 Districts (Least Active)")
            bottom_dist = total_dist.sort_values(by='Total Activity', ascending=True).head(10)
            fig_bar_low = plot_bar_distribution(bottom_dist, 'district', 'Total Activity', 'Least Active Districts')
            st.plotly_chart(fig_bar_low, use_container_width=True)


elif page == "Enrolment Analysis":
    st.title("Enrolment Analysis")
    filtered_df = filter_data(enrolment_df)
    
    col1, col2 = st.columns(2)
    
    # 1. Trend Analysis (Line)
    with col1:
        st.subheader("Enrolment Trends Over Time")
        daily_trends = filtered_df.groupby('date')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().reset_index()
        daily_trends_melted = daily_trends.melt(id_vars='date', var_name='Age Group', value_name='Count')
        fig_trend = plot_trend(daily_trends_melted, 'date', 'Count', 'Enrolments by Age Group', color='Age Group')
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # 2. Age Distribution (Pie)
    with col2:
        st.subheader("Age Group Distribution")
        total_by_age = filtered_df[['age_0_5', 'age_5_17', 'age_18_greater']].sum().reset_index()
        total_by_age.columns = ['Age Group', 'Total']
        fig_pie = px.pie(total_by_age, values='Total', names='Age Group', title='Enrolment Share by Age', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

    col3, col4 = st.columns(2)

    # 3. Geographic Hotspots (Bar)
    with col3:
        group_col = 'district' if selected_state != 'All' else 'state'
        st.subheader(f"Top 10 {group_col.title()}s by Enrolment")
        geo_group = filtered_df.groupby(group_col)[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Total')
        top_geo = geo_group.sort_values(by='Total', ascending=False).head(10)
        fig_geo = plot_bar_distribution(top_geo, group_col, 'Total', f'Top 10 {group_col.title()}s')
        st.plotly_chart(fig_geo, use_container_width=True)

    # 4. Performance Heatmap (Treemap)
    with col4:
        st.subheader("Enrolment Volume Heatmap")
        from src.plots import plot_treemap
        # If All states, show State > District hierarchy. If specific state, show District hierarchy
        if selected_state == "All":
            path = ['state', 'district']
            # Limit to top 500 rows for performance in treemap if dataset is huge, or aggregate
            treemap_df = filtered_df.groupby(['state', 'district'])[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Total')
            # Filter zero values
            treemap_df = treemap_df[treemap_df['Total'] > 0]
            fig_tree = plot_treemap(treemap_df, path, 'Total', 'Enrolment Distribution')
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            path = ['district']
            treemap_df = filtered_df.groupby(['district'])[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Total')
            treemap_df = treemap_df[treemap_df['Total'] > 0]
            fig_tree = plot_treemap(treemap_df, path, 'Total', 'District Enrolment Distribution')
            st.plotly_chart(fig_tree, use_container_width=True)

elif page == "Demographic Updates":
    st.title("Demographic Update Trends")
    filtered_df = filter_data(demographic_df)
    
    col1, col2 = st.columns(2)

    # 1. Update Trends (Line)
    with col1:
        st.subheader("Update Activity Over Time")
        daily_updates = filtered_df.groupby('date')[['demo_age_5_17', 'demo_age_17_']].sum().reset_index()
        daily_updates_melted = daily_updates.melt(id_vars='date', var_name='Age Category', value_name='Updates')
        fig = plot_trend(daily_updates_melted, 'date', 'Updates', 'Demographic Updates vs Time', color='Age Category')
        st.plotly_chart(fig, use_container_width=True)

    # 2. Age Composition (Pie)
    with col2:
        st.subheader("Updates by Age Category")
        total_by_age = filtered_df[['demo_age_5_17', 'demo_age_17_']].sum().reset_index()
        total_by_age.columns = ['Age Group', 'Total']
        fig_pie = px.pie(total_by_age, values='Total', names='Age Group', title='Demographic Updates Share', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

    col3, col4 = st.columns(2)

    # 3. Geographic Spread (Bar)
    with col3:
        group_col = 'district' if selected_state != 'All' else 'state'
        st.subheader(f"Top 10 {group_col.title()}s for Updates")
        geo_group = filtered_df.groupby(group_col)[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='Total')
        top_geo = geo_group.sort_values(by='Total', ascending=False).head(10)
        fig_geo = plot_bar_distribution(top_geo, group_col, 'Total', f'Highest Update Regions ({group_col.title()})')
        st.plotly_chart(fig_geo, use_container_width=True)

    # 4. Correlation Analysis (Scatter) - Enrolment vs Updates
    with col4:
        st.subheader("Correlation: Enrolment vs Updates")
        # Need to merge enrolment and demographic data on district level
        # Aggregate filtered enrolment
        filt_enrol = filter_data(enrolment_df)
        e_agg = filt_enrol.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Enrolment_Count')
        d_agg = filtered_df.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='Update_Count')
        
        merged_scatter = pd.merge(e_agg, d_agg, on='district')
        from src.plots import plot_scatter
        fig_scatter = plot_scatter(merged_scatter, 'Enrolment_Count', 'Update_Count', 'Enrolment vs Update Volume', hover_data=['district'])
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 5. Migration/Movement Patterns (Sunburst)
    st.markdown("---")
    st.subheader("Migration Pattern Analysis (State > District > Age Group)")
    st.info("Visualizing where demographic updates (often linked to relocation) are happening, broken down by Age Group.")
    
    # Prepare data for Sunburst
    # Use filtered_df to respect active filters
    move_df = filtered_df.copy()
    
    # Melt to get Age Group as a dimension
    move_melted = move_df.melt(id_vars=['state', 'district'], 
                               value_vars=['demo_age_5_17', 'demo_age_17_'], 
                               var_name='Age_Group', value_name='Count')
    
    # Rename Age Groups for better readability
    move_melted['Age_Group'] = move_melted['Age_Group'].replace({
        'demo_age_5_17': 'Age 5-17',
        'demo_age_17_': 'Age 17+'
    })
    
    # Aggregate data
    if selected_state == "All":
        # Group by State -> District -> Age Group
        move_agg = move_melted.groupby(['state', 'district', 'Age_Group'])['Count'].sum().reset_index()
        # Filter zero counts
        move_agg = move_agg[move_agg['Count'] > 0]
        
        # Use Sunburst with limited depth or top values if needed, but plotting all for now
        fig_sun = px.sunburst(move_agg, path=['state', 'district', 'Age_Group'], values='Count',
                              title="Demographic Updates Hierarchy (Migration Proxy)",
                              color='Count', color_continuous_scale='RdBu_r')
    else:
        # Group by District -> Age Group (State is fixed)
        move_agg = move_melted.groupby(['district', 'Age_Group'])['Count'].sum().reset_index()
        move_agg = move_agg[move_agg['Count'] > 0]
        
        fig_sun = px.sunburst(move_agg, path=['district', 'Age_Group'], values='Count',
                              title=f"Demographic Updates Hierarchy in {selected_state}",
                              color='Count', color_continuous_scale='RdBu_r')
        
    st.plotly_chart(fig_sun, use_container_width=True)


elif page == "Biometric Updates":
    st.title("Biometric Update Trends")
    filtered_df = filter_data(biometric_df)
    
    col1, col2 = st.columns(2)

    # 1. Biometric Trends (Line)
    with col1:
        st.subheader("Biometric Updates Over Time")
        daily_bio = filtered_df.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum().reset_index()
        daily_bio_melted = daily_bio.melt(id_vars='date', var_name='Age Category', value_name='Updates')
        fig = plot_trend(daily_bio_melted, 'date', 'Updates', 'Biometric Updates vs Time', color='Age Category')
        st.plotly_chart(fig, use_container_width=True)

    # 2. Age Segmentation (Pie)
    with col2:
        st.subheader("Biometric Updates by Age")
        total_by_age = filtered_df[['bio_age_5_17', 'bio_age_17_']].sum().reset_index()
        total_by_age.columns = ['Age Group', 'Total']
        fig_pie = px.pie(total_by_age, values='Total', names='Age Group', title='Biometric Updates Share', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

    col3, col4 = st.columns(2)

    # 3. Geographic Focus (Bar)
    with col3:
        group_col = 'district' if selected_state != 'All' else 'state'
        st.subheader(f"Top 10 {group_col.title()}s for Biometrics")
        geo_group = filtered_df.groupby(group_col)[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).reset_index(name='Total')
        top_geo = geo_group.sort_values(by='Total', ascending=False).head(10)
        fig_geo = plot_bar_distribution(top_geo, group_col, 'Total', f'Highest Biometric Update Areas')
        st.plotly_chart(fig_geo, use_container_width=True)

    # 4. Update Intensity (Scatter) - Demographic vs Biometric
    with col4:
        st.subheader("Demographic vs Biometric Intensity")
        # Aggregate Demographic
        filt_demo = filter_data(demographic_df)
        d_agg = filt_demo.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='Demo_Count')
        b_agg = filtered_df.groupby('district')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).reset_index(name='Bio_Count')
        
        merged_scatter = pd.merge(d_agg, b_agg, on='district')
        from src.plots import plot_scatter
        fig_scatter = plot_scatter(merged_scatter, 'Demo_Count', 'Bio_Count', 'Demographic vs Biometric', hover_data=['district'])
        st.plotly_chart(fig_scatter, use_container_width=True)


elif page == "Visual Analysis":
    st.title("Visual Model Analysis")
    st.markdown("### Exploratory Data Analysis & Visualizations")
    
    # Check if dataframes are available
    if 'enrolment_df' not in locals() or 'demographic_df' not in locals() or 'biometric_df' not in locals():
        st.error("Dataframes not loaded properly.")
    else:
        tab1, tab2, tab3 = st.tabs(["Missing Values", "Correlation Analysis", "Distributions"])
        
        # helper for missing values
        def plot_missing_values(df, name):
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if missing.empty:
                st.info(f"No missing values in {name} Dataset!")
                return None
            
            missing_df = missing.reset_index()
            missing_df.columns = ['Column', 'Missing Count']
            missing_df['Percentage'] = (missing_df['Missing Count'] / len(df)) * 100
            
            fig = px.bar(missing_df, x='Column', y='Percentage', 
                        title=f'Missing Values in {name} Data',
                        color='Percentage', 
                        text=missing_df['Percentage'].apply(lambda x: f'{x:.2f}%'),
                        color_continuous_scale='Reds')
            return fig

        with tab1:
            st.subheader("Missing Data Assessment")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Enrolment Data")
                fig_e = plot_missing_values(enrolment_df, "Enrolment")
                if fig_e: st.plotly_chart(fig_e, use_container_width=True)
                
            with col2:
                st.markdown("#### Demographic Data")
                fig_d = plot_missing_values(demographic_df, "Demographic")
                if fig_d: st.plotly_chart(fig_d, use_container_width=True)
                
            with col3:
                st.markdown("#### Biometric Data")
                fig_b = plot_missing_values(biometric_df, "Biometric")
                if fig_b: st.plotly_chart(fig_b, use_container_width=True)

        with tab2:
            st.subheader("Correlation Heatmaps")
            
            # Prepare datasets for correlation
            # Select only numeric columns
            e_corr = enrolment_df.select_dtypes(include=['float64', 'int64']).corr()
            d_corr = demographic_df.select_dtypes(include=['float64', 'int64']).corr()
            b_corr = biometric_df.select_dtypes(include=['float64', 'int64']).corr()

            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### Enrolment Correlations")
                fig_hm_e = px.imshow(e_corr, text_auto=True, aspect="auto", title="Enrolment Correlation Matrix", color_continuous_scale='RdBu_r')
                st.plotly_chart(fig_hm_e, use_container_width=True)
                
            with col_b:
                st.markdown("#### Demographic Correlations")
                fig_hm_d = px.imshow(d_corr, text_auto=True, aspect="auto", title="Demographic Correlation Matrix", color_continuous_scale='Viridis')
                st.plotly_chart(fig_hm_d, use_container_width=True)
                
            st.markdown("#### Biometric Correlations")
            fig_hm_b = px.imshow(b_corr, text_auto=True, aspect="auto", title="Biometric Correlation Matrix", color_continuous_scale='Magma')
            st.plotly_chart(fig_hm_b, use_container_width=True)

        with tab3:
            st.subheader("Feature Distributions")
            
            dataset_choice = st.selectbox("Select Dataset", ["Enrolment", "Demographic", "Biometric"])
            
            if dataset_choice == "Enrolment":
                target_df = enrolment_df
                num_cols = [c for c in ['age_0_5', 'age_5_17', 'age_18_greater'] if c in target_df.columns]
            elif dataset_choice == "Demographic":
                target_df = demographic_df
                num_cols = [c for c in ['demo_age_5_17', 'demo_age_17_'] if c in target_df.columns]
            else:
                target_df = biometric_df
                num_cols = [c for c in ['bio_age_5_17', 'bio_age_17_'] if c in target_df.columns]
                
            if num_cols:
                selected_col = st.selectbox("Select Column to Visualize", num_cols)
                
                # Histogram
                fig_hist = px.histogram(target_df, x=selected_col, nbins=50, title=f"Distribution of {selected_col}", marginal="box", color_discrete_sequence=['teal'])
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("No suitable numeric columns found for distribution plot.")


elif page == "Demand Forecasting":
    st.title("Predictive Demand Forecasting")
    st.markdown("### Anticipate Volume & Optimize Resource Allocation")
    
    # Use global filters
    st.info(f"Forecasting Demand for State: **{selected_state}**, District: **{selected_district}**")
    
    # 1. Prepare Historical Data
    # Combine Enrolment, Demographic, and Biometric counts per day
    
    # Filter dfs
    f_enro = filter_data(enrolment_df)
    f_demo = filter_data(demographic_df)
    f_bio = filter_data(biometric_df)
    
    # Group by date
    d_enro = f_enro.groupby('date')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum(axis=1).reset_index(name='Enrolments')
    d_demo = f_demo.groupby('date')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).reset_index(name='Demo Updates')
    d_bio = f_bio.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum().sum(axis=1).reset_index(name='Bio Updates')
    
    # Merge all
    hist_df = pd.merge(d_enro, d_demo, on='date', how='outer').merge(d_bio, on='date', how='outer').fillna(0)
    hist_df['Total Demand'] = hist_df['Enrolments'] + hist_df['Demo Updates'] + hist_df['Bio Updates']
    hist_df = hist_df.sort_values('date')
    
    # 2. Simple Forecast Logic (Placeholder: Moving Average + Trend)
    # create future dates
    last_date = hist_df['date'].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)
    
    # Simple logic: Take last 30 days average and add some random fluctuation or slight trend
    last_30_avg = hist_df['Total Demand'].tail(30).mean()
    if pd.isna(last_30_avg): last_30_avg = 0
    
    import numpy as np
    
    # Create forecast dataframe
    forecast_values = [last_30_avg * (1 + np.random.uniform(-0.1, 0.1)) for _ in range(30)]
    forecast_df = pd.DataFrame({'date': future_dates, 'Total Demand': forecast_values})
    forecast_df['Type'] = 'Forecast'
    
    # Label historical
    hist_plot_df = hist_df[['date', 'Total Demand']].copy()
    hist_plot_df['Type'] = 'Historical'
    
    # Combine
    full_plot_df = pd.concat([hist_plot_df, forecast_df])
    
    # 3. Plot
    st.subheader("30-Day Demand Forecast")
    
    fig_forecast = px.line(full_plot_df, x='date', y='Total Demand', color='Type', 
                           color_discrete_map={'Historical': 'blue', 'Forecast': 'orange'},
                           title=f"Projected Daily Volume for {selected_district if selected_district != 'All' else selected_state}")
    
    # Add vertical line at split
    # Add vertical line at split
    fig_forecast.add_vline(x=last_date, line_dash="dash", line_color="green")
    fig_forecast.add_annotation(x=last_date, y=1, yref="paper", text="Today", showarrow=False, font=dict(color="green"), yanchor="bottom")
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # 4. Actionable Insights
    st.markdown("---")
    st.subheader("Resource Allocation Recommendations")
    
    predicted_avg = forecast_df['Total Demand'].mean()
    current_avg = hist_df['Total Demand'].tail(30).mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Current Avg Daily Volume (Last 30d)", f"{current_avg:,.0f}")
    col2.metric("Predicted Avg Daily Volume (Next 30d)", f"{predicted_avg:,.0f}", 
                delta=f"{((predicted_avg - current_avg)/current_avg)*100:.1f}%" if current_avg > 0 else "N/A")
    
    st.markdown("#### Operational Actions:")
    if predicted_avg > current_avg * 1.2:
        st.error("⚠️ **High Anticipated Demand**: Recommend deploying **Mobile Aadhaar Van** to this region.")
    elif predicted_avg > current_avg * 1.05:
        st.warning("⚠️ **Rising Demand**: Ensure full staff availability at permanent centres.")
    else:
        st.success("✅ **Stable/Low Demand**: Standard operations sufficient. Consider maintenance activities.")


elif page == "MBU Compliance Tracker":
    st.title("Mandatory Biometric Update (MBU) Compliance")
    st.markdown("### Targeting Missing Updates for Children (Age 5-17)")
    
    st.info(f"Analyzing MBU Gaps for State: **{selected_state}**")
    
    # 1. Prepare Data
    # We need Enrolment (Age 5-17) vs Biometric Updates (Age 5-17) at District Level
    
    # Use filtered data based on state global filter
    # Note: If specific district is selected in sidebar, we still want to show ALL districts in that state for comparison
    # So we re-apply state filter but ignore district filter for the main chart
    
    m_enro = enrolment_df[enrolment_df['state'] == selected_state] if selected_state != 'All' else enrolment_df
    m_bio = biometric_df[biometric_df['state'] == selected_state] if selected_state != 'All' else biometric_df
    
    # Group by District
    e_grp = m_enro.groupby('district')[['age_5_17']].sum().reset_index().rename(columns={'age_5_17': 'Child Enrolments'})
    b_grp = m_bio.groupby('district')[['bio_age_5_17']].sum().reset_index().rename(columns={'bio_age_5_17': 'Child Bio Updates'})
    
    # Merge
    mbu_df = pd.merge(e_grp, b_grp, on='district', how='outer').fillna(0)
    
    # Calculate Metrics
    # Compliance Ratio = Updates / Enrolments (Proxy)
    # Avoid division by zero
    mbu_df['Compliance Score'] = mbu_df['Child Bio Updates'] / mbu_df['Child Enrolments'].replace(0, 1)
    
    # Categorize Regions
    def categorize_gap(row):
        if row['Child Enrolments'] < 100: return "Low Data" # Ignore small samples
        if row['Compliance Score'] < 0.3: return "Critical Gap (Action Needed)"
        if row['Compliance Score'] < 0.6: return "Moderate Gap"
        return "Good Compliance"

    mbu_df['Status'] = mbu_df.apply(categorize_gap, axis=1)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 2. Scatter Plot: Volume vs Compliance
        st.subheader("Compliance Gap Analysis")
        st.markdown("Districts with **High Child Enrolment** but **Low Updates** are critical targets.")
        
        fig_mbu = px.scatter(mbu_df, x="Child Enrolments", y="Child Bio Updates", 
                             color="Status", 
                             hover_data=['district', 'Compliance Score'],
                             size="Child Enrolments",
                             color_discrete_map={
                                 "Critical Gap (Action Needed)": "red",
                                 "Moderate Gap": "orange",
                                 "Good Compliance": "green",
                                 "Low Data": "gray"
                             },
                             title=f"MBU Gap Analysis: {selected_state}")
        
        # Add diagonal line (Ideal theoretical 1:1, though realistic target is lower)
        # fig_mbu.add_shape(type="line", x0=0, y0=0, x1=mbu_df['Child Enrolments'].max(), y1=mbu_df['Child Enrolments'].max(),
        #                   line=dict(color="gray", dash="dash"))
        
        st.plotly_chart(fig_mbu, use_container_width=True)

    with col2:
        # 3. Intervention Planner
        st.subheader("⚠️ Priority Intervention List")
        st.markdown("Districts requiring **School-Based Camps**:")
        
        critical_districts = mbu_df[mbu_df['Status'] == "Critical Gap (Action Needed)"].sort_values(by='Child Enrolments', ascending=False)
        
        if not critical_districts.empty:
            for i, row in critical_districts.head(5).iterrows():
                st.error(f"**{row['district']}**")
                st.caption(f"Pop: {row['Child Enrolments']:,.0f} | Updates: {row['Child Bio Updates']:,.0f} | Ratio: {row['Compliance Score']:.2f}")
        else:
            st.success("No Critical Gaps detected in this region!")

    # 4. Detailed Data View
    with st.expander("View Detailed District Data"):
        st.dataframe(mbu_df.sort_values(by="Compliance Score", ascending=True).style.format({
            'Child Enrolments': '{:,.0f}',
            'Child Bio Updates': '{:,.0f}',
            'Compliance Score': '{:.2%}'
        }))


elif page == "Automated Profiling":
    st.title("Automated Data Profiling")
    st.markdown("### Generate Comprehensive Data Quality Reports")
    
    dataset_option = st.selectbox("Select Dataset to Profile", ["Enrolment Data", "Demographic Data", "Biometric Data"])
    
    if dataset_option == "Enrolment Data":
        target_df = enrolment_df
    elif dataset_option == "Demographic Data":
        target_df = demographic_df
    else:
        target_df = biometric_df
        
    st.warning("⚠️ **Note**: Generating a profile report can take a few minutes depending on dataset size.")
    
    if st.button("Generate Profiling Report"):
        with st.spinner(f"Generating report for {dataset_option}..."):
            try:
                # Use a minimal configuration if data is large, or default
                pr = ProfileReport(target_df, title=f"{dataset_option} Profiling Report", minimal=True)
                # Display using components.html
                components.html(pr.to_html(), height=1000, scrolling=True)
            except Exception as e:
                st.error(f"Error generating report: {e}")

