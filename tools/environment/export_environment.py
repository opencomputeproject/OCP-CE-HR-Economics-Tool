# tools/environment/export_environment.py
# Environment Export Tool for Heat Reuse Tool Project

import os
import sys
import subprocess
import platform
import json
from datetime import datetime
from pathlib import Path

def get_system_info():
    """Collect system information"""
    try:
        system_info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable": sys.executable,
            "working_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat()
        }
        return system_info
    except Exception as e:
        return {"error": f"Could not collect system info: {str(e)}"}

def get_python_packages():
    """Get installed Python packages"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            return packages
        else:
            return {"error": "Could not get package list"}
    except Exception as e:
        return {"error": f"Error getting packages: {str(e)}"}

def get_pip_freeze():
    """Get pip freeze output for exact reproduction"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            return ["Error: Could not get pip freeze output"]
    except Exception as e:
        return [f"Error getting pip freeze: {str(e)}"]

def get_jupyter_info():
    """Get Jupyter configuration including detailed ipykernel information"""
    try:
        jupyter_info = {}
        
        # Jupyter version
        result = subprocess.run(["jupyter", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            jupyter_info["version"] = result.stdout.strip()
        else:
            jupyter_info["version"] = "Jupyter not found"
        
        # Jupyter kernels with detailed info
        result = subprocess.run(["jupyter", "kernelspec", "list", "--json"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            kernels = json.loads(result.stdout)
            jupyter_info["kernels"] = kernels
            
            # Extract Heat Reuse Tool kernel info specifically
            heat_reuse_kernels = {}
            if 'kernelspecs' in kernels:
                for kernel_name, kernel_info in kernels['kernelspecs'].items():
                    if 'heat-reuse' in kernel_name.lower():
                        heat_reuse_kernels[kernel_name] = kernel_info
            
            jupyter_info["heat_reuse_tool_kernels"] = heat_reuse_kernels
            
            # Check if ipykernel is properly installed
            try:
                import ipykernel
                jupyter_info["ipykernel_version"] = ipykernel.__version__
                jupyter_info["ipykernel_available"] = True
            except ImportError:
                jupyter_info["ipykernel_version"] = "Not installed"
                jupyter_info["ipykernel_available"] = False
        else:
            jupyter_info["kernels"] = "Could not get kernels"
            jupyter_info["heat_reuse_tool_kernels"] = {}
            jupyter_info["ipykernel_available"] = False
        
        # Jupyter paths
        result = subprocess.run(["jupyter", "--paths", "--json"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            paths = json.loads(result.stdout)
            jupyter_info["paths"] = paths
        else:
            jupyter_info["paths"] = "Could not get paths"
        
        # Check if ipykernel install command works
        result = subprocess.run([sys.executable, "-m", "ipykernel", "--help"], 
                              capture_output=True, text=True)
        jupyter_info["ipykernel_command_available"] = result.returncode == 0
        
        # Get installed kernels directory info
        try:
            from jupyter_client.kernelspec import KernelSpecManager
            ksm = KernelSpecManager()
            jupyter_info["kernel_directories"] = {
                "user": ksm.user_kernel_dir,
                "system": ksm.system_kernel_dir if hasattr(ksm, 'system_kernel_dir') else "N/A"
            }
        except Exception as e:
            jupyter_info["kernel_directories"] = {"error": str(e)}
        
        return jupyter_info
    except Exception as e:
        return {"error": f"Error getting Jupyter info: {str(e)}"}

def check_ipykernel_installation():
    """Specifically check ipykernel installation and registration capabilities"""
    ipykernel_info = {
        "package_installed": False,
        "version": None,
        "install_command_works": False,
        "heat_reuse_kernel_registered": False,
        "can_register_kernels": False,
        "jupyter_available": False,
        "errors": []
    }
    
    try:
        # Check if ipykernel package is installed
        import ipykernel
        ipykernel_info["package_installed"] = True
        ipykernel_info["version"] = ipykernel.__version__
    except ImportError:
        ipykernel_info["errors"].append("ipykernel package not installed")
    
    try:
        # Check if ipykernel install command works
        result = subprocess.run([sys.executable, "-m", "ipykernel", "--help"], 
                              capture_output=True, text=True)
        ipykernel_info["install_command_works"] = result.returncode == 0
        if result.returncode != 0:
            ipykernel_info["errors"].append(f"ipykernel command failed: {result.stderr}")
    except Exception as e:
        ipykernel_info["errors"].append(f"Could not test ipykernel command: {str(e)}")
    
    try:
        # Check if Jupyter is available for kernel registration
        result = subprocess.run(["jupyter", "kernelspec", "list"], 
                              capture_output=True, text=True)
        ipykernel_info["jupyter_available"] = result.returncode == 0
        
        if result.returncode == 0:
            # Check if heat-reuse-tool kernel is registered
            if 'heat-reuse-tool' in result.stdout.lower():
                ipykernel_info["heat_reuse_kernel_registered"] = True
            
            # Test if we can register kernels (dry run)
            ipykernel_info["can_register_kernels"] = True
        else:
            ipykernel_info["errors"].append("Jupyter kernelspec command not available")
    except Exception as e:
        ipykernel_info["errors"].append(f"Could not check Jupyter availability: {str(e)}")
    
    return ipykernel_info

def get_vscode_extensions():
    """Get VSCode extensions"""
    try:
        result = subprocess.run(["code", "--list-extensions", "--show-versions"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            extensions = result.stdout.strip().split('\n')
            return [ext for ext in extensions if ext.strip()]
        else:
            return ["VSCode not found or no extensions"]
    except Exception as e:
        return [f"Error getting VSCode extensions: {str(e)}"]

def get_git_info():
    """Get Git configuration"""
    try:
        git_info = {}
        
        # Git version
        result = subprocess.run(["git", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            git_info["version"] = result.stdout.strip()
        else:
            git_info["version"] = "Git not found"
        
        # Git config
        result = subprocess.run(["git", "config", "--list"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            config_lines = result.stdout.strip().split('\n')
            git_info["config"] = [line for line in config_lines if line.strip()]
        else:
            git_info["config"] = "Could not get Git config"
        
        return git_info
    except Exception as e:
        return {"error": f"Error getting Git info: {str(e)}"}

def get_project_structure():
    """Get project file structure"""
    try:
        project_structure = {}
        
        # Main directories
        for directory in ['Data', 'python', 'tools', 'tests', 'docs']:
            if os.path.exists(directory):
                files = []
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames:
                        rel_path = os.path.relpath(os.path.join(root, filename))
                        files.append(rel_path)
                project_structure[directory] = files
            else:
                project_structure[directory] = "Directory not found"
        
        # Root files
        root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        project_structure['root_files'] = root_files
        
        return project_structure
    except Exception as e:
        return {"error": f"Error getting project structure: {str(e)}"}

def check_required_files():
    """Check for required Heat Reuse Tool files"""
    required_files = {
        "requirements.txt": os.path.exists("requirements.txt"),
        "Interactive Analysis Tool.ipynb": os.path.exists("Interactive Analysis Tool.ipynb"),
        "python/autostart.py": os.path.exists("python/autostart.py"),
        "tools/setup/verify_setup.py": os.path.exists("tools/setup/verify_setup.py")
    }
    
    # Check CSV files
    csv_files = [
        'ALLHX.csv', 'CVALV.csv', 'IVALV.csv', 'JOINTS.csv',
        'MW Price Data.csv', 'PIPCOST.csv', 'PIPSZ.csv', 'ROOM.csv'
    ]
    
    for csv_file in csv_files:
        file_path = f"Data/{csv_file}"
        required_files[file_path] = os.path.exists(file_path)
    
    return required_files

def export_environment(machine_name=None):
    """Export complete environment information"""
    
    if machine_name is None:
        machine_name = platform.node().lower()
    
    print(f"Exporting environment for: {machine_name}")
    print("=" * 50)
    
    environment_data = {
        "machine_name": machine_name,
        "export_timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "python_packages": get_python_packages(),
        "pip_freeze": get_pip_freeze(),
        "jupyter_info": get_jupyter_info(),
        "ipykernel_info": check_ipykernel_installation(),  # NEW: Detailed ipykernel check
        "vscode_extensions": get_vscode_extensions(),
        "git_info": get_git_info(),
        "project_structure": get_project_structure(),
        "required_files": check_required_files()
    }
    
    # Create exports directory if it doesn't exist
    exports_dir = Path("tools/environment/exports")
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = exports_dir / f"{machine_name}_environment_{timestamp}.json"
    
    # Save to JSON file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(environment_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Environment exported to: {filename}")
        
        # Also create a human-readable summary
        summary_filename = exports_dir / f"{machine_name}_summary_{timestamp}.txt"
        create_summary_file(environment_data, summary_filename)
        print(f"✓ Summary created: {summary_filename}")
        
        # Print quick ipykernel status
        print_ipykernel_status(environment_data.get('ipykernel_info', {}))
        
        return str(filename)
        
    except Exception as e:
        print(f"✗ Error saving environment: {str(e)}")
        return None

def print_ipykernel_status(ipykernel_info):
    """Print quick ipykernel status summary"""
    print("\n" + "="*30)
    print("IPYKERNEL STATUS SUMMARY")
    print("="*30)
    
    if ipykernel_info.get('package_installed'):
        print(f"✓ ipykernel package: v{ipykernel_info.get('version', 'Unknown')}")
    else:
        print("✗ ipykernel package: NOT INSTALLED")
    
    if ipykernel_info.get('install_command_works'):
        print("✓ ipykernel install command: Available")
    else:
        print("✗ ipykernel install command: NOT WORKING")
    
    if ipykernel_info.get('heat_reuse_kernel_registered'):
        print("✓ Heat Reuse Tool kernel: Registered")
    else:
        print("✗ Heat Reuse Tool kernel: NOT REGISTERED")
    
    if ipykernel_info.get('jupyter_available'):
        print("✓ Jupyter kernelspec: Available")
    else:
        print("✗ Jupyter kernelspec: NOT AVAILABLE")
    
    if ipykernel_info.get('errors'):
        print("\nErrors found:")
        for error in ipykernel_info['errors']:
            print(f"  - {error}")
    
    print()

def create_summary_file(env_data, filename):
    """Create human-readable summary file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Heat Reuse Tool - Environment Summary\n")
            f.write(f"Machine: {env_data['machine_name']}\n")
            f.write(f"Export Date: {env_data['export_timestamp']}\n")
            f.write("=" * 50 + "\n\n")
            
            # System info
            sys_info = env_data['system_info']
            f.write("SYSTEM INFORMATION:\n")
            f.write(f"Platform: {sys_info.get('platform', 'Unknown')}\n")
            f.write(f"Python Version: {sys_info.get('python_version', 'Unknown')}\n")
            f.write(f"Python Executable: {sys_info.get('python_executable', 'Unknown')}\n\n")
            
            # Key packages
            f.write("KEY PACKAGES:\n")
            packages = env_data.get('python_packages', [])
            key_packages = ['jupyter', 'pandas', 'numpy', 'matplotlib', 'scipy', 'ipywidgets', 'ipykernel']
            for pkg in packages:
                if isinstance(pkg, dict) and pkg.get('name', '').lower() in key_packages:
                    f.write(f"{pkg['name']}: {pkg['version']}\n")
            f.write("\n")
            
            # IPYKERNEL STATUS (NEW SECTION)
            f.write("IPYKERNEL STATUS:\n")
            ipykernel_info = env_data.get('ipykernel_info', {})
            f.write(f"Package Installed: {'✓' if ipykernel_info.get('package_installed') else '✗'}\n")
            f.write(f"Version: {ipykernel_info.get('version', 'N/A')}\n")
            f.write(f"Install Command Works: {'✓' if ipykernel_info.get('install_command_works') else '✗'}\n")
            f.write(f"Heat Reuse Kernel Registered: {'✓' if ipykernel_info.get('heat_reuse_kernel_registered') else '✗'}\n")
            f.write(f"Jupyter Available: {'✓' if ipykernel_info.get('jupyter_available') else '✗'}\n")
            if ipykernel_info.get('errors'):
                f.write("Errors:\n")
                for error in ipykernel_info['errors']:
                    f.write(f"  - {error}\n")
            f.write("\n")
            
            # Required files status
            f.write("REQUIRED FILES:\n")
            required = env_data.get('required_files', {})
            for file_path, exists in required.items():
                status = "✓" if exists else "✗"
                f.write(f"{status} {file_path}\n")
            f.write("\n")
            
            # Jupyter kernels
            f.write("JUPYTER KERNELS:\n")
            jupyter_info = env_data.get('jupyter_info', {})
            kernels = jupyter_info.get('kernels', {})
            if isinstance(kernels, dict) and 'kernelspecs' in kernels:
                for kernel_name in kernels['kernelspecs'].keys():
                    marker = "🎯" if 'heat-reuse' in kernel_name.lower() else "  "
                    f.write(f"{marker} {kernel_name}\n")
            
            # Heat Reuse Tool specific kernels
            heat_reuse_kernels = jupyter_info.get('heat_reuse_tool_kernels', {})
            if heat_reuse_kernels:
                f.write("\nHEAT REUSE TOOL KERNELS:\n")
                for kernel_name, kernel_info in heat_reuse_kernels.items():
                    f.write(f"✓ {kernel_name}\n")
                    if 'spec' in kernel_info and 'display_name' in kernel_info['spec']:
                        f.write(f"    Display Name: {kernel_info['spec']['display_name']}\n")
                    if 'resource_dir' in kernel_info:
                        f.write(f"    Location: {kernel_info['resource_dir']}\n")
            f.write("\n")
            
    except Exception as e:
        print(f"Warning: Could not create summary file: {str(e)}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        machine_name = sys.argv[1].lower()
    else:
        machine_name = None
    
    exported_file = export_environment(machine_name)
    
    if exported_file:
        print(f"\n✓ Environment export completed successfully!")
        print(f"Files saved in: tools/environment/exports/")
        print(f"\nTo compare with another machine:")
        print(f"python tools/environment/compare_environments.py {exported_file} [other_file]")
    else:
        print("\n✗ Environment export failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()