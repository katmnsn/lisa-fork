# LISA Build, Run, and Troubleshooting Commands

**Reference library for LISA development commands, troubleshooting, and validation workflows.**

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Build and Format Commands](#build-and-format-commands)
3. [Running Tests](#running-tests)
4. [Platform Options](#platform-options)
5. [Common Command Line Options](#common-command-line-options)
6. [Testing Workflow Recommendations](#testing-workflow-recommendations)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Validation Checklist](#validation-checklist)

---

## Development Environment Setup

### Initial Setup (PowerShell/Windows)

```powershell
# Clone repository
git clone https://github.com/microsoft/lisa.git
cd lisa

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install --editable .[dev,test,azure]
```

### Initial Setup (Bash/Linux)

```bash
# Clone repository
git clone https://github.com/microsoft/lisa.git
cd lisa

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install --editable .[dev,test,azure]
```

---

## Build and Format Commands

### Code Formatting

```powershell
# Format single file
python -m black microsoft/testsuites/<area>/<file>.py

# Format entire directory
python -m black microsoft/testsuites/<area>/

# Check format without changing files
python -m black --check microsoft/testsuites/<area>/<file>.py
```

### Linting

```powershell
# Run pylint on file
python -m pylint microsoft/testsuites/<area>/<file>.py

# Run pylint on directory
python -m pylint microsoft/testsuites/<area>/

# Disable specific warnings
python -m pylint --disable=C0103,W0212 microsoft/testsuites/<area>/<file>.py
```

### Type Checking

```powershell
# Run mypy type checker
python -m mypy microsoft/testsuites/<area>/<file>.py

# Run mypy on entire codebase
python -m mypy lisa/ microsoft/
```

---

## Running Tests

### Azure Platform

```powershell
# Basic Azure run
lisa -r microsoft/runbook/azure.yml -v subscription_id:<subscription_id>

# Run specific test
lisa -r microsoft/runbook/azure.yml -v subscription_id:<id> -t test_name

# Run with custom location
lisa -r microsoft/runbook/azure.yml -v subscription_id:<id> -v location:westus3

# Run with specific VM size
lisa -r microsoft/runbook/azure.yml -v subscription_id:<id> -v vm_size:Standard_D2s_v3

# Run with custom marketplace image
lisa -r microsoft/runbook/azure.yml `
    -v subscription_id:<id> `
    -v "marketplace_image:Canonical UbuntuServer 18.04-LTS Latest"
```

### Ready Platform (Existing VM/Remote Host)

```powershell
# Connect to existing VM
lisa -r microsoft/runbook/ready.yml `
    -v "public_address:<ip>" `
    -v "user_name:<user>" `
    -v "admin_private_key_file:<key>"

# With custom port
lisa -r microsoft/runbook/ready.yml `
    -v "public_address:<ip>" `
    -v "user_name:<user>" `
    -v "admin_private_key_file:<key>" `
    -v "port:2222"
```

### Local Platform

```powershell
# Run tests on current machine
lisa -r microsoft/runbook/local.yml

# Run specific test locally
lisa -r microsoft/runbook/local.yml -t test_name
```

### Debug Platform (Targeted Testing)

```powershell
# Debug specific test case
lisa -r microsoft/runbook/debug.yml `
    -v "case:test_name" `
    -v "origin:azure.yml" `
    -v subscription_id:<id>

# Debug with custom environment
lisa -r microsoft/runbook/debug.yml `
    -v "case:test_name" `
    -v "origin:ready.yml" `
    -v "public_address:<ip>" `
    -v "user_name:<user>"
```

---

## Platform Options

| Platform | Use Case | Runbook | Required Variables |
|----------|----------|---------|-------------------|
| **Azure** | Cloud testing on Azure VMs | `azure.yml` | `subscription_id` |
| **Ready** | Existing VM/remote host | `ready.yml` | `public_address`, `user_name`, `admin_private_key_file` |
| **Local** | Current machine only | `local.yml` | None |
| **AWS** | Cloud testing on AWS | `aws.yml` | `aws_access_key_id`, `aws_secret_access_key` |
| **Debug** | Run specific tests by name | `debug.yml` | `case`, `origin`, platform-specific vars |

---

## Common Command Line Options

### Logging and Output

```powershell
# Run with debug logging
lisa -r <runbook> -d

# Custom log path
lisa -r <runbook> -l custom_log_path

# Custom working path
lisa -r <runbook> -w custom_working_path
```

### Variable Overrides

```powershell
# Override single variable
lisa -r <runbook> -v location:westus3

# Override multiple variables
lisa -r azure.yml `
    -v subscription_id:<id> `
    -v location:eastus `
    -v vm_size:Standard_D2s_v3

# Secret variables (not logged)
lisa -r <runbook> -v s:password:secret_value

# Custom run ID
lisa -r <runbook> -i custom_run_id
```

### Test Selection

```powershell
# Run specific test
lisa -r <runbook> -t test_method_name

# Run tests matching pattern
lisa -r <runbook> -t "*gpu*"

# Run tests in specific suite
lisa -r <runbook> -t "TestGpu.*"
```

---

## Testing Workflow Recommendations

### For Development (Fast Iteration)

1. **Use local or ready platform for quick testing**
   ```powershell
   # Test on local machine
   lisa -r microsoft/runbook/local.yml -t test_name
   
   # Test on existing VM
   lisa -r microsoft/runbook/ready.yml `
       -v "public_address:<ip>" `
       -v "user_name:<user>" `
       -v "admin_private_key_file:<key>" `
       -t test_name
   ```

2. **Use debug.yml to run only your test case**
   ```powershell
   lisa -r microsoft/runbook/debug.yml `
       -v "case:test_name" `
       -v "origin:azure.yml" `
       -v subscription_id:<id>
   ```

3. **Format with black before committing**
   ```powershell
   python -m black microsoft/testsuites/<area>/<file>.py
   ```

### For Validation (Before PR)

1. **Run your specific test on Azure**
   ```powershell
   lisa -r microsoft/runbook/azure.yml `
       -v subscription_id:<id> `
       -t test_name
   ```

2. **Run related test suite to catch regressions**
   ```powershell
   lisa -r microsoft/runbook/azure.yml `
       -v subscription_id:<id> `
       -t "TestSuiteName.*"
   ```

3. **Check for linter and type errors**
   ```powershell
   python -m pylint microsoft/testsuites/<area>/<file>.py
   python -m mypy microsoft/testsuites/<area>/<file>.py
   ```

### For Full Testing (CI/CD)

1. **Use azure.yml with tier selection**
   ```powershell
   lisa -r microsoft/runbook/azure.yml `
       -v subscription_id:<id> `
       -v "tier:0,1"
   ```

2. **Test across multiple distros/versions**
   ```powershell
   # Use runbook with multiple OS configurations
   lisa -r microsoft/runbook/multi_distro.yml -v subscription_id:<id>
   ```

3. **Use HTML report for results analysis**
   ```powershell
   # Reports are automatically generated in runtime/log/
   # Open runtime/log/<run_id>/lisa.html in browser
   ```

---

## Troubleshooting Guide

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Import errors:** `ModuleNotFoundError` | Wrong module path or tool doesn't exist | Check `lisa/tools/` directory. Use: `from lisa.tools import ToolName` |
| **Feature not found:** `KeyError: 'FeatureName'` | Feature not registered or typo | Verify feature name in `lisa/features/`. Use exact class name |
| **Test always skipped:** `SkippedException: unsupported_os` | OS requirements too restrictive | Check `supported_os` in TestCaseMetadata. Add missing distros |
| **Node reused when dirty:** Test pollution | Missing `node.mark_dirty()` call | Add `node.mark_dirty()` in exception handler (Pattern #1) |
| **Flaky test failures:** Network/device not ready | No retry mechanism | Use `@retry` decorator on helper function (Pattern #6) |
| **Test hangs indefinitely:** Cleanup blocked | No timeout protection | Wrap cleanup in `func_timeout()` (Pattern #7) |
| **Feature crash vs skip:** Missing support check | No `is_supported()` check | Add feature support check before use (Pattern #2) |
| **Tool command fails:** Tool not available on OS | OS doesn't have required package | Add OS to `unsupported_os` or install in `before_case()` |
| **Assertion too generic:** Message unclear | No `.described_as()` message | Add descriptive message to every assertion |
| **Multi-node test fails:** Wrong signature | Using `node` instead of `environment` | Use `environment` parameter with `min_count=2` (Pattern #5) |
| **Black formatting fails:** Line too long | Lines exceed 88 characters | Break long lines, use parentheses for line continuation |
| **Type hints missing:** Linter warnings | Forgot type annotations | Add type hints: `def func(param: Type) -> ReturnType:` |
| **Helper conflicts:** Name collision | Not following naming convention | Use `_` prefix for module-private helpers (Pattern #3) |
| **Lifecycle hook not running:** Wrong signature | Missing `**kwargs` parameter | Use: `def before_case(self, log: Logger, **kwargs: Any)` |
| **Feature requirement ignored:** Wrong syntax | `Feature()` vs `Feature` | In requirements use: `supported_features=[Feature]` (no parens) |
| **Test runs on wrong OS:** Exclusions not working | Typo in OS name | Verify OS name: `Ubuntu`, `Redhat`, `CentOS`, etc. |
| **Disk space errors:** Not checking space | No space validation | Check: `node.tools[Df].get_filesystem_available()` |
| **Cleanup not running:** Exception in test | Exception prevents after_case | Use try-finally or timeout-protected cleanup (Pattern #7) |
| **Environment contaminated:** Previous test state | No cleanup between tests | Implement `after_case()` for cleanup (Pattern #4) |
| **Regex pattern fails:** Incorrect syntax | Wrong regex pattern | Test with `re` module first, use raw strings `r"pattern"` |

### Quick Debugging Commands (PowerShell)

```powershell
# Check available tools
Get-ChildItem lisa\tools\*.py | Select-Object Name

# Check available features
Get-ChildItem lisa\features\*.py | Select-Object Name

# Search for similar test implementations
Select-String -Path "microsoft\testsuites\**\*.py" -Pattern "pattern_to_find"

# Find tool usage examples
Select-String -Path "microsoft\testsuites\**\*.py" -Pattern "node.tools\[ToolName\]"

# Check test suite structure
Get-ChildItem microsoft\testsuites\ -Recurse -Filter "test_*.py"
```

### Quick Debugging Commands (Bash)

```bash
# Check available tools
ls -1 lisa/tools/*.py

# Check available features
ls -1 lisa/features/*.py

# Search for similar test implementations
grep -r "pattern_to_find" microsoft/testsuites/

# Find tool usage examples
grep -r "node.tools\[ToolName\]" microsoft/testsuites/

# Check test suite structure
find microsoft/testsuites/ -name "test_*.py"
```

### Error Message Interpretation

**"Test skipped: unsupported_os"**
- Cause: OS requirements in `TestCaseMetadata` exclude current OS
- Fix: Add missing OS to `supported_os` or remove from `unsupported_os`

**"Feature 'X' not supported on this platform"**
- Cause: Feature check failed (expected behavior)
- Action: Ensure test has proper `is_supported()` check to skip gracefully

**"Node marked dirty"**
- Cause: Previous test failed and marked node unusable
- Action: Framework will provision new node (expected behavior)

**"Timeout waiting for condition"**
- Cause: Operation took longer than expected
- Fix: Increase timeout value or use `@retry` decorator

**"Command not found: tool_name"**
- Cause: Tool not installed on OS
- Fix: Add OS to `unsupported_os` or install tool in `before_case()`

---

## Validation Checklist

### Before Proposing Changes

Verify:

1. ✅ Code is syntactically valid Python
2. ✅ All imports are valid and available in LISA
3. ✅ TestSuiteMetadata and TestCaseMetadata are complete
4. ✅ OS requirements match actual distro native capabilities
5. ✅ Type hints are complete on all functions and methods
6. ✅ Assertions use assertpy with `.described_as()` for clarity
7. ✅ Code follows black formatting (88 char line length)
8. ✅ Test method names use snake_case with `test_` prefix
9. ✅ No duplicate test method names
10. ✅ No hardcoded values (use environment/node properties)
11. ✅ Proper exception handling and error messages
12. ✅ Comments explain business logic, not code logic
13. ✅ `node.mark_dirty()` called in all exception handlers
14. ✅ Module-private helpers use single underscore (`_function`)
15. ✅ Implementation details use double underscore (`__function`)
16. ✅ Refactored existing functions instead of creating parallel ones
17. ✅ Cleanup has timeout protection (`func_timeout`)
18. ✅ Disk space checks are reactive (after failure), not proactive
19. ✅ ONE focused test per PR, not multiple scenarios
20. ✅ Delegation pattern used for alternative implementations
21. ✅ `before_case()` used for suite-level setup when applicable
22. ✅ Features checked for support before use (`is_supported()`)
23. ✅ Working path requested with space requirements for large operations
24. ✅ Regex patterns compiled at class level with named groups
25. ✅ `@retry` decorator on helpers for flaky operations
26. ✅ Multi-node tests use `min_count` requirement and `environment.nodes.list()`
27. ✅ Appropriate test method signature chosen (node vs environment vs result)

### Code Quality Checks

```powershell
# Run all quality checks
python -m black microsoft/testsuites/<area>/<file>.py
python -m pylint microsoft/testsuites/<area>/<file>.py
python -m mypy microsoft/testsuites/<area>/<file>.py

# Check if tests can be discovered
python -m pytest --collect-only microsoft/testsuites/<area>/<file>.py
```

### Pattern Compliance

- [ ] Pattern #1: `node.mark_dirty()` in exception handlers
- [ ] Pattern #2: Feature support checks before feature usage
- [ ] Pattern #3: Helper functions use `_` prefix
- [ ] Pattern #4: Lifecycle hooks used for suite-level setup/cleanup
- [ ] Pattern #5: Multi-node tests use correct signature
- [ ] Pattern #6: Retry decorator on flaky operations
- [ ] Pattern #7: Timeout protection on cleanup operations

---

## File Organization Rules

### Do Not Modify

- `lisa/__init__.py`, `lisa/*.py` - Core framework
- `*.pyc`, `__pycache__/`, `.venv/` - Generated files
- `.github/workflows/*.yml` - CI/CD
- `microsoft/runbook/*.yml` - Runbooks
- `pyproject.toml` - Package config

### Safe to Modify

- `microsoft/testsuites/**/*.py` - Test files
- `examples/testsuites/**/*.py` - Example tests
- `selftests/**/*.py` - Framework tests

---

## Quick Reference Commands

### Most Common Development Workflow

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Format code
python -m black microsoft/testsuites/<area>/<file>.py

# 3. Run linter
python -m pylint microsoft/testsuites/<area>/<file>.py

# 4. Test locally (fast iteration)
lisa -r microsoft/runbook/local.yml -t test_name

# 5. Test on Azure (validation)
lisa -r microsoft/runbook/azure.yml -v subscription_id:<id> -t test_name
```

### Most Common Debugging Workflow

```powershell
# 1. Run test with debug logging
lisa -r <runbook> -d -t test_name

# 2. Check logs
cat runtime/log/<run_id>/lisa.log

# 3. View HTML report
start runtime/log/<run_id>/lisa.html

# 4. Re-run specific failed test
lisa -r microsoft/runbook/debug.yml `
    -v "case:test_name" `
    -v "origin:azure.yml" `
    -v subscription_id:<id>
```
