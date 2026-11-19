import logging
import re

import streamlit as st

logger = logging.getLogger("sncf_project.pages.components.render_trip_recommendations")


def starts_with_paris_transfer(path: list[str]) -> bool:
    """Return True if the route starts with a transfer between two Parisian stations."""
    if len(path) < 2:
        return False
    return all(re.search(r"\bparis\b", station, re.IGNORECASE) for station in path[:2])


def render_trip_recommendations(
    routes: list[tuple[list[str], float]],
    target_airport: str,
) -> None:
    """Display candidate TGV routes and their end-to-end reliability scores.

    Args:
        routes (list[tuple[list[str], float]]): List of ``(station_path, reliability)``
            pairs where ``reliability`` is a float in ``[0.0, 1.0]``.
        target_airport (str): Name of the destination airport.
    """
    valid_routes = [
        (path, float(score))
        for path, score in routes
        if path and score is not None and not starts_with_paris_transfer(path)
    ]

    if not valid_routes:
        logger.info(f"No route available: {valid_routes}")
        st.warning(
            f"No valid TGV connection found to reach **{target_airport}** from your nearby stations."
        )
        return

    sorted_routes = sorted(valid_routes, key=lambda item: item[1], reverse=True)
    best_score = sorted_routes[0][1]

    st.subheader(f"Recommended TGV Routes to {target_airport}")
    st.caption(
        "Reliability is computed by compounding historical punctuality across every rail leg."
    )

    for rank, (path, reliability) in enumerate(sorted_routes, start=1):
        pct = reliability * 100
        delta_vs_best = (reliability - best_score) * 100
        is_best = rank == 1

        with st.container(border=True):
            col_route, col_score = st.columns([4, 1])

            with col_route:
                badge = "🏆 Best Reliability" if is_best else f"Option #{rank}"
                st.markdown(f"**{badge} — Departure from `{path[0]}`**")

                # Visual itinerary chain
                st.markdown(" ➔ ".join(f"**{station}**" for station in path))
                st.caption(
                    f"{(len(path) + 1) // 2} rail leg(s) · Arrival hub: {path[-1]}"
                )

                # Visual 0-to-1 progress bar
                st.progress(
                    min(max(reliability, 0.0), 1.0),
                    text=f"Connection Reliability: {pct:.1f}%",
                )

            with col_score:
                st.metric(
                    label="Fiabilité",
                    value=f"{pct:.1f}%",
                    delta="Recommended" if is_best else f"{delta_vs_best:.1f}%",
                    delta_color="normal" if is_best else "off",
                )
