import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide", page_title="HealthKart Influencer Dashboard")



@st.cache_data
def load_data():

    try:
        influencers = pd.read_csv("influencers.csv")
        posts = pd.read_csv("posts.csv")
        tracking = pd.read_csv("tracking_data.csv")
        payouts = pd.read_csv("payouts.csv")
        return influencers, posts, tracking, payouts
    except FileNotFoundError as e:

        st.error(f"Error: Missing data file - {e.filename}. Please make sure all CSV files are in the correct folder.")
        return None, None, None, None


influencers, posts, tracking, payouts = load_data()


if influencers is None:
    st.stop()

st.title("📊 HealthKart Influencer Campaign Dashboard")
st.markdown("Welcome! Use this dashboard to analyze campaign performance and measure your return on investment.")

st.sidebar.header("Filter Your View")

platform_filter = st.sidebar.multiselect(
    "Which platforms do you want to see?",
    options=influencers['platform'].unique(),
    default=influencers['platform'].unique()
)

campaign_filter = st.sidebar.multiselect(
    "Which campaigns do you want to include?",
    options=tracking['campaign'].unique(),
    default=tracking['campaign'].unique()
)


filtered_influencers = influencers[influencers['platform'].isin(platform_filter)]


filtered_tracking = tracking[
    tracking['campaign'].isin(campaign_filter) &
    tracking['influencer_id'].isin(filtered_influencers['influencer_id'])
    ]


filtered_payouts = payouts[payouts['influencer_id'].isin(filtered_influencers['influencer_id'])]

st.subheader("Quick Overview")

total_revenue = filtered_tracking['revenue'].sum()
total_spend = filtered_payouts['total_payout'].sum()

overall_roas = total_revenue / total_spend if total_spend > 0 else 0


col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
col2.metric("Total Spend", f"₹{total_spend:,.2f}")
col3.metric("Overall ROAS", f"{overall_roas:.2f}x")


st.subheader("Which influencers are giving us the best return?")


if not filtered_tracking.empty and not filtered_payouts.empty:

    revenue_per_influencer = filtered_tracking.groupby('influencer_id')['revenue'].sum().reset_index()


    roi_df = pd.merge(revenue_per_influencer, filtered_payouts[['influencer_id', 'total_payout']], on='influencer_id',
                      how='left')

    roi_df['total_payout'].fillna(0, inplace=True)
    roi_df['ROAS'] = roi_df.apply(
        lambda row: row['revenue'] / row['total_payout'] if row['total_payout'] > 0 else np.inf, axis=1)


    roi_df = roi_df.merge(influencers[['influencer_id', 'name']], on='influencer_id')


    fig = px.bar(
        roi_df.sort_values('ROAS', ascending=False),
        x='name',
        y='ROAS',
        title="Return on Ad Spend (ROAS) per Influencer",
        color='ROAS',
        color_continuous_scale='Blues',
        labels={'name': 'Influencer Name', 'ROAS': 'ROAS (Revenue / Spend)'},
        hover_data={'revenue': ':.2f', 'total_payout': ':.2f'}  # Show extra info on hover
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters. Please adjust your selections.")


st.subheader("🏆 Who are our top-performing influencers?")
if 'roi_df' in locals() and not roi_df.empty:
    top_influencers = roi_df.sort_values(by='revenue', ascending=False).head(10)
    st.dataframe(top_influencers[['name', 'revenue', 'total_payout', 'ROAS']])
else:
    st.info("No influencer data to display based on the current filters.")


st.subheader("📣 How are individual posts performing?")


post_metrics = posts[posts['influencer_id'].isin(filtered_influencers['influencer_id'])].copy()

if not post_metrics.empty:

    post_metrics['engagement'] = post_metrics['likes'] + post_metrics['comments']


    st.dataframe(
        post_metrics[['platform', 'date', 'caption', 'reach', 'likes', 'comments', 'engagement']].sort_values(
            by='reach', ascending=False
        )
    )
else:
    st.info("No post data to display based on the current filters.")
