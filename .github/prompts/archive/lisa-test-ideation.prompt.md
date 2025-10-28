---
mode: 'agent'
description: 'LISA test ideation and requirements gathering through structured conversation.'
tools: ['search', 'search/codebase']
---

# LISA Test Ideation & Requirements

Systematically gather requirements and design a complete LISA test specification through guided conversation.

---

## Purpose

Transform your testing idea into a detailed, actionable test design specification ready for code generation.

---

## Process

Four-phase structured conversation:

1. **Understand Intent** - Clarify what you're testing and why
2. **Define Requirements** - Specify platforms, resources, and dependencies
3. **Analyze Infrastructure** - Search codebase for reusable components
4. **Propose Design** - Deliver complete test specification

---

## Phase 1: Understanding Test Intent

### Questions I'll Ask

**Purpose & Scope:**
- What functionality/feature are you testing?
- What specific behavior should be validated?
- Is this functional, performance, stress, regression, or compatibility testing?
- What would constitute test success?

**Target & Coverage:**
- Testing a specific tool/command or broader system capability?
- Linux kernel behavior, Azure platform, or application-level features?
- Known edge cases or failure modes to cover?

### Response Template

```markdown
## Test Intent Summary

**Test Goal:** [one-sentence summary]
**Test Type:** [functional/performance/stress/regression/compatibility]
**Success Criteria:** [what makes the test pass]
**Validation Approach:** [how we verify success]

**Is this correct?** (Yes/No/Modify)
```

---

## Phase 2: Defining Technical Requirements

### Platform Requirements

**Operating Systems:**
- Which distributions? (Ubuntu, RHEL, Debian, SUSE, Oracle Linux, Azure Linux)
- Specific versions? (e.g., Ubuntu 22.04+, RHEL 8+)
- Any exclusions? Why?

**Architecture & Generation:**
- x86_64, ARM64, or both?
- Gen1, Gen2, or both?
- Architecture-specific dependencies?

### Hardware & Resources

**Compute:**
- Single VM or multi-node? (If multi-node: count and roles)
- Minimum CPU cores? Special features (AVX, nested virtualization)?
- Minimum memory?

**Storage & Network:**
- Disk requirements? (size/count/type: NVMe, premium SSD, ephemeral)
- Network type? (standard/accelerated/SR-IOV/multiple NICs)

**Special Hardware:**
- GPU required? Which types?
- InfiniBand or other specialized hardware?

### Software Dependencies

**Native Tools & Packages:**
- Required commands/packages (e.g., `lscpu`, `iperf3`, `nvme-cli`)
- Pre-installed or need installation?
- Package names across different distros?

**LISA Components:**
- **Tools:** Which from `lisa/tools/`? Need new tools?
- **Features:** Which from `lisa/features/`? (e.g., `Gpu`, `Nvme`, `Sriov`, `StartStop`, `Resize`)

### Response Template

```markdown
## Technical Requirements Specification

**Platform Support:**
- **OS:** [Ubuntu 22.04+, RHEL 8+, ...]
- **Architecture:** [x86_64, ARM64, or both]
- **VM Generation:** [Gen1, Gen2, or both]
- **Excluded:** [distros/versions] - **Reason:** [why]

**Hardware Requirements:**
- **Nodes:** [single/multi - count and roles]
- **CPU:** [minimum cores, special features]
- **Memory:** [minimum GB]
- **Storage:** [disk specs if relevant]
- **Network:** [standard/accelerated/SR-IOV]
- **Special:** [GPU/InfiniBand/other]

**Software Dependencies:**
- **Native Tools:** [required commands]
- **Package Names:** [across distros if different]
- **LISA Tools:** [existing OR new tools needed]
- **LISA Features:** [for capability checks]

**Test Metadata:**
- **Priority:** [0=critical, 1=high, 2=medium, 3=low]
- **Test Area:** [core/network/storage/gpu/performance/...]

**Does this capture your requirements?** (Yes/No/Modify)
```

---

## Phase 3: Infrastructure Analysis

### What I'll Search

1. **Similar Tests** - Search `microsoft/testsuites/` for tests with similar functionality
2. **LISA Tools** - Find available tools in `lisa/tools/` and usage examples from tests
3. **LISA Features** - Identify platform capability checks in `lisa/features/`
4. **Test Organization** - Examine test suite structure in target area

**Search Strategy:**
```
"Find tests in microsoft/testsuites/[area]/ that test [similar functionality]"
"Show examples of [FeatureName] usage in test code"
"Search for tests using [ToolName] in microsoft/testsuites/"
```

