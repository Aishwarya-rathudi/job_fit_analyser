"""
charts.py
---------
Plotly visualisation functions for the Streamlit dashboard.
Each function takes analysis data and returns a Plotly figure object.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


COLORS = {
    "primary": "#1F4E79",
    "accent": "#2E75B6",
    "success": "#2E7D32",
    "warning": "#F57F17",
    "danger": "#C62828",
    "light": "#E3F2FD",
    "matched": "#4CAF50",
    "gap_must": "#F44336",
    "gap_nice": "#FF9800",
}


def match_score_gauge(score: int) -> go.Figure:
    """
    Donut-style gauge showing overall match percentage.
    
    Args:
        score: Integer 0-100
    """
    color = COLORS["success"] if score >= 70 else COLORS["warning"] if score >= 50 else COLORS["danger"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Overall Job Match", "font": {"size": 18, "color": COLORS["primary"]}},
        number={"suffix": "%", "font": {"size": 36, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "white",
            "steps": [
                {"range": [0, 50], "color": "#FFEBEE"},
                {"range": [50, 70], "color": "#FFF8E1"},
                {"range": [70, 100], "color": "#E8F5E9"},
            ],
            "threshold": {
                "line": {"color": COLORS["primary"], "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=10, l=20, r=20))
    return fig


def skills_breakdown_chart(matched_skills: list, gap_skills: list) -> go.Figure:
    """
    Horizontal bar chart showing matched vs gap skills by category.
    
    Args:
        matched_skills: List of matched skill dicts from gap analysis
        gap_skills: List of gap skill dicts from gap analysis
    """
    # Count by category
    categories = [
        "Programming", "Machine Learning", "MLOps",
        "Cloud", "Data Engineering", "Visualization",
        "Soft Skills", "Domain Knowledge"
    ]
    
    matched_counts = {c: 0 for c in categories}
    gap_must_counts = {c: 0 for c in categories}
    gap_nice_counts = {c: 0 for c in categories}
    
    for s in matched_skills:
        cat = s.get("category", "Other")
        if cat in matched_counts:
            matched_counts[cat] += 1
    
    for s in gap_skills:
        cat = s.get("category", "Other")
        importance = s.get("importance", "nice-to-have")
        if cat in gap_must_counts:
            if importance == "must-have":
                gap_must_counts[cat] += 1
            else:
                gap_nice_counts[cat] += 1
    
    # Only show categories with data
    active_cats = [c for c in categories 
                   if matched_counts[c] + gap_must_counts[c] + gap_nice_counts[c] > 0]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="✅ You have this",
        y=active_cats,
        x=[matched_counts[c] for c in active_cats],
        orientation="h",
        marker_color=COLORS["matched"],
    ))
    fig.add_trace(go.Bar(
        name="❌ Gap (Must-have)",
        y=active_cats,
        x=[gap_must_counts[c] for c in active_cats],
        orientation="h",
        marker_color=COLORS["gap_must"],
    ))
    fig.add_trace(go.Bar(
        name="⚠️ Gap (Nice-to-have)",
        y=active_cats,
        x=[gap_nice_counts[c] for c in active_cats],
        orientation="h",
        marker_color=COLORS["gap_nice"],
    ))
    
    fig.update_layout(
        barmode="stack",
        title={"text": "Skills Breakdown by Category", "font": {"color": COLORS["primary"]}, "y": 0.98},
        xaxis_title="Number of Skills",
        height=350,
        margin=dict(t=70, b=30, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def learning_timeline_chart(gap_skills: list) -> go.Figure:
    """
    Gantt-style chart showing estimated time to close each skill gap.
    Only shows must-have gaps.
    
    Args:
        gap_skills: List of gap skill dicts from gap analysis
    """
    must_have_gaps = [s for s in gap_skills if s.get("importance") == "must-have"]
    
    if not must_have_gaps:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="🎉 No must-have skill gaps found!",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=16, color=COLORS["success"])
        )
        fig.update_layout(height=200)
        return fig
    
    # Parse estimated times to weeks
    def to_weeks(time_str: str) -> int:
        time_str = time_str.lower()
        if "month" in time_str:
            try:
                return int(time_str.split()[0]) * 4
            except:
                return 4
        elif "week" in time_str:
            try:
                return int(time_str.split()[0])
            except:
                return 2
        return 2
    
    skills = [s["skill"] for s in must_have_gaps]
    durations = [to_weeks(s.get("estimated_time", "2 weeks")) for s in must_have_gaps]
    
    # Stack them sequentially
    starts = [0]
    for d in durations[:-1]:
        starts.append(starts[-1] + d)
    
    fig = go.Figure()
    for i, (skill, start, duration) in enumerate(zip(skills, starts, durations)):
        fig.add_trace(go.Bar(
            name=skill,
            y=[skill],
            x=[duration],
            base=[start],
            orientation="h",
            marker_color=px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)],
            text=f"{duration}w",
            textposition="inside",
        ))
    
    fig.update_layout(
        title={"text": "Estimated Learning Timeline (Must-Have Gaps)", "font": {"color": COLORS["primary"]}},
        xaxis_title="Weeks",
        showlegend=False,
        height=max(200, len(skills) * 45 + 80),
        margin=dict(t=50, b=30, l=10, r=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        barmode="overlay",
    )
    return fig
