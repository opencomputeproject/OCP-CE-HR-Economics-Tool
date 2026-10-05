"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2025-10-08
"""

"""
Display Formatting and Input Validation
Extracted from Interactive Analysis Tool.ipynb
Updated 2026-01-07: High-contrast colors for light/dark mode compatibility
"""

from .config import DISPLAY_ROUNDING, VALIDATION_RULES, MESSAGE_STYLES
from .styles import COLORS, wrap_in_container, create_styled_table

# =============================================================================
# DISPLAY FORMATTING FUNCTIONS
# =============================================================================

def format_display_value(value, rounding_type, include_units=True, units=""):
    """
    Format a value for display according to the rounding preferences.
    
    Args:
        value: The numerical value to format
        rounding_type: Key from DISPLAY_ROUNDING dict
        include_units: Whether to include units in the output
        units: Unit string to append (e.g., "°C", "€", "l/m")
    
    Returns:
        Formatted string ready for display
    """
    if value is None:
        return "N/A"
    
    try:
        decimal_places = DISPLAY_ROUNDING.get(rounding_type, 0)
        
        if decimal_places >= 0:
            # Standard decimal rounding
            rounded_value = round(float(value), decimal_places)
            if decimal_places == 0:
                formatted = f"{int(rounded_value):,}"
            else:
                formatted = f"{rounded_value:,.{decimal_places}f}"
        else:
            # Round to nearest 10^(-decimal_places)
            # e.g., -2 means round to nearest 100, -3 means round to nearest 1000
            multiplier = 10 ** (-decimal_places)
            rounded_value = round(float(value) / multiplier) * multiplier
            formatted = f"{int(rounded_value):,}"
        
        if include_units and units:
            return f"{formatted}{units}"
        else:
            return formatted
            
    except (ValueError, TypeError):
        return str(value)

# =============================================================================
# HTML GENERATION FUNCTIONS
# =============================================================================

def create_result_html(title, data_rows, border_color, title_color):
    """
    Generate HTML for result displays with consistent styling.
    Uses explicit backgrounds and high-contrast colors for light/dark mode compatibility.

    Args:
        title: Section title
        data_rows: List of (label, value) tuples
        border_color: CSS color for border
        title_color: CSS color for title

    Returns:
        HTML string for display
    """
    rows_html = ""
    for i, (label, value) in enumerate(data_rows):
        is_last = i == len(data_rows) - 1
        is_total = is_last and "TOTAL" in label.upper()

        if is_total:
            # Total row - highly visible purple on gradient background
            rows_html += f"""
            <tr style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <td style="padding: 14px 15px; font-weight: bold; font-size: 18px; color: white;">{label}</td>
                <td style="padding: 14px 15px; font-weight: bold; font-size: 18px; color: white; text-align: right;">{value}</td>
            </tr>"""
        else:
            # Regular row - DARK text on light background for high contrast
            row_bg = "#ECEFF1" if i % 2 == 1 else "white"
            border_style = "border-bottom: 1px solid #e0e0e0;" if not is_last else ""
            rows_html += f"""
            <tr style="background-color: {row_bg};">
                <td style="padding: 10px 15px; font-weight: 600; color: #000000; {border_style}">{label}</td>
                <td style="padding: 10px 15px; color: #00C853; font-weight: 700; text-align: right; {border_style}">{value}</td>
            </tr>"""

    # Title gradient based on color
    if '#4CAF50' in title_color or 'green' in title_color.lower():
        title_gradient = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
    elif '#2196F3' in title_color or 'blue' in title_color.lower():
        title_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    else:
        title_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    return f"""
    <div style="background-color: #f8f9fa; padding: 0; border-radius: 12px;
                border: 2px solid {border_color}; margin: 10px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;">
        <div style="background: {title_gradient}; color: white;
                    padding: 14px 20px; margin: 0; font-size: 16px; font-weight: 600;">
            {title}
        </div>
        <div style="padding: 15px; background-color: #f8f9fa;">
            <table style="width: 100%; border-collapse: collapse; background: white;
                          border-radius: 8px; overflow: hidden;">
                {rows_html}
            </table>
        </div>
    </div>
    """

def create_error_html(message, message_type='error'):
    """
    Generate error/warning/info HTML with consistent styling.
    Uses explicit colors for visibility on both light and dark backgrounds.

    Args:
        message: Message to display
        message_type: Type of message ('error', 'warning', 'info', 'success')

    Returns:
        HTML string for display
    """
    # High-contrast message styles
    styles = {
        'success': {
            'bg': '#d4edda',
            'border': '#28a745',
            'text': '#155724',
            'icon': '✅'
        },
        'error': {
            'bg': '#f8d7da',
            'border': '#dc3545',
            'text': '#721c24',
            'icon': '❌'
        },
        'warning': {
            'bg': '#fff3cd',
            'border': '#ffc107',
            'text': '#856404',
            'icon': '⚠️'
        },
        'info': {
            'bg': '#e3f2fd',
            'border': '#2196F3',
            'text': '#0d47a1',
            'icon': 'ℹ️'
        }
    }

    s = styles.get(message_type, styles['error'])

    return f"""
    <div style="background-color: {s['bg']}; color: {s['text']};
                padding: 15px 20px; border-radius: 8px; margin: 10px 0;
                border: 2px solid {s['border']};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <strong>{s['icon']} {message}</strong>
    </div>
    """

def create_validation_errors_html(errors):
    """
    Generate HTML for multiple validation errors.
    Uses explicit styling for visibility on both light and dark backgrounds.

    Args:
        errors: List of error messages

    Returns:
        HTML string for display
    """
    error_list = "".join([f"<li style='margin: 5px 0; color: #721c24;'>{error}</li>" for error in errors])
    return f"""
    <div style="background-color: #f8d7da; color: #721c24;
                padding: 15px 20px; border-radius: 8px; margin: 10px 0;
                border: 2px solid #dc3545;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <strong style="color: #721c24;">❌ Input Validation Errors:</strong>
        <ul style="margin: 10px 0 0 0; padding-left: 20px;">
            {error_list}
        </ul>
    </div>
    """

# =============================================================================
# INPUT VALIDATION FUNCTIONS
# =============================================================================

def validate_user_inputs(wha, T1, itdt, approach):
    """
    Validate user inputs against configured rules.
    
    Args:
        wha: Selected wha value
        T1: Selected T1 temperature
        itdt: Selected temperature difference
        approach: Selected approach value
    
    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    
    # Validate wha
    wha_rule = VALIDATION_RULES['wha']
    if wha not in wha_rule['valid_options']:
        errors.append(f"{wha_rule['error_message']} (got {wha})")
    
    # Validate T1
    T1_rule = VALIDATION_RULES['T1']
    if T1 not in T1_rule['valid_options']:
        errors.append(f"{T1_rule['error_message']} (got {T1})")
    
    # Validate temperature difference
    itdt_rule = VALIDATION_RULES['itdt']
    if itdt not in itdt_rule['valid_options']:
        errors.append(f"{itdt_rule['error_message']} (got {itdt})")
    
    # Validate approach
    approach_rule = VALIDATION_RULES['approach']
    if approach not in approach_rule['valid_options']:
        errors.append(f"{approach_rule['error_message']} (got {approach})")
    
    return errors

