# visualizations.py - Final, Robust Version
#
# This version uses a more direct data-to-chart approach, bypassing
# potential Pandas DataFrame structural issues that can confuse Plotly.

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go # Import graph_objects for more control
import traceback
import json
from typing import Optional, Tuple, List, Dict, Any

import matplotlib
matplotlib.use('Agg')

# --- Configuration Constants (Unchanged) ---
POTENTIAL_STATUS_COLS = ['Note', 'Status', 'Interpretation', 'Risk Level', 'Condition']
STATUS_COLORS = {"Normal": "#28a745", "Borderline": "#ffc107", "Concerning": "#dc3545"}
DEFAULT_COLOR = "#6c757d"
TEXT_COLOR_DARK = "#1F1F1F"
AXIS_LINE_COLOR = "#444444"
PLOTLY_TEMPLATE = "plotly_white"

# --- Helper Functions (Unchanged) ---
def convert_to_serializable(obj: Any) -> Any:
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, np.generic): return obj.item()
    if isinstance(obj, dict): return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [convert_to_serializable(item) for item in obj]
    return obj

def standardize_status(note_value: Optional[Any]) -> str:
    if pd.isna(note_value): return "Unknown"
    try:
        note_str = str(note_value).strip().lower()
        note_str = ' '.join(note_str.split())
    except Exception: return "Unknown"
    if not note_str: return "Unknown"
    if "concern" in note_str: return "Concerning"
    if "border" in note_str or "equivocal" in note_str: return "Borderline"
    if "normal" in note_str or "within normal limits" in note_str: return "Normal"
    if note_str in ["n/a", "na", "nan"]: return "N/A"
    if note_str == "normal": return "Normal"
    if note_str == "borderline": return "Borderline"
    if note_str == "concerning": return "Concerning"
    return "Unknown"

def find_status_column(df_columns: List[str]) -> Optional[str]:
    df_columns_lower = {c.lower(): c for c in df_columns}
    for col in POTENTIAL_STATUS_COLS:
        if col.lower() in df_columns_lower:
            return df_columns_lower[col.lower()]
    return None

# ========================================================================
#   RE-WRITTEN CHART CREATION FUNCTION (THE FIX)
# ========================================================================
def create_status_charts_plotly(df: pd.DataFrame) -> Tuple[Optional[Dict], Optional[Dict]]:
    if not isinstance(df, pd.DataFrame) or df.empty: return None, None
    status_col = find_status_column(df.columns.tolist())
    if not status_col: return None, None

    try:
        # 1. Standardize and count statuses
        status_series = df[status_col].apply(standardize_status)
        status_counts = status_series.value_counts()

        # 2. Filter the Pandas Series directly
        statuses_to_keep = ["Normal", "Borderline", "Concerning"]
        filtered_counts = status_counts[status_counts.index.isin(statuses_to_keep)]

        if filtered_counts.empty:
            print("Viz Info: No data to plot after filtering.")
            return None, None

        # 3. Extract labels and values into simple lists
        labels = filtered_counts.index.tolist()
        values = filtered_counts.values.tolist()
        
        # 4. Create a sorting map and apply it
        sort_order = { "Normal": 0, "Borderline": 1, "Concerning": 2 }
        sorted_indices = sorted(range(len(labels)), key=lambda k: sort_order.get(labels[k], 99))
        
        sorted_labels = [labels[i] for i in sorted_indices]
        sorted_values = [values[i] for i in sorted_indices]
        
        print(f"Viz: Final data for charts -> Labels: {sorted_labels}, Values: {sorted_values}")

        # 5. Build charts using these clean lists
        color_map = {s: STATUS_COLORS.get(s, DEFAULT_COLOR) for s in sorted_labels}
        total_count = sum(sorted_values)

        # --- Pie Chart (using graph_objects for robustness) ---
        fig_pie = go.Figure(data=[go.Pie(
            labels=sorted_labels,
            values=sorted_values,
            hole=0.4,
            marker_colors=[color_map.get(s) for s in sorted_labels],
            hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>",
            textinfo='percent+label'
        )])
        fig_pie.update_layout(
            title_text="Biomarker Status Distribution", title_x=0.5,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            annotations=[dict(text=f'Total<br><b>{total_count}</b>', x=0.5, y=0.5, font_size=16, showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR_DARK), margin=dict(l=20, r=20, t=60, b=80)
        )

        # --- Bar Chart (using graph_objects for robustness) ---
        fig_bar = go.Figure(data=[go.Bar(
            x=sorted_labels,
            y=sorted_values,
            text=sorted_values,
            textposition='outside',
            marker_color=[color_map.get(s) for s in sorted_labels],
            hovertemplate="<b>%{x}</b>: %{y} Tests<extra></extra>"
        )])
        max_y = max(sorted_values) if sorted_values else 0
        y_range_upper = max(2, max_y + max(1, max_y * 0.25))
        fig_bar.update_layout(
            title_text="Biomarker Status Counts", title_x=0.5,
            xaxis_title=None, yaxis_title="Number of Tests",
            yaxis=dict(range=[0, y_range_upper]),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR_DARK), bargap=0.4
        )
        fig_bar.update_yaxes(tickformat='d')

        return convert_to_serializable(fig_pie.to_dict()), convert_to_serializable(fig_bar.to_dict())

    except Exception as e:
        print(f"Viz Error (Chart Creation): {e}")
        traceback.print_exc()
        return None, None

# ========================================================================
#   MAIN FUNCTION (Unchanged)
# ========================================================================
def generate_visualizations(csv_file_path: str) -> Dict[str, Any]:
    if not csv_file_path or not os.path.exists(csv_file_path):
        return {"status": "error", "message": "Input file not found on the server."}
    print(f"Viz: Starting visualization generation for: {csv_file_path}")
    try:
        df = pd.read_csv(csv_file_path, on_bad_lines='skip')
        if df.empty:
            return {"status": "no_data", "message": "The uploaded file is empty."}
        
        pie_json, bar_json = create_status_charts_plotly(df)

        if not pie_json and not bar_json:
            return {"status": "no_data", "message": "No data for 'Normal', 'Borderline', or 'Concerning' statuses found in the file."}
        
        response_data = {"status": "success", "pie_chart": pie_json, "bar_chart": bar_json}
        print(f"Viz: Finished. Successfully created JSON plot objects.")
        return response_data
    except Exception as e:
        print(f"Viz Error (Main): An unexpected error occurred: {e}")
        traceback.print_exc()
        return {"status": "error", "message": f"A server error occurred during visualization: {e}"}

# --- Test Block (Unchanged) ---
if __name__ == "__main__":
    def create_test_csv(filename="test_data.csv"):
        print(f"--- Creating test file: '{filename}' ---")
        data = {"Note": ["Normal", "normal", "Borderline", "Concerning", "N/A", "Equivocal"]}
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    test_csv_file = create_test_csv()
    visualizations_dict = generate_visualizations(test_csv_file)
    if visualizations_dict and visualizations_dict.get("status") == "success":
        output_filename = "visualizations_output.json"
        with open(output_filename, 'w') as f:
            json.dump(visualizations_dict, f, indent=2)
        print(f"\n✅ Success! Saved to '{output_filename}'.")
    else:
        print(f"\n❌ Operation finished with status '{visualizations_dict.get('status')}'.")
    os.remove(test_csv_file)