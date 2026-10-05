"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2025-10-08
"""

"""
Output Display Functions
Extracted from Interactive Analysis Tool.ipynb
Updated 2026-01-07: High-contrast colors for light/dark mode compatibility
"""

from IPython.display import display, HTML
import matplotlib.pyplot as plt
from .config import OUTPUT_CONFIG
from .styles import COLORS, inject_global_styles
from .formatting import (
    create_result_html, create_error_html, create_validation_errors_html,
    extract_formatted_system_params, extract_formatted_cost_analysis, 
    extract_delta_t_values,
    generate_smart_insights, generate_performance_rating,
    create_recommendations_html, create_summary_cards_html,
    calculate_effectiveness 
)
from .charts import create_system_charts

# =============================================================================
# MAIN OUTPUT DISPLAY FUNCTIONS
# =============================================================================

def display_system_parameters(output_area, analysis):
    """
    Display system parameters with proper formatting.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    output_area.clear_output(wait=True)
    with output_area:
        try:
            system = analysis['system']
            
            # Extract and format basic parameters
            basic_params = extract_formatted_system_params(system)
            
            # Extract and format Delta T values
            delta_t_params = extract_delta_t_values(system)
            
            # Combine all parameters
            all_params = basic_params + delta_t_params
            
            # Get styling configuration
            config = OUTPUT_CONFIG['system_params']
            
            # Create and display HTML
            html_content = create_result_html(
                title=config['title'],
                data_rows=all_params,
                border_color=config['border_color'],
                title_color=config['title_color']
            )
            
            display(HTML(html_content))
            
        except Exception as e:
            display_error(output_area, f"Error displaying system parameters: {str(e)}")

def display_cost_analysis(output_area, analysis):
    """
    Display cost analysis with proper formatting.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    output_area.clear_output(wait=True)
    with output_area:
        try:
            costs = analysis['costs']
            sizing = analysis['sizing']
            
            # Extract and format cost data
            cost_params = extract_formatted_cost_analysis(costs, sizing)
            
            # Get styling configuration
            config = OUTPUT_CONFIG['cost_analysis']
            
            # Create and display HTML
            html_content = create_result_html(
                title=config['title'],
                data_rows=cost_params,
                border_color=config['border_color'],
                title_color=config['title_color']
            )
            
            display(HTML(html_content))
            
        except Exception as e:
            display_error(output_area, f"Error displaying cost analysis: {str(e)}")

def display_charts(output_area, analysis):
    """
    Display charts with guaranteed fresh creation.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    # Double-clear to ensure fresh start
    output_area.clear_output()

    with output_area:
        try:
            # Force matplotlib to close any existing figures
            plt.close('all')

            # Create fresh charts
            create_system_charts(analysis)

        except Exception as e:
            display_error(output_area, f"Error creating charts: {str(e)}")

def display_economics_panel(output_area, analysis):
    """
    Display economics analysis panel with comparison table and charts.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    from .economics_panel import display_economics_analysis

    try:
        # Extract parameters from analysis
        system = analysis.get('system', {})
        wha = system.get('wha', 1.0)
        T1 = system.get('T1', 20)
        temp_rise = system.get('itdt', 10)

        # Display economics analysis
        display_economics_analysis(output_area, wha, T1, temp_rise)

    except Exception as e:
        display_error(output_area, f"Error displaying economics analysis: {str(e)}")


def display_advanced_economics_panel(output_area, analysis):
    """
    Display Advanced Economic Analysis panel.

    This analysis includes:
    - Annualized Capital Cost
    - Total Annualized Cost
    - Normalized CapEx (€/MW)
    - Unit Heat Recovery Cost (€/kWh)

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    try:
        from .advanced_economics import display_advanced_economics, should_show_advanced_economics

        # Check if advanced economics should be shown (master toggle)
        if not should_show_advanced_economics():
            return

        # Extract parameters from analysis
        system = analysis.get('system', {})
        wha = system.get('wha', 1.0)
        T1 = system.get('T1', 20)
        temp_rise = system.get('itdt', 10)

        # Display advanced economics (with default 5-year payback)
        display_advanced_economics(output_area, wha, T1, temp_rise, payback_years=5.0)

    except ImportError as e:
        # If advanced_economics module not found, silently skip
        pass
    except Exception as e:
        display_error(output_area, f"Error displaying advanced economics: {str(e)}")


