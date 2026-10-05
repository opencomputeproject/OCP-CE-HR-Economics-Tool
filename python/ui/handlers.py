"""
Author: Ahliana Byrd <ahliana.byrd@gmail.com>
Created: 2025-10-08
"""

"""
Event Handlers - Button click and interaction logic
Extracted from Interactive Analysis Tool.ipynb
"""

from .inputs import get_widget_values, clear_all_outputs
from .outputs import (
    display_complete_analysis, display_validation_errors, 
    display_no_data_error, display_loading_message
)
from .formatting import validate_user_inputs

# =============================================================================
# MAIN BUTTON HANDLER
# =============================================================================

def create_calculate_handler(widgets_dict, outputs_dict, core_functions):
    """
    Create the main calculate button handler.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
    
    Returns:
        Button click handler function
    """
    
    def on_calculate_click(button):
        """
        Handle calculate button click event.
        
        Args:
            button: The button widget that was clicked
        """
        try:
            # Clear all previous outputs
            clear_all_outputs(outputs_dict)
            
            # Show loading message
            display_loading_message(outputs_dict['system_params'], "Calculating system parameters...")
            
            # Get values from widgets
            values = get_widget_values(widgets_dict)
            wha = values['wha']
            T1 = values['T1']
            itdt = values['itdt']
            approach = values['approach']
            
            # Clear loading message and validate inputs
            clear_all_outputs(outputs_dict)
            
            # Validate inputs
            errors = validate_user_inputs(wha, T1, itdt, approach)
            if errors:
                display_validation_errors(outputs_dict['system_params'], errors)
                return
            
            # Show calculation in progress
            display_loading_message(outputs_dict['system_params'], "Running system analysis...")
            
            # Get complete system analysis using core functions
            analysis = core_functions['get_complete_system_analysis'](wha, T1, itdt, approach)
            
            # Clear loading message
            clear_all_outputs(outputs_dict)
            
            # Display results or error
            if analysis:
                display_complete_analysis(outputs_dict, analysis)
            else:
                display_no_data_error(outputs_dict['system_params'], approach)
                
        except Exception as e:
            # Clear any loading messages and show error
            clear_all_outputs(outputs_dict)
            display_validation_errors(outputs_dict['system_params'], [f"Calculation error: {str(e)}"])
    
    return on_calculate_click

# =============================================================================
# WIDGET EVENT HANDLERS
# =============================================================================

def create_dropdown_change_handler(widget_name, widgets_dict, validation_callback=None):
    """
    Create handler for dropdown value changes.
    
    Args:
        widget_name: Name of the widget
        widgets_dict: Dictionary of all widgets
        validation_callback: Optional callback for real-time validation
    
    Returns:
        Change handler function
    """
    
    def on_dropdown_change(change):
        """
        Handle dropdown value change.
        
        Args:
            change: Widget change event
        """
        if validation_callback:
            # Get all current values
            values = get_widget_values(widgets_dict)
            
            # Run validation
            errors = validate_user_inputs(
                values['wha'], values['T1'], 
                values['itdt'], values['approach']
            )
            
            # Call validation callback with results
            validation_callback(widget_name, change['new'], errors)
    
    return on_dropdown_change

def create_real_time_validation_callback(outputs_dict):
    """
    Create callback function for real-time validation display.
    
    Args:
        outputs_dict: Dictionary of output widgets
    
    Returns:
        Validation callback function
    """
    
    def validation_callback(widget_name, new_value, errors):
        """
        Handle real-time validation results.
        
        Args:
            widget_name: Name of widget that changed
            new_value: New value of the widget
            errors: List of validation errors
        """
        # For now, just clear errors if there are none
        # Could be enhanced to show real-time feedback
        if not errors:
            # Clear any existing error displays
            outputs_dict['system_params'].clear_output()
    
    return validation_callback

# =============================================================================
# ADVANCED HANDLERS
# =============================================================================

