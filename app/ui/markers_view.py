from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.core.waveform_service import WaveformEnvelope


@dataclass(frozen=True)
class Marker:
    """Represent a marker displayed on the waveform."""

    time_s: float
    label: str


class MarkersView:
    """Render waveform and allow manual marker editing."""

    def __init__(self) -> None:
        """Initialize view."""
        self._state_key = "markers"

    def render(self, envelope: WaveformEnvelope) -> list[Marker]:
        """Render waveform + markers editor and return markers."""
        self._render_add_marker(envelope)

        markers = self._get_markers()
        markers = self._render_editor(markers, envelope)

        self._set_markers(markers)
        self._render_plot(envelope, markers)
        return markers

    def _get_markers(self) -> list[Marker]:
        """Read markers from session state."""
        raw = st.session_state.get(self._state_key, [])
        return [Marker(time_s=m["time_s"], label=m["label"]) for m in raw]

    def _set_markers(self, markers: list[Marker]) -> None:
        """Write markers to session state."""
        st.session_state[self._state_key] = [
            {"time_s": float(m.time_s), "label": str(m.label)} for m in markers
        ]

    def _render_add_marker(self, envelope: WaveformEnvelope) -> None:
        """Render a small form to add a marker."""
        st.subheader("Markers")
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            label = st.text_input("Label", value="deb1", key="marker_label")

        with col2:
            time_s = st.number_input(
                "Time (s)",
                min_value=0.0,
                max_value=float(envelope.times_s[-1]),
                value=0.0,
                step=0.5,
                key="marker_time_s",
            )

        with col3:
            if st.button("Add marker"):
                self._append_marker(time_s, label)

    def _append_marker(self, time_s: float, label: str) -> None:
        """Append a marker into session state."""
        markers = st.session_state.get(self._state_key, [])
        markers.append({"time_s": float(time_s), "label": str(label)})
        markers.sort(key=lambda x: x["time_s"])
        st.session_state[self._state_key] = markers

    def _render_editor(
        self,
        markers: list[Marker],
        envelope: WaveformEnvelope,
    ) -> list[Marker]:
        """Render a data editor to update markers."""
        if not markers:
            st.caption("No markers yet. Add `deb1`, `fin1`, etc.")
            return markers

        df = pd.DataFrame([{"time_s": m.time_s, "label": m.label} for m in markers])

        edited = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "time_s": st.column_config.NumberColumn(
                    "time_s",
                    min_value=0.0,
                    max_value=float(envelope.times_s[-1]),
                    step=0.1,
                ),
                "label": st.column_config.TextColumn("label"),
            },
            key="markers_editor",
        )

        cleaned = self._clean_df(edited)
        cleaned.sort_values("time_s", inplace=True)
        return [Marker(time_s=float(r.time_s), label=str(r.label)) for r in cleaned.itertuples()]

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize and validate marker rows."""
        df = df.copy()
        df["label"] = df["label"].fillna("").astype(str).str.strip()
        df = df[df["label"] != ""]
        df["time_s"] = pd.to_numeric(df["time_s"], errors="coerce")
        df = df.dropna(subset=["time_s"])
        return df

    def _render_plot(self, envelope: WaveformEnvelope, markers: list[Marker]) -> None:
        """Render waveform plot with marker lines and labels."""
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=envelope.times_s,
                y=envelope.values,
                mode="lines",
                name="waveform",
            )
        )

        for m in markers:
            fig.add_vline(x=m.time_s)
            fig.add_annotation(
                x=m.time_s,
                y=1.0,
                yref="paper",
                text=m.label,
                showarrow=False,
                yanchor="bottom",
            )

        fig.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Time (s)",
            yaxis_title="Volume",
        )

        st.plotly_chart(fig, use_container_width=True)