def display_export_panel(output_area, analysis):
    """
    Display Export panel with CSV and PNG download buttons.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    try:
        from .export import display_export_section, SHOW_EXPORT

        # Check if export should be shown (master toggle)
        if not SHOW_EXPORT:
            return

        display_export_section(output_area, analysis)

    except ImportError as e:
        # If export module not found, silently skip
        pass
    except Exception as e:
        display_error(output_area, f"Error displaying export panel: {str(e)}")


# =============================================================================
# ERROR AND MESSAGE DISPLAY FUNCTIONS
# =============================================================================

def display_validation_errors(output_area, errors):
    """
    Display validation errors in the output area.
    
    Args:
        output_area: Output widget to display in
        errors: List of error messages
    """
    with output_area:
        html_content = create_validation_errors_html(errors)
        display(HTML(html_content))

def no_data_message(approach, available):
    """
    Message for a combination with no data.

    If the selected approach has no rows at all in the heat exchanger data,
    say so and list the approaches that do. Otherwise use the general message.

    Args:
        approach: Selected approach temperature in °C
        available: Approaches present in the data (from get_available_approaches)
    """
    if available and approach not in available:
        listed = ", ".join(f"{a:g}" for a in available)
        return (f"Data for a {approach:g} °C approach is not yet available. "
                f"Available approaches: {listed} °C.")
    return "No data found for the selected parameters. Please try a different combination."

def display_no_data_error(output_area, approach=None):
    """
    Display error when no data is found for selected parameters.

    Args:
        output_area: Output widget to display in
        approach: Selected approach temperature in °C, if known
    """
    from core.lookup import get_available_approaches

    available = get_available_approaches() if approach is not None else []
    with output_area:
        html_content = create_error_html(no_data_message(approach, available), 'error')
        display(HTML(html_content))

def display_error(output_area, message, message_type='error'):
    """
    Display a general error message.
    
    Args:
        output_area: Output widget to display in
        message: Error message to display
        message_type: Type of message ('error', 'warning', 'info')
    """
    with output_area:
        html_content = create_error_html(message, message_type)
        display(HTML(html_content))

def display_success_message(output_area, message):
    """
    Display a success message.
    
    Args:
        output_area: Output widget to display in
        message: Success message to display
    """
    display_error(output_area, message, 'success')

def display_info_message(output_area, message):
    """
    Display an info message.
    
    Args:
        output_area: Output widget to display in
        message: Info message to display
    """
    display_error(output_area, message, 'info')

# =============================================================================
# COMBINED DISPLAY FUNCTIONS
# =============================================================================

def display_complete_analysis(outputs_dict, analysis):
    """
    Display complete analysis in all output areas including new sections.

    Args:
        outputs_dict: Dictionary of output widgets
        analysis: Complete system analysis dictionary
    """
    try:
        display_system_parameters(outputs_dict['system_params'], analysis)
        display_cost_analysis(outputs_dict['cost_analysis'], analysis)

        # Economics Analysis panel
        if 'economics_analysis' in outputs_dict:
            display_economics_panel(outputs_dict['economics_analysis'], analysis)

        display_charts(outputs_dict['charts'], analysis)

        # Smart recommendations in their own section
        if 'smart_recommendations' in outputs_dict:
            display_smart_recommendations(outputs_dict['smart_recommendations'], analysis)

        # Visual summary at the bottom
        if 'visual_summary' in outputs_dict:
            display_visual_summary_cards(outputs_dict['visual_summary'], analysis)

        # Advanced Economic Analysis
        if 'advanced_economics' in outputs_dict:
            display_advanced_economics_panel(outputs_dict['advanced_economics'], analysis)

        # Export section (CSV, PNG downloads)
        if 'export' in outputs_dict:
            display_export_panel(outputs_dict['export'], analysis)

    except Exception as e:
        display_error(outputs_dict['system_params'], f"Error displaying complete analysis: {str(e)}")
        
def clear_all_displays(outputs_dict):
    """
    Clear all output displays.
    
    Args:
        outputs_dict: Dictionary of output widgets
    """
    for output in outputs_dict.values():
        output.clear_output()

# =============================================================================
# UTILITY FUNCTIONS FOR OUTPUT MANAGEMENT
# =============================================================================

def display_loading_message(output_area, message="Calculating..."):
    """
    Display a loading message while calculations are in progress.
    Uses explicit styling for visibility on light/dark backgrounds.

    Args:
        output_area: Output widget to display in
        message: Loading message to display
    """
    with output_area:
        html_content = f"""
        <div style="background-color: #e3f2fd; color: #0d47a1; padding: 15px 20px;
                    border-radius: 8px; border: 2px solid #2196F3; margin: 10px 0; text-align: center;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <strong style="color: #0d47a1;">⏳ {message}</strong>
        </div>
        """
        display(HTML(html_content))

def display_calculation_summary(output_area, summary_data):
    """
    Display a quick calculation summary.
    Uses explicit styling for visibility on light/dark backgrounds.

    Args:
        output_area: Output widget to display in
        summary_data: Dictionary with summary information
    """
    with output_area:
        try:
            wha = summary_data.get('wha', 'N/A')
            total_cost = summary_data.get('total_cost_eur', 'N/A')

            html_content = f"""
            <div style="background-color: #f8f9fa; padding: 0; border-radius: 12px;
                        border: 2px solid #dee2e6; margin: 10px 0; overflow: hidden;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 12px 20px; font-size: 16px; font-weight: 600; text-align: center;">
                    📊 Quick Summary
                </div>
                <div style="padding: 15px; text-align: center; background-color: white;">
                    <p style="margin: 5px 0; font-size: 16px; color: #000000;">
                        <strong style="color: #000000;">System Capacity:</strong>
                        <span style="color: #00C853; font-weight: bold;">{wha} MW</span> |
                        <strong style="color: #000000;">Total Cost:</strong>
                        <span style="color: #00C853; font-weight: bold;">€{total_cost:,}</span>
                    </p>
                </div>
            </div>
            """
            display(HTML(html_content))

        except Exception as e:
            display_error(output_area, f"Error displaying summary: {str(e)}")

# =============================================================================
# ADVANCED DISPLAY OPTIONS
# =============================================================================

def display_detailed_breakdown(output_area, analysis, show_validation=True):
    """
    Display detailed breakdown including validation results.
    
    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
        show_validation: Whether to show validation results
    """
    with output_area:
        try:
            # Display main results
            display_system_parameters(output_area, analysis)
            
            # Display validation if available and requested
            if show_validation and 'validation' in analysis:
                validation = analysis['validation']

                validation_html = f"""
                <div style="background-color: #fff3cd; padding: 0; border-radius: 8px;
                            margin: 10px 0; border: 2px solid #ffc107; overflow: hidden;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <div style="background: linear-gradient(135deg, #ffc107 0%, #FF9800 100%);
                                color: white; padding: 10px 15px; font-size: 14px; font-weight: 600;">
                        🔬 Validation Results
                    </div>
                    <div style="padding: 15px; background-color: #fff8e1;">
                        <p style="margin: 8px 0; color: #000000;">
                            <strong style="color: #000000;">Calculated MW:</strong>
                            <span style="color: #000000; font-weight: 600;">{validation.get('calculated_mw', 'N/A')}</span>
                        </p>
                        <p style="margin: 8px 0; color: #000000;">
                            <strong style="color: #000000;">Delta T TCS:</strong>
                            <span style="color: #000000; font-weight: 600;">{validation.get('itdt', 'N/A')}°C</span>
                        </p>
                        <p style="margin: 8px 0; color: #000000;">
                            <strong style="color: #000000;">Delta T FWS:</strong>
                            <span style="color: #000000; font-weight: 600;">{validation.get('oftkrdt', 'N/A')}°C</span>
                        </p>
                        <p style="margin: 8px 0; color: #000000;">
                            <strong style="color: #000000;">Approach:</strong>
                            <span style="color: #000000; font-weight: 600;">{validation.get('approach_calculated', 'N/A')}</span>
                        </p>
                    </div>
                </div>
                """
                display(HTML(validation_html))
                
        except Exception as e:
            display_error(output_area, f"Error displaying detailed breakdown: {str(e)}")

def display_export_options(output_area, analysis):
    """
    Display export options for the analysis results.
    Uses explicit styling for visibility on light/dark backgrounds.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    with output_area:
        try:
            export_html = f"""
            <div style="background-color: #f8f9fa; padding: 0; border-radius: 12px;
                        border: 2px solid #4CAF50; margin: 10px 0; overflow: hidden;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                            color: white; padding: 12px 20px; font-size: 16px; font-weight: 600;">
                    📤 Export Options
                </div>
                <div style="padding: 15px; background-color: white;">
                    <p style="color: #000000; margin: 10px 0; font-weight: 500;">Results are ready for export. Available formats:</p>
                    <ul style="color: #000000; margin: 10px 0; padding-left: 25px;">
                        <li style="margin: 5px 0;">Charts: <span style="color: #00C853; font-weight: 600;">PNG/PDF format</span></li>
                        <li style="margin: 5px 0;">Data: <span style="color: #00C853; font-weight: 600;">CSV/Excel format</span></li>
                        <li style="margin: 5px 0;">Report: <span style="color: #00C853; font-weight: 600;">PDF summary</span></li>
                    </ul>
                    <p style="color: #000000; font-size: 12px; margin-top: 15px;">
                        Contact your system administrator for export functionality.
                    </p>
                </div>
            </div>
            """
            display(HTML(export_html))

        except Exception as e:
            display_error(output_area, f"Error displaying export options: {str(e)}")