def create_auto_calculate_handler(widgets_dict, outputs_dict, core_functions, delay_ms=1000):
    """
    Create handler for automatic calculation after input changes.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
        delay_ms: Delay in milliseconds before auto-calculation
    
    Returns:
        Auto-calculate handler function
    """
    import threading
    import time
    
    last_change_time = [0]  # Use list to make it mutable in nested function
    
    def auto_calculate_handler(change):
        """
        Handle automatic calculation after input change.
        
        Args:
            change: Widget change event
        """
        last_change_time[0] = time.time()
        
        def delayed_calculate():
            time.sleep(delay_ms / 1000.0)  # Convert to seconds
            
            # Check if there were any more recent changes
            if time.time() - last_change_time[0] >= delay_ms / 1000.0 - 0.1:
                # Trigger calculation
                calculate_handler = create_calculate_handler(widgets_dict, outputs_dict, core_functions)
                calculate_handler(None)  # Pass None since we don't have a button
        
        # Start delayed calculation in background thread
        thread = threading.Thread(target=delayed_calculate)
        thread.daemon = True
        thread.start()
    
    return auto_calculate_handler

def create_export_handler(analysis_data):
    """
    Create handler for exporting results.
    
    Args:
        analysis_data: Current analysis data to export
    
    Returns:
        Export handler function
    """
    
    def export_handler(button):
        """
        Handle export button click.
        
        Args:
            button: Export button widget
        """
        try:
            # This could be enhanced to actually export data
            # For now, functionality is placeholder
            pass
        except Exception as e:
            pass  # Export error silently handled
    
    return export_handler

# =============================================================================
# WIDGET ATTACHMENT HELPERS
# =============================================================================

def attach_handlers_to_widgets(widgets_dict, outputs_dict, core_functions, enable_real_time=False):
    """
    Attach all necessary event handlers to widgets.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
        enable_real_time: Whether to enable real-time validation
    
    Returns:
        Dictionary of attached handlers
    """
    handlers = {}
    
    # Attach main calculate button handler
    calculate_handler = create_calculate_handler(widgets_dict, outputs_dict, core_functions)
    widgets_dict['calculate_button'].on_click(calculate_handler)
    handlers['calculate'] = calculate_handler
    
    # Attach real-time validation if enabled
    if enable_real_time:
        validation_callback = create_real_time_validation_callback(outputs_dict)
        
        # Attach to each dropdown
        for widget_name in ['wha', 'T1', 'itdt', 'approach']:
            widget_key = f"{widget_name}_widget"
            if widget_key in widgets_dict:
                change_handler = create_dropdown_change_handler(
                    widget_name, widgets_dict, validation_callback
                )
                widgets_dict[widget_key].observe(change_handler, names='value')
                handlers[f"{widget_name}_change"] = change_handler
    
    return handlers

def detach_handlers_from_widgets(widgets_dict, handlers_dict):
    """
    Detach event handlers from widgets (useful for cleanup).
    
    Args:
        widgets_dict: Dictionary of input widgets
        handlers_dict: Dictionary of handlers to detach
    """
    try:
        # Detach button handler
        if 'calculate' in handlers_dict:
            # Note: ipywidgets doesn't have a direct way to remove click handlers
            # This would need to be implemented if cleanup is required
            pass
        
        # Detach change handlers
        for widget_name in ['wha', 'T1', 'itdt', 'approach']:
            handler_key = f"{widget_name}_change"
            widget_key = f"{widget_name}_widget"
            
            if handler_key in handlers_dict and widget_key in widgets_dict:
                # Remove observer
                widgets_dict[widget_key].unobserve(handlers_dict[handler_key], names='value')
                
    except Exception as e:
        pass  # Error detaching handlers silently handled

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_debug_handler(widgets_dict, outputs_dict):
    """
    Create debug handler for troubleshooting.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
    
    Returns:
        Debug handler function
    """
    
    def debug_handler(button):
        """
        Handle debug button click - shows current widget states.
        
        Args:
            button: Debug button widget
        """
        try:
            values = get_widget_values(widgets_dict)
            
            debug_info = f"""
            Debug Information:
            - wha: {values['wha']}
            - T1: {values['T1']}
            - Temperature Diff: {values['itdt']}
            - Approach: {values['approach']}
            
            Widget States:
            - Widgets loaded: {len(widgets_dict)}
            - Outputs available: {len(outputs_dict)}
            """
            # Debug info only shown when explicitly requested via debug output widget
            pass

        except Exception as e:
            pass  # Debug error silently handled
    
    return debug_handler

