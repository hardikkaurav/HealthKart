import streamlit as st
import pandas as pd
import plotly.express as px

# File uploaders for CSVs
st.sidebar.header("📁 Upload Campaign Data")
uploaded_influencers = st.sidebar.file_uploader("Upload influencers.csv", type="csv")
uploaded_posts = st.sidebar.file_uploader("Upload posts.csv", type="csv")
uploaded_tracking = st.sidebar.file_uploader("Upload tracking_data.csv", type="csv")
uploaded_payouts = st.sidebar.file_uploader("Upload payouts.csv", type="csv")

# Load datasets from uploaded files
if uploaded_influencers and uploaded_posts and uploaded_tracking and uploaded_payouts:
    influencers = pd.read_csv(uploaded_influencers)
    posts = pd.read_csv(uploaded_posts)
    tracking = pd.read_csv(uploaded_tracking)
    payouts = pd.read_csv(uploaded_payouts)

    st.title("📊 HealthKart Influencer Campaign Dashboard")

    # Sidebar filters
    platform_filter = st.sidebar.multiselect("Select Platform(s):", influencers['platform'].unique(), default=influencers['platform'].unique())
    campaign_filter = st.sidebar.multiselect("Select Campaign(s):", tracking['campaign'].unique(), default=tracking['campaign'].unique())

    # Optional additional filters
    if 'brand' in tracking.columns:
        brand_filter = st.sidebar.multiselect("Select Brand(s):", tracking['brand'].unique(), default=tracking['brand'].unique())
        tracking = tracking[tracking['brand'].isin(brand_filter)]

    if 'product' in tracking.columns:
        product_filter = st.sidebar.multiselect("Select Product(s):", tracking['product'].unique(), default=tracking['product'].unique())
        tracking = tracking[tracking['product'].isin(product_filter)]

    if 'category' in influencers.columns:
        category_filter = st.sidebar.multiselect("Select Influencer Type(s):", influencers['category'].unique(), default=influencers['category'].unique())
        influencers = influencers[influencers['category'].isin(category_filter)]

    # Filtered data
    filtered_influencers = influencers[influencers['platform'].isin(platform_filter)]
    filtered_tracking = tracking[tracking['campaign'].isin(campaign_filter) & tracking['influencer_id'].isin(filtered_influencers['influencer_id'])]
    filtered_payouts = payouts[payouts['influencer_id'].isin(filtered_influencers['influencer_id'])]

    # ROI and ROAS calculation
    revenue = filtered_tracking.groupby('influencer_id')['revenue'].sum().reset_index()
    payout = filtered_payouts[['influencer_id', 'total_payout']]
    roi_df = pd.merge(revenue, payout, on='influencer_id', how='left')
    roi_df['ROAS'] = roi_df['revenue'] / roi_df['total_payout']
    roi_df = roi_df.merge(influencers[['influencer_id', 'name']], on='influencer_id')

    # ROI chart
    st.subheader("📈 ROAS per Influencer")
    fig = px.bar(roi_df, x='name', y='ROAS', title="Return on Ad Spend (ROAS)", color='ROAS', color_continuous_scale='Blues')
    st.plotly_chart(fig)

    # Top Influencers
    st.subheader("🏆 Top Influencers by Revenue")
    top_influencers = roi_df.sort_values(by='revenue', ascending=False).head(5)
    st.dataframe(top_influencers[['name', 'revenue', 'total_payout', 'ROAS']])

    # Post Performance
    st.subheader("📣 Post Performance")
    post_metrics = posts[posts['influencer_id'].isin(filtered_influencers['influencer_id'])]
    post_metrics['engagement'] = post_metrics['likes'] + post_metrics['comments']
    st.dataframe(post_metrics[['platform', 'date', 'caption', 'reach', 'likes', 'comments', 'engagement']].sort_values(by='reach', ascending=False))

    # Poor ROIs
    st.subheader("⚠️ Influencers with Poor ROIs")
    poor_roi = roi_df[roi_df['ROAS'] < 1].sort_values(by='ROAS')
    st.dataframe(poor_roi[['name', 'revenue', 'total_payout', 'ROAS']])

    # CSV download
    st.subheader("⬇️ Export Data")
    csv = roi_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download ROAS Table as CSV", csv, "roas_table.csv", "text/csv")

else:
    st.warning("📥 Please upload all four required CSV files to continue.")
