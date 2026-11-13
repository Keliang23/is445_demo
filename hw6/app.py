"""IS445 Homework 6 — two interactive views of one course dataset."""
import altair as alt
import streamlit as st

from analysis import SOURCE_URL, agency_summary, decade_summary, load_inventory

st.set_page_config(page_title="Illinois Building Inventory | Keliang Zhu", page_icon="🏛️", layout="wide")


@st.cache_data
def get_data():
    return load_inventory()


def style(chart):
    return (chart.configure_view(stroke=None)
            .configure_axis(labelFontSize=12, titleFontSize=13, titlePadding=12,
                            gridColor="#E5E9EB", labelColor="#35434B", titleColor="#35434B"))


data = get_data()
st.caption("IS445  /  HOMEWORK 6  /  KELIANG ZHU")
st.title("Illinois buildings, in perspective")
st.markdown("Which agencies account for the most recorded floor space, and when were the buildings constructed? "
            "Explore two views of the **Illinois building inventory** provided for this course.")
st.caption("This is a historical inventory snapshot, not a live census of Illinois buildings. Counts refer to rows in the source file.")

with st.sidebar:
    st.header("Explore the inventory")
    statuses = sorted(data["status"].unique().tolist())
    selected_statuses = st.multiselect("Building status · both charts", statuses, default=statuses, key="statuses")
    st.caption("Changing status filters both charts and the totals below. Chart-specific controls appear beside each view.")
    st.markdown(f"[Course dataset]({SOURCE_URL})")

filtered = data.loc[data["status"].isin(selected_statuses)]
c1, c2, c3 = st.columns(3)
c1.metric("Inventory records", f"{len(filtered):,}")
c2.metric("Recorded floor space", f"{filtered['area'].sum() / 1_000_000:,.2f}M sq ft")
c3.metric("Agencies represented", f"{filtered['agency'].nunique():,}")
st.divider()

st.subheader("01 / Which agencies hold the largest footprint?")
left, right = st.columns([2, 1])
with left:
    measure = st.radio("Rank agencies by", ["Recorded floor space", "Inventory records"], horizontal=True, key="measure")
with right:
    top_n = st.slider("Number of agencies shown", 5, 30, 10, key="top_n")

summary = agency_summary(filtered)
field = "area" if measure == "Recorded floor space" else "records"
axis_title = "Recorded floor space (sq ft)" if field == "area" else "Inventory records"
ranked = summary.sort_values([field, "agency"], ascending=[False, True]).head(top_n)
if ranked.empty:
    st.info("Choose at least one building status to display the agency ranking.")
else:
    chart = alt.Chart(ranked).mark_bar(color="#176B80", cornerRadiusEnd=3).encode(
        x=alt.X(f"{field}:Q", title=axis_title, scale=alt.Scale(zero=True), axis=alt.Axis(format="~s")),
        y=alt.Y("agency:N", sort=ranked["agency"].tolist(), title=None, axis=alt.Axis(labelLimit=350)),
        tooltip=[alt.Tooltip("agency:N", title="Agency"), alt.Tooltip("records:Q", title="Records", format=","),
                 alt.Tooltip("area:Q", title="Recorded sq ft", format=",.0f"),
                 alt.Tooltip("known_area:Q", title="Records with positive area", format=",")],
    ).properties(height=max(240, 29 * len(ranked)))
    st.altair_chart(style(chart), width="stretch")
    first = ranked.iloc[0]
    value = f"{first[field]:,.0f} sq ft" if field == "area" else f"{int(first[field]):,} records"
    st.caption(f"Current view: {first['agency']} ranks first with {value}. Showing {len(ranked)} of {len(summary)} agencies.")

st.markdown("**Design and interpretation.** This horizontal bar chart compares agencies by total recorded floor space, "
            "with an option to rank them by inventory record count. Switching the measure separates the number of entries "
            "from the amount of space they represent: many small structures can produce a high count without a large footprint. "
            "Agency is a nominal variable on the vertical axis; bar length encodes a quantitative value on a linear axis starting "
            "at zero. Descending order makes the largest totals easy to locate, and horizontal labels give long agency names room. "
            "A single teal color keeps attention on magnitude rather than implying an extra category. The status filter recomputes "
            "the totals, while the top-N slider controls how many agencies are shown; the axis rescales with the selection, so exact "
            "comparisons across settings should use the tick labels or tooltips. Nonpositive floor areas are omitted from area sums "
            "but their rows still count as inventory records. With more time, I would add a county breakdown within each agency "
            "to show whether its buildings are concentrated in a few locations.")

