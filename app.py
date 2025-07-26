import streamlit as st
import pandas as pd
import plotly.express as px

# Load datasets
@st.cache_data
def load_data():
    influencers = pd.read_csv("influencers.csv")
    posts = pd.read_csv("posts.csv")
    tracking = pd.read_csv("tracking_data.csv")
    payouts = pd.read_csv("payouts.csv")
    return influencers, posts, tracking, payouts

influencers, posts, tracking, payouts = load_data()

st.title("📊 HealthKart Influencer Campaign Dashboard")

# Sidebar filters
platform_filter = st.sidebar.multiselect("Select Platform(s):", influencers['platform'].unique(), default=influencers['platform'].unique())
campaign_filter = st.sidebar.multiselect("Select Campaign(s):", tracking['campaign'].unique(), default=tracking['campaign'].unique())

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