### Response Template

```markdown
## Infrastructure Analysis

**Similar Tests Found:**
- [List tests found via search with relevant patterns]

**Recommendation:** [Extend existing OR create new file] - **Reason:** [why]

**LISA Tools Available:**
- [Tools found in lisa/tools/ relevant to this test]

**Tools Needed:** [New tools required OR "None - use existing"]

**LISA Features Available:**
- [Features from lisa/features/ relevant to this test]

**Reusable Patterns:**
- [Patterns from lisa-patterns.md that apply to this test]

**Summary:**
- **Code Reuse:** [High/Medium/Low based on search results]
- **New Code Needed:** [what must be written]
- **Complexity:** [Simple/Moderate/Complex]

**Ready to proceed to design?** (Yes/No)
```

---

## Phase 4: Design Proposal

### Complete Specification Template

```markdown
## LISA Test Design Specification

### Test Metadata
- **File:** `microsoft/testsuites/[area]/[filename].py`
- **Test Suite:** `[ClassName]TestSuite`
- **Test Method:** `test_[descriptive_name]`
- **Priority:** [0/1/2/3]
- **Area:** [core/network/storage/gpu/performance/...]
- **Category:** [functional/performance/stress/...]

### Test Description
[2-3 sentence description of validation purpose and importance]

### Platform Requirements

**Supported Platforms:**
```python
simple_requirement(
    supported_platform_type=[AZURE],
    supported_os=[Ubuntu, RedHat, ...],
    min_os_version={Ubuntu: "22.04", RedHat: "8.0"},
    supported_features=[FeatureName1, FeatureName2],
)
```

**Excluded OS & Rationale:**
- [Distro/Version] - [Technical reason for exclusion]

### Test Signature
```python
def test_[name](
    self,
    node: Node,  # OR environment: Environment for multi-node
    log: Logger,
) -> None:
```

**Signature Rationale:** [Why node vs environment]

### Test Implementation Flow

**Setup (if needed):**
- [Setup steps]

**Validation Logic:**
```
Step 1: [Action]
  - Command: [specific command]
  - Expected: [result]
  
Step 2: [Action]
  - Command: [specific command]
  - Expected: [result]

Step 3: [Assertion]
  - Verify: [what we check]
  - Failure message: [user-facing error]
```

**Teardown (if needed):**
- [Cleanup steps]

### Components Used

**LISA Tools:**
- `lisa.tools.[ToolName]` - [purpose]

**LISA Features:**
- `lisa.features.[FeatureName]` - [purpose]

**Helper Functions:**
- `[helper_name]` - [purpose] - [NEW/EXISTING]

### Pattern Compliance

**Applied Patterns:**
- **Node Cleanup:** [Where `node.mark_dirty()` called and why]
- **Feature Support:** [How feature availability verified - Pattern #2]
- **[Other Patterns]:** [Application details from lisa-patterns.md or codebase examples]

### Code Organization

**Recommendation:** [Extend existing file OR Create new file]
- **File:** `microsoft/testsuites/[area]/[file].py`
- **Reason:** [Justification]

### Success Criteria

**Test Passes:**
1. [Success condition 1]
2. [Success condition 2]

**Test Skips:**
1. [Skip condition - e.g., feature unavailable]

**Test Fails:**
1. [Failure condition 1]
2. [Failure condition 2]

### Example Output

**Success Case (Ubuntu 22.04):**
```
[Expected log output]
```

**Skip Case (if applicable):**
```
SkippedException: [Reason]
```
```

---

## Design Approval

**What would you like to do?**

**A. Approve & Generate Code**
- Transfer specification to code generation workflow
- Create production-ready Python files

**B. Modify Design**
- Tell me what sections need changes
- I'll update and re-present

**C. Stop Here**
- Keep the specification for later use

**Choose A, B, or C.**

---

## Reference Materials

- **[LISA Patterns](../references/lisa-patterns.md)** - Implementation patterns
- **[Guidelines](../../docs/write_test/guidelines.rst)** - Coding standards
- **[Test Writing](../../docs/write_test/write_case.rst)** - How to write tests
- **[Dev Setup](../../docs/write_test/dev_setup.rst)** - Development environment

---

**Next Step:** [Code Generation](./lisa-test-codegen.prompt.md) (after approval)  
**Main Menu:** [LISA Test Generator](./write-lisa-test.prompt.md)
