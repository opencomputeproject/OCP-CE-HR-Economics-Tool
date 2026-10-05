"""
Export Functionality for Heat Reuse Economics Tool

Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2026-01-08

Provides CSV export for data and PNG export for charts.
Works in both Google Colab and local Jupyter environments.
"""

import io
import base64
from datetime import datetime
from IPython.display import display, HTML
import ipywidgets as widgets
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# ENVIRONMENT DETECTION
# =============================================================================

def is_colab():
    """Detect if running in Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        return False


# =============================================================================
# DOWNLOAD HELPERS
# =============================================================================

def _download_colab(filepath: str):
    """Trigger download in Colab environment."""
    from google.colab import files
    files.download(filepath)


def _create_download_link(data: bytes, filename: str, mime_type: str) -> str:
    """
    Create a browser-native download link using base64 encoding.
    Works in any Jupyter environment.
    """
    b64 = base64.b64encode(data).decode()
    return f'<a download="{filename}" href="data:{mime_type};base64,{b64}" style="text-decoration: none;">Download {filename}</a>'


# =============================================================================
# CSV EXPORT
# =============================================================================

# The CSV shows CapEx in euros, so it gets its own wording of the CapEx note
CAPEX_CSV_NOTE = ("CapEx = Capital Estimate: equipment x 1.15 installation x 1.10 engineering x 1.10 contingency, "
                  "rounded to €500. Not comparable with the QUICK ESTIMATE above.")


def export_system_data_csv(analysis: dict) -> bytes:
    """
    Export comprehensive analysis data to CSV format.

    Includes:
    - System Parameters (temperatures, flows, sizing)
    - Cost Breakdown (equipment costs, installation, total)
    - Economics Comparison (2°C, 3°C, 5°C approaches with advanced metrics)
    - Economy of Scale (1-5 MW capacity comparison)

    This export provides all the data engineers need to evaluate heat recovery options.

    Args:
        analysis: Complete analysis dictionary from get_complete_system_analysis()

    Returns:
        CSV content as bytes
    """
    system = analysis.get('system', {})
    costs = analysis.get('costs', {})
    sizing = analysis.get('sizing', {})

    wha = float(system.get('wha', 1))
    T1 = float(system.get('T1', 20))
    temp_rise = float(system.get('itdt', 10))
    current_approach = float(system.get('approach', 3))

    # We'll create multiple sections in one CSV
    all_rows = []

    # =========================================================================
    # SECTION 1: Current System Configuration
    # =========================================================================
    all_rows.append({'Section': 'CURRENT SYSTEM CONFIGURATION', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'Capacity', 'Value': wha, 'Unit': 'MW'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'TCS Inlet (T1)', 'Value': system.get('T1', ''), 'Unit': '°C'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'TCS Outlet (T2)', 'Value': system.get('T2', ''), 'Unit': '°C'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'FWS Inlet (T3)', 'Value': system.get('T3', ''), 'Unit': '°C'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'FWS Outlet (T4)', 'Value': system.get('T4', ''), 'Unit': '°C'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'TCS Flow Rate (F1)', 'Value': system.get('F1', ''), 'Unit': 'L/min'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'FWS Flow Rate (F2)', 'Value': system.get('F2', ''), 'Unit': 'L/min'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'Temperature Rise', 'Value': temp_rise, 'Unit': '°C'})
    all_rows.append({'Section': 'System Parameters', 'Parameter': 'Approach Temperature', 'Value': current_approach, 'Unit': '°C'})
    all_rows.append({'Section': 'Sizing', 'Parameter': 'Primary Pipe Size', 'Value': sizing.get('primary_pipe_size', ''), 'Unit': 'DN'})
    all_rows.append({'Section': 'Sizing', 'Parameter': 'Pipe Length Used', 'Value': float(costs.get('total_pipe_length', 0)), 'Unit': 'm'})
    all_rows.append({'Section': 'Sizing', 'Parameter': 'Room Size', 'Value': sizing.get('room_size', ''), 'Unit': 'm²'})

    # =========================================================================
    # SECTION 2: Cost Breakdown for Current Configuration
    # =========================================================================
    all_rows.append({'Section': '', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'COST BREAKDOWN (Current Config)', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'Equipment', 'Parameter': 'Heat Exchanger', 'Value': costs.get('hx_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'Equipment', 'Parameter': 'Piping', 'Value': costs.get('total_pipe_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'Equipment', 'Parameter': 'Fittings (not in quick estimate)', 'Value': costs.get('fittings_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'Equipment', 'Parameter': 'Valves', 'Value': costs.get('total_valve_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'Equipment', 'Parameter': 'Pump', 'Value': costs.get('pump_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'Soft Costs', 'Parameter': 'Installation', 'Value': costs.get('installation_cost', 0), 'Unit': '€'})
    all_rows.append({'Section': 'TOTAL', 'Parameter': 'QUICK ESTIMATE (excludes fittings, instrumentation, engineering, contingency)', 'Value': costs.get('total_cost', 0), 'Unit': '€'})

    if 'operating_cost_eur_year' in costs:
        all_rows.append({'Section': 'Operating', 'Parameter': 'Annual Operating Cost', 'Value': costs.get('operating_cost_eur_year', 0), 'Unit': '€/year'})

    # =========================================================================
    # SECTION 3: Economics Comparison - Approach Temperature Analysis
    # =========================================================================
    all_rows.append({'Section': '', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'APPROACH TEMPERATURE COMPARISON', 'Parameter': f'(Fixed: {wha} MW capacity)', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'Note', 'Parameter': CAPEX_CSV_NOTE, 'Value': '', 'Unit': ''})

    try:
        from .advanced_economics import generate_approach_comparison_data
        approach_data = generate_approach_comparison_data(wha, T1, temp_rise, 5.0, 8760)

        if approach_data:
            # Header row for this section
            all_rows.append({
                'Section': 'Approach Analysis',
                'Parameter': 'Approach (°C)',
                'Value': 'See columns below',
                'Unit': ''
            })

            for d in approach_data:
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'CapEx (Capital Estimate)',
                    'Value': round(d['capex_eur'], 0),
                    'Unit': '€'
                })
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'OpEx',
                    'Value': round(d['opex_eur_year'], 0),
                    'Unit': '€/year'
                })
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'Annualized CapEx (5yr)',
                    'Value': round(d['annualized_capex_eur_year'], 0),
                    'Unit': '€/year'
                })
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'Total Annualized Cost',
                    'Value': round(d['total_annualized_eur_year'], 0),
                    'Unit': '€/year'
                })
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'Normalized CapEx',
                    'Value': round(d['normalized_capex_eur_per_mw'], 0),
                    'Unit': '€/MW'
                })
                all_rows.append({
                    'Section': f"Approach {d['approach']}°C",
                    'Parameter': 'Unit Heat Recovery Cost',
                    'Value': round(d['unit_heat_recovery_cost_eur_per_kwh'], 4),
                    'Unit': '€/kWh'
                })
    except Exception:
        all_rows.append({'Section': 'Approach Analysis', 'Parameter': 'Not available', 'Value': '', 'Unit': ''})

    # =========================================================================
    # SECTION 4: Economy of Scale - Capacity Analysis
    # =========================================================================
    all_rows.append({'Section': '', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'ECONOMY OF SCALE ANALYSIS', 'Parameter': '(Fixed: 3°C approach)', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'Note', 'Parameter': CAPEX_CSV_NOTE, 'Value': '', 'Unit': ''})

    try:
        from .advanced_economics import generate_capacity_comparison_data
        capacity_data = generate_capacity_comparison_data(T1, temp_rise, 3, 5.0, 8760)

        if capacity_data:
            for d in capacity_data:
                all_rows.append({
                    'Section': f"Capacity {d['capacity_mw']} MW",
                    'Parameter': 'CapEx (Capital Estimate)',
                    'Value': round(d['capex_eur'], 0),
                    'Unit': '€'
                })
                all_rows.append({
                    'Section': f"Capacity {d['capacity_mw']} MW",
                    'Parameter': 'OpEx',
                    'Value': round(d['opex_eur_year'], 0),
                    'Unit': '€/year'
                })
                all_rows.append({
                    'Section': f"Capacity {d['capacity_mw']} MW",
                    'Parameter': 'Total Annualized Cost (5yr)',
                    'Value': round(d['total_annualized_eur_year'], 0),
                    'Unit': '€/year'
                })
                all_rows.append({
                    'Section': f"Capacity {d['capacity_mw']} MW",
                    'Parameter': 'Normalized CapEx',
                    'Value': round(d['normalized_capex_eur_per_mw'], 0),
                    'Unit': '€/MW'
                })
                all_rows.append({
                    'Section': f"Capacity {d['capacity_mw']} MW",
                    'Parameter': 'Unit Heat Recovery Cost',
                    'Value': round(d['unit_heat_recovery_cost_eur_per_kwh'], 4),
                    'Unit': '€/kWh'
                })
    except Exception:
        all_rows.append({'Section': 'Capacity Analysis', 'Parameter': 'Not available', 'Value': '', 'Unit': ''})

    # =========================================================================
    # SECTION 5: Key Benchmarks
    # =========================================================================
    all_rows.append({'Section': '', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'ENERGY COST BENCHMARKS', 'Parameter': '', 'Value': '', 'Unit': ''})
    all_rows.append({'Section': 'Benchmark', 'Parameter': 'Natural Gas (EU avg)', 'Value': 0.05, 'Unit': '€/kWh'})
    all_rows.append({'Section': 'Benchmark', 'Parameter': 'EU Industrial Electricity', 'Value': 0.15, 'Unit': '€/kWh'})
    all_rows.append({'Section': 'Note', 'Parameter': 'Heat recovery is competitive if Unit Cost < benchmarks', 'Value': '', 'Unit': ''})

    df = pd.DataFrame(all_rows)

    # Convert to CSV bytes
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    # utf-8-sig adds a byte order mark so Excel on Windows shows °C and € correctly
    return csv_buffer.getvalue().encode('utf-8-sig')


# =============================================================================
# PNG EXPORT FOR CHARTS
# =============================================================================

def _render_table_to_axis(ax, data: list, title: str, columns: list, highlight_lowest: bool = True):
    """
    Render a data table as a matplotlib table on the given axis.

    Args:
        ax: Matplotlib axis
        data: List of data dictionaries
        title: Table title
        columns: List of column definitions [(key, header, format_func), ...]
        highlight_lowest: If True, highlight row with lowest total_annualized_eur_year
    """
    ax.axis('off')

    if not data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        return

    # Find optimal row (lowest total annualized cost)
    min_val = None
    if highlight_lowest and all('total_annualized_eur_year' in d for d in data):
        min_val = min(d['total_annualized_eur_year'] for d in data)

    # Build table data
    cell_text = []
    cell_colors = []

    for row in data:
        is_optimal = False
        if min_val is not None and 'total_annualized_eur_year' in row:
            is_optimal = abs(row['total_annualized_eur_year'] - min_val) < 1

        row_data = []
        row_colors = []

        for col_key, _, fmt_func in columns:
            row_data.append(fmt_func(row.get(col_key, '')))
            if is_optimal:
                row_colors.append('#C8E6C9')  # Light green for optimal
            else:
                row_colors.append('white')

        cell_text.append(row_data)
        cell_colors.append(row_colors)

    # Column headers
    col_labels = [col[1] for col in columns]

    # Create table
    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellColours=cell_colors,
        colColours=['#667eea'] * len(columns),
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 0.85]
    )

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    # Style header cells
    for j in range(len(columns)):
        cell = table[(0, j)]
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#667eea')

    ax.set_title(title, fontsize=11, fontweight='bold', pad=5, loc='center')


def _render_simple_table(ax, rows: list, title: str, header_color: str = '#667eea'):
    """
    Render a simple 2-column table (Label, Value) to an axis.

    Args:
        ax: Matplotlib axis
        rows: List of (label, value) tuples
        title: Table title
        header_color: Color for header row
    """
    ax.axis('off')

    if not rows:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        return

    cell_text = [[label, value] for label, value in rows]
    cell_colors = [['white', 'white'] if i % 2 == 0 else ['#ECEFF1', '#ECEFF1']
                   for i in range(len(rows))]

    table = ax.table(
        cellText=cell_text,
        colLabels=['Parameter', 'Value'],
        cellColours=cell_colors,
        colColours=[header_color, header_color],
        cellLoc='left',
        loc='center',
        bbox=[0, 0, 1, 0.85]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    # Style header cells
    for j in range(2):
        cell = table[(0, j)]
        cell.set_text_props(weight='bold', color='white')

    ax.set_title(title, fontsize=11, fontweight='bold', pad=5, loc='center')


def _render_economics_comparison_table(ax, comparison_data: dict, title: str):
    """
    Render the Economics Analysis comparison table (2°C, 3°C, 5°C).

    Args:
        ax: Matplotlib axis
        comparison_data: The 'approaches' dict from compare_approaches, with '2C', '3C', '5C' keys
        title: Table title
    """
    ax.axis('off')

    if not comparison_data:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=12)
        ax.set_title(title, fontsize=11, fontweight='bold', pad=5)
        return

    # Build rows
    row_labels = [
        'Heat Exchanger (€)',
        'Pump (€)',
        'Piping & Fittings (€)',
        'Instrumentation (€)',
        'Valves (€)',
        '─────────────',
        'Equipment Subtotal (€)',
        'Installation, 15% of equipment (€)',
        'Engineering, 10% of equipment + installation (€)',
        'Contingency, 10% of running total (€)',
        '═════════════',
        'CAPITAL ESTIMATE, rounded to €500 (€)',
        'OpEx (€/yr)'
    ]

    keys = [
        'heat_exchanger', 'pumps', 'pipe_fittings', 'instrumentation', 'valves',
        None,  # separator
        'equipment_subtotal', 'installation_cost', 'engineering_cost', 'contingency_cost',
        None,  # separator
        'capital_total', 'operating_cost_eur_year'
    ]
    equipment_keys = ['heat_exchanger', 'pumps', 'pipe_fittings', 'instrumentation', 'valves']

    cell_text = []
    cell_colors = []

    for i, (label, key) in enumerate(zip(row_labels, keys)):
        if key is None:
            # Separator row
            cell_text.append([label, '─────', '─────', '─────'])
            cell_colors.append(['#f0f0f0'] * 4)
        else:
            row = [label]
            for approach in ['2C', '3C', '5C']:
                data = comparison_data.get(approach, {})
                if key == 'equipment_subtotal':
                    val = sum(data.get(k, 0) for k in equipment_keys)
                elif key == 'valves':
                    # Rounded to the nearest 100, as on screen (economics_panel.py)
                    val = round(data.get(key, 0) / 100) * 100
                else:
                    val = data.get(key, 0)
                row.append(f'€{val:,.0f}')
            cell_text.append(row)

            # Highlight total row
            if key == 'capital_total':
                cell_colors.append(['#C8E6C9'] * 4)
            else:
                cell_colors.append(['white' if i % 2 == 0 else '#ECEFF1'] * 4)

    table = ax.table(
        cellText=cell_text,
        colLabels=['Cost Component', '2°C', '3°C', '5°C'],
        cellColours=cell_colors,
        colColours=['#667eea'] * 4,
        colWidths=[0.37, 0.21, 0.21, 0.21],  # wide enough for the longest row label
        cellLoc='right',
        loc='center',
        bbox=[0, 0, 1, 0.85]
    )

    # Left-align first column
    for i in range(len(cell_text) + 1):
        table[(i, 0)].set_text_props(ha='left')

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    # Style header
    for j in range(4):
        table[(0, j)].set_text_props(weight='bold', color='white')

    ax.set_title(title, fontsize=11, fontweight='bold', pad=5)


def export_charts_png(analysis: dict, dpi: int = None) -> bytes:
    """
    Export ALL charts AND tables to PNG format - comprehensive export of entire UI.

    Layout (11 rows):
    - Row 0: System Parameters | Piping Cost Analysis
    - Row 1: Economics Analysis (3-column comparison: 2°C, 3°C, 5°C)
    - Row 2: Equipment Cost Breakdown by Approach (3 pie charts)
    - Row 3: Cost Contrast Analysis (Capital vs Operating)
    - Row 4: System Approach Profiles | Effectiveness Gauge
    - Row 5: Table A (Advanced Economics - Approach Comparison)
    - Row 6: Chart 1 (Annual Costs) | Chart 2 (Unit Cost)
    - Row 7: Table B (Economy of Scale)
    - Row 8: Chart 3 (Economy of Scale)
    - Row 9: Key Insights summary
    - Row 10: Benchmarks footer

    Args:
        analysis: Complete analysis dictionary
        dpi: Resolution (default 100 for Colab compatibility, 150 for local)

    Returns:
        PNG image as bytes
    """
    import numpy as np
    from .formatting import calculate_effectiveness

    # Close any existing figures to free memory (important for Colab)
    plt.close('all')

    # Auto-detect DPI based on environment if not specified
    # Colab has memory constraints, so use lower DPI there
    if dpi is None:
        dpi = 100 if is_colab() else 150

    system = analysis.get('system', {})
    costs = analysis.get('costs', {})
    sizing = analysis.get('sizing', {})

    wha = float(system.get('wha', 1))
    T1 = float(system.get('T1', 20))
    temp_rise = float(system.get('itdt', 10))
    approach = float(system.get('approach', 3))

    # Create figure with GridSpec for flexible layout
    # Reduced from (18, 58) to (14, 45) for Colab memory compatibility
    # At 100 DPI this is ~6.3 megapixels vs ~23 megapixels before
    fig = plt.figure(figsize=(14, 45))

    # Use GridSpec: 11 rows (added Cost Contrast Analysis)
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(11, 2, figure=fig,
                  height_ratios=[0.8, 1.1, 0.9, 0.8, 0.9, 0.7, 0.9, 0.7, 0.9, 0.4, 0.2],
                  hspace=0.35, wspace=0.2)

    # =========================================================================
    # ROW 0: System Parameters | Piping Cost Analysis
    # =========================================================================
    ax_sys_params = fig.add_subplot(gs[0, 0])
    ax_piping = fig.add_subplot(gs[0, 1])

    # System Parameters table
    sys_params_rows = [
        ('Capacity', f"{wha} MW"),
        ('TCS Inlet (T1)', f"{system.get('T1', '')}°C"),
        ('TCS Outlet (T2)', f"{system.get('T2', '')}°C"),
        ('FWS Inlet (T3)', f"{system.get('T3', '')}°C"),
        ('FWS Outlet (T4)', f"{system.get('T4', '')}°C"),
        ('Approach Temperature', f"{approach}°C"),
        ('TCS Flow Rate (F1)', f"{system.get('F1', '')} L/min"),
        ('FWS Flow Rate (F2)', f"{system.get('F2', '')} L/min"),
        ('Primary Pipe Size', f"DN{sizing.get('primary_pipe_size', '')}"),
        ('Pipe Length Used', f"{float(costs.get('total_pipe_length', 0)):.1f} m"),
        ('Room Size', f"{sizing.get('room_size', '')} m²"),
    ]
    _render_simple_table(ax_sys_params, sys_params_rows, 'System Parameters (Auto-Calculated)', '#667eea')

    # Piping Cost Analysis table
    piping_rows = [
        ('Total Pipe Cost', f"€{costs.get('total_pipe_cost', 0):,.0f}"),
        ('Fittings', f"€{costs.get('fittings_cost', 0):,.0f}"),
        ('Valve Costs', f"€{costs.get('total_valve_cost', 0):,.0f}"),
        ('─────────', '─────────'),
        ('TOTAL PIPING', f"€{costs.get('total_pipe_cost', 0) + costs.get('fittings_cost', 0) + costs.get('total_valve_cost', 0):,.0f}"),
    ]
    _render_simple_table(ax_piping, piping_rows, 'Piping Cost Analysis', '#667eea')

    # =========================================================================
    # ROW 1: Economics Analysis - Order of Magnitude Estimate (full width)
    # =========================================================================
    ax_econ_compare = fig.add_subplot(gs[1, :])

    # Build economics comparison data for 2°C, 3°C, 5°C
    try:
        from .economics_panel import compare_approaches
        econ_comparison = compare_approaches(wha, T1, temp_rise)
        _render_economics_comparison_table(ax_econ_compare, econ_comparison.get('approaches', {}),
                                          f'Economics Analysis - Order of Magnitude Estimate ({wha} MW)')
    except Exception as e:
        ax_econ_compare.axis('off')
        ax_econ_compare.text(0.5, 0.5, f'Economics comparison not available: {str(e)}',
                            ha='center', va='center', fontsize=11)
        ax_econ_compare.set_title('Economics Analysis', fontsize=11, fontweight='bold')

    # =========================================================================
    # ROW 2: Equipment Cost Breakdown by Approach - 3 PIE CHARTS
    # =========================================================================
    try:
        from core.costs import compare_approaches as get_cost_comparison
        comparison = get_cost_comparison(wha, T1, temp_rise, approaches=[2, 3, 5])

        if comparison.get('status') == 'success':
            approaches_data = comparison['approaches']

            # Colors and labels for pie charts
            colors = [
                '#E74C3C',  # Red - Heat Exchangers
                '#FF9F43',  # Orange - Pumps
                '#F1C40F',  # Yellow - Piping & Fittings
                '#2ECC71',  # Green - Instrumentation
                '#3498DB',  # Blue - Valves
                '#9B59B6'   # Purple - I&C Subtotal
            ]
            labels = ['Heat Exchangers', 'Pumps', 'Piping & Fittings', 'Instrumentation', 'Valves', 'I&C Subtotal']

            # Create nested GridSpec for 3 pie charts in row 2
            from matplotlib.gridspec import GridSpecFromSubplotSpec
            gs_pies = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[2, :], wspace=0.3)

            pie_axes = [fig.add_subplot(gs_pies[0, i]) for i in range(3)]

            for idx, appr in enumerate([2, 3, 5]):
                key = f"{appr}C"
                data = approaches_data.get(key, {})

                heat_exchanger = data.get('heat_exchanger', 0)
                pumps = data.get('pumps', 0)
                pipe_fittings = data.get('pipe_fittings', 0)
                instrumentation = data.get('instrumentation', 0)
                valves = data.get('valves', 0)
                ic_subtotal = sum([
                    data.get('installation_cost', 0),
                    data.get('engineering_cost', 0),
                    data.get('contingency_cost', 0)
                ])

                values = [heat_exchanger, pumps, pipe_fittings, instrumentation, valves, ic_subtotal]

                wedges, texts, autotexts = pie_axes[idx].pie(
                    values,
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    pctdistance=0.75
                )

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(8)

                pie_axes[idx].set_title(f"{appr}°C Approach", fontsize=12, fontweight='bold')

            # Add shared legend below center pie
            pie_axes[1].legend(wedges, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                              fontsize=8, ncol=3, frameon=False)

            # Add section title
            fig.text(0.5, gs[2, :].get_position(fig).y1 + 0.01,
                    'Equipment Cost Breakdown by Approach', fontsize=11, fontweight='bold',
                    ha='center', va='bottom')
        else:
            ax_pie_err = fig.add_subplot(gs[2, :])
            ax_pie_err.axis('off')
            ax_pie_err.text(0.5, 0.5, 'Equipment breakdown not available', ha='center', va='center')
    except Exception as e:
        ax_pie_err = fig.add_subplot(gs[2, :])
        ax_pie_err.axis('off')
        ax_pie_err.text(0.5, 0.5, f'Equipment breakdown not available', ha='center', va='center')

    # =========================================================================
    # ROW 3: Cost Contrast Analysis (Capital vs Operating)
    # =========================================================================
    ax_contrast = fig.add_subplot(gs[3, :])
    try:
        from core.costs import compare_approaches as get_cost_comparison
        comparison = get_cost_comparison(wha, T1, temp_rise, approaches=[2, 3, 5])

        if comparison.get('status') == 'success':
            approaches_data = comparison['approaches']
            approach_vals = [2, 3, 5]
            capital_costs = []
            operating_costs = []

            for appr in approach_vals:
                key = f"{appr}C"
                capital_costs.append(approaches_data.get(key, {}).get('capital_total', 0))
                operating_costs.append(approaches_data.get(key, {}).get('operating_cost_eur_year', 0))

            # Plot both lines
            ax_contrast.plot(approach_vals, capital_costs, marker='o', linewidth=2, markersize=8,
                            label='Capital Estimate', color='#2196F3')
            ax_contrast.plot(approach_vals, operating_costs, marker='s', linewidth=2, markersize=8,
                            label='Annual Operating Cost', color='#FF9800')

            ax_contrast.set_xlabel('Approach Temperature (°C)', fontsize=11, fontweight='bold')
            ax_contrast.set_ylabel('Cost (€)', fontsize=11)
            ax_contrast.set_title('Cost Contrast Analysis: Capital Estimate vs Operating Cost', fontsize=12, fontweight='bold')
            ax_contrast.legend(loc='best', fontsize=10, frameon=True)
            ax_contrast.grid(True, alpha=0.3, linestyle='--')
            ax_contrast.set_xticks(approach_vals)

            # Add value labels
            for i, appr in enumerate(approach_vals):
                ax_contrast.annotate(f'€{capital_costs[i]:,.0f}',
                                    (appr, capital_costs[i]),
                                    textcoords="offset points", xytext=(0, 10), ha='center', fontsize=9)
                ax_contrast.annotate(f'€{operating_costs[i]:,.0f}',
                                    (appr, operating_costs[i]),
                                    textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9)
        else:
            ax_contrast.axis('off')
            ax_contrast.text(0.5, 0.5, 'Cost contrast data not available', ha='center', va='center')
    except Exception:
        ax_contrast.axis('off')
        ax_contrast.text(0.5, 0.5, 'Cost contrast data not available', ha='center', va='center')

    # =========================================================================
    # ROW 4: System Charts (Approach Profiles + Effectiveness Gauge)
    # =========================================================================
    ax1 = fig.add_subplot(gs[4, 0])
    ax2 = fig.add_subplot(gs[4, 1])

    # Chart 1a: Approach Profiles
    try:
        from core.original_calculations import calculate_combined_approach_profiles
        profiles = calculate_combined_approach_profiles(system)

        if profiles and profiles.get('tcs_profile') and profiles.get('fws_profile'):
            tcs = profiles['tcs_profile']
            fws = profiles['fws_profile']
            time_percent = [t * 100 for t in tcs['time_progression']]

            ax1.plot(time_percent, tcs['temperatures'], color='#ff6666', linewidth=3, marker='o', markersize=4,
                     label=f'TCS ({tcs["start_temp"]:.0f}°C → {tcs["target_temp"]:.0f}°C)')
            ax1.plot(time_percent, fws['temperatures'], color='#66b3ff', linewidth=3, marker='s', markersize=4,
                     label=f'FWS ({fws["start_temp"]:.0f}°C → {fws["target_temp"]:.0f}°C)')
            ax1.set_title('System Approach Profiles', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Process Completion (%)')
            ax1.set_ylabel('Temperature (°C)')
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
        else:
            ax1.text(0.5, 0.5, 'Approach Profile Data\nNot Available', ha='center', va='center', fontsize=12)
            ax1.set_title('System Approach Profiles', fontsize=14, fontweight='bold')
    except Exception as e:
        ax1.text(0.5, 0.5, f'Approach Profile\nNot Available', ha='center', va='center', fontsize=10)
        ax1.set_title('System Approach Profiles', fontsize=14, fontweight='bold')
        ax1.axis('off')

    # Chart 1b: Effectiveness Gauge
    try:
        effectiveness = calculate_effectiveness(analysis)
        theta = np.linspace(0, np.pi, 100)
        ax2.plot(np.cos(theta), np.sin(theta), 'lightgray', linewidth=8)
        theta_red = np.linspace(0, np.pi * 0.6, 50)
        ax2.plot(np.cos(theta_red), np.sin(theta_red), '#FF5252', linewidth=8)
        theta_yellow = np.linspace(np.pi * 0.6, np.pi * 0.8, 50)
        ax2.plot(np.cos(theta_yellow), np.sin(theta_yellow), '#FFC107', linewidth=8)
        theta_green = np.linspace(np.pi * 0.8, np.pi, 50)
        ax2.plot(np.cos(theta_green), np.sin(theta_green), '#4CAF50', linewidth=8)

        needle_angle = np.pi * (1 - effectiveness)
        ax2.plot([0, 0.8 * np.cos(needle_angle)], [0, 0.8 * np.sin(needle_angle)], 'black', linewidth=4)
        ax2.plot(0, 0, 'ko', markersize=8)
        ax2.text(0, -0.3, f'{effectiveness:.1%}', ha='center', va='center', fontsize=16, fontweight='bold')
        ax2.text(0, -0.5, 'Effectiveness', ha='center', va='center', fontsize=12)
        ax2.set_xlim(-1.2, 1.2)
        ax2.set_ylim(-0.6, 1.2)
        ax2.set_aspect('equal')
        ax2.axis('off')
        ax2.set_title('Heat Exchanger Effectiveness', fontsize=14, fontweight='bold', pad=20)
    except Exception:
        ax2.text(0.5, 0.5, 'Effectiveness gauge not available', ha='center', va='center')
        ax2.axis('off')

    # =========================================================================
    # ROW 5-9: Advanced Economics Tables and Charts
    # =========================================================================
    try:
        from .advanced_economics import (
            generate_approach_comparison_data,
            generate_capacity_comparison_data,
            CAPEX_NOTE
        )

        # Get data (using default 5yr payback, 8760 hours)
        approach_data = generate_approach_comparison_data(wha, T1, temp_rise, 5.0, 8760)
        capacity_data = generate_capacity_comparison_data(T1, temp_rise, 3, 5.0, 8760)

        # -----------------------------------------------------------------
        # ROW 5: Table A - Approach Temperature Comparison (full width)
        # -----------------------------------------------------------------
        ax_table_a = fig.add_subplot(gs[5, :])
        if approach_data:
            approach_columns = [
                ('capacity_mw', 'MW', lambda x: f'{x}'),
                ('approach', 'Approach\n(°C)', lambda x: f'{x}'),
                ('capex_eur', 'CapEx\n(K€)', lambda x: f'{x/1000:,.0f}'),
                ('opex_eur_year', 'OpEx\n(K€/yr)', lambda x: f'{x/1000:,.1f}'),
                ('annualized_capex_eur_year', 'Ann. CapEx\n(K€/yr)', lambda x: f'{x/1000:,.0f}'),
                ('total_annualized_eur_year', 'Total Ann.\n(K€/yr)', lambda x: f'{x/1000:,.0f}'),
                ('normalized_capex_eur_per_mw', 'Norm. CapEx\n(K€/MW)', lambda x: f'{x/1000:,.0f}'),
                ('unit_heat_recovery_cost_eur_per_kwh', 'Unit Cost\n(€/kWh)', lambda x: f'{x:.4f}'),
            ]
            _render_table_to_axis(ax_table_a, approach_data,
                                  f'Table A: {wha} MW System - Approach Temperature Comparison (5yr payback, 8760 hrs)',
                                  approach_columns, highlight_lowest=True)
        else:
            ax_table_a.axis('off')
            ax_table_a.text(0.5, 0.5, 'Approach data not available', ha='center', va='center')

        # -----------------------------------------------------------------
        # ROW 6: Chart 1 (Annual Costs) | Chart 2 (Unit Cost)
        # -----------------------------------------------------------------
        if approach_data:
            ax3 = fig.add_subplot(gs[6, 0])
            ax4 = fig.add_subplot(gs[6, 1])

            approaches = [d['approach'] for d in approach_data]
            opex = [d['opex_eur_year'] / 1000 for d in approach_data]
            annualized_capex = [d['annualized_capex_eur_year'] / 1000 for d in approach_data]
            total_annualized = [d['total_annualized_eur_year'] / 1000 for d in approach_data]
            unit_cost = [d['unit_heat_recovery_cost_eur_per_kwh'] for d in approach_data]

            x_pos = np.arange(len(approaches))

            # Chart 1: Annual Costs
            ax3.plot(x_pos, opex, 'b--', marker='o', linewidth=2, markersize=8, label='OpEx (K€/yr)')
            ax3.plot(x_pos, annualized_capex, 'r--', marker='s', linewidth=2, markersize=8, label='Ann. CapEx (K€/yr)')
            ax3.plot(x_pos, total_annualized, 'purple', marker='^', linewidth=3, markersize=10, label='Total Ann. (K€/yr)')
            min_idx = total_annualized.index(min(total_annualized))
            ax3.scatter([min_idx], [total_annualized[min_idx]], s=200, c='gold', marker='*', zorder=5, edgecolors='black')
            ax3.set_xlabel('Approach (°C)', fontsize=11, fontweight='bold')
            ax3.set_ylabel('Annual Cost (K€/yr)', fontsize=10)
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels([f'{a}°C' for a in approaches])
            ax3.grid(True, alpha=0.3, linestyle='--')
            ax3.legend(loc='upper left', fontsize=8)
            ax3.set_title('Chart 1: Annual Costs vs. Approach', fontsize=12, fontweight='bold')

            # Chart 2: Unit Cost
            ax4.plot(x_pos, unit_cost, 'm-', marker='o', linewidth=3, markersize=10, label='Heat Recovery (€/kWh)')
            ax4.axhline(y=0.05, color='orange', linestyle=':', linewidth=2, alpha=0.7, label='Natural Gas (€0.05)')
            ax4.axhline(y=0.15, color='red', linestyle=':', linewidth=2, alpha=0.7, label='EU Electricity (€0.15)')
            min_idx = unit_cost.index(min(unit_cost))
            ax4.scatter([min_idx], [unit_cost[min_idx]], s=200, c='gold', marker='*', zorder=5, edgecolors='black')
            ax4.set_xlabel('Approach (°C)', fontsize=11, fontweight='bold')
            ax4.set_ylabel('Unit Cost (€/kWh)', fontsize=10, color='#9C27B0')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels([f'{a}°C' for a in approaches])
            ax4.grid(True, alpha=0.3, linestyle='--')
            ax4.legend(loc='upper left', fontsize=8)
            ax4.set_title('Chart 2: Unit Heat Recovery Cost vs. Approach', fontsize=12, fontweight='bold')

        # -----------------------------------------------------------------
        # ROW 7: Table B - Economy of Scale (full width)
        # -----------------------------------------------------------------
        ax_table_b = fig.add_subplot(gs[7, :])
        if capacity_data:
            capacity_columns = [
                ('capacity_mw', 'MW', lambda x: f'{x}'),
                ('approach', 'Approach\n(°C)', lambda x: f'{x}'),
                ('capex_eur', 'CapEx\n(K€)', lambda x: f'{x/1000:,.0f}'),
                ('opex_eur_year', 'OpEx\n(K€/yr)', lambda x: f'{x/1000:,.1f}'),
                ('annualized_capex_eur_year', 'Ann. CapEx\n(K€/yr)', lambda x: f'{x/1000:,.0f}'),
                ('total_annualized_eur_year', 'Total Ann.\n(K€/yr)', lambda x: f'{x/1000:,.0f}'),
                ('normalized_capex_eur_per_mw', 'Norm. CapEx\n(K€/MW)', lambda x: f'{x/1000:,.0f}'),
                ('unit_heat_recovery_cost_eur_per_kwh', 'Unit Cost\n(€/kWh)', lambda x: f'{x:.4f}'),
            ]
            _render_table_to_axis(ax_table_b, capacity_data,
                                  'Table B: Economy of Scale - 3°C Approach, Variable Capacity (5yr payback, 8760 hrs)',
                                  capacity_columns, highlight_lowest=True)
        else:
            ax_table_b.axis('off')
            ax_table_b.text(0.5, 0.5, 'Capacity data not available', ha='center', va='center')

        # -----------------------------------------------------------------
        # ROW 8: Chart 3 - Economy of Scale (full width)
        # -----------------------------------------------------------------
        if capacity_data:
            ax5 = fig.add_subplot(gs[8, :])
            capacities = [d['capacity_mw'] for d in capacity_data]
            unit_cost_cap = [d['unit_heat_recovery_cost_eur_per_kwh'] for d in capacity_data]
            normalized_capex = [d['normalized_capex_eur_per_mw'] / 1000 for d in capacity_data]

            x_pos_cap = np.arange(len(capacities))

            # Dual axis chart
            ax5_twin = ax5.twinx()
            bars = ax5_twin.bar(x_pos_cap, normalized_capex, 0.6, color='#4CAF50', alpha=0.3,
                               hatch='///', label='Norm. CapEx (K€/MW)', edgecolor='#2E7D32')
            ax5_twin.set_ylabel('Normalized CapEx (K€/MW)', fontsize=10, color='#2E7D32')
            ax5_twin.tick_params(axis='y', labelcolor='#2E7D32')

            ax5.plot(x_pos_cap, unit_cost_cap, 'm-', marker='o', linewidth=3, markersize=10, label='Heat Recovery (€/kWh)')
            ax5.axhline(y=0.05, color='orange', linestyle=':', linewidth=2, alpha=0.7, label='Natural Gas (€0.05)')
            ax5.axhline(y=0.15, color='red', linestyle=':', linewidth=2, alpha=0.7, label='EU Electricity (€0.15)')

            # Add cost reduction annotation
            if len(unit_cost_cap) > 1:
                cost_reduction = (unit_cost_cap[0] - unit_cost_cap[-1]) / unit_cost_cap[0] * 100
                ax5.annotate(f'{cost_reduction:.0f}% cost reduction\n1→{capacities[-1]} MW',
                            xy=(len(capacities)-1, unit_cost_cap[-1]),
                            xytext=(-80, 30), textcoords='offset points',
                            fontsize=10, fontweight='bold', color='#9C27B0',
                            arrowprops=dict(arrowstyle='->', color='#9C27B0'))

            ax5.set_xlabel('Heat Recovery Capacity (MW)', fontsize=11, fontweight='bold')
            ax5.set_ylabel('Unit Heat Recovery Cost (€/kWh)', fontsize=10, color='#9C27B0')
            ax5.tick_params(axis='y', labelcolor='#9C27B0')
            ax5.set_xticks(x_pos_cap)
            ax5.set_xticklabels([f'{c} MW' for c in capacities])
            ax5.grid(True, alpha=0.3, linestyle='--')

            # Combined legend
            lines1, labels1 = ax5.get_legend_handles_labels()
            lines2, labels2 = ax5_twin.get_legend_handles_labels()
            ax5.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
            ax5.set_title('Chart 3: Economy of Scale - Unit Cost vs. Capacity', fontsize=12, fontweight='bold')

        # -----------------------------------------------------------------
        # ROW 9: Key Insights Summary
        # -----------------------------------------------------------------
        ax_insights = fig.add_subplot(gs[9, :])
        ax_insights.axis('off')

        if approach_data and capacity_data:
            optimal_approach = min(approach_data, key=lambda x: x['total_annualized_eur_year'])
            mw_1 = next((d for d in capacity_data if d['capacity_mw'] == 1), None)
            mw_5 = next((d for d in capacity_data if d['capacity_mw'] == 5), None)

            insights_text = f"KEY INSIGHTS:\n"
            insights_text += f"• Optimal approach for {wha} MW: {optimal_approach['approach']}°C "
            insights_text += f"(Total Annualized: €{optimal_approach['total_annualized_eur_year']:,.0f}/yr)\n"
            insights_text += f"• Unit Heat Recovery Cost at optimal: €{optimal_approach['unit_heat_recovery_cost_eur_per_kwh']:.4f}/kWh\n"

            if mw_1 and mw_5:
                improvement = (mw_1['unit_heat_recovery_cost_eur_per_kwh'] - mw_5['unit_heat_recovery_cost_eur_per_kwh']) / mw_1['unit_heat_recovery_cost_eur_per_kwh'] * 100
                insights_text += f"• Economy of Scale: {improvement:.0f}% unit cost reduction from 1 MW to 5 MW\n"

            unit_cost = optimal_approach['unit_heat_recovery_cost_eur_per_kwh']
            if unit_cost < 0.05:
                insights_text += "• Competitiveness: ✓ Below natural gas benchmark (€0.05/kWh)"
            elif unit_cost < 0.15:
                insights_text += "• Competitiveness: ✓ Below EU electricity benchmark (€0.15/kWh)"
            else:
                insights_text += "• Competitiveness: Above typical energy benchmarks"

            ax_insights.text(0.5, 0.5, insights_text, ha='center', va='center', fontsize=11,
                           fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='#E8F5E9',
                           edgecolor='#4CAF50', linewidth=2))

        # -----------------------------------------------------------------
        # ROW 10: Benchmarks footer
        # -----------------------------------------------------------------
        ax_footer = fig.add_subplot(gs[10, :])
        ax_footer.axis('off')
        footer_text = ("Benchmarks: Natural Gas €0.05/kWh | EU Industrial Electricity €0.15/kWh | Green highlight = optimal (lowest Total Annualized Cost)\n"
                       + CAPEX_NOTE)
        ax_footer.text(0.5, 0.5, footer_text, ha='center', va='center', fontsize=9, color='#666',
                      style='italic')

    except Exception as e:
        # If advanced economics fails, show error
        ax_err = fig.add_subplot(gs[5:9, :])
        ax_err.text(0.5, 0.5, f'Advanced Economics Not Available\n{str(e)}',
                   ha='center', va='center', fontsize=12)
        ax_err.axis('off')

    # Overall title
    fig.suptitle(f'Heat Reuse Economics - Complete Analysis ({wha} MW System)',
                fontsize=18, fontweight='bold', y=0.99)

    # Save to bytes buffer
    png_buffer = io.BytesIO()
    fig.savefig(png_buffer, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    png_buffer.seek(0)
    return png_buffer.getvalue()


# =============================================================================
# EXPORT UI
# =============================================================================

def create_export_buttons(analysis: dict, output_area) -> widgets.HBox:
    """
    Create export buttons that trigger downloads.

    Args:
        analysis: Complete analysis dictionary
        output_area: Output widget for status messages

    Returns:
        HBox containing export buttons
    """

    # CSV Export Button
    csv_button = widgets.Button(
        description='Export CSV',
        icon='download',
        button_style='info',
        tooltip='Download system data as CSV file',
        layout=widgets.Layout(width='140px')
    )

    # PNG Export Button
    png_button = widgets.Button(
        description='Export Charts',
        icon='image',
        button_style='success',
        tooltip='Download charts as PNG image',
        layout=widgets.Layout(width='140px')
    )

    def on_csv_click(b):
        """Handle CSV export button click."""
        output_area.clear_output()
        with output_area:
            try:
                # Generate timestamp for filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'heat_reuse_data_{timestamp}.csv'

                # Generate CSV data
                csv_data = export_system_data_csv(analysis)

                if is_colab():
                    # Write to temp file and download
                    with open(filename, 'wb') as f:
                        f.write(csv_data)
                    _download_colab(filename)
                    display(HTML(f'<p style="color: #28a745;">CSV downloaded: {filename}</p>'))
                else:
                    # Create download link for local Jupyter
                    link = _create_download_link(csv_data, filename, 'text/csv')
                    display(HTML(f'''
                        <div style="padding: 10px; background: #d4edda; border-radius: 8px; margin: 5px 0;">
                            <span style="color: #155724;">CSV ready: </span>{link}
                        </div>
                    '''))
            except Exception as e:
                display(HTML(f'<p style="color: #dc3545;">Export error: {str(e)}</p>'))

    def on_png_click(b):
        """Handle PNG export button click."""
        output_area.clear_output()
        with output_area:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'heat_reuse_charts_{timestamp}.png'

                # Show progress message - important for Colab where this takes time
                display(HTML('<p style="color: #666;">⏳ Generating charts... (this may take 5-15 seconds)</p>'))

                # Generate PNG data (reduced size for Colab compatibility)
                png_data = export_charts_png(analysis)

                # Clear progress message and show result
                output_area.clear_output()

                if is_colab():
                    with open(filename, 'wb') as f:
                        f.write(png_data)
                    _download_colab(filename)
                    display(HTML(f'<p style="color: #28a745;">✓ Charts downloaded: {filename}</p>'))
                else:
                    link = _create_download_link(png_data, filename, 'image/png')
                    display(HTML(f'''
                        <div style="padding: 10px; background: #d4edda; border-radius: 8px; margin: 5px 0;">
                            <span style="color: #155724;">Charts ready: </span>{link}
                        </div>
                    '''))
            except Exception as e:
                output_area.clear_output()
                display(HTML(f'''
                    <div style="padding: 10px; background: #f8d7da; border-radius: 8px; margin: 5px 0;">
                        <p style="color: #721c24; margin: 0 0 5px 0;"><strong>Export failed:</strong> {str(e)}</p>
                        <p style="color: #856404; margin: 0; font-size: 12px;">
                            Tip: If in Colab, try Runtime → Restart runtime, then re-run the notebook.
                        </p>
                    </div>
                '''))

    csv_button.on_click(on_csv_click)
    png_button.on_click(on_png_click)

    return widgets.HBox(
        [csv_button, png_button],
        layout=widgets.Layout(gap='10px')
    )


def display_export_section(output_area, analysis: dict):
    """
    Display the export section with buttons.

    Args:
        output_area: Output widget to display in
        analysis: Complete analysis dictionary
    """
    output_area.clear_output(wait=True)

    with output_area:
        # Section header
        header_html = """
        <div style="margin: 20px 0 10px 0; background-color: #f8f9fa; padding: 0; border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); overflow: hidden;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 12px 20px; font-size: 16px; font-weight: 600;">
                📥 Export Results
            </div>
            <div style="padding: 10px 20px; background: white;">
                <p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">
                    Save your analysis before the session ends. Downloads work in Colab and local Jupyter.
                </p>
            </div>
        </div>
        """
        display(HTML(header_html))

        # Create status output area for download messages
        status_output = widgets.Output()

        # Create and display buttons
        buttons = create_export_buttons(analysis, status_output)
        display(buttons)
        display(status_output)


# =============================================================================
# TOGGLE FOR EXPORT SECTION
# =============================================================================

SHOW_EXPORT = True  # Set to False to hide export section