# =============================================================================
# RESPONSIVE DISPLAY HELPERS
# =============================================================================

def get_display_mode():
    """
    Determine display mode based on available space.
    
    Returns:
        Display mode string ('compact', 'normal', 'detailed')
    """
    # This could be enhanced to detect screen size or user preferences
    return 'normal'

def display_responsive_results(outputs_dict, analysis):
    """
    Display results in a responsive manner based on display mode.
    
    Args:
        outputs_dict: Dictionary of output widgets
        analysis: Complete system analysis dictionary
    """
    mode = get_display_mode()
    
    if mode == 'compact':
        # Show only summary and key metrics
        display_calculation_summary(outputs_dict['system_params'], analysis.get('summary', {}))
        display_charts(outputs_dict['charts'], analysis)
    elif mode == 'detailed':
        # Show everything including validation
        display_detailed_breakdown(outputs_dict['system_params'], analysis, show_validation=True)
        display_cost_analysis(outputs_dict['cost_analysis'], analysis)
        display_charts(outputs_dict['charts'], analysis)
        display_export_options(outputs_dict['cost_analysis'], analysis)
    else:
        # Normal mode - standard display
        display_complete_analysis(outputs_dict, analysis)
        
        
        
def display_smart_recommendations(output_area, analysis):
    """
    Display smart recommendations in a rounded box below cost analysis.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    output_area.clear_output(wait=True)
    with output_area:
        try:
            # Extract key metrics for analysis
            system = analysis['system']
            costs = analysis['costs']
            sizing = analysis['sizing']
            
            wha = system['wha']
            total_cost = costs['total_cost']
            cost_per_mw = total_cost / wha
            
            # Generate smart insights
            recommendations = generate_smart_insights(analysis)
            
            # Get styling configuration (reuse cost analysis style)
            config = OUTPUT_CONFIG['cost_analysis']  # Reuse existing styling
            
            # Create recommendations HTML
            rec_html = create_recommendations_html(
                recommendations=recommendations,
                border_color=config['border_color'],
                title_color=config['title_color']
            )
            
            display(HTML(rec_html))
            
        except Exception as e:
            display_error(output_area, f"Error displaying recommendations: {str(e)}")
            
            
def display_visual_summary_cards(output_area, analysis):
    """
    Display visual summary cards above charts section.

    Args:
        output_area: Output widget to display in
        analysis: Complete system analysis dictionary
    """
    output_area.clear_output(wait=True)
    with output_area:
        try:
            # Extract key metrics
            system = analysis['system']
            costs = analysis['costs']
            sizing = analysis['sizing']
            
            wha = system['wha']
            total_cost = costs['total_cost']
            cost_per_mw = total_cost / wha
            
            # Get effectiveness estimate
            effectiveness = calculate_effectiveness(analysis)
            
            # Generate performance rating
            rating_info = generate_performance_rating(cost_per_mw, effectiveness)
            
            # Create cards HTML
            cards_html = create_summary_cards_html(
                wha=wha,
                total_cost=total_cost,
                cost_per_mw=cost_per_mw,
                effectiveness=effectiveness,
                rating_info=rating_info,
                eu_compliant=True  # Based on your validation
            )
            
            display(HTML(cards_html))
            
        except Exception as e:
            display_error(output_area, f"Error displaying summary cards: {str(e)}")
            