def create_reset_handler(widgets_dict, outputs_dict):
    """
    Create reset handler to restore default values.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
    
    Returns:
        Reset handler function
    """
    
    def reset_handler(button):
        """
        Handle reset button click - restore default values.
        
        Args:
            button: Reset button widget
        """
        try:
            from .config import UI_CONFIG
            
            # Reset each dropdown to default value
            for widget_name, config in UI_CONFIG['dropdowns'].items():
                widget_key = f"{widget_name}_widget"
                if widget_key in widgets_dict:
                    widgets_dict[widget_key].value = config['default']
            
            # Clear all outputs
            clear_all_outputs(outputs_dict)

        except Exception as e:
            pass  # Reset error silently handled
    
    return reset_handler

# =============================================================================
# ERROR HANDLING DECORATORS
# =============================================================================

def with_error_handling(handler_func, error_output=None):
    """
    Decorator to add error handling to event handlers.
    
    Args:
        handler_func: Original handler function
        error_output: Output widget to display errors in
    
    Returns:
        Wrapped handler function with error handling
    """
    
    def wrapped_handler(*args, **kwargs):
        try:
            return handler_func(*args, **kwargs)
        except Exception as e:
            error_message = f"Handler error: {str(e)}"
            
            if error_output:
                from .outputs import display_error
                display_error(error_output, error_message)
    
    return wrapped_handler

def create_safe_calculate_handler(widgets_dict, outputs_dict, core_functions):
    """
    Create calculate handler with enhanced error handling.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
    
    Returns:
        Safe calculate handler with error handling
    """
    base_handler = create_calculate_handler(widgets_dict, outputs_dict, core_functions)
    return with_error_handling(base_handler, outputs_dict.get('system_params'))

# =============================================================================
# PERFORMANCE MONITORING
# =============================================================================

