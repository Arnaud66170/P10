# tdb_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------- Données ----------
project_phases = [
    {"Phase": "Initialisation & cadrage",      "Jours": 2},
    {"Phase": "Préparation des données",       "Jours": 3},
    {"Phase": "Modélisation IA",               "Jours": 4},
    {"Phase": "Optimisation production",       "Jours": 3},
    {"Phase": "Infrastructure Azure",          "Jours": 3},
    {"Phase": "Développement backend",         "Jours": 3},
    {"Phase": "Résolution problèmes critiques", "Jours": 3},
    {"Phase": "Interface utilisateur",         "Jours": 3},
    {"Phase": "Déploiement production",        "Jours": 2},
    {"Phase": "Tests & validation",            "Jours": 2},
]

metrics = {
    "Utilisateurs supportés":      1_028,
    "Articles disponibles":        2_498,
    "Temps de réponse (ms)":       1_600,
    "Coût mensuel (€)":            0.05,
    "Réduction embeddings (%)":    79.7,
    "Variance préservée PCA (%)":  95,
    "Composantes PCA":             52,
}

architecture = {
    "Frontend (Streamlit Cloud)":         ["Backend (Azure Functions)"],
    "Backend (Azure Functions)":          ["Blob Storage", "IA – CBF", "IA – CF", "IA – Hybride"],
    "Blob Storage":                       [],
    "IA – CBF":                           [],
    "IA – CF":                            [],
    "IA – Hybride":                       [],
}

# ---------- Préparation ----------
df = pd.DataFrame(project_phases)
df["Début cumulé"] = df["Jours"].cumsum() - df["Jours"]
df["Fin"]          = df["Jours"].cumsum()
total_days = df["Jours"].sum()
df["%"] = (df["Jours"] / total_days * 100).round(1)

# ---------- Mise en page ----------
st.set_page_config(page_title="Tableau de bord P10", page_icon="📊", layout="wide")
st.title("📊 Tableau de Bord Interactif – Projet P10 MyContent")

# ---------- Diagramme de Gantt ----------
with st.container():
    st.subheader("Chronologie du projet")
    gantt = px.timeline(
        df,
        x_start="Début cumulé",
        x_end="Fin",
        y="Phase",
        color="Phase",
        hover_data={"Jours": True},
        height=400,
    )
    gantt.update_layout(showlegend=False, xaxis_title="Jours")
    st.plotly_chart(gantt, use_container_width=True)

# ---------- Donut de répartition ----------
with st.container():
    st.subheader("Répartition du temps par phase")
    donut = px.pie(
        df,
        names="Phase",
        values="Jours",
        hole=0.55,
        hover_data={"%": True},
        height=400,
    )
    donut.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(donut, use_container_width=True)

# ---------- Métriques clés ----------
st.subheader("Métriques de performance")
cols = st.columns(3)
for i, (label, value) in enumerate(metrics.items()):
    cols[i % 3].metric(label, value)

# ---------- Schéma d’architecture ----------
st.subheader("Architecture du système")
nodes = list(architecture.keys())
edges = [(src, dst) for src, dsts in architecture.items() for dst in dsts]

# Construction d’un graph Plotly simple
edge_x, edge_y = [], []
node_x, node_y, node_text = [], [], [], []
angle_step = 360 / len(nodes)
radius = 1  # cercle pour disposer les nœuds

for i, node in enumerate(nodes):
    angle = i * angle_step
    x = radius * pd.np.cos(pd.np.radians(angle))
    y = radius * pd.np.sin(pd.np.radians(angle))
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

    for edge in [e for e in edges if e[0] == node]:
        j = nodes.index(edge[1])
        x2 = radius * pd.np.cos(pd.np.radians(j * angle_step))
        y2 = radius * pd.np.sin(pd.np.radians(j * angle_step))
        edge_x.extend([x, x2, None])
        edge_y.extend([y, y2, None])

edge_trace = go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1,color="#888"), hoverinfo="none")
node_trace = go.Scatter(x=node_x, y=node_y, mode="markers+text",
                        marker=dict(size=30, color="#1f77b4"), text=node_text,
                        textposition="bottom center")

fig_arch = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(showlegend=False, height=500,
                                      xaxis=dict(showgrid=False, zeroline=False, visible=False),
                                      yaxis=dict(showgrid=False, zeroline=False, visible=False)))
st.plotly_chart(fig_arch, use_container_width=True)

st.caption("Cliquez-glissez pour explorer le schéma ; survolez les éléments pour plus de détails.")