st.divider()
st.subheader("02 / When were the recorded buildings constructed?")
left, right = st.columns([1, 2])
with left:
    agency = st.selectbox("Agency · construction chart only", ["All agencies"] + sorted(data["agency"].unique().tolist()), key="agency")
with right:
    year_range = st.slider("Construction years · construction chart only", int(data["year"].min()), int(data["year"].max()),
                           (int(data["year"].min()), int(data["year"].max())), key="years")
population = filtered if agency == "All agencies" else filtered.loc[filtered["agency"].eq(agency)]
unknown_years = int(population["year"].isna().sum())
decades = decade_summary(population, *year_range)
shown = int(decades["records"].sum())
if shown == 0:
    st.info("No records with known construction years match these filters. Try another agency, status, or year range.")
else:
    chart = alt.Chart(decades).mark_bar(color="#B45D32", binSpacing=2).encode(
        x=alt.X("decade:Q", bin="binned", title="Construction decade",
                scale=alt.Scale(domain=[int(decades["decade"].min()), int(decades["end"].max())], nice=False),
                axis=alt.Axis(format="d", tickMinStep=10, tickCount=12)),
        x2="end:Q",
        y=alt.Y("records:Q", title="Inventory records", scale=alt.Scale(zero=True), axis=alt.Axis(tickMinStep=1)),
        tooltip=[alt.Tooltip("label:N", title="Decade"), alt.Tooltip("records:Q", title="Matching records", format=",")],
    ).properties(height=340)
    st.altair_chart(style(chart), width="stretch")
    peak = decades.loc[decades["records"].eq(decades["records"].max()), "label"].tolist()
    st.caption(f"Current view: {shown:,} records; highest count in {', '.join(peak)} ({int(decades['records'].max()):,} each).")
st.caption(f"{unknown_years:,} records in the selected agency/status population have no valid construction year and are excluded. "
           f"Only years {year_range[0]}–{year_range[1]} are counted; the first and last decade bins may be partial.")

st.markdown("**Design and interpretation.** This histogram shows the construction-year distribution of buildings represented "
            "in the inventory. I group known construction years into ten-year bins and count records in each bin; a year recorded "
            "as zero is treated as unknown. The horizontal axis uses a continuous, linear year scale, so empty decades retain their "
            "space and historical gaps remain visible. Bar height uses a linear count scale beginning at zero. The muted orange "
            "distinguishes this time-focused view from the teal agency ranking without assigning unsupported meaning to individual "
            "decades. The agency dropdown and year-range slider recalculate the distribution, providing interaction beyond pan, zoom, "
            "or hover. These controls affect only this chart; the sidebar status filter affects both. A restricted year range can "
            "leave partial bins at its edges, and the caption reports the included years and excluded unknown dates. Peaks describe "
            "construction dates of entries in this snapshot, not all construction activity in Illinois: buildings absent from the "
            "inventory cannot be counted. With more time, I would add normalized small multiples by agency to compare the shapes "
            "of their age distributions despite different inventory sizes.")

st.divider()
st.subheader("Relationship to Homework 5")
st.markdown("Homework 5 used U.S. UFO reports from 2000–2013, displayed as a month-by-year heatmap and a "
            "median-and-interquartile-range plot of reported duration by shape. This assignment uses the course's building "
            "inventory dataset from a different source, with an agency ranking and a construction-year histogram. "
            "Both the plotted variables and the plot types have changed. No HW5 plots, analysis code, or write-up passages "
            "are reused; using Python and Altair is the shared tool choice.")

with st.expander("Data source and preparation"):
    st.markdown(f"Source: [UIUC-iSchool-DataViz / building_inventory.csv]({SOURCE_URL}). "
                "The original CSV is bundled with this app so it runs without a live data download. "
                "Snapshot downloaded November 13, 2026; the most recent recorded construction year is 2019. "
                "The retrieval date is not the inventory's collection date.")
    st.markdown(f"The source contains **{len(data):,} rows**. Agency and status labels are trimmed; years and square footage "
                "are parsed as numbers. Unknown, nonpositive, or implausible years are excluded only from the construction "
                "chart. Nonpositive or nonfinite areas are excluded from area sums. "
                f"There are **{int(data['year'].isna().sum()):,} unknown construction years** and "
                f"**{int(data['area'].isna().sum()):,} records without positive floor area** in the full dataset.")
    st.markdown("Repeated rows are retained: the file has no unique building identifier, and multiple small buildings at "
                "one site can share all listed attributes. Removing identical rows could remove real entries. Consequently, "
                "the app reports inventory records rather than claiming verified counts of distinct buildings. No claim "
                "is made that the inventory covers every building in the state.")
