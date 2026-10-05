# Heat Reuse Tool - Tools Directory

This directory contains setup, environment management, and deployment tools for the Heat Reuse Tool project.

## Directory Structure

```
tools/
├── setup/                     # Environment verification and setup
│   ├── verify_setup.py       # Comprehensive environment verification
│   └── (future setup tools)
├── environment/               # Environment management and comparison
│   ├── export_environment.py # Export current environment details
│   ├── compare_environments.py # Compare two environments
│   └── exports/              # Generated environment export files
└── README.md                 # This file
```

## Quick Start

### Verify Your Setup
```powershell
# Run comprehensive verification
python tools/setup/verify_setup.py

# Quick essential checks only
python tools/setup/verify_setup.py quick
```

### Export Environment for Comparison
```powershell
# Export current environment (auto-detects machine name)
python tools/environment/export_environment.py

# Export with custom machine name
python tools/environment/export_environment.py dragonraider
```

### Compare Environments
```powershell
# Compare two environment files
python tools/environment/compare_environments.py file1.json file2.json

# Auto-find latest exports by machine name
python tools/environment/compare_environments.py dragonraider swiftsetup

# List available environment exports
python tools/environment/compare_environments.py
```

## Tool Descriptions

### `tools/setup/verify_setup.py`
**Purpose**: Comprehensive environment verification for Heat Reuse Tool

**Features**:
- ✅ Checks Python version and packages
- ✅ Verifies virtual environment setup
- ✅ Tests Jupyter configuration and kernels
- ✅ Validates project structure and required files
- ✅ Tests CSV data loading
- ✅ Verifies autostart.py imports
- ✅ Color-coded pass/fail results
- ✅ Specific recommendations for issues

**Usage**:
```powershell
python tools/setup/verify_setup.py        # Full verification
python tools/setup/verify_setup.py quick  # Essential checks only
python tools/setup/verify_setup.py export # Export environment details
```

**Expected Result**: 9/9 checks passed on properly configured system

### `tools/environment/export_environment.py`
**Purpose**: Export complete environment details for comparison and troubleshooting

**What it captures**:
- System information (OS, Python version, architecture)
- All installed Python packages with versions
- Jupyter configuration and kernels
- VSCode extensions
- Git version
- Project file structure
- Required Heat Reuse Tool files status

**Output Files**:
- `{machine}_environment_{timestamp}.json` - Complete environment data
- `{machine}_summary_{timestamp}.txt` - Human-readable summary

**Usage**:
```powershell
python tools/environment/export_environment.py [machine_name]
```

### `tools/environment/compare_environments.py`
**Purpose**: Compare two environment exports to identify differences

**Features**:
- ✅ System information comparison
- ✅ Package version differences
- ✅ Jupyter kernel compatibility
- ✅ Required files status
- ✅ VSCode extension differences
- ✅ Automatic sync recommendations
- ✅ Generated PowerShell sync scripts

**Usage**:
```powershell
# Compare specific files
python tools/environment/compare_environments.py env1.json env2.json

# Auto-find latest by machine name
python tools/environment/compare_environments.py dragonraider swiftsetup

# List available exports
python tools/environment/compare_environments.py
```

**Output**: Detailed comparison report + sync script for fixing differences

## Typical Workflow

### Setting Up a New Machine (e.g., SwiftSetup)

1. **Export baseline environment** (from working machine):
   ```powershell
   python tools/environment/export_environment.py dragonraider
   ```

2. **Set up new machine** following main setup guide

3. **Verify new setup**:
   ```powershell
   python tools/setup/verify_setup.py
   ```

4. **Export new environment**:
   ```powershell
   python tools/environment/export_environment.py swiftsetup
   ```

5. **Compare environments**:
   ```powershell
   python tools/environment/compare_environments.py dragonraider swiftsetup
   ```

6. **Apply sync recommendations** from generated script

7. **Re-verify until 9/9 passes**:
   ```powershell
   python tools/setup/verify_setup.py
   ```

### Troubleshooting Environment Issues

1. **Run verification** to identify specific problems:
   ```powershell
   python tools/setup/verify_setup.py
   ```

2. **Export environment** for detailed analysis:
   ```powershell
   python tools/environment/export_environment.py problematic-machine
   ```

3. **Compare with working environment**:
   ```powershell
   python tools/environment/compare_environments.py working-machine problematic-machine
   ```

4. **Apply generated sync script** to fix differences

## File Locations

### Generated Files
All generated files are saved in `tools/environment/exports/` and are excluded from git via `.gitignore`.

### Export File Naming
- Environment exports: `{machine}_environment_{timestamp}.json`
- Summary files: `{machine}_summary_{timestamp}.txt`
- Sync scripts: `sync_{source}_to_{target}_{timestamp}.ps1`

### Auto-detection
The comparison tool can auto-find the latest export for a machine name:
```powershell
# These commands are equivalent if latest files exist:
python tools/environment/compare_environments.py dragonraider swiftsetup
python tools/environment/compare_environments.py dragonraider_environment_20250623_143022.json swiftsetup_environment_20250623_150415.json
```

## Integration with Main Setup

These tools are integrated into the main setup process:

1. **Setup Plan** references `tools/setup/verify_setup.py` for validation
2. **Troubleshooting Guide** uses these tools for diagnosis
3. **Environment Comparison** workflow uses `tools/environment/` utilities

## Adding New Tools

When adding new setup or environment tools:

1. Place in appropriate subdirectory (`setup/`, `environment/`, etc.)
2. Update this README with usage instructions
3. Add to main setup documentation if user-facing
4. Follow naming convention: `{purpose}_{description}.py`
5. Include help text and error handling
6. Add to `.gitignore` if tool generates output files

## Requirements

These tools require the same Python environment as the Heat Reuse Tool:
- Python 3.10+
- Standard library modules (json, subprocess, pathlib, etc.)
- No additional dependencies beyond Heat Reuse Tool requirements

## Cross-Platform Compatibility

- **Windows**: Full functionality with PowerShell
- **Mac/Linux**: Core functionality (some Windows-specific features may be skipped)
- **Commands**: Use forward slashes for cross-platform: `python tools/setup/verify_setup.py`