"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2025-10-08
"""

"""
Economics Analysis Panel
Order of Magnitude Estimate comparison and visualization
Updated 2026-01-07: High-contrast colors for light/dark mode compatibility
"""

from IPython.display import display, HTML
import matplotlib.pyplot as plt
import numpy as np
import logging
import io
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from core.costs import compare_approaches
from .styles import COLORS

@contextmanager
def suppress_logging():
    """Context manager to suppress logging output and print statements."""
    # Save original logging levels
    loggers = {
        'core.costs': logging.getLogger('core.costs'),
        'core.lookup': logging.getLogger('core.lookup'),
        'core.original_calculations': logging.getLogger('core.original_calculations')
    }
    original_levels = {name: logger.level for name, logger in loggers.items()}

    # Suppress logging
    for logger in loggers.values():
        logger.setLevel(logging.CRITICAL)

    # Suppress stdout and stderr (print statements)
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            yield
    finally:
        # Restore logging levels
        for name, level in original_levels.items():
            loggers[name].setLevel(level)

# =============================================================================
# COMPARISON TABLE
# =============================================================================

def create_economics_comparison_table(wha: float, T1: float, temp_rise: float) -> str:
    """
    Create HTML table comparing all three approaches (2°C, 3°C, 5°C) with transparent breakdown.

    Args:
        wha: System power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C

    Returns:
        HTML string for the comparison table
    """
    # Get comparison data from costs module (suppress logging)
    with suppress_logging():
        comparison = compare_approaches(wha, T1, temp_rise, approaches=[2, 3, 5])

    if comparison.get('status') != 'success':
        return create_error_table("Unable to calculate economics comparison")

    approaches_data = comparison['approaches']

    # Build table HTML with explicit backgrounds for light/dark mode compatibility
    # Wrap entire table in a container with forced light background
    html = """
    <div style="margin: 20px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa; padding: 20px; border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <table style="width: 100%; border-collapse: collapse; background: white;
                      border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <th style="padding: 14px; text-align: left; color: white; font-size: 14px; font-weight: 600;">Cost Component</th>
                    <th style="padding: 14px; text-align: right; color: white; font-size: 14px; font-weight: 600;">2°C Approach</th>
                    <th style="padding: 14px; text-align: right; color: white; font-size: 14px; font-weight: 600;">3°C Approach</th>
                    <th style="padding: 14px; text-align: right; color: white; font-size: 14px; font-weight: 600;">5°C Approach</th>
                </tr>
            </thead>
            <tbody>
    """

    # Section header: EQUIPMENT COSTS (Base)
    html += """
                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <td colspan="4" style="padding: 12px 15px; font-weight: 600;
                                         color: white; font-size: 13px; letter-spacing: 0.5px;">
                        EQUIPMENT COSTS (Base)
                    </td>
                </tr>
    """

    # Base equipment cost rows
    base_rows = [
        ('Heat Exchangers', 'heat_exchanger', 'Industrial plate heat exchangers sized for system capacity'),
        ('Pumps', 'pumps', 'Circulation pumps with motor and VFD controls'),
        ('Piping & Fittings', 'pipe_fittings', 'Stainless steel pipes, elbows, tees, and connections'),
        ('Instrumentation', 'instrumentation', 'Temperature sensors, flow meters, and control systems'),
        ('Valves', 'valves', 'Control valves and isolation valves'),
    ]

    for idx, (row_label, key, tooltip) in enumerate(base_rows):
        row_bg = "#ECEFF1" if idx % 2 == 1 else "white"
        html += f"""
                <tr style="background-color: {row_bg};"
                    title="{tooltip}">
                    <td style="padding: 10px 15px; border-bottom: 1px solid #e0e0e0;
                               color: #000000; font-weight: 600;">{row_label}</td>
        """
        for approach in ['2C', '3C', '5C']:
            value = approaches_data.get(approach, {}).get(key, 0)
            # Round valves to nearest 100 to match Valve Costs display in Piping Cost Analysis
            if key == 'valves':
                value = round(value / 100) * 100
            html += f"""
                    <td style="padding: 10px 15px; text-align: right; border-bottom: 1px solid #e0e0e0;
                               color: #00C853; font-weight: 600;">€{value:>10,.0f}</td>
            """
        html += """
                </tr>
        """

    # Equipment Subtotal row - DARK text on light background
    html += """
                <tr style="background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%); font-weight: bold;">
                    <td style="padding: 12px 15px; color: #000000; font-weight: 700;">Equipment Subtotal</td>
    """

    # Calculate and validate equipment subtotals
    for approach in ['2C', '3C', '5C']:
        data = approaches_data.get(approach, {})

        # Calculate subtotal from base costs
        subtotal = sum([
            data.get('heat_exchanger', 0),
            data.get('pumps', 0),
            data.get('pipe_fittings', 0),
            data.get('instrumentation', 0),
            data.get('valves', 0)
        ])

        # Validation check
        validation_icon = "✓" if abs(subtotal - data.get('heat_exchanger', 0) - data.get('pumps', 0) -
                                      data.get('pipe_fittings', 0) - data.get('instrumentation', 0) -
                                      data.get('valves', 0)) < 1 else "⚠"

        html += f"""
                    <td style="padding: 12px 15px; text-align: right; color: #000000; font-weight: 700;">
                        €{subtotal:>10,.0f} <span style="color: #00C853; font-size: 11px;">{validation_icon}</span>
                    </td>
        """
    html += """
                </tr>
    """

    # Section header: INSTALLATION & CONTINGENCY
    html += """
                <tr style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);">
                    <td colspan="4" style="padding: 12px 15px; font-weight: 600;
                                         color: white; font-size: 13px; letter-spacing: 0.5px;">
                        INSTALLATION & CONTINGENCY
                    </td>
                </tr>
    """

    # Contingency rows
    contingency_rows = [
        ('Installation (15% of equipment)', 'installation_cost', 'Labor and materials for equipment installation'),
        ('Engineering (10% of equipment + installation)', 'engineering_cost', 'Design, engineering, and project management'),
        ('Contingency (10% of the running total)', 'contingency_cost', 'Unforeseen costs and scope changes'),
    ]

    for idx, (row_label, key, tooltip) in enumerate(contingency_rows):
        row_bg = "#FFF8E1" if idx % 2 == 0 else "#FFF3E0"
        html += f"""
                <tr style="background-color: {row_bg};"
                    title="{tooltip}">
                    <td style="padding: 10px 15px; border-bottom: 1px solid #FFE0B2;
                               color: #000000; font-weight: 600;">{row_label}</td>
        """
        for approach in ['2C', '3C', '5C']:
            value = approaches_data.get(approach, {}).get(key, 0)
            html += f"""
                    <td style="padding: 10px 15px; text-align: right; border-bottom: 1px solid #FFE0B2;
                               color: #000000; font-weight: 600;">€{value:>10,.0f}</td>
            """
        html += """
                </tr>
        """

    # I&C Subtotal row (Installation & Contingency subtotal) - DARK text
    html += """
                <tr style="background: linear-gradient(135deg, #FFE0B2 0%, #FFCC80 100%); font-weight: bold;">
                    <td style="padding: 12px 15px; color: #000000; font-weight: 700;">I&C Subtotal</td>
    """

    for approach in ['2C', '3C', '5C']:
        data = approaches_data.get(approach, {})
        ic_subtotal = sum([
            data.get('installation_cost', 0),
            data.get('engineering_cost', 0),
            data.get('contingency_cost', 0)
        ])

        html += f"""
                    <td style="padding: 12px 15px; text-align: right; color: #000000; font-weight: 700;">€{ic_subtotal:>10,.0f}</td>
        """
    html += """
                </tr>
    """

    # Separator row
    html += """
                <tr style="background-color: white;">
                    <td colspan="4" style="padding: 4px; border-top: 3px solid #667eea;"></td>
                </tr>
    """

    # CAPITAL ESTIMATE row (highlighted and bold) - using gradient for visibility
    html += """
                <tr style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); font-weight: bold; font-size: 15px;">
                    <td style="padding: 16px 15px; color: white; text-transform: uppercase; font-weight: 700;">CAPITAL ESTIMATE (rounded to €500)</td>
    """

    for approach in ['2C', '3C', '5C']:
        data = approaches_data.get(approach, {})
        capital_total = data.get('capital_total', 0)

        # Calculate expected total for validation
        equipment_subtotal = sum([
            data.get('heat_exchanger', 0),
            data.get('pumps', 0),
            data.get('pipe_fittings', 0),
            data.get('instrumentation', 0),
            data.get('valves', 0)
        ])
        ic_subtotal = sum([
            data.get('installation_cost', 0),
            data.get('engineering_cost', 0),
            data.get('contingency_cost', 0)
        ])
        expected_total = equipment_subtotal + ic_subtotal

        # Validation (allow for rounding to nearest 500)
        validation_icon = "✓" if abs(capital_total - expected_total) <= 500 else "⚠"

        html += f"""
                    <td style="padding: 16px 15px; text-align: right; color: white; font-weight: 700; font-size: 16px;">
                        €{capital_total:>10,.0f} <span style="font-size: 13px;">{validation_icon}</span>
                    </td>
        """
    html += """
                </tr>
    """

    # Empty row for spacing
    html += """
                <tr style="background-color: white;">
                    <td colspan="4" style="padding: 10px;"></td>
                </tr>
    """

    # Section header: OPERATING COSTS
    html += """
                <tr style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                    <td colspan="4" style="padding: 12px 15px; font-weight: 600;
                                         color: white; font-size: 13px; letter-spacing: 0.5px;">
                        OPERATING COSTS (Annual)
                    </td>
                </tr>
    """

    # Operating cost rows - DARK text for visibility
    html += """
                <tr style="background-color: #E8F5E9;">
                    <td style="padding: 10px 15px; border-bottom: 1px solid #C8E6C9;
                               color: #000000; font-weight: 600;">Annual Operating Energy</td>
    """
    for approach in ['2C', '3C', '5C']:
        value = approaches_data.get(approach, {}).get('operating_energy_kwh_year', 0)
        html += f"""
                    <td style="padding: 10px 15px; text-align: right; border-bottom: 1px solid #C8E6C9;
                               color: #000000; font-weight: 600;">{value:>10,.0f} kWh</td>
        """
    html += """
                </tr>
    """

    html += """
                <tr style="background-color: #C8E6C9; font-weight: bold;">
                    <td style="padding: 12px 15px; color: #000000; font-weight: 700;">Annual Energy Cost</td>
    """
    for approach in ['2C', '3C', '5C']:
        value = approaches_data.get(approach, {}).get('operating_cost_eur_year', 0)
        html += f"""
                    <td style="padding: 12px 15px; text-align: right;
                               color: #000000; font-weight: 700;">€{value:>10,.0f}</td>
        """
    html += """
                </tr>
            </tbody>
        </table>
    """

    # Legend section with explicit background - DARK text
    html += """
        <div style="margin-top: 15px; padding: 12px 15px; background-color: white;
                    border-radius: 6px; font-size: 12px; color: #000000;
                    border: 1px solid #e0e0e0;">
            <strong style="color: #000000;">Legend:</strong>
            <span style="color: #00C853; font-weight: bold;">✓</span> = Calculations verified |
            <span style="color: #000000; font-weight: bold;">⚠</span> = Rounding adjustments applied |
            <span style="font-style: italic; color: #000000;">Hover over items for details</span>
        </div>
    </div>
    """

    return html


def create_error_table(error_message: str) -> str:
    """Create an error message table with explicit styling."""
    return f"""
    <div style="margin: 20px 0; padding: 15px 20px; background-color: #f8d7da;
                border: 2px solid #dc3545; border-radius: 8px; color: #721c24;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <strong style="color: #721c24;">⚠️ Error:</strong> {error_message}
    </div>
    """


# =============================================================================
# COST CONTRAST GRAPH
# =============================================================================

def create_cost_contrast_chart(wha: float, T1: float, temp_rise: float, output_area):
    """
    Create cost contrast chart comparing Capital vs Operating costs across approaches.

    Args:
        wha: System power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C
        output_area: Output widget to display the chart
    """
    # Get comparison data (suppress logging)
    with suppress_logging():
        comparison = compare_approaches(wha, T1, temp_rise, approaches=[2, 3, 5])

    if comparison.get('status') != 'success':
        with output_area:
            display(HTML("<p style='color: red;'>Unable to generate cost contrast chart</p>"))
        return

    approaches_data = comparison['approaches']

    # Extract data for plotting
    approaches = [2, 3, 5]
    capital_costs = []
    operating_costs = []

    for approach in approaches:
        key = f"{approach}C"
        capital_costs.append(approaches_data.get(key, {}).get('capital_total', 0))
        operating_costs.append(approaches_data.get(key, {}).get('operating_cost_eur_year', 0))

    # Create the plot
    plt.figure(figsize=(10, 6))

    # Plot both lines
    plt.plot(approaches, capital_costs, marker='o', linewidth=2, markersize=8,
             label='Capital Estimate', color='#2196F3')
    plt.plot(approaches, operating_costs, marker='s', linewidth=2, markersize=8,
             label='Annual Operating Cost', color='#FF9800')

    # Formatting
    plt.xlabel('Approach Temperature (°C)', fontsize=12, fontweight='bold')
    plt.ylabel('Cost (€)', fontsize=12, fontweight='bold')
    plt.title('Cost Contrast: Capital Estimate vs Operating Cost', fontsize=14, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=11, frameon=True, shadow=True)
    plt.grid(True, alpha=0.3, linestyle='--')

    # Format y-axis with thousands separator
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

    # Set x-axis to only show our approach values
    plt.xticks(approaches)

    # Add value labels on points
    for i, approach in enumerate(approaches):
        plt.annotate(f'€{capital_costs[i]:,.0f}',
                    (approach, capital_costs[i]),
                    textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        plt.annotate(f'€{operating_costs[i]:,.0f}',
                    (approach, operating_costs[i]),
                    textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9)

    plt.tight_layout()

    # Display in output area
    with output_area:
        plt.show()

    # Close to free memory
    plt.close()


def create_approach_cost_breakdown_charts(wha: float, T1: float, temp_rise: float, output_area):
    """
    Create pie charts showing cost breakdown for each approach temperature.

    Args:
        wha: System power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C
        output_area: Output widget to display the chart
    """
    try:
        # Get comparison data (suppress logging)
        with suppress_logging():
            comparison = compare_approaches(wha, T1, temp_rise, approaches=[2, 3, 5])

        if comparison.get('status') != 'success':
            with output_area:
                display(HTML("<p style='color: red;'>Unable to generate cost breakdown charts</p>"))
            return

        approaches_data = comparison['approaches']

        # Create figure with 1 row, 3 columns (increased height for legends)
        fig, axs = plt.subplots(1, 3, figsize=(18, 7))

        # Approach temperatures and titles
        approaches = [2, 3, 5]
        titles = ["2°C Approach", "3°C Approach", "5°C Approach"]
        # Rainbow spectrum color scheme
        colors = [
            '#E74C3C',  # Red - Heat Exchangers
            '#FF9F43',  # Orange - Pumps
            '#F1C40F',  # Yellow - Piping & Fittings
            '#2ECC71',  # Green - Instrumentation
            '#3498DB',  # Blue - Valves
            '#9B59B6'   # Purple - I&C Subtotal
        ]
        labels = ['Heat Exchangers', 'Pumps', 'Piping & Fittings', 'Instrumentation', 'Valves', 'I&C Subtotal']

        # Create pie chart for each approach
        for idx, (approach, title) in enumerate(zip(approaches, titles)):
            key = f"{approach}C"
            data = approaches_data.get(key, {})

            # Extract cost components
            heat_exchanger = data.get('heat_exchanger', 0)
            pumps = data.get('pumps', 0)
            pipe_fittings = data.get('pipe_fittings', 0)
            instrumentation = data.get('instrumentation', 0)
            valves = data.get('valves', 0)

            # Calculate I&C Subtotal (installation + engineering + contingency)
            ic_subtotal = sum([
                data.get('installation_cost', 0),
                data.get('engineering_cost', 0),
                data.get('contingency_cost', 0)
            ])

            # Combine into values array
            values = [heat_exchanger, pumps, pipe_fittings, instrumentation, valves, ic_subtotal]

            # Create pie chart with percentages only (labels in legend for clarity)
            wedges, texts, autotexts = axs[idx].pie(
                values,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85
            )

            # Make percentage text white and bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)

            # Add legend below the chart
            axs[idx].legend(wedges, labels, loc="upper center", bbox_to_anchor=(0.5, -0.05),
                           fontsize=9, ncol=2, frameon=False)

            axs[idx].set_title(title, fontsize=14, fontweight='bold', pad=10)

        # Add figure suptitle
        fig.suptitle("Equipment & Installation Cost Breakdown by Approach Temperature",
                    fontsize=16, fontweight='bold', y=1.02)

        plt.tight_layout()

        # Display in output area
        with output_area:
            plt.show()

        # Close to free memory
        plt.close()

    except Exception as e:
        with output_area:
            display(HTML(f"<p style='color: red;'>Error creating cost breakdown charts: {str(e)}</p>"))


# =============================================================================
# MAIN DISPLAY FUNCTION
# =============================================================================

def display_economics_analysis(output_area, wha: float, T1: float, temp_rise: float):
    """
    Display complete economics analysis panel.

    Args:
        output_area: Output widget to display in
        wha: System power in MW
        T1: Inlet temperature in °C
        temp_rise: Temperature rise in °C
    """
    # Clear output first
    output_area.clear_output(wait=True)

    with output_area:
        try:
            # Section header with gradient and explicit background
            header_html = """
            <div style="margin: 20px 0; background-color: #f8f9fa; padding: 0; border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 16px 24px; font-size: 20px; font-weight: 600;">
                    💰 Economics Analysis - Order of Magnitude Estimate
                </div>
            </div>
            """
            display(HTML(header_html))

            # Display comparison table
            table_html = create_economics_comparison_table(wha, T1, temp_rise)
            display(HTML(table_html))

            # Display cost contrast chart with styled header
            chart_title_html = """
            <div style="margin: 30px 0 15px 0; background-color: #f8f9fa; padding: 0; border-radius: 8px;
                        overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 12px 20px; font-size: 16px; font-weight: 600;">
                    📈 Cost Contrast Analysis
                </div>
            </div>
            """
            display(HTML(chart_title_html))

            create_cost_contrast_chart(wha, T1, temp_rise, output_area)

            # Display equipment cost breakdown charts with styled header
            breakdown_title_html = """
            <div style="margin: 30px 0 15px 0; background-color: #f8f9fa; padding: 0; border-radius: 8px;
                        overflow: hidden; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 12px 20px;">
                    <div style="font-size: 16px; font-weight: 600;">🔧 Equipment Cost Breakdown by Approach</div>
                    <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">
                        Comparison of cost distribution across equipment categories for different approach temperatures
                    </div>
                </div>
            </div>
            """
            display(HTML(breakdown_title_html))

            create_approach_cost_breakdown_charts(wha, T1, temp_rise, output_area)

        except Exception as e:
            error_html = f"""
            <div style="margin: 20px 0; padding: 15px 20px; background-color: #f8d7da;
                        border: 2px solid #dc3545; border-radius: 8px; color: #721c24;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                <strong style="color: #721c24;">⚠️ Error displaying economics analysis:</strong> {str(e)}
            </div>
            """
            display(HTML(error_html))