def create_performance_monitoring_handler(base_handler, performance_callback=None):
    """
    Create handler wrapper that monitors performance.
    
    Args:
        base_handler: Original handler function
        performance_callback: Optional callback for performance data
    
    Returns:
        Performance monitoring handler
    """
    import time
    
    def performance_handler(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = base_handler(*args, **kwargs)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if performance_callback:
                performance_callback({
                    'execution_time': execution_time,
                    'status': 'success',
                    'timestamp': end_time
                })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            if performance_callback:
                performance_callback({
                    'execution_time': execution_time,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': end_time
                })
            
            raise e
    
    return performance_handler

# =============================================================================
# BATCH OPERATIONS
# =============================================================================

def create_batch_calculate_handler(widgets_dict, outputs_dict, core_functions, parameter_sets):
    """
    Create handler for batch calculations with multiple parameter sets.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
        parameter_sets: List of parameter dictionaries to calculate
    
    Returns:
        Batch calculate handler function
    """
    
    def batch_handler(button):
        """
        Handle batch calculation button click.
        
        Args:
            button: Batch calculate button widget
        """
        try:
            clear_all_outputs(outputs_dict)
            display_loading_message(outputs_dict['system_params'], f"Running batch calculation for {len(parameter_sets)} parameter sets...")
            
            results = []
            
            for i, params in enumerate(parameter_sets):
                # Update progress
                progress_msg = f"Processing set {i+1}/{len(parameter_sets)}: wha={params['wha']}MW, T1={params['T1']}°C"
                clear_all_outputs(outputs_dict)
                display_loading_message(outputs_dict['system_params'], progress_msg)
                
                # Validate parameters
                errors = validate_user_inputs(
                    params['wha'], params['T1'], 
                    params['itdt'], params['approach']
                )
                
                if not errors:
                    # Calculate
                    analysis = core_functions['get_complete_system_analysis'](
                        params['wha'], params['T1'], 
                        params['itdt'], params['approach']
                    )
                    
                    if analysis:
                        results.append({
                            'parameters': params,
                            'analysis': analysis,
                            'status': 'success'
                        })
                    else:
                        results.append({
                            'parameters': params,
                            'status': 'no_data'
                        })
                else:
                    results.append({
                        'parameters': params,
                        'errors': errors,
                        'status': 'validation_error'
                    })
            
            # Display batch results
            clear_all_outputs(outputs_dict)
            display_batch_results(outputs_dict, results)
            
        except Exception as e:
            clear_all_outputs(outputs_dict)
            display_validation_errors(outputs_dict['system_params'], [f"Batch calculation error: {str(e)}"])
    
    return batch_handler

def display_batch_results(outputs_dict, results):
    """
    Display results from batch calculations.
    
    Args:
        outputs_dict: Dictionary of output areas
        results: List of calculation results
    """
    from .outputs import display_error
    
    try:
        successful_results = [r for r in results if r['status'] == 'success']
        
        if successful_results:
            # Display summary
            summary_html = f"""
            <div style="background-color: #e8f5e8; color: #2e7d32; padding: 15px; 
                        border-radius: 8px; border: 2px solid #c8e6c9; margin: 10px 0;">
                <h3 style="margin-top: 0;">📊 Batch Calculation Summary</h3>
                <p><strong>Total Calculations:</strong> {len(results)}</p>
                <p><strong>Successful:</strong> {len(successful_results)}</p>
                <p><strong>Failed:</strong> {len(results) - len(successful_results)}</p>
            </div>
            """
            
            with outputs_dict['system_params']:
                from IPython.display import display, HTML
                display(HTML(summary_html))
            
            # Display first successful result as example
            if successful_results:
                display_complete_analysis(outputs_dict, successful_results[0]['analysis'])
        else:
            display_error(outputs_dict['system_params'], "No successful calculations in batch")
            
    except Exception as e:
        display_error(outputs_dict['system_params'], f"Error displaying batch results: {str(e)}")

# =============================================================================
# HANDLER FACTORY
# =============================================================================

def create_handlers_suite(widgets_dict, outputs_dict, core_functions, options=None):
    """
    Create a complete suite of handlers based on options.
    
    Args:
        widgets_dict: Dictionary of input widgets
        outputs_dict: Dictionary of output areas
        core_functions: Dictionary of core calculation functions
        options: Dictionary of handler options
    
    Returns:
        Dictionary of all created handlers
    """
    if options is None:
        options = {}
    
    handlers = {}
    
    # Always create main calculate handler
    if options.get('safe_mode', True):
        handlers['calculate'] = create_safe_calculate_handler(widgets_dict, outputs_dict, core_functions)
    else:
        handlers['calculate'] = create_calculate_handler(widgets_dict, outputs_dict, core_functions)
    
    # Add performance monitoring if requested
    if options.get('monitor_performance', False):
        handlers['calculate'] = create_performance_monitoring_handler(
            handlers['calculate'], 
            options.get('performance_callback')
        )
    
    # Create optional handlers
    if options.get('enable_reset', False):
        handlers['reset'] = create_reset_handler(widgets_dict, outputs_dict)
    
    if options.get('enable_debug', False):
        handlers['debug'] = create_debug_handler(widgets_dict, outputs_dict)
    
    # Attach main handler to button
    widgets_dict['calculate_button'].on_click(handlers['calculate'])
    
    # Attach real-time validation if enabled
    if options.get('enable_real_time', False):
        validation_handlers = attach_handlers_to_widgets(
            widgets_dict, outputs_dict, core_functions, enable_real_time=True
        )
        handlers.update(validation_handlers)
    
    return handlers