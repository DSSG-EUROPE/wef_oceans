from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="Fishing Risk Explorer",
    layout="wide",
    page_icon="⚓",
)


@st.cache_data
def generate_sample_vessel_data(num_vessels=200):
    np.random.seed(42)
    vessel_ids = [
        f"V-{int(x):06d}" for x in np.random.randint(1000, 999999, num_vessels)
    ]
    latitudes = np.random.uniform(-60, 60, num_vessels)
    longitudes = np.random.uniform(-180, 180, num_vessels)
    last_timestamps = [
        datetime.utcnow() - timedelta(days=int(x))
        for x in np.random.exponential(scale=10, size=num_vessels)
    ]
    ais_counts = np.random.poisson(25, num_vessels)
    satellite_coverage = np.random.randint(0, 12, num_vessels)
    mpa_presence = np.random.choice([0, 1], num_vessels, p=[0.8, 0.2])
    eez_presence = np.random.choice([0, 1], num_vessels, p=[0.6, 0.4])
    fishing_prob = np.clip(
        np.random.beta(2.5, 3.5, num_vessels)
        + 0.15 * mpa_presence
        + 0.1 * eez_presence,
        0,
        1,
    )

    df = pd.DataFrame(
        {
            "vessel_id": vessel_ids,
            "last_timestamp": last_timestamps,
            "latitude": latitudes,
            "longitude": longitudes,
            "ais_message_count": ais_counts,
            "satellite_coverage": satellite_coverage,
            "mpa_presence": mpa_presence,
            "eez_presence": eez_presence,
            "fishing_probability": fishing_prob,
        }
    )

    df["risk_score"] = (
        0.45 * df["fishing_probability"]
        + 0.2 * df["mpa_presence"]
        + 0.15 * df["eez_presence"]
        + 0.1 * (df["ais_message_count"] / df["ais_message_count"].max())
        + 0.1 * (df["satellite_coverage"] / df["satellite_coverage"].max())
    )
    df["risk_rank"] = df["risk_score"].rank(method="first", ascending=False).astype(int)
    df["country"] = np.random.choice(
        ["Brazil", "Indonesia", "Senegal", "Philippines", "Spain", "India"],
        num_vessels,
    )
    return df.sort_values("risk_score", ascending=False).reset_index(drop=True)


def render_map(data):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position="[longitude, latitude]",
        get_fill_color="[255 * risk_score, 100, 255 * (1 - risk_score)]",
        get_radius=25000,
        pickable=True,
        auto_highlight=True,
    )
    view_state = pdk.ViewState(
        latitude=data["latitude"].mean(), longitude=data["longitude"].mean(), zoom=1.5
    )
    return pdk.Deck(
        map_style="light",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "html": (
                "<b>Vessel ID:</b> {vessel_id}<br/>"
                "<b>Risk score:</b> {risk_score}<br/>"
                "<b>Fishing prob:</b> {fishing_probability}<br/>"
                "<b>MPA:</b> {mpa_presence}<br/>"
                "<b>EEZ:</b> {eez_presence}"
            ),
            "style": {"color": "#ffffff"},
        },
    )


def main():
    st.title("Fishing Risk Explorer")
    st.markdown(
        "Use the vessel ranking dashboard to explore suspicious fishing behavior and risk indicators in a modern, interactive UI."
    )

    df = generate_sample_vessel_data(250)

    with st.sidebar:
        st.header("Filters")
        risk_min = st.slider("Minimum risk score", 0.0, 1.0, 0.35, 0.01)
        top_n = st.slider("Top vessels to show", 5, 50, 20)
        selected_country = st.multiselect(
            "Country",
            sorted(df["country"].unique()),
            default=sorted(df["country"].unique()),
        )
        mpa_only = st.checkbox("Show only MPA presence", value=False)
        eez_only = st.checkbox("Show only EEZ presence", value=False)
        show_raw = st.checkbox("Show raw sample data")

    filtered = df[df["risk_score"] >= risk_min]
    filtered = filtered[filtered["country"].isin(selected_country)]
    if mpa_only:
        filtered = filtered[filtered["mpa_presence"] == 1]
    if eez_only:
        filtered = filtered[filtered["eez_presence"] == 1]

    st.subheader("Top vessel risk indicators")
    st.metric("Vessels matching filters", len(filtered))
    st.metric("Average risk score", f"{filtered['risk_score'].mean():.2f}")

    top_vessels = filtered.sort_values("risk_score", ascending=False).head(top_n)
    st.dataframe(
        top_vessels[
            [
                "risk_rank",
                "vessel_id",
                "country",
                "risk_score",
                "fishing_probability",
                "mpa_presence",
                "eez_presence",
                "ais_message_count",
                "satellite_coverage",
                "latitude",
                "longitude",
            ]
        ].rename(
            columns={
                "risk_rank": "Rank",
                "vessel_id": "Vessel ID",
                "country": "Country",
                "risk_score": "Risk score",
                "fishing_probability": "Fishing probability",
                "mpa_presence": "MPA presence",
                "eez_presence": "EEZ presence",
                "ais_message_count": "AIS message count",
                "satellite_coverage": "Satellite coverage",
            }
        ),
        use_container_width=True,
    )

    st.subheader("Geospatial risk overview")
    deck = render_map(top_vessels)
    st.pydeck_chart(deck)

    if show_raw:
        st.subheader("Raw sample dataset")
        st.write(df)


if __name__ == "__main__":
    main()
