# Heat Reuse Tool - Setup Verification Script
# Save as: verify_setup.py
# Run with: python verify_setup.py

import os
import sys
import subprocess
import importlib
from pathlib import Path
import platform

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "PASS": Colors.GREEN + "✓",
        "FAIL": Colors.RED + "✗", 
        "WARN": Colors.YELLOW + "⚠",
        "INFO": Colors.BLUE + "ℹ"
    }
    print(f"{colors.get(status, '')} {message}{Colors.END}")

def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "PASS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.8+", "FAIL")
        return False

def check_pip():
    """Verify pip is available"""
    try:
        import pip
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"pip available: {result.stdout.strip()}", "PASS")
            return True
        else:
            print_status("pip not working properly", "FAIL")
            return False
    except ImportError:
        print_status("pip not installed", "FAIL")
        return False

def check_virtual_environment():
    """Check if virtual environment is active"""
    venv_active = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if venv_active:
        print_status(f"Virtual environment active: {sys.prefix}", "PASS")
        return True
    else:
        print_status("No virtual environment detected", "WARN")
        print_status("  Consider using: python -m venv venv && venv\\Scripts\\activate", "INFO")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    required_packages = {
        'jupyter': '1.0.0',
        'ipywidgets': '8.0.0', 
        'notebook': '6.4.0',
        'pandas': '1.5.0',
        'numpy': '1.20.0',
        'matplotlib': '3.5.0',
        'scipy': '1.9.0',
        'ipython': '8.0.0'
    }
    
    all_good = True
    
    for package, min_version in required_packages.items():
        try:
            # Special case for ipython - import as IPython
            if package == 'ipython':
                module = importlib.import_module('IPython')
            else:
                module = importlib.import_module(package)
            
            if hasattr(module, '__version__'):
                version = module.__version__
                print_status(f"{package} {version}", "PASS")
            else:
                print_status(f"{package} (version unknown)", "PASS")
        except ImportError:
            print_status(f"{package} not installed", "FAIL")
            all_good = False
    
    return all_good