def validate_single_input(field_name, value):
    """
    Validate a single input field.
    
    Args:
        field_name: Name of the field to validate
        value: Value to validate
    
    Returns:
        True if valid, False otherwise
    """
    rule = VALIDATION_RULES.get(field_name)
    if not rule:
        return True  # No rule defined, assume valid
    
    return value in rule['valid_options']

# =============================================================================
# VALUE EXTRACTION AND FORMATTING HELPERS
# =============================================================================

def extract_formatted_system_params(system_data):
    """
    Extract and format system parameters for display.
    
    Args:
        system_data: System analysis data dictionary
    
    Returns:
        List of (label, formatted_value) tuples
    """
    return [
        ("T1 (Outlet to TCS):", format_display_value(system_data['T1'], 'temperature', True, '°C')),
        ("T2 (Inlet from TCS):", format_display_value(system_data['T2'], 'temperature', True, '°C')),
        ("T3 (Outlet to Consumer):", format_display_value(system_data['T3'], 'temperature', True, '°C')),
        ("T4 (Inlet from Consumer):", format_display_value(system_data['T4'], 'temperature', True, '°C')),
        ("F1 (TCS Flow Rate):", format_display_value(system_data['F1'], 'flow_rate', True, ' L/min')),
        ("F2 (FWS Flow Rate):", format_display_value(system_data['F2'], 'flow_rate', True, ' L/min'))
    ]

