# LISA Decision Trees Reference

**Reusable decision trees for common LISA testing scenarios. Referenced by prompt files.**

---

## Table of Contents

1. [Test Method Signature Selection](#test-method-signature-selection)
2. [OS Requirements Decision](#os-requirements-decision)
3. [Feature vs Tool Decision](#feature-vs-tool-decision)
4. [Error Handling Strategy](#error-handling-strategy)

---

## Test Method Signature Selection

```
What parameters do I need?
├─ Single node, basic functionality
│   └─ Signature: def test_name(self, node: Node, log: Logger) -> None:
│       └─ Use when: Most common case, single VM test
├─ Need logging to file
│   └─ Signature: def test_name(self, node: Node, log: Logger, log_path: Path) -> None:
│       └─ Use when: Writing custom logs, artifacts
├─ Multi-node test
│   └─ Signature: def test_name(self, environment: Environment, log: Logger) -> None:
│       └─ Requirement: min_count=2 or higher
│       └─ Access nodes: environment.nodes.list()
├─ Need both environment and specific node
│   └─ Signature: def test_name(self, environment: Environment, node: Node, log: Logger) -> None:
│       └─ Use when: Need environment context but operate on one node
└─ Runtime test parameters
    └─ Signature: def test_name(self, result: TestResult) -> None:
        └─ Use when: Need test case metadata or runtime config

Cross-reference with Pattern #4: before_case() for suite-level setup
```

## OS Requirements Decision

```
What determines OS compatibility?
├─ Command availability (e.g., lspci, dmesg, ethtool)
│   └─ Check: Which distros have command in PATH by default?
│   └─ Include: Distros with command natively available
│   └─ Exclude: Distros where command not in base install
├─ Package availability (e.g., sysbench, iperf3)
│   └─ Check: Which distros have package in official repos?
│   └─ Include: Distros with package in official repos
│   └─ Exclude: Distros where package not available
├─ Hardware feature (e.g., SR-IOV, GPU)
│   └─ Use: supported_features in requirement
│   └─ Framework handles OS filtering automatically
├─ Distribution-specific (e.g., systemd, SELinux config)
│   └─ Include: Only distros with that specific implementation
│   └─ Exclude: All others explicitly
└─ Universal Linux functionality
    └─ Include: All Linux distros (Posix)
    └─ Exclude: Only if known incompatibility

Cross-reference with Pattern #2: Always add feature.is_supported() check
```

## Feature vs Tool Decision

```
What am I testing?
├─ Platform capability (GPU, SR-IOV, Hibernate, Resize)
│   └─ Use: node.features[FeatureName]
│       └─ Benefit: Automatic platform compatibility checks
│       └─ Pattern #2: MUST check feature.is_supported()
├─ Command-line operation (lspci, dmesg, ip)
│   └─ Use: node.tools[ToolName]
│       └─ Benefit: Parsed output, error handling
├─ Simple command with no parsing needed
│   └─ Use: node.execute("command")
│       └─ When: One-off commands, not worth creating tool
└─ Complex multi-step operation
    └─ Create: Helper function that coordinates tools/features
        └─ Follow Pattern #3 naming conventions
```

## Error Handling Strategy

```
What happens on failure?
├─ Node state changed (kernel crash, config modified, drivers unloaded)
│   └─ Action: node.mark_dirty() in exception handler (Pattern #1)
│       └─ Reason: Prevent contamination of subsequent tests
├─ Feature not supported on this platform
│   └─ Action: raise SkippedException() after feature.is_supported() (Pattern #2)
│       └─ Reason: Graceful skip, not a failure
├─ Transient failure (network discovery, device enumeration)
│   └─ Action: Use @retry decorator on helper (Pattern #6)
│       └─ Reason: Handle timing-dependent operations
├─ Cleanup might hang
│   └─ Action: Wrap in func_timeout() (Pattern #7)
│       └─ Reason: Prevent indefinite hangs
└─ Normal test assertion failure
    └─ Action: Let exception propagate naturally
        └─ Reason: Framework handles test failure reporting
```

## Helper Function Organization

```
When should I create a helper function?
├─ Code used by multiple test methods
│   └─ Create: Module-level helper with single _ prefix
│       └─ Example: _install_component(node, log, path)
│       └─ Pattern #3: Single _ = module-private (reusable)
├─ Complex logic that obscures test intent
│   └─ Create: Helper that encapsulates complexity
│       └─ Benefit: Test method reads like documentation
├─ Implementation detail of another helper
│   └─ Create: Private helper with double __ prefix
│       └─ Pattern #3: Double __ = implementation detail only
├─ Used only once, simple operation
│   └─ Action: Inline in test method
│       └─ Reason: Avoid unnecessary indirection
└─ Suite-level setup/teardown
    └─ Use: before_case() / after_case() hooks
        └─ Pattern #4: Lifecycle hooks for all tests
```

## Test Organization Strategy

```
Where should this test go?
├─ Functionality matches existing suite
│   └─ Action: Add method to existing TestSuite class
│       └─ Benefit: Leverage existing helpers and patterns
│       └─ Check: Pattern #4 hooks compatible?
├─ New feature area with multiple test cases
│   └─ Action: Create new test suite file
│       └─ Structure: microsoft/testsuites/[area]/test_[name].py
│       └─ Include: TestSuiteMetadata with area/category
├─ Single test case, doesn't fit existing suites
│   └─ Action: Add to most closely related suite
│       └─ Or: Create new suite if likely to expand
└─ Example/demonstration test
    └─ Location: lisa/examples/testsuites/
        └─ Not: microsoft/ (production tests only)
```

## Requirement Complexity

```
How complex is my test requirement?
├─ Just OS filtering
│   └─ Use: simple_requirement(supported_os=[Ubuntu, Redhat])
├─ Hardware requirements (CPU, memory, disk)
│   └─ Use: simple_requirement(min_core_count=4, min_memory_mb=8192)
├─ Feature requirements (GPU, SR-IOV)
│   └─ Use: simple_requirement(supported_features=[Gpu()])
│       └─ Still need Pattern #2 check in test!
├─ Node count requirements
│   └─ Use: simple_requirement(min_count=2)
│       └─ Signature must include environment parameter
└─ Complex custom requirements
    └─ Use: Requirement subclass with search_space
        └─ Example: GPU + specific OS + memory combination
```

---

**Usage Notes:**

- These decision trees are **referenced by prompt files** to reduce duplication
- Each tree links to **specific patterns** in [lisa-patterns.md](./lisa-patterns.md)
- **Update once, applies everywhere** - single source of truth
- AI should **load relevant tree** based on user's question

**Related References:**
- [LISA Patterns Library](./lisa-patterns.md)
- [LISA Commands Reference](./lisa-commands.md)