def check_jupyter_installation():
    """Check Jupyter installation and kernels"""
    try:
        # Check jupyter command
        result = subprocess.run(["jupyter", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Jupyter command available", "PASS")
        else:
            print_status("Jupyter command not found", "FAIL")
            return False
            
        # Check kernels
        result = subprocess.run(["jupyter", "kernelspec", "list"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if "heat-reuse-tool" in result.stdout:
                print_status("Heat Reuse Tool kernel found", "PASS")
            else:
                print_status("Heat Reuse Tool kernel not found", "WARN")
                print_status("  Run: python -m ipykernel install --user --name=heat-reuse-tool", "INFO")
        
        return True
        
    except FileNotFoundError:
        print_status("Jupyter not installed or not in PATH", "FAIL")
        return False

def check_project_structure():
    """Verify project directory structure"""
    required_dirs = ['Data', 'python']
    required_files = [
        'requirements.txt',
        'python/autostart.py'
    ]
    
    # Check for notebook in either location (flexible)
    notebook_locations = [
        'notebooks/Interactive_Analysis_Tool.ipynb',
        'Interactive Analysis Tool.ipynb'
    ]
    
    all_good = True
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print_status(f"Directory {directory}/ exists", "PASS")
        else:
            print_status(f"Directory {directory}/ missing", "FAIL")
            all_good = False
    
    # Check core files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"File {file_path} exists", "PASS")
        else:
            print_status(f"File {file_path} missing", "FAIL")
            all_good = False
    
    # Check for notebook in any valid location
    notebook_found = False
    for notebook_path in notebook_locations:
        if os.path.exists(notebook_path):
            print_status(f"Notebook found: {notebook_path}", "PASS")
            notebook_found = True
            break
    
    if not notebook_found:
        print_status("Interactive Analysis Tool.ipynb not found in any expected location", "FAIL")
        all_good = False
    
    return all_good

def check_csv_files():
    """Check for all required CSV data files"""
    required_csvs = [
        'ALLHX.csv',
        'CVALV.csv', 
        'IVALV.csv',
        'JOINTS.csv',
        'MW Price Data.csv',
        'PIPCOST.csv',
        'PIPSZ.csv',
        'ROOM.csv'
    ]
    
    data_dir = 'Data'
    all_good = True
    
    if not os.path.exists(data_dir):
        print_status(f"Data directory not found", "FAIL")
        return False
    
    for csv_file in required_csvs:
        file_path = os.path.join(data_dir, csv_file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                print_status(f"{csv_file} exists ({file_size} bytes)", "PASS")
            else:
                print_status(f"{csv_file} exists but is empty", "WARN")
        else:
            print_status(f"{csv_file} missing", "FAIL")
            all_good = False
    
    return all_good

def test_data_loading():
    """Test if CSV files can be loaded with pandas"""
    try:
        import pandas as pd
        
        test_files = [
            'Data/ALLHX.csv',
            'Data/CVALV.csv',
            'Data/PIPCOST.csv'
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    print_status(f"{os.path.basename(file_path)} loads OK ({len(df)} rows)", "PASS")
                except Exception as e:
                    print_status(f"{os.path.basename(file_path)} load error: {str(e)}", "FAIL")
                    return False
            else:
                print_status(f"{file_path} not found for testing", "WARN")
        
        return True
        
    except ImportError:
        print_status("pandas not available for CSV testing", "FAIL")
        return False

def test_autostart_import():
    """Test if autostart module can be imported"""
    try:
        # Add python directory to path like the notebook does
        python_dir = os.path.join(os.getcwd(), "python")
        if python_dir not in sys.path:
            sys.path.insert(0, python_dir)
        
        import autostart
        print_status("autostart.py imports successfully", "PASS")
        
        # Check if key functions exist
        if hasattr(autostart, 'discover_modules'):
            print_status("discover_modules function found", "PASS")
        else:
            print_status("discover_modules function missing", "WARN")
        
        return True
        
    except ImportError as e:
        print_status(f"autostart.py import failed: {str(e)}", "FAIL")
        return False
    except Exception as e:
        print_status(f"autostart.py error: {str(e)}", "FAIL")
        return False

def check_system_info():
    """Display system information"""
    print_status(f"Platform: {platform.platform()}", "INFO")
    print_status(f"Python executable: {sys.executable}", "INFO")
    print_status(f"Working directory: {os.getcwd()}", "INFO")
    print_status(f"PATH includes: {'; '.join(sys.path[:3])}...", "INFO")

def run_full_verification():
    """Run complete verification suite"""
    print(f"{Colors.BOLD}Heat Reuse Tool - Setup Verification{Colors.END}")
    print("=" * 50)
    
    # System Information
    print(f"\n{Colors.BOLD}System Information:{Colors.END}")
    check_system_info()
    
    # Core Components
    print(f"\n{Colors.BOLD}Core Components:{Colors.END}")
    python_ok = check_python_version()
    pip_ok = check_pip()
    venv_ok = check_virtual_environment()
    
    # Package Installation
    print(f"\n{Colors.BOLD}Required Packages:{Colors.END}")
    packages_ok = check_required_packages()
    
    # Jupyter Setup
    print(f"\n{Colors.BOLD}Jupyter Configuration:{Colors.END}")
    jupyter_ok = check_jupyter_installation()
    
    # Project Structure
    print(f"\n{Colors.BOLD}Project Structure:{Colors.END}")
    structure_ok = check_project_structure()
    
    # Data Files
    print(f"\n{Colors.BOLD}Data Files:{Colors.END}")
    csv_ok = check_csv_files()
    
    # Functionality Tests
    print(f"\n{Colors.BOLD}Functionality Tests:{Colors.END}")
    data_load_ok = test_data_loading()
    autostart_ok = test_autostart_import()
    
    # Summary
    print(f"\n{Colors.BOLD}Verification Summary:{Colors.END}")
    print("=" * 30)
    
    all_checks = [
        ("Python Version", python_ok),
        ("Pip Available", pip_ok),
        ("Virtual Environment", venv_ok),
        ("Required Packages", packages_ok),
        ("Jupyter Setup", jupyter_ok),
        ("Project Structure", structure_ok),
        ("CSV Data Files", csv_ok),
        ("Data Loading", data_load_ok),
        ("Autostart Import", autostart_ok)
    ]
    
    passed = sum(1 for _, status in all_checks if status)
    total = len(all_checks)
    
    for check_name, status in all_checks:
        print_status(f"{check_name:<20}: {'PASS' if status else 'FAIL'}", 
                    "PASS" if status else "FAIL")
    
    print(f"\n{Colors.BOLD}Overall Status: {passed}/{total} checks passed{Colors.END}")
    
    if passed == total:
        print_status("🎉 All checks passed! Heat Reuse Tool should work correctly.", "PASS")
        return True
    elif passed >= total * 0.8:  # 80% pass rate
        print_status("⚠️  Most checks passed. Minor issues may affect functionality.", "WARN")
        print_recommendations(all_checks)
        return False
    else:
        print_status("❌ Multiple critical issues found. Setup needs attention.", "FAIL")
        print_recommendations(all_checks)
        return False

def print_recommendations(all_checks):
    """Print specific recommendations based on failed checks"""
    print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
    
    failed_checks = [name for name, status in all_checks if not status]
    
    recommendations = {
        "Python Version": [
            "Install Python 3.8 or higher from https://python.org",
            "Ensure 'Add to PATH' is checked during installation"
        ],
        "Pip Available": [
            "Reinstall Python with pip included",
            "Or install pip manually: python -m ensurepip --upgrade"
        ],
        "Virtual Environment": [
            "Create virtual environment: python -m venv venv",
            "Activate it: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)"
        ],
        "Required Packages": [
            "Install requirements: pip install -r requirements.txt",
            "Or install manually: pip install jupyter pandas numpy matplotlib scipy ipywidgets"
        ],
        "Jupyter Setup": [
            "Install Jupyter: pip install jupyter",
            "Register kernel: python -m ipykernel install --user --name=heat-reuse-tool"
        ],
        "Project Structure": [
            "Clone repository: git clone [REPO_URL]",
            "Ensure you're in the correct project directory",
            "Check that all required folders and files exist"
        ],
        "CSV Data Files": [
            "Copy all CSV files to the Data/ directory",
            "Verify file names match exactly (case-sensitive)",
            "Check files are not empty or corrupted"
        ],
        "Data Loading": [
            "Check CSV file encoding (should be UTF-8)",
            "Verify pandas can read files: pd.read_csv('Data/ALLHX.csv')",
            "Check file permissions"
        ],
        "Autostart Import": [
            "Verify python/autostart.py exists",
            "Check current working directory",
            "Run from project root directory"
        ]
    }
    
    for failed_check in failed_checks:
        if failed_check in recommendations:
            print(f"\n{Colors.YELLOW}For {failed_check}:{Colors.END}")
            for rec in recommendations[failed_check]:
                print(f"  • {rec}")

def quick_check():
    """Run a quick essential-only check"""
    print(f"{Colors.BOLD}Heat Reuse Tool - Quick Check{Colors.END}")
    print("=" * 40)
    
    essential_checks = [
        ("Python 3.8+", check_python_version()),
        ("Required packages", check_required_packages()),
        ("Project structure", check_project_structure()),
        ("CSV files", check_csv_files())
    ]
    
    passed = sum(1 for _, status in essential_checks if status)
    total = len(essential_checks)
    
    for check_name, status in essential_checks:
        print_status(f"{check_name}: {'PASS' if status else 'FAIL'}", 
                    "PASS" if status else "FAIL")
    
    if passed == total:
        print_status(f"✓ Quick check passed ({passed}/{total})", "PASS")
    else:
        print_status(f"✗ Quick check failed ({passed}/{total})", "FAIL")
    
    return passed == total

def export_environment():
    """Export current environment details for comparison"""
    try:
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"environment_export_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("=== HEAT REUSE TOOL ENVIRONMENT EXPORT ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Platform: {platform.platform()}\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Python Executable: {sys.executable}\n")
            f.write(f"Working Directory: {os.getcwd()}\n\n")
            
            # Installed packages
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                      capture_output=True, text=True)
                f.write("=== INSTALLED PACKAGES ===\n")
                f.write(result.stdout)
                f.write("\n")
            except:
                f.write("Could not get package list\n\n")
            
            # Jupyter kernels
            try:
                result = subprocess.run(["jupyter", "kernelspec", "list"], 
                                      capture_output=True, text=True)
                f.write("=== JUPYTER KERNELS ===\n")
                f.write(result.stdout)
                f.write("\n")
            except:
                f.write("Could not get Jupyter kernels\n\n")
            
            # File structure
            f.write("=== PROJECT STRUCTURE ===\n")
            for root, dirs, files in os.walk('.'):
                if '.git' in root or '__pycache__' in root:
                    continue
                level = root.replace('.', '').count(os.sep)
                indent = ' ' * 2 * level
                f.write(f"{indent}{os.path.basename(root)}/\n")
                subindent = ' ' * 2 * (level + 1)
                for file in files[:10]:  # Limit files shown
                    f.write(f"{subindent}{file}\n")
                if len(files) > 10:
                    f.write(f"{subindent}... and {len(files)-10} more files\n")
        
        print_status(f"Environment exported to: {filename}", "PASS")
        return filename
        
    except Exception as e:
        print_status(f"Could not export environment: {str(e)}", "FAIL")
        return None

def main():
    """Main function - run verification based on command line args"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_check()
        elif sys.argv[1] == "export":
            export_environment()
        elif sys.argv[1] == "help":
            print("Heat Reuse Tool Verification Script")
            print("Usage:")
            print("  python verify_setup.py        - Full verification")
            print("  python verify_setup.py quick  - Quick essential checks")
            print("  python verify_setup.py export - Export environment details")
            print("  python verify_setup.py help   - Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use 'python verify_setup.py help' for usage")
    else:
        run_full_verification()

if __name__ == "__main__":
    main()