def extract_formatted_cost_analysis(costs_data, sizing_data):
    """
    Extract and format cost analysis data for display.

    Args:
        costs_data: Cost analysis data dictionary
        sizing_data: Sizing data dictionary

    Returns:
        List of (label, formatted_value) tuples
    """
    return [
        ("Room Size:", format_display_value(sizing_data['room_size'], 'room_size', True, ' m²')),
        ("Pipe Length Used:", format_display_value(costs_data['total_pipe_length'], 'room_size', True, ' m')),
        ("Suggested Pipe Size:", f"DN{format_display_value(sizing_data['primary_pipe_size'], 'pipe_size', False)}"),
        ("Pipe Cost per Meter:", f"€{format_display_value(costs_data['pipe_cost_per_meter'], 'pipe_cost_per_meter', False)}/m"),
        ("Total Pipe Cost:", f"€{format_display_value(costs_data['total_pipe_cost'], 'total_pipe_cost', False)}"),
        ("Fittings:", f"€{format_display_value(costs_data['fittings_cost'], 'fittings_cost', False)}"),
        ("Valve Costs:", f"€{format_display_value(costs_data['total_valve_cost'], 'valve_costs', False)}")
    ]

def extract_delta_t_values(system_data):
    """
    Calculate and format Delta T values for display.
    
    Args:
        system_data: System analysis data dictionary
    
    Returns:
        List of (label, formatted_value) tuples for Delta T values
    """
    # Import the calculation functions
    from core.original_calculations import get_itdt, get_oftkrdt
    
    itdt = get_itdt(system_data['T1'], system_data['T2'])
    oftkrdt = get_oftkrdt(system_data['T3'], system_data['T4'])
    
    return [
        ("Delta T for TCS (IT Medium):", format_display_value(itdt, 'temperature', True, '°C')),
        ("Delta T for FWS (Heating Medium):", format_display_value(oftkrdt, 'temperature', True, '°C'))
    ]

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def safe_float_convert(value):
    """
    Safely convert any value to float, handling strings with commas.
    
    Args:
        value: Value to convert
    
    Returns:
        Float value or 0.0 if conversion fails
    """
    from data.converter import universal_float_convert
    
    if isinstance(value, str):
        return universal_float_convert(value)
    elif isinstance(value, (int, float)):
        return float(value)
    else:
        return 0.0
    


def generate_smart_insights(analysis):
    """
    Generate smart recommendations based on current system analysis.
    
    Args:
        analysis: Complete system analysis dictionary
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    try:
        system = analysis['system']
        costs = analysis['costs']
        
        wha = system['wha']
        total_cost = costs['total_cost']
        cost_per_mw = total_cost / wha
        
        # Get heat exchanger effectiveness if available
        effectiveness = analysis.get('validation', {}).get('hx_effectiveness', 0.75)  # Default estimate
        
        # Cost efficiency recommendations
        if cost_per_mw < 20000:
            recommendations.append("💰 Excellent cost efficiency - below €20,000 per MW")
        elif cost_per_mw > 30000:
            recommendations.append("📈 Consider larger system size for better cost efficiency")
        else:
            recommendations.append("✅ Good cost efficiency for this system size")
        
        # wha size recommendations
        if wha < 1.5:
            next_size_cost_per_mw = estimate_cost_per_mw(wha + 0.5)
            improvement = ((cost_per_mw - next_size_cost_per_mw) / cost_per_mw) * 100
            if improvement > 10:
                recommendations.append(f"🎯 Scaling to {wha + 0.5} MW could improve cost efficiency by {improvement:.0f}%")
        
        # Temperature recommendations
        T1 = system['T1']
        T2 = system['T2']
        temp_rise = T2 - T1
        
        if T1 == 20:
            recommendations.append("🌟 Optimal T1 temperature for server cooling compatibility")
        elif T1 < 18:
            recommendations.append("❄️ Low T1 may require additional server cooling consideration")
        
        if temp_rise >= 12:
            recommendations.append("🔥 High temperature rise enables excellent heat recovery potential")
        elif temp_rise < 8:
            recommendations.append("⚡ Consider higher temperature rise for better heat recovery")
        
        # European compliance
        approach = system.get('approach', analysis.get('validation', {}).get('approach_calculated', 2))
        if approach >= 3:
            recommendations.append("✅ Conservative approach temperature - excellent for European standards")
        elif approach >= 2:
            recommendations.append("✅ Meets European minimum approach temperature requirements")
        
        # Flow rate insights
        F1 = system['F1']
        F2 = system['F2']
        if abs(F1 - F2) / max(F1, F2) < 0.1:
            recommendations.append("⚖️ Well-balanced flow rates for optimal heat transfer")
        
    except Exception as e:
        recommendations.append("⚠️ Unable to generate recommendations - check system data")
    
    return recommendations[:4]  # Limit to 4 recommendations for clean display

def estimate_cost_per_mw(target_mw):
    """
    Estimate cost per MW for a target wha size.
    Based on your MW price data trends.
    """
    # Simplified estimation based on your price data
    if target_mw <= 1:
        return 21000
    elif target_mw <= 2:
        return 19000
    elif target_mw <= 3:
        return 17300
    else:
        return 16000

def create_recommendations_html(recommendations, border_color="#4CAF50", title_color="#2E7D32"):
    """
    Create HTML for recommendations display matching cost analysis style.
    Uses explicit backgrounds and high-contrast colors for visibility.

    Args:
        recommendations: List of recommendation strings
        border_color: Border color for the box
        title_color: Title color

    Returns:
        HTML string for recommendations
    """
    rec_rows = ""
    for i, rec in enumerate(recommendations):
        row_bg = "#ECEFF1" if i % 2 == 1 else "white"
        rec_rows += f"""
        <tr style="background-color: {row_bg};">
            <td style="padding: 12px 15px; color: #000000; font-size: 14px; font-weight: 500;
                       border-bottom: 1px solid #e0e0e0;">
                {rec}
            </td>
        </tr>"""

    return f"""
    <div style="background-color: #f8f9fa; border-radius: 12px; margin: 15px 0;
                border: 2px solid {border_color};
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    color: white; padding: 14px 20px; font-size: 16px; font-weight: 600; text-align: center;">
            💡 Smart Recommendations
        </div>
        <div style="padding: 15px; background-color: #f8f9fa;">
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                {rec_rows}
            </table>
        </div>
    </div>
    """
    

def generate_performance_rating(cost_per_mw, effectiveness):
    """
    Generate performance rating based on cost efficiency and effectiveness.
    
    Returns:
        Dictionary with rating info
    """
    # Cost efficiency scoring
    if cost_per_mw < 20000:
        cost_score = 5
    elif cost_per_mw < 25000:
        cost_score = 4
    elif cost_per_mw < 30000:
        cost_score = 3
    else:
        cost_score = 2
    
    # Effectiveness scoring
    if effectiveness > 0.8:
        eff_score = 5
    elif effectiveness > 0.7:
        eff_score = 4
    elif effectiveness > 0.6:
        eff_score = 3
    else:
        eff_score = 2
    
    # Overall rating
    overall_score = (cost_score + eff_score) / 2
    
    if overall_score >= 4.5:
        rating = "⭐⭐⭐⭐⭐ EXCELLENT"
        color = "#4CAF50"
    elif overall_score >= 3.5:
        rating = "⭐⭐⭐⭐ VERY GOOD"
        color = "#8BC34A"
    elif overall_score >= 2.5:
        rating = "⭐⭐⭐ GOOD"
        color = "#FFC107"
    else:
        rating = "⭐⭐ ACCEPTABLE"
        color = "#FF9800"
    
    return {
        'rating': rating,
        'color': color,
        'cost_score': cost_score,
        'eff_score': eff_score
    }
    
def calculate_effectiveness(analysis):
    """
    Calculate real heat exchanger effectiveness from system parameters.
    
    Args:
        analysis: System analysis dictionary
    
    Returns:
        Float: Effectiveness value (0.0 to 1.0)
    """
    # Import the heat exchanger function
    from physics.heat_exchangers import heat_exchanger_for_heat_reuse_tool
    
    # Extract parameters
    system = analysis['system']
    F1 = system['F1']  # TCS flow
    F2 = system['F2']  # FWS flow  
    T1 = system['T1']  # TCS inlet
    T2 = system['T2']  # TCS outlet
    T3 = system['T3']  # FWS outlet
    T4 = system['T4']  # FWS inlet
    
    # Calculate real effectiveness
    hx_analysis = heat_exchanger_for_heat_reuse_tool(F1, F2, T1, T2, T3, T4)
    
    return hx_analysis['effectiveness']

def create_summary_cards_html(wha, total_cost, cost_per_mw, effectiveness, rating_info, eu_compliant):
    """
    Create HTML for visual summary cards.
    Uses explicit backgrounds and high-contrast colors for visibility on light/dark modes.
    """
    return f"""
    <div style="margin: 20px 0; background-color: #f8f9fa; padding: 20px; border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

        <!-- Section Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 14px 20px; border-radius: 8px;
                    font-size: 18px; font-weight: 600; text-align: center; margin-bottom: 20px;">
            📊 System Overview
        </div>

        <div style="display: flex; gap: 20px; flex-wrap: wrap;">

            <!-- System Performance Card -->
            <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 12px;
                        flex: 1; min-width: 280px; background: white;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                            color: white; padding: 10px 15px; border-radius: 6px;
                            margin: -20px -20px 15px -20px; font-size: 14px; font-weight: 600;">
                    🏢 System Performance
                </div>
                <div style="margin-bottom: 12px; color: #000000;">
                    <span style="color: #00C853; font-weight: bold; font-size: 18px;">{wha} MW</span>
                    <span style="color: #000000; font-weight: 500;"> Heat Recovery System</span>
                </div>
                <div style="margin-bottom: 12px; color: #000000; font-weight: 500;">
                    Effectiveness: <span style="color: #00C853; font-weight: bold;">{effectiveness:.1%}</span>
                    <div style="background: #e0e0e0; height: 10px; border-radius: 5px; margin-top: 6px;">
                        <div style="background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
                                    height: 10px; border-radius: 5px; width: {min(effectiveness*100, 100)}%;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 12px; color: #000000; font-weight: 500;">
                    EU Compliant: <span style="color: {'#00C853' if eu_compliant else '#f44336'}; font-weight: bold;">
                        {"✅ Yes" if eu_compliant else "❌ No"}</span>
                </div>
                <div style="color: {rating_info['color']}; font-weight: bold; font-size: 13px;
                            padding: 8px 12px; background: #f8f9fa; border-radius: 6px; text-align: center;">
                    {rating_info['rating']}
                </div>
            </div>

            <!-- Investment Summary Card -->
            <div style="border: 2px solid #2196F3; padding: 20px; border-radius: 12px;
                        flex: 1; min-width: 280px; background: white;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 10px 15px; border-radius: 6px;
                            margin: -20px -20px 15px -20px; font-size: 14px; font-weight: 600;">
                    💰 Investment Summary
                </div>
                <div style="margin-bottom: 12px; color: #000000; font-weight: 500;">
                    Quick Estimate: <span style="color: #00C853; font-weight: bold; font-size: 18px;">€{total_cost:,.0f}</span>
                    <div style="color: #555555; font-size: 12px; font-weight: 400; margin-top: 4px;">
                        Heat exchanger, pipe, valves, pumps at €5,000 per MW and a €10,000 installation allowance. Excludes fittings, instrumentation, engineering and contingency.
                    </div>
                </div>
                <div style="margin-bottom: 12px; color: #000000; font-weight: 500;">
                    Cost/MW: <span style="color: #00C853; font-weight: bold;">€{cost_per_mw:,.0f}</span>
                </div>
                <div style="margin-bottom: 12px; color: #000000; font-weight: 500;">
                    Cost/kW: <span style="color: #00C853; font-weight: bold;">€{cost_per_mw/1000:,.0f}</span>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="background: #e0e0e0; height: 24px; border-radius: 12px; position: relative; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 50%, #FFC107 100%);
                                    height: 24px; border-radius: 12px; width: 70%;"></div>
                        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                                    display: flex; align-items: center; justify-content: center;
                                    color: white; font-weight: bold; font-size: 11px;
                                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                            Cost Efficiency
                        </div>
                    </div>
                </div>
                <div style="color: {rating_info['color']}; font-weight: bold; font-size: 13px;
                            padding: 8px 12px; background: #f8f9fa; border-radius: 6px; text-align: center;">
                    Performance Rating: {rating_info['cost_score']}/5 ⭐
                </div>
            </div>

        </div>
    </div>
    """
    
    