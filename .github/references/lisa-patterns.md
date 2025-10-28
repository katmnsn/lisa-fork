# LISA Test Patterns Library

**Reference library for common LISA testing patterns. This file is referenced by prompt files and provides detailed pattern implementations.**

---

## Table of Contents

1. [Pattern Quick Reference](#pattern-quick-reference)
   - [Pattern #1: Node Cleanup (node.mark_dirty)](#pattern-1-node-cleanup-nodemarkdirty--critical)
   - [Pattern #2: Feature Support Check](#pattern-2-feature-support-check--required)
   - [Pattern #3: Helper Naming Convention](#pattern-3-helper-naming-convention--consistency)
   - [Pattern #4: Lifecycle Hooks](#pattern-4-lifecycle-hooks--efficiency)
   - [Pattern #5: Multi-Node Test Structure](#pattern-5-multi-node-test-structure--distributed)
   - [Pattern #6: @retry Decorator](#pattern-6-retry-decorator--reliability)
   - [Pattern #7: Timeout Protection](#pattern-7-timeout-protection--safety)
   - [Pattern #8: Logging Best Practices](#pattern-8-logging-best-practices--clarity)
   - [Pattern #9: Error Messages](#pattern-9-error-messages--actionable)
   - [Pattern #10: Code Comments](#pattern-10-code-comments--maintainability)
   - [Pattern #11: Assertion Best Practices](#pattern-11-assertion-best-practices--validation)
2. [Critical Patterns](#critical-patterns)
3. [Lifecycle Hooks](#lifecycle-hooks)
4. [Feature Patterns](#feature-patterns)
5. [Helper Naming Conventions](#helper-naming-conventions)
6. [Advanced Patterns](#advanced-patterns)
7. [Multi-Node Patterns](#multi-node-patterns)
8. [Alternative Signatures](#alternative-signatures)
9. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Pattern Quick Reference

### Pattern #1: Node Cleanup (node.mark_dirty) ⚠️ CRITICAL

**When to use:** Test fails or encounters errors that change node state  
**Usage:** `node.mark_dirty()` in exception handler  
**Why this matters:** Prevents corrupted VMs from being reused in subsequent tests

**Impact if missed:**
- Contaminated test environment for next test
- Hard-to-debug cascading failures
- Wasted infrastructure resources on bad VMs

**Real-world consequence:** A test that crashes the kernel without marking dirty will cause the next test to fail on a broken VM, wasting 30+ minutes of test time.

```python
try:
    perform_state_changing_operation(node)
except Exception:
    node.mark_dirty()  # Pattern #1 - prevents test contamination
    raise
```

### Pattern #2: Feature Support Check ✅ REQUIRED

**When to use:** Using any platform feature (GPU, SRIOV, NetworkInterface)  
**Usage:** `if not feature.is_supported(): raise SkippedException()`  
**Why this matters:** Graceful skip on unsupported platforms vs cryptic failures

**Impact if missed:**
- Tests crash with confusing errors on unsupported platforms
- No clear diagnostic why test can't run
- try-except hides root cause

**Real-world consequence:** Without support check, GPU test fails on non-GPU VM with "lspci command not found" instead of clear "GPU not supported on this platform" skip message.

```python
gpu = node.features[Gpu]

# Pattern #2: Check support
if not gpu.is_supported():
    raise SkippedException(f"GPU not supported on {node.os.name}")

# Use feature methods
expected = node.capability.gpu_count
actual = gpu.get_gpu_count_with_lspci()
assert_that(actual).described_as(
    "GPU count should match capability"
).is_equal_to(expected)
```

### Pattern #3: Helper Naming Convention 📛 CONSISTENCY

**When to use:** Creating helper functions  
**Usage:** Single `_` for module-private, double `__` for implementation details  
**Why this matters:** Signals visibility scope and prevents accidental external usage

**Impact if missed:**
- Confusion about which helpers are meant for reuse
- Accidental coupling between modules
- Harder code maintenance

**Real-world consequence:** Public helper gets used by other modules, then when you refactor it, you break those modules. Single `_` prefix prevents this by signaling "internal use only."

```python
# Single _ for module-private (called by multiple test cases)
def _install_component(node: Node, log: Logger, log_path: Path) -> None:
    """Install and configure component - reusable across tests."""
    try:
        __install_using_extension(node, log)
    except Exception:
        log.info("Extension install failed, trying SDK")
        __install_using_sdk(node, log, log_path)

# Double __ for implementation details (called only by other helpers)
def __install_using_extension(node: Node, log: Logger) -> None:
    """Internal: Install via extension (called only by _install_component)."""
    pass

def __install_using_sdk(node: Node, log: Logger, log_path: Path) -> None:
    """Internal: Install via SDK (called only by _install_component)."""
    pass
```

### Pattern #4: Lifecycle Hooks 🔄 EFFICIENCY

**When to use:** Suite-level setup/teardown needed for ALL tests  
**Usage:** `before_case()` for setup, `after_case()` for cleanup  
**Why this matters:** DRY principle - setup once instead of repeating in every test

**Impact if missed:**
- Duplicated setup code in every test method
- Higher maintenance burden
- Inconsistent setup across tests

**Real-world consequence:** Network test suite with 10 tests, each checking firewall status separately = 10x the code. `before_case()` does it once.

```python
def before_case(self, log: Logger, **kwargs: Any) -> None:
    """Suite-level setup before each test case."""
    node: Node = kwargs["node"]
    
    # OS compatibility checks
    if isinstance(node.os, (BSD, Windows)):
        raise SkippedException(f"{node.os} not supported")
    
    # Prerequisite validation
    if not node.tools[RequiredTool].command_exists():
        raise SkippedException("Required tool not available")

def after_case(self, log: Logger, **kwargs: Any) -> None:
    """Suite-level cleanup after each test case."""
    environment: Environment = kwargs.pop("environment")
    
    # Cleanup with timeout protection
    try:
        func_timeout(
            timeout=300,
            func=self._cleanup_resources,
            args=(environment, log)
        )
    except Exception as cleanup_ex:
        log.info(f"Cleanup failed: {cleanup_ex}")
        for node in environment.nodes.list():
            if isinstance(node, RemoteNode):
                node.mark_dirty()
```

### Pattern #5: Multi-Node Test Structure 🌐 DISTRIBUTED

**When to use:** Testing distributed systems, network connectivity, replication  
**Usage:** `min_count=2`, `environment.nodes.list()`, `environment` parameter  
**Why this matters:** Enables coordination and communication across multiple VMs

**Impact if missed:**
- Can't test multi-node scenarios
- Network tests limited to single-node
- No distributed system validation

**Real-world consequence:** Network throughput test needs client and server VMs. Without `min_count=2`, test framework won't provision the second node.

```python
@TestCaseMetadata(
    description="Multi-node network connectivity test",
    priority=2,
    requirement=simple_requirement(
        min_count=2,
        network_interface=Sriov(),
    ),
)
def verify_multi_node_network(self, environment: Environment, log: Logger) -> None:
    """Test requiring multiple nodes."""
    nodes = environment.nodes.list()
    assert_that(len(nodes)).described_as(
        "Test requires at least 2 nodes"
    ).is_greater_than_or_equal_to(2)
    
    node1, node2 = nodes[0], nodes[1]
    
    try:
        # Multi-node test implementation
        _test_connectivity(node1, node2, log)
    except Exception:
        node1.mark_dirty()
        node2.mark_dirty()
        raise
```

### Pattern #6: @retry Decorator 🔁 RELIABILITY

**When to use:** Flaky operations (network discovery, device enumeration)  
**Usage:** `@retry(exceptions=AssertionError, tries=30, delay=2)` on helpers ONLY  
**Why this matters:** Handles transient failures without complicating test method logic

**Impact if missed:**
- Flaky test failures on valid scenarios
- Manual retry logic clutters test code
- Lower test reliability

**Real-world consequence:** SR-IOV device takes 10 seconds to appear after enablement. Without `@retry`, test fails instantly. With retry, it polls for up to 60 seconds and succeeds.

```python
from retry import retry

@retry(exceptions=AssertionError, tries=30, delay=2)
def _check_condition(node: Node, expected_value: Any) -> None:
    """
    Check condition with retry for transient failures.
    
    Pattern #6: Retry decorator for flaky operations.
    """
    result = node.tools[ToolName].check_condition()
    assert_that(result).described_as(
        f"Expected {expected_value}"
    ).is_equal_to(expected_value)
```

### Pattern #7: Timeout Protection ⏱️ SAFETY

**When to use:** Cleanup operations that might hang indefinitely  
**Usage:** `func_timeout(timeout=300, func=cleanup_fn, args=(...))`  
**Why this matters:** Prevents hanging tests, ensures timely failure with diagnostics

**Impact if missed:**
- Test runs hang indefinitely
- CI/CD pipelines stuck
- No clear failure diagnostics

**Real-world consequence:** Network cleanup waits for firewall rule deletion that never completes. Without timeout, test hangs for hours. With timeout, fails after 5 minutes with clear error.

```python
from func_timeout import func_timeout, FunctionTimedOut

def _cleanup_with_timeout(node: Node, log: Logger) -> None:
    """
    Cleanup operation with timeout protection.
    
    Pattern #7: Prevent hanging cleanup operations.
    """
    try:
        func_timeout(
            timeout=300,
            func=_perform_cleanup,
            args=(node, log)
        )
    except FunctionTimedOut:
        log.warn("Cleanup timed out after 300 seconds")
        node.mark_dirty()  # Pattern #1: Mark dirty on timeout
    except Exception as e:
        log.error(f"Cleanup failed: {e}")
        node.mark_dirty()
        raise
```

### Pattern #8: Logging Best Practices 📝 CLARITY

**When to use:** All test code - logging helps debugging and progress tracking  
**Usage:** `log.debug()` for details, `log.info()` for story  
**Why this matters:** Good logs make debugging 10x faster, poor logs waste hours

**Impact if missed:**
- Cannot debug failures without rerunning tests
- Log output is confusing or overwhelming
- Cannot find where log line came from in code

**Real-world consequence:** Test fails with generic "operation failed" - no details in logs. Spend 2 hours reproducing issue just to add debug logging. With good logging, root cause is obvious from first failure.

**Key rules:**
1. **DEBUG** = Detailed troubleshooting info (always in log file)
2. **INFO** = Story-like progress (console output, should read like narrative)
3. **Make each log line unique** - Add context so you can search code
4. **Use f-strings** for formatting (Python 3.6+)

```python
# ✅ GOOD: Unique, informative, proper levels
def test_network_performance(self, node: Node, log: Logger) -> None:
    log.info("Starting network performance test with iperf3")
    
    server_ip = "10.0.0.5"
    log.debug(f"test_network_performance: connecting to server {server_ip}")
    
    result = node.tools[Iperf3].run_as_client(server_ip, log_path)
    log.debug(f"test_network_performance: iperf3 output: {result.stdout[:200]}")
    
    log.info(f"Network throughput: {throughput} Gbps")

# ❌ BAD: Generic, duplicate, wrong levels
def test_network_performance(self, node: Node, log: Logger) -> None:
    log.debug("Starting test")  # Should be INFO, not unique
    log.debug("Running command")  # Not unique, appears 50x in codebase
    log.info(result.stdout)  # Too verbose for INFO, use DEBUG
```

### Pattern #9: Error Messages 💬 ACTIONABLE

**When to use:** All exceptions - SkippedException, LisaException, assertions  
**Usage:** Include WHAT happened + WHY + HOW to fix  
**Why this matters:** Good error messages save hours of debugging time

**Impact if missed:**
- Users cannot diagnose failures without re-running
- Generic "operation failed" requires code reading to understand
- No actionable guidance on resolution

**Real-world consequence:** Test fails with "GPU not found". Spend 30 minutes checking if GPU is broken, driver issue, or just wrong VM size. Better message: "GPU not found - expected 1 GPU based on VM size Standard_NC6, but lspci shows 0. Verify VM was provisioned correctly or try different VM size."

**Key rules:**
1. **State what failed** - Specific operation/check that didn't work
2. **Include context** - Relevant values (VM size, distro, expected vs actual)
3. **Suggest resolution** - What user should check or try next
4. **Don't hide original errors** - Include underlying error details

```python
# ✅ GOOD: Actionable error messages
def test_gpu_count(self, node: Node, log: Logger) -> None:
    gpu = node.features[Gpu]
    if not gpu.is_supported():
        raise SkippedException(
            f"GPU not supported on {node.os.name} {node.os.information.version}. "
            f"This test requires CUDA-capable GPU. Verify VM size has GPU."
        )
    
    expected = node.capability.gpu_count
    actual = gpu.get_gpu_count_with_lspci()
    
    assert_that(actual).described_as(
        f"GPU count mismatch on {node.capability.vm_size}: "
        f"expected {expected} based on VM capability, but lspci found {actual}. "
        f"Check if GPU driver loaded correctly (lspci -v) or VM provisioned wrong size."
    ).is_equal_to(expected)

# ❌ BAD: Vague, no context, no resolution
def test_gpu_count(self, node: Node, log: Logger) -> None:
    gpu = node.features[Gpu]
    if not gpu.is_supported():
        raise SkippedException("GPU not supported")  # Missing: WHY and WHAT TO DO
    
    expected = node.capability.gpu_count
    actual = gpu.get_gpu_count_with_lspci()
    
    assert_that(actual).is_equal_to(expected)  # Missing: context about what failed
```

### Pattern #10: Code Comments 📖 MAINTAINABILITY

**When to use:** Complex logic, business rules, regex patterns, tricky workarounds  
**Usage:** Explain WHY and business logic, not WHAT (code shows what)  
**Why this matters:** Comments help future developers (including you) understand intent

**Impact if missed:**
- Cannot understand why code does something unusual
- Regex patterns are cryptic without examples
- Business logic hidden in implementation details

**Real-world consequence:** Code has `if version < "18.04": use_legacy_method()`. No comment explaining why. 6 months later, someone removes it thinking it's outdated, breaks Ubuntu 16.04 support.

**Key rules:**
1. **Don't repeat code** - No "if x > 5" comments, code is already clear
2. **Explain business logic** - Why this check matters, what it prevents
3. **Document tricky code** - Magic numbers, workarounds, platform quirks
4. **Provide regex examples** - Show what input the pattern matches

```python
# ✅ GOOD: Explains WHY and provides context
def _parse_network_stats(self, output: str) -> Dict[str, int]:
    # Ubuntu 16.04 uses different ifconfig output format without RX/TX labels
    # Example output: "packets:12345 errors:0 dropped:0"
    pattern = r"packets:(\d+)\s+errors:(\d+)"
    
    # Timeout of 300s because large VMs can take 4-5 minutes to configure
    # all NICs (seen Standard_D96_v5 with 8 NICs take 280s)
    result = self._wait_for_nics(timeout=300)
    
    return stats

# ❌ BAD: Repeats what code already shows
def _parse_network_stats(self, output: str) -> Dict[str, int]:
    # Parse the output  (obvious from function name)
    pattern = r"packets:(\d+)\s+errors:(\d+)"  # No example of what this matches
    
    # Wait for NICs with timeout  (code already shows this)
    result = self._wait_for_nics(timeout=300)  # Why 300? Why not 60?
    
    return stats
```

### Pattern #11: Assertion Best Practices ✔️ VALIDATION

**When to use:** All test validation - every assert_that() call  
**Usage:** `assert_that(actual).described_as("reason").is_equal_to(expected)`  
**Why this matters:** Clear assertions make failures self-explanatory

**Impact if missed:**
- Failures show confusing error messages
- Cannot understand what was being tested
- Harder to debug without description context

**Real-world consequence:** Test fails with "Expected 4 but got 2". What does this mean? GPU count? CPU cores? Network interfaces? With `.described_as()`: "Expected 4 GPUs based on VM size Standard_NC4as_T4_v3 but lspci found 2" - immediately actionable.

**Key rules:**
1. **Actual before expected** - `assert_that(actual).is_equal_to(expected)`
2. **Always use .described_as()** - Explain business logic being validated
3. **Use native assertions** - `is_length(6)` not `len()==6`
4. **Collection assertions** - `contains()`, `is_subset_of()` for lists

```python
# ✅ GOOD: Clear, native assertions with descriptions
def test_network_interfaces(self, node: Node, log: Logger) -> None:
    nics = node.nics.get_nic_count()
    expected = node.capability.network_interface_count
    
    # Actual value first, with business context
    assert_that(nics).described_as(
        f"NIC count on {node.capability.vm_size} should match capability"
    ).is_equal_to(expected)
    
    # Native assertion for length
    nic_names = node.nics.get_nic_names()
    assert_that(nic_names).described_as(
        "All NICs should have eth* naming pattern"
    ).is_length(expected)
    
    # Collection assertions for list validation
    assert_that(nic_names).described_as(
        "Primary NIC eth0 must be present"
    ).contains("eth0")

# ❌ BAD: No descriptions, awkward assertions
def test_network_interfaces(self, node: Node, log: Logger) -> None:
    nics = node.nics.get_nic_count()
    expected = node.capability.network_interface_count
    
    # No description - failure message unclear
    assert_that(nics).is_equal_to(expected)
    
    # Manipulating data instead of native assertion
    nic_names = node.nics.get_nic_names()
    assert_that(len(nic_names)).is_equal_to(expected)  # Use is_length() instead
    
    # Manual checking instead of collection assertion
    assert_that("eth0" in nic_names).is_true()  # Use contains() instead
```

---

## Critical Patterns

### Refactoring Existing Functions (Delegation Pattern)

When adding alternative implementations, refactor with a parameter instead of creating parallel functions:

**DO: Refactor with delegation**

```python
def _verify_by_method_a(node: Node, log: Logger) -> None:
    # Method A implementation
    pass

def _verify_by_method_b(node: Node, log: Logger) -> None:
    # Method B implementation  
    pass

def verify_operation(node: Node, log: Logger, use_method_a: bool = True) -> None:
    """Refactored to support both methods via parameter."""
    _prepare_environment(node)
    if use_method_a:
        _verify_by_method_a(node, log)
    else:
        _verify_by_method_b(node, log)
```

**DON'T: Create parallel functions**

```python
# WRONG - duplicates logic
def verify_operation_alternative(node, log):
    # Duplicate implementation
```

### Cleanup Timeout Protection

Add timeout protection to cleanup:

```python
def after_case(self, log: Logger, **kwargs: Any) -> None:
    environment: Environment = kwargs.pop("environment")
    
    try:
        func_timeout(timeout=300, func=cleanup_env, args=(environment,))
    except Exception as cleanup_ex:
        log.info(f"Cleanup failed: {cleanup_ex}")
        for node in environment.nodes.list():
            if isinstance(node, RemoteNode):
                node.mark_dirty()  # Pattern #1
```

### Disk Space Checking - Reactive Not Proactive

Check disk space AFTER failures for diagnostics, not before tests:

```python
def _check_disk_space(node: Node, log: Logger) -> None:
    """Log disk space for debugging - does NOT fail test."""
    df = node.tools[Df]
    partition = df.get_partition_by_mountpoint("/")
    if partition:
        available_gb = partition.available_blocks / 1024 / 1024
        log.info(f"Disk space: {available_gb:.2f}GB available")

# Usage - only on failure
try:
    perform_operation(node, log)
except Exception:
    _check_disk_space(node, log)  # Diagnostic aid
    raise
```

### Test Case Focus - One Feature Per PR

Add ONE focused test per PR, not multiple "nice to have" tests:

**DO THIS - Single focused test:**

```python
@TestCaseMetadata(
    description="Verify hibernation using LinuxHibernateExtension",
    priority=2,
)
def verify_hibernation_with_vm_extension(self, node: Node, log: Logger) -> None:
    is_distro_supported(node)
    verify_hibernation(
        node, log,
        use_hibernation_setup_tool=False,
        verify_using_logs=False
    )
```

**DON'T DO THIS - Multiple tests in one PR:**

```python
# Don't add all of these in one PR:
def verify_hibernation_with_extension(...)  # Main feature
def verify_hibernation_multiple_cycles(...)  # Nice to have
def verify_hibernation_disk_space_check(...)  # Edge case
```

---

## Lifecycle Hooks

### before_case() - Suite-Level Setup

Runs before EVERY test case in the suite. Use for common setup that applies to all tests.

**Behavior:**
- Called before each test case runs
- If `before_case` fails → test case is **SKIPPED** (not failed)
- Use `raise SkippedException()` for unsupported platforms

#### Single-Node Setup (Most Common)

```python
class MyTestSuite(TestSuite):
    def before_case(self, log: Logger, **kwargs: Any) -> None:
        node: Node = kwargs["node"]
        
        # OS compatibility checks - failure skips test
        if isinstance(node.os, (BSD, Windows)):
            raise SkippedException(f"{node.os} not supported")
        
        # Prerequisite validation - failure skips test
        if not node.tools[RequiredTool].command_exists():
            raise SkippedException("Required tool not available")
```

#### Multi-Node Setup (For Network/Distributed Tests)

```python
def before_case(self, log: Logger, **kwargs: Any) -> None:
    environment: Environment = kwargs.pop("environment")
    
    # Configure ALL nodes for network testing
    for node in environment.nodes.list():
        node.tools[Firewall].stop()
        node.features[NetworkInterface].switch_sriov(
            enable=True, wait=True, reset_connections=True
        )
```

### after_case() - Suite-Level Cleanup

Runs after EVERY test case in the suite. Use for cleanup that applies to all tests.

**Behavior:**
- Called after each test case completes (regardless of pass/fail)
- If `after_case` fails → does **NOT** affect test result
- Test result determined before `after_case` runs
- Use for cleanup that shouldn't fail tests

```python
class MyTestSuite(TestSuite):
    def after_case(self, log: Logger, **kwargs: Any) -> None:
        node: Node = kwargs["node"]
        
        try:
            # Cleanup operations
            node.tools[ServiceTool].stop_service("test-service")
            node.tools[Package].remove("test-package")
        except Exception as cleanup_ex:
            # Cleanup failure logged but doesn't fail test
            log.info(f"Cleanup failed (non-critical): {cleanup_ex}")
```

---

## Feature Patterns

Features are the PRIMARY way to interact with platform-specific capabilities in LISA.

### Feature Usage Pattern

Always follow this pattern when working with features:

```python
def my_test(self, node: Node, log: Logger) -> None:
    gpu = node.features[Gpu]
    
    # Pattern #2: Check support
    if not gpu.is_supported():
        raise SkippedException(f"GPU not supported on {node.os.name}")
    
    # Use feature methods
    expected = node.capability.gpu_count
    actual = gpu.get_gpu_count_with_lspci()
    assert_that(actual).described_as(
        "GPU count should match capability"
    ).is_equal_to(expected)
```

### Common LISA Features

```python
from lisa.features import (
    Gpu,           # GPU operations and driver management
    StartStop,     # VM start/stop operations
    SerialConsole, # Serial console access
    Resize,        # VM resize operations
    Nvme,          # NVMe storage operations
    NetworkInterface,  # Network interface management
    Sriov,         # SR-IOV operations
    Infiniband,    # InfiniBand operations
)
```

### VM Lifecycle Testing with StartStop

Standard pattern for testing resource persistence across VM operations:

```python
def test_persistence_across_lifecycle(self, node: Node, log: Logger) -> None:
    """Verify resources persist across stop-start cycle."""
    start_stop = node.features[StartStop]
    
    # Step 1: Capture initial state
    initial_state = self._capture_resource_state(node)
    log.debug(f"Initial state: {initial_state}")
    
    # Step 2: Validate initial state meets requirements
    assert_that(initial_state).is_not_none()
    
    # Step 3: Perform VM lifecycle operation
    start_stop.stop()
    start_stop.start()
    
    # Step 4: Re-capture state after restart
    current_state = self._capture_resource_state(node)
    log.debug(f"State after restart: {current_state}")
    
    # Step 5: Validate persistence
    assert_that(current_state).described_as(
        "State should persist across stop-start cycle"
    ).is_equal_to(initial_state)
```

---

## Helper Naming Conventions

### Single Underscore (_) - Module-Private, Reusable

Functions that are private to the module but can be called by multiple test cases:

```python
def _install_component(node: Node, log: Logger, log_path: Path) -> None:
    """Install and configure component - reusable across tests."""
    try:
        __install_using_extension(node, log)
    except Exception:
        log.info("Extension install failed, trying SDK")
        __install_using_sdk(node, log, log_path)

def _verify_component_loaded(node: Node) -> bool:
    """Check if component is loaded - reusable validation."""
    return component.is_loaded()

def _cleanup_component(node: Node, log: Logger) -> None:
    """Clean up component resources - reusable cleanup."""
    pass
```

### Double Underscore (__) - Implementation Detail

Functions that are implementation details, only called by other helper functions:

```python
def __install_using_extension(node: Node, log: Logger) -> None:
    """Internal: Install via extension (called only by _install_component)."""
    pass

def __install_using_sdk(node: Node, log: Logger, log_path: Path) -> None:
    """Internal: Install via SDK (called only by _install_component)."""
    pass

def __cleanup_temporary_files(node: Node, file_list: List[str]) -> None:
    """Internal: Remove temp files (called only by _cleanup_component)."""
    pass
```

### No Underscore - Public API (Rare)

Functions called directly by test methods (rare for helper functions):

```python
def verify_feature(node: Node, log: Logger, use_method_a: bool = True) -> None:
    """Public entry point - called directly by test methods."""
    _prepare_environment(node)
    if use_method_a:
        _verify_by_method_a(node, log)
    else:
        _verify_by_method_b(node, log)
```

**Rule of thumb:**
- If multiple test cases call it directly: single underscore `_`
- If only helper functions call it: double underscore `__`
- If test methods call it directly: no underscore (but rare for helpers)

---

## Advanced Patterns

### Working Path with Disk Space Requirements

For tests that download or install large components:

```python
def test_large_installation(self, node: Node, log: Logger) -> None:
    """Test that requires downloading and installing large components."""
    
    # Step 1: Calculate space needed (in GB)
    required_space_gb = 20
    
    # Step 2: Get working path with enough space
    work_path = node.get_working_path_with_required_space(required_space_gb)
    log.debug(f"Using working path: {work_path}")
    
    # Step 3: Clean package cache proactively
    if isinstance(node.os, Linux):
        node.os.clean_package_cache()
    
    # Step 4: Use work_path for all downloads
    download_path = f"{work_path}/downloads"
    node.tools[Mkdir].create_directory(download_path)
    
    wget = node.tools[Wget]
    wget.get(url=large_file_url, file_path=download_path, filename="package.tar.gz")
```

### Output Parsing with Regex Patterns

Use compiled regex patterns with named groups:

```python
import re
from lisa.util import get_matched_str

class MyTestSuite(TestSuite):
    # Define patterns at class level with named groups
    _version_pattern = re.compile(r"^Version: (?P<version>[\d.]+)", re.M)
    _status_pattern = re.compile(r"Status: (?P<status>\w+)", re.M)
    _count_pattern = re.compile(r"^gpu count: (?P<count>\d+)", re.M)
    
    def my_test(self, node: Node, log: Logger) -> None:
        result = node.execute("my_command --version")
        
        # Extract value using named group
        version = get_matched_str(result.stdout, self._version_pattern)
        
        # Validate extraction succeeded
        assert_that(version).described_as(
            f"version not found in output: {result.stdout}"
        ).is_not_empty()
        
        assert_that(version).is_equal_to("1.2.3")
```

### Class-Level Constants and Patterns

Define reusable constants, timeouts, and regex patterns at class level:

```python
import re

class MyTestSuite(TestSuite):
    # Public constants (no underscore)
    TIMEOUT = 2000
    MAX_RETRIES = 3
    DEFAULT_WAIT_SECONDS = 30
    
    # Private patterns (underscore prefix)
    _success_pattern = re.compile(r"^Status: (?P<status>\w+)", re.M)
    _error_pattern = re.compile(r"ERROR: (?P<message>.*)", re.M)
    
    @TestCaseMetadata(
        description="Test with class timeout",
        timeout=TIMEOUT,
        priority=1,
    )
    def my_test(self, node: Node, log: Logger) -> None:
        for attempt in range(self.MAX_RETRIES):
            result = node.execute("command")
            if result.exit_code == 0:
                break
            time.sleep(self.DEFAULT_WAIT_SECONDS)
        
        status = get_matched_str(result.stdout, self._success_pattern)
        assert_that(status).is_equal_to("OK")
```

### Try-Except-Fallback with Cleanup

```python
def test_with_fallback(self, node: Node, log: Logger) -> None:
    """Test with fallback method and guaranteed cleanup."""
    try:
        # Try primary method
        _install_via_extension(node, log)
    except Exception as e:
        log.info(f"Primary method failed: {e}, trying fallback")
        try:
            # Fallback to alternative
            _install_via_sdk(node, log)
        except Exception:
            node.mark_dirty()
            raise
    finally:
        # Guaranteed cleanup regardless of success/failure
        _cleanup_temp_files(node, log)
```

### Retry Logic for Known Errors

```python
from retry import retry

@retry(exceptions=LisaException, tries=5, delay=60)
def _provision_with_retry(node: Node, log: Logger) -> None:
    """Provision with retry on known transient failures."""
    try:
        provision_component(node)
    except LisaException as e:
        if "known_transient_error" in str(e):
            log.info("Encountered known transient error, retrying...")
            raise  # Will trigger retry
        else:
            # Unknown error, don't retry
            raise
```

---

## Multi-Node Patterns

### Multi-Node Requirements

```python
from lisa import Environment

@TestCaseMetadata(
    description="Network connectivity between multiple nodes",
    priority=2,
    requirement=simple_requirement(
        min_count=2,
        network_interface=Sriov(),
    ),
)
def verify_multi_node_network(self, environment: Environment, log: Logger) -> None:
    """Test requiring multiple nodes."""
    vm_nics = _discover_network_interfaces(environment)
    
    nodes = environment.nodes.list()
    source_node = nodes[0]
    dest_node = nodes[1]
    
    _test_connectivity(source_node, dest_node, log)
```

### Environment-Level Helpers

```python
def _configure_all_nodes(environment: Environment, log: Logger) -> None:
    """Configure all nodes in the environment."""
    for node in environment.nodes.list():
        node.tools[Firewall].stop()
        node.features[NetworkInterface].switch_sriov(
            enable=True, wait=True, reset_connections=True
        )
        log.debug(f"Configured node {node.name}")

def _test_connectivity(source: Node, dest: Node, log: Logger) -> None:
    """Test network connectivity between two nodes."""
    dest_ip = dest.nics.get_primary_nic().ip_addr
    
    ping = source.tools[Ping]
    result = ping.ping(dest_ip, count=10)
    
    assert_that(result.success_count).described_as(
        f"Ping from {source.name} to {dest.name} failed"
    ).is_equal_to(10)
```

### Retry with Multi-Node Discovery

```python
@retry(exceptions=AssertionError, tries=30, delay=2)
def _discover_network_interfaces(environment: Environment) -> List[VmNics]:
    """
    Discover network interfaces with retry.
    May take 30-60s for all interfaces to be ready.
    """
    vm_nics: List[VmNics] = []
    for node in environment.nodes.list():
        default_nic = node.nics.get_nic_by_index(0)
        vm_nics.append(VmNics(node, default_nic))
    
    assert_that(vm_nics).described_as(
        "All nodes must have network interface"
    ).is_not_empty()
    
    return vm_nics
```

---

## Alternative Signatures

### Option 1: Direct Parameters (Most Common)

```python
def verify_basic_functionality(
    self, node: Node, log: Logger, log_path: Path
) -> None:
    """Direct access to node, logger, and log path."""
    log.debug("Starting test")
    node.execute("echo 'test'")
```

### Option 2: With Environment (For Platform Checks)

```python
def verify_platform_specific_feature(
    self, environment: Environment, node: Node, log: Logger
) -> None:
    """Access to environment for platform-specific operations."""
    if isinstance(environment.platform, AzurePlatform):
        node_capability = node.capability.get_extended_runbook(
            AzureNodeSchema, AZURE
        )
        vm_size = node_capability.vm_size
        log.debug(f"Testing on Azure VM size: {vm_size}")
```

### Option 3: With TestResult (For Parameterized Tests)

```python
def verify_configurable_test(self, result: TestResult) -> None:
    """Access test result for runtime data and environment."""
    environment = result.environment
    assert environment, "fail to get environment from testresult"
    
    node = cast(RemoteNode, environment.nodes[0])
    log = result.get_logger()
    
    # Test implementation
    pass
```

---

## Anti-Patterns to Avoid

### ❌ Forgetting node.mark_dirty() in Exception Handlers

```python
# WRONG - Node state changed but not marked dirty
try:
    node.execute("reboot")
except Exception:
    raise  # Missing node.mark_dirty()

# RIGHT - Always mark dirty on state-changing failures
try:
    node.execute("reboot")
except Exception:
    node.mark_dirty()
    raise
```

### ❌ Public Functions Without Underscore Prefix

```python
# WRONG - Internal helper looks public
def prepare_environment(node: Node) -> None:
    pass

# RIGHT - Private helpers use underscore
def _prepare_environment(node: Node) -> None:
    pass
```

### ❌ Proactive Disk Space Checks

```python
# WRONG - Fails test before trying
def test_feature(node, log):
    if disk_space < threshold:
        raise SkippedException("Low disk space")
    perform_operation()

# RIGHT - Check only on failure
def test_feature(node, log):
    try:
        perform_operation()
    except Exception:
        check_disk_space(node, log)  # Diagnostic info
        raise
```

### ❌ No Cleanup Timeout Protection

```python
# WRONG - Can hang indefinitely
def after_case(self, log, **kwargs):
    environment = kwargs.pop("environment")
    cleanup_env(environment)  # No timeout!

# RIGHT - Timeout protection
def after_case(self, log, **kwargs):
    environment = kwargs.pop("environment")
    try:
        func_timeout(timeout=300, func=cleanup_env, args=(environment,))
    except Exception as e:
        log.info(f"Cleanup failed: {e}")
        for node in environment.nodes.list():
            if isinstance(node, RemoteNode):
                node.mark_dirty()
```

### ❌ Generic Log Collection on Failures

```python
# WRONG - Generic dmesg only
except Exception:
    dmesg.get_output(force_run=True)
    raise

# RIGHT - Extension-specific logs
except Exception:
    collect_extension_specific_logs(node, log)
    check_disk_space(node, log)
    node.mark_dirty()
    raise
```
