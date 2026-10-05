"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2026-01-07

Advanced Economic Analysis Module
Based on October 24, 2025 email specifications

Key Calculations:
1. Annualized Capital Cost = CapEx / Payback Period
2. Total Annualized Cost = OpEx + Annualized CapEx
3. Normalized Capital Cost = CapEx / Capacity (MW)
4. Unit Heat Recovery Cost = Total Annualized Cost / (MW × 1000 × 8760) [€/kWh]

TOGGLE: Set SHOW_ADVANCED_ECONOMICS = False to hide this entire section
"""

from IPython.display import display, HTML, clear_output
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
import logging
import io
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from core.costs import calculate_order_of_magnitude_estimate

# =============================================================================
# MASTER TOGGLE - Set to False to hide advanced economics section completely
# =============================================================================
SHOW_ADVANCED_ECONOMICS = True

# What the CapEx column is, shown under Tables A and B and in the PNG export
CAPEX_NOTE = ("CapEx is the same calculation as the Capital Estimate in the Economics Analysis table: "
              "equipment × 1.15 installation × 1.10 engineering × 1.10 contingency (× 1.3915), "
              "rounded to €500, shown in K€.")

@contextmanager
def suppress_logging():
    """Context manager to suppress logging output and print statements."""
    loggers = {
        'core.costs': logging.getLogger('core.costs'),
        'core.lookup': logging.getLogger('core.lookup'),
        'core.original_calculations': logging.getLogger('core.original_calculations')
    }
    original_levels = {name: logger.level for name, logger in loggers.items()}

    for logger in loggers.values():
        logger.setLevel(logging.CRITICAL)

    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            yield
    finally:
        for name, level in original_levels.items():
            loggers[name].setLevel(level)


# =============================================================================
# ADVANCED ECONOMIC CALCULATIONS
# =============================================================================

def calculate_advanced_metrics(capex_eur: float, opex_eur_year: float,
                               capacity_mw: float, payback_years: float = 5.0,
                               on_stream_hours: int = 8760) -> dict:
    """
    Calculate advanced economic metrics for heat recovery analysis.

    Args:
        capex_eur: Total capital cost in EUR
        opex_eur_year: Annual operating cost in EUR/year
        capacity_mw: Heat recovery capacity in MW
        payback_years: Payback period in years (default 5)
        on_stream_hours: Annual operating hours (default 8760 = 100% uptime)

    Returns:
        dict with all calculated metrics
    """
    # 1. Annualized Capital Cost (EUR/yr)
    annualized_capex = capex_eur / payback_years

    # 2. Total Annualized Cost (EUR/yr)
    total_annualized = opex_eur_year + annualized_capex

    # 3. Normalized Capital Cost (EUR/MW)
    normalized_capex = capex_eur / capacity_mw

    # 4. Unit Heat Recovery Cost (EUR/kWh)
    # = Total Annualized Cost / (MW × 1000 kW/MW × on_stream_hours)
    annual_energy_potential_kwh = capacity_mw * 1000 * on_stream_hours
    unit_heat_recovery_cost = total_annualized / annual_energy_potential_kwh

    # Calculate capacity factor for display
    capacity_factor = (on_stream_hours / 8760) * 100

    return {
        'capex_eur': capex_eur,
        'opex_eur_year': opex_eur_year,
        'capacity_mw': capacity_mw,
        'payback_years': payback_years,
        'on_stream_hours': on_stream_hours,
        'capacity_factor_pct': capacity_factor,
        'annualized_capex_eur_year': annualized_capex,
        'total_annualized_eur_year': total_annualized,
        'normalized_capex_eur_per_mw': normalized_capex,
        'unit_heat_recovery_cost_eur_per_kwh': unit_heat_recovery_cost,
        'annual_energy_potential_kwh': annual_energy_potential_kwh
    }


def generate_approach_comparison_data(wha: float, T1: float, temp_rise: float,
                                       payback_years: float = 5.0,
                                       on_stream_hours: int = 8760,
                                       approaches: list = None) -> list:
    """
    Generate comparison data across different approach temperatures.

    Args:
        wha: System power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C
        payback_years: Payback period in years
        on_stream_hours: Annual operating hours (default 8760)
        approaches: List of approach temperatures (default [2, 3, 5])

    Returns:
        List of dictionaries with metrics for each approach
    """
    if approaches is None:
        approaches = [2, 3, 5]

    results = []

    for approach in approaches:
        with suppress_logging():
            estimate = calculate_order_of_magnitude_estimate(wha, T1, temp_rise, approach)

        if estimate.get('status') == 'success':
            capex = estimate.get('capital_total', 0)
            opex = estimate.get('operating_cost_eur_year', 0)

            metrics = calculate_advanced_metrics(capex, opex, wha, payback_years, on_stream_hours)
            metrics['approach'] = approach
            results.append(metrics)

    return results


def generate_capacity_comparison_data(T1: float, temp_rise: float, approach: float,
                                       payback_years: float = 5.0,
                                       on_stream_hours: int = 8760,
                                       capacities: list = None) -> list:
    """
    Generate comparison data across different capacities.

    Args:
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C
        approach: Approach temperature in °C
        payback_years: Payback period in years
        on_stream_hours: Annual operating hours (default 8760)
        capacities: List of capacities in MW (default [1, 2, 3, 4, 5])

    Returns:
        List of dictionaries with metrics for each capacity
    """
    if capacities is None:
        capacities = [1, 2, 3, 4, 5]

    results = []

    for capacity in capacities:
        with suppress_logging():
            estimate = calculate_order_of_magnitude_estimate(capacity, T1, temp_rise, approach)

        if estimate.get('status') == 'success':
            capex = estimate.get('capital_total', 0)
            opex = estimate.get('operating_cost_eur_year', 0)

            metrics = calculate_advanced_metrics(capex, opex, capacity, payback_years, on_stream_hours)
            metrics['approach'] = approach
            results.append(metrics)

    return results


# =============================================================================
# HTML TABLE GENERATION
# =============================================================================

def create_comparison_table(data: list, title: str = "Economic Analysis") -> str:
    """
    Create HTML table with advanced economic metrics.

    Args:
        data: List of metric dictionaries from generate_*_comparison_data
        title: Table title

    Returns:
        HTML string
    """
    if not data:
        return "<p style='color: red;'>No data available</p>"

    html = f"""
    <div style="margin: 20px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa; padding: 20px; border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    color: white; padding: 14px 20px; border-radius: 8px 8px 0 0;
                    margin: -20px -20px 15px -20px; font-size: 18px; font-weight: 600;">
            📊 {title}
        </div>
        <table style="width: 100%; border-collapse: collapse; background: white;
                      border-radius: 0 0 8px 8px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <th style="padding: 12px; text-align: center; color: white; font-size: 12px;">Capacity<br/>(MW)</th>
                    <th style="padding: 12px; text-align: center; color: white; font-size: 12px;">Approach<br/>(°C)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px;">CapEx<br/>(K€)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px;">OpEx<br/>(K€/yr)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px;">Annualized<br/>CapEx (K€/yr)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px;">Total Ann.<br/>Cost (K€/yr)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px;">Normalized<br/>CapEx (K€/MW)</th>
                    <th style="padding: 12px; text-align: right; color: white; font-size: 12px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">Heat Recovery<br/>Cost (€/kWh)</th>
                </tr>
            </thead>
            <tbody>
    """

    # Find minimum total annualized cost for highlighting
    min_total = min(d['total_annualized_eur_year'] for d in data)

    for idx, row in enumerate(data):
        row_bg = "#ECEFF1" if idx % 2 == 1 else "white"
        is_optimal = abs(row['total_annualized_eur_year'] - min_total) < 1

        if is_optimal:
            row_bg = "#C8E6C9"  # Light green for optimal

        html += f"""
                <tr style="background-color: {row_bg};">
                    <td style="padding: 10px; text-align: center; color: #000; font-weight: 600;">{row['capacity_mw']}</td>
                    <td style="padding: 10px; text-align: center; color: #000; font-weight: 600;">{row['approach']}</td>
                    <td style="padding: 10px; text-align: right; color: #000; font-weight: 500;">{row['capex_eur']/1000:,.0f}</td>
                    <td style="padding: 10px; text-align: right; color: #000; font-weight: 500;">{row['opex_eur_year']/1000:,.1f}</td>
                    <td style="padding: 10px; text-align: right; color: #000; font-weight: 500;">{row['annualized_capex_eur_year']/1000:,.0f}</td>
                    <td style="padding: 10px; text-align: right; color: {'#00C853' if is_optimal else '#000'}; font-weight: {'700' if is_optimal else '500'};">{row['total_annualized_eur_year']/1000:,.0f}{'  ✓' if is_optimal else ''}</td>
                    <td style="padding: 10px; text-align: right; color: #000; font-weight: 500;">{row['normalized_capex_eur_per_mw']/1000:,.0f}</td>
                    <td style="padding: 10px; text-align: right; color: #9C27B0; font-weight: 700;">{row['unit_heat_recovery_cost_eur_per_kwh']:.4f}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
        <div style="margin-top: 12px; padding: 10px; background: white; border-radius: 6px;
                    font-size: 11px; color: #666; border: 1px solid #e0e0e0;">
            <strong>Note:</strong> Heat Recovery Cost assumes 100% on-stream (8760 hrs/yr).
            <span style="color: #00C853;">✓</span> = Lowest Total Annualized Cost (optimal economic point).
            <br/>Benchmark: &lt; €0.05/kWh competitive with natural gas, &lt; €0.15/kWh competitive with EU electricity.
        </div>
    </div>
    """

    return html


# =============================================================================
# CHART GENERATION
# =============================================================================

def create_annual_costs_chart(data: list, output_area, title_suffix: str = ""):
    """
    Chart 1: Annual Costs vs. Approach Temperature
    Shows OpEx, Annualized CapEx, Total Annualized Cost lines + Normalized CapEx bars.

    Args:
        data: List from generate_approach_comparison_data
        output_area: IPython output widget
        title_suffix: Optional suffix for title
    """
    if not data:
        return

    approaches = [d['approach'] for d in data]
    opex = [d['opex_eur_year'] / 1000 for d in data]  # K€
    annualized_capex = [d['annualized_capex_eur_year'] / 1000 for d in data]  # K€
    total_annualized = [d['total_annualized_eur_year'] / 1000 for d in data]  # K€
    normalized_capex = [d['normalized_capex_eur_per_mw'] / 1000 for d in data]  # K€/MW

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for Normalized CapEx (right axis)
    ax2 = ax1.twinx()
    bar_width = 0.6
    x_pos = np.arange(len(approaches))
    bars = ax2.bar(x_pos, normalized_capex, bar_width, color='#4CAF50', alpha=0.3,
                   hatch='///', label='Normalized CapEx (K€/MW)', edgecolor='#2E7D32')
    ax2.set_ylabel('Normalized CapEx (K€/MW)', fontsize=11, color='#2E7D32')
    ax2.tick_params(axis='y', labelcolor='#2E7D32')

    # Line charts (left axis)
    ax1.plot(x_pos, opex, 'b--', marker='o', linewidth=2, markersize=8, label='OpEx (K€/yr)')
    ax1.plot(x_pos, annualized_capex, 'r--', marker='s', linewidth=2, markersize=8, label='Annualized CapEx (K€/yr)')
    ax1.plot(x_pos, total_annualized, 'purple', marker='^', linewidth=3, markersize=10, label='Total Annualized Cost (K€/yr)')

    # Mark optimal point
    min_idx = total_annualized.index(min(total_annualized))
    ax1.scatter([min_idx], [total_annualized[min_idx]], s=200, c='gold', marker='*', zorder=5, edgecolors='black')
    ax1.annotate(f'Optimal: {total_annualized[min_idx]:.0f} K€/yr',
                xy=(min_idx, total_annualized[min_idx]),
                xytext=(10, 15), textcoords='offset points',
                fontsize=10, fontweight='bold', color='purple',
                arrowprops=dict(arrowstyle='->', color='purple'))

    ax1.set_xlabel('Approach Temperature (°C)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Annual Cost (K€/yr)', fontsize=11)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f'{a}°C' for a in approaches])
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    capacity = data[0]['capacity_mw']
    plt.title(f'Annual Costs vs. Approach Temperature - {capacity} MW System{title_suffix}',
              fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    # Show directly - caller is already in output context
    plt.show()
    plt.close()


def create_unit_cost_chart(data: list, output_area, title_suffix: str = ""):
    """
    Chart 2: Unit Heat Recovery Cost vs. Approach Temperature
    Shows Unit Cost line + Normalized CapEx bars.

    Args:
        data: List from generate_approach_comparison_data
        output_area: IPython output widget
        title_suffix: Optional suffix for title
    """
    if not data:
        return

    approaches = [d['approach'] for d in data]
    unit_cost = [d['unit_heat_recovery_cost_eur_per_kwh'] for d in data]  # €/kWh
    normalized_capex = [d['normalized_capex_eur_per_mw'] / 1000 for d in data]  # K€/MW

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for Normalized CapEx (right axis)
    ax2 = ax1.twinx()
    bar_width = 0.6
    x_pos = np.arange(len(approaches))
    bars = ax2.bar(x_pos, normalized_capex, bar_width, color='#4CAF50', alpha=0.3,
                   hatch='///', label='Normalized CapEx (K€/MW)', edgecolor='#2E7D32')
    ax2.set_ylabel('Normalized CapEx (K€/MW)', fontsize=11, color='#2E7D32')
    ax2.tick_params(axis='y', labelcolor='#2E7D32')

    # Line chart for Unit Cost (left axis)
    ax1.plot(x_pos, unit_cost, 'm-', marker='o', linewidth=3, markersize=10,
             label='Heat Recovery Cost (€/kWh)')

    # Add benchmark lines
    ax1.axhline(y=0.05, color='orange', linestyle=':', linewidth=2, alpha=0.7, label='Natural Gas Benchmark (€0.05)')
    ax1.axhline(y=0.15, color='red', linestyle=':', linewidth=2, alpha=0.7, label='EU Electricity Benchmark (€0.15)')

    # Mark minimum point
    min_idx = unit_cost.index(min(unit_cost))
    ax1.scatter([min_idx], [unit_cost[min_idx]], s=200, c='gold', marker='*', zorder=5, edgecolors='black')
    ax1.annotate(f'Min: €{unit_cost[min_idx]:.4f}/kWh',
                xy=(min_idx, unit_cost[min_idx]),
                xytext=(10, 15), textcoords='offset points',
                fontsize=10, fontweight='bold', color='#9C27B0')

    ax1.set_xlabel('Approach Temperature (°C)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Unit Heat Recovery Cost (€/kWh)', fontsize=11, color='#9C27B0')
    ax1.tick_params(axis='y', labelcolor='#9C27B0')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f'{a}°C' for a in approaches])
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    capacity = data[0]['capacity_mw']
    plt.title(f'Unit Heat Recovery Cost vs. Approach Temperature - {capacity} MW System{title_suffix}',
              fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    # Show directly - caller is already in output context
    plt.show()
    plt.close()


def create_economy_of_scale_chart(data: list, output_area, title_suffix: str = ""):
    """
    Chart 3: Economy of Scale - Unit Cost vs. Capacity
    Shows how unit cost decreases with larger systems.

    Args:
        data: List from generate_capacity_comparison_data
        output_area: IPython output widget
        title_suffix: Optional suffix for title
    """
    if not data:
        return

    capacities = [d['capacity_mw'] for d in data]
    unit_cost = [d['unit_heat_recovery_cost_eur_per_kwh'] for d in data]  # €/kWh
    normalized_capex = [d['normalized_capex_eur_per_mw'] / 1000 for d in data]  # K€/MW

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for Normalized CapEx (right axis)
    ax2 = ax1.twinx()
    bar_width = 0.6
    x_pos = np.arange(len(capacities))
    bars = ax2.bar(x_pos, normalized_capex, bar_width, color='#4CAF50', alpha=0.3,
                   hatch='///', label='Normalized CapEx (K€/MW)', edgecolor='#2E7D32')
    ax2.set_ylabel('Normalized CapEx (K€/MW)', fontsize=11, color='#2E7D32')
    ax2.tick_params(axis='y', labelcolor='#2E7D32')

    # Line chart for Unit Cost (left axis)
    ax1.plot(x_pos, unit_cost, 'm-', marker='o', linewidth=3, markersize=10,
             label='Heat Recovery Cost (€/kWh)')

    # Add benchmark lines
    ax1.axhline(y=0.05, color='orange', linestyle=':', linewidth=2, alpha=0.7, label='Natural Gas (€0.05)')
    ax1.axhline(y=0.15, color='red', linestyle=':', linewidth=2, alpha=0.7, label='EU Electricity (€0.15)')

    # Add annotation for economy of scale
    cost_reduction = (unit_cost[0] - unit_cost[-1]) / unit_cost[0] * 100
    ax1.annotate(f'{cost_reduction:.0f}% cost reduction\n1→{capacities[-1]} MW',
                xy=(len(capacities)-1, unit_cost[-1]),
                xytext=(-60, 30), textcoords='offset points',
                fontsize=10, fontweight='bold', color='#9C27B0',
                arrowprops=dict(arrowstyle='->', color='#9C27B0'))

    ax1.set_xlabel('Heat Recovery Capacity (MW)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Unit Heat Recovery Cost (€/kWh)', fontsize=11, color='#9C27B0')
    ax1.tick_params(axis='y', labelcolor='#9C27B0')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f'{c} MW' for c in capacities])
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

    approach = data[0]['approach']
    plt.title(f'Economy of Scale: Unit Cost vs. Capacity - {approach}°C Approach{title_suffix}',
              fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    # Show directly - caller is already in output context
    plt.show()
    plt.close()


# =============================================================================
# MAIN DISPLAY FUNCTION
# =============================================================================

def display_advanced_economics(output_area, wha: float, T1: float, temp_rise: float,
                               payback_years: float = 5.0, on_stream_hours: int = 8760):
    """
    Display complete advanced economic analysis with interactive parameter selection.

    Args:
        output_area: IPython output widget to display in
        wha: Current system power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C (itdt)
        payback_years: Initial payback period in years (default 5)
        on_stream_hours: Initial on-stream hours (default 8760)
    """
    if not SHOW_ADVANCED_ECONOMICS:
        return

    output_area.clear_output(wait=True)

    with output_area:
        # Section header
        header_html = f"""
        <div style="margin: 20px 0 0 0; background-color: #f8f9fa; padding: 0; border-radius: 12px 12px 0 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                        color: white; padding: 16px 24px; font-size: 20px; font-weight: 600;">
                📈 Advanced Economic Analysis
            </div>
            <div style="padding: 10px 24px; background: white; border-bottom: 1px solid #e0e0e0;">
                <p style="margin: 0 0 8px 0; color: #333; font-size: 14px;">
                    <strong>Current System:</strong> <span style="color: #2196F3;">{wha} MW</span>
                </p>
            </div>
        </div>
        """
        display(HTML(header_html))

        # Use ipywidgets.interactive for Colab compatibility
        # This creates a self-contained interactive widget that works in Colab
        capex_note_html = f'<p style="margin: 6px 0 0 0; color: #555555; font-size: 12px;">{CAPEX_NOTE}</p>'

        def render_with_params(payback_yrs, on_stream_hrs):
            """Render analysis with given parameters - called by interactive."""
            try:
                # Calculate capacity factor percentage for display
                capacity_factor = (on_stream_hrs / 8760) * 100

                # Table A: Fixed Capacity, Variable Approach
                approach_data = generate_approach_comparison_data(
                    wha, T1, temp_rise, payback_yrs, on_stream_hrs
                )
                if approach_data:
                    table_a = create_comparison_table(
                        approach_data,
                        f"Table A: {wha} MW System - Variable Approach Temperature"
                    )
                    display(HTML(table_a))
                    display(HTML(capex_note_html))

                # Chart 1: Annual Costs vs Approach
                chart_header_1 = """
                <div style="margin: 25px 0 10px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600;">
                    📊 Chart 1: Annual Costs vs. Approach Temperature
                </div>
                """
                display(HTML(chart_header_1))
                create_annual_costs_chart(approach_data, None)

                # Chart 2: Unit Cost vs Approach
                chart_header_2 = """
                <div style="margin: 25px 0 10px 0; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600;">
                    ⚡ Chart 2: Unit Heat Recovery Cost vs. Approach Temperature
                </div>
                """
                display(HTML(chart_header_2))
                create_unit_cost_chart(approach_data, None)

                # Table B: Fixed Approach (current), Variable Capacity
                current_approach = 3  # Default to 3°C for comparison
                capacity_data = generate_capacity_comparison_data(
                    T1, temp_rise, current_approach, payback_yrs, on_stream_hrs
                )
                if capacity_data:
                    table_b = create_comparison_table(
                        capacity_data,
                        f"Table B: {current_approach}°C Approach - Variable Capacity (Economy of Scale)"
                    )
                    display(HTML(table_b))
                    display(HTML(capex_note_html))

                # Chart 3: Economy of Scale
                chart_header_3 = """
                <div style="margin: 25px 0 10px 0; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                            color: white; padding: 12px 20px; border-radius: 8px; font-weight: 600;">
                    🏭 Chart 3: Economy of Scale - Unit Cost vs. Capacity
                </div>
                """
                display(HTML(chart_header_3))
                create_economy_of_scale_chart(capacity_data, None)

                # Key insights
                insights_html = create_insights_summary(
                    approach_data, capacity_data, wha, payback_yrs, on_stream_hrs
                )
                display(HTML(insights_html))

            except Exception as e:
                error_html = f"""
                <div style="margin: 20px 0; padding: 15px 20px; background-color: #f8d7da;
                            border: 2px solid #dc3545; border-radius: 8px; color: #721c24;">
                    <strong>⚠️ Error in Advanced Economic Analysis:</strong> {str(e)}
                </div>
                """
                display(HTML(error_html))

        # Create interactive widget with dropdowns
        # Using interact_manual=False so it updates automatically on dropdown change
        interactive_widget = widgets.interactive(
            render_with_params,
            payback_yrs=widgets.Dropdown(
                options=[('5 years', 5.0), ('10 years', 10.0), ('15 years', 15.0), ('20 years', 20.0)],
                value=payback_years,
                description='Payback:',
                style={'description_width': '70px'},
                layout=widgets.Layout(width='180px')
            ),
            on_stream_hrs=widgets.Dropdown(
                options=[
                    ('8760 hrs (100%)', 8760),
                    ('8000 hrs (91%)', 8000),
                    ('6000 hrs (68%)', 6000),
                    ('4000 hrs (46%)', 4000)
                ],
                value=on_stream_hours,
                description='On-stream:',
                style={'description_width': '70px'},
                layout=widgets.Layout(width='200px')
            )
        )

        # Style the controls box
        interactive_widget.children[0].layout = widgets.Layout(
            padding='10px',
            margin='0 0 10px 0'
        )

        display(interactive_widget)


def create_insights_summary(approach_data: list, capacity_data: list, current_mw: float,
                            payback_years: float = 5.0, on_stream_hours: int = 8760) -> str:
    """
    Create summary of key economic insights.

    Args:
        approach_data: List of metrics for different approach temperatures
        capacity_data: List of metrics for different capacities
        current_mw: Current system capacity in MW
        payback_years: User-selected payback period
        on_stream_hours: User-selected on-stream hours
    """
    if not approach_data or not capacity_data:
        return ""

    # Calculate capacity factor for display
    capacity_factor = (on_stream_hours / 8760) * 100

    # Find optimal approach
    optimal_approach = min(approach_data, key=lambda x: x['total_annualized_eur_year'])

    # Find unit cost improvement from 1 MW to 5 MW
    mw_1 = next((d for d in capacity_data if d['capacity_mw'] == 1), None)
    mw_5 = next((d for d in capacity_data if d['capacity_mw'] == 5), None)

    cost_improvement = ""
    if mw_1 and mw_5:
        improvement_pct = (mw_1['unit_heat_recovery_cost_eur_per_kwh'] - mw_5['unit_heat_recovery_cost_eur_per_kwh']) / mw_1['unit_heat_recovery_cost_eur_per_kwh'] * 100
        cost_improvement = f"""
        <li><strong>Economy of Scale:</strong> {improvement_pct:.0f}% unit cost reduction from 1 MW to 5 MW</li>
        """

    # Check competitiveness
    current_approach_data = next((d for d in approach_data if d['approach'] == optimal_approach['approach']), None)
    competitive_status = ""
    if current_approach_data:
        unit_cost = current_approach_data['unit_heat_recovery_cost_eur_per_kwh']
        if unit_cost < 0.05:
            competitive_status = "✅ <strong>Competitive with natural gas</strong> (&lt;€0.05/kWh)"
        elif unit_cost < 0.15:
            competitive_status = "✅ <strong>Competitive with EU electricity</strong> (&lt;€0.15/kWh)"
        else:
            competitive_status = "⚠️ Above typical energy benchmarks"

    return f"""
    <div style="margin: 25px 0; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                padding: 20px; border-radius: 12px; border: 2px solid #4CAF50;">
        <h3 style="margin: 0 0 15px 0; color: #2E7D32;">💡 Key Economic Insights</h3>
        <ul style="margin: 0; padding-left: 20px; color: #333; line-height: 1.8;">
            <li><strong>Optimal Approach for {current_mw} MW:</strong> {optimal_approach['approach']}°C
                (Total Annualized: €{optimal_approach['total_annualized_eur_year']:,.0f}/yr)</li>
            <li><strong>Unit Heat Recovery Cost:</strong> €{optimal_approach['unit_heat_recovery_cost_eur_per_kwh']:.4f}/kWh at optimal point</li>
            {cost_improvement}
            <li><strong>Competitiveness:</strong> {competitive_status}</li>
        </ul>
        <p style="margin: 15px 0 0 0; font-size: 12px; color: #666; font-style: italic;">
            Based on <strong>{payback_years:.0f}-year</strong> payback period and <strong>{on_stream_hours:,} hrs/yr</strong> ({capacity_factor:.0f}%) on-stream operation.
        </p>
    </div>
    """


# =============================================================================
# PARAMETER SELECTION WIDGETS
# =============================================================================

def create_payback_dropdown():
    """
    Create payback period dropdown widget.

    Returns:
        ipywidgets.Dropdown
    """
    return widgets.Dropdown(
        options=[('5 years', 5), ('10 years', 10), ('15 years', 15), ('20 years', 20)],
        value=5,
        description='Payback Period:',
        style={'description_width': '110px'},
        layout=widgets.Layout(width='220px')
    )


def create_on_stream_dropdown():
    """
    Create on-stream hours dropdown widget.

    Options represent common operating scenarios:
    - 8760 hrs = 100% uptime (theoretical max)
    - 8000 hrs = 91% uptime (high availability)
    - 6000 hrs = 68% uptime (seasonal demand)
    - 4000 hrs = 46% uptime (winter heating only)

    Returns:
        ipywidgets.Dropdown
    """
    return widgets.Dropdown(
        options=[
            ('8760 hrs (100%)', 8760),
            ('8000 hrs (91%)', 8000),
            ('6000 hrs (68%)', 6000),
            ('4000 hrs (46%)', 4000)
        ],
        value=8760,
        description='On-stream:',
        style={'description_width': '110px'},
        layout=widgets.Layout(width='220px')
    )


# =============================================================================
# INTEGRATION HELPER
# =============================================================================

def should_show_advanced_economics() -> bool:
    """Check if advanced economic analysis should be displayed."""
    return SHOW_ADVANCED_ECONOMICS
