---
mode: 'agent'
description: 'LISA test ideation and requirements gathering - structured conversation to collect all information needed for test generation.'
tools: ['search', 'search/codebase']
---

# LISA Test Ideation & Requirements Gathering

**Purpose:** Systematically gather requirements and analyze infrastructure to design a viable LISA test.

**Output:** Complete specification ready for code generation workflow.

---

## Workflow Overview

This is a **structured 4-phase conversation** that ensures we collect everything needed to generate production-ready test code:

1. **Understand Intent** - What are you trying to test?
2. **Define Requirements** - Platform, resources, constraints
3. **Analyze Infrastructure** - Search existing code for reuse opportunities
4. **Propose Design** - Complete test specification ready for codegen

**Goal:** By the end, you'll have a detailed design that can be handed to the code generation workflow.

---

## Phase 1: Understanding Test Intent

**I will ask clarifying questions to understand your goals.**

### Questions to Explore

**A. Test Purpose**
- What functionality/feature are you testing?
- What specific behavior should be validated?
- Is this functional validation, performance measurement, or regression coverage?
- What would constitute test success?

**B. Target Scope**
- Should this test a specific tool/command or a broader system capability?
- Is this testing Linux kernel behavior, Azure platform functionality, or application-level features?
- Are there known edge cases or failure modes to cover?

**C. Test Category**
- Functional (does it work?)
- Performance (how fast/efficient?)
- Stress (does it survive load?)
- Regression (prevent past bugs?)
- Compatibility (works across OS/hardware?)

### My Response Format

```
## Test Intent Summary

Based on your description, here's what I understand:

**Test Goal:** [one-sentence summary]
**Test Type:** [functional/performance/stress/regression]
**Success Criteria:** [what makes the test pass]
**Validation Approach:** [how we verify success]

**Is this correct?** (Yes/No/Modify)

If you want to modify, tell me what to change.
```

---

## Phase 2: Defining Technical Requirements

**I will help you specify platforms, resources, and constraints.**

### A. Platform Requirements

**Questions I'll ask:**

1. **Operating Systems:**
   - Which Linux distributions? (Ubuntu, RHEL, Debian, SUSE, Oracle Linux, Azure Linux?)
   - Specific versions? (e.g., Ubuntu 22.04+, RHEL 8+)
   - Should we exclude any distros? Why?

2. **Architecture:**
   - x86_64 only, ARM64 only, or both?
   - Does the feature/tool have architecture dependencies?

3. **VM Generation:**
   - Gen1, Gen2, or both?
   - Any generation-specific requirements?

### B. Hardware & Resources

**Questions I'll ask:**

1. **Node Count:**
   - Single VM or multiple VMs?
   - If multi-node, how many? What roles? (e.g., client/server, primary/secondary)

2. **CPU Requirements:**
   - Minimum core count?
   - Specific CPU features needed? (AVX, nested virtualization, etc.)

3. **Memory Requirements:**
   - Minimum RAM?
   - Any specific memory configurations?

4. **Storage Requirements:**
   - Disk size/count/type?
   - Need for NVME, premium SSD, ephemeral disks?

5. **Network Requirements:**
   - Standard NIC sufficient?
   - Need accelerated networking?
   - SR-IOV required?
   - Multiple NICs?

6. **Special Hardware:**
   - GPU required? If yes, which GPU types?
   - InfiniBand needed?
   - Other specialized hardware?

### C. Software Dependencies

**Questions I'll ask:**

1. **Native Tools/Packages:**
   - Which commands/packages must be available? (e.g., `lscpu`, `iperf3`, `nvme-cli`)
   - Are they pre-installed on target OS, or do we need to install them?
   - Package names across different distros?

2. **LISA Tools:**
   - Do we need tools from `lisa/tools/`?
   - Should we create new LISA tools or use existing ones?

3. **LISA Features:**
   - Which platform capabilities? (from `lisa/features/`)
   - Examples: `Gpu`, `Nvme`, `Sriov`, `NetworkInterface`, `SerialConsole`, `StartStop`, `Resize`

### My Response Format

```
## Technical Requirements Specification

**Platform Support:**
- **OS:** [Ubuntu 22.04+, RHEL 8+, ...]
- **Architecture:** [x86_64, ARM64, or both]
- **VM Generation:** [Gen1, Gen2, or both]
- **Excluded:** [distros/versions to skip] - **Reason:** [why]

**Hardware Requirements:**
- **Nodes:** [single/multi - count and roles]
- **CPU:** [minimum cores, special features if any]
- **Memory:** [minimum GB]
- **Storage:** [disk specs if relevant]
- **Network:** [standard/accelerated/SR-IOV]
- **Special:** [GPU/InfiniBand/other]

**Software Dependencies:**
- **Native Tools:** [commands that must exist]
- **Package Names:** [across distros if different]
- **LISA Tools:** [existing tools to use OR new tools needed]
- **LISA Features:** [features for capability checks]

**Test Metadata:**
- **Priority:** [0=critical, 1=high, 2=medium, 3=low]
- **Test Area:** [core/network/storage/gpu/performance/...]

---

**Does this capture your requirements?** (Yes/No/Modify)
```

---

## Phase 3: Infrastructure Analysis

**I will search the codebase to find reusable components and patterns.**

### What I'll Search For

1. **Similar Tests**
   - Existing tests in `microsoft/testsuites/` that test similar functionality
   - Test patterns and structures we can follow
   - Test organization decisions (which file to extend vs create new)

2. **LISA Tools** (`lisa/tools/`)
   - Existing tools that match your requirements
   - Examples of tool usage
   - Gaps where new tools might be needed

3. **LISA Features** (`lisa/features/`)
   - Platform capability checks we can reuse
   - Feature support patterns
   - Feature requirement specifications

4. **Test Utilities & Helpers**
   - Existing helper functions we can leverage
   - Common test patterns in use
   - Before/after test setup patterns

### My Response Format

```
## Infrastructure Analysis

**1. Similar Tests Found:**
- `microsoft/testsuites/[area]/[file].py` - [what it tests, what we can reuse]
- [additional similar tests]

**Recommendation:** [Extend existing file OR create new file] - **Reason:** [why]

**2. LISA Tools Available:**
- `lisa.tools.[ToolName]` - [capability, usage example]
- [additional relevant tools]

**Tools Needed:** [List any new tools required, or "None - use existing tools"]

**3. LISA Features Available:**
- `lisa.features.[FeatureName]` - [what it checks, how to use]
- [additional relevant features]

**Feature Support Pattern:** [How to check feature availability before use]

**4. Reusable Patterns:**
- Pattern N: [pattern name] - [how it applies to your test]
- [other applicable patterns from lisa-patterns.md]

**5. Helper Functions:**
- [Existing helpers found] - [what they do]
- [New helpers needed] OR "None needed"

**Infrastructure Summary:**
- **Code Reuse Score:** [High/Medium/Low]
- **New Code Needed:** [What needs to be written]
- **Complexity:** [Simple/Moderate/Complex]

---

**Ready to proceed to design?** (Yes/No)
```

---

## Phase 4: Design Proposal

**I will present a complete, actionable test design specification.**

### Design Document Format

```
## LISA Test Design Specification

### Test Metadata
- **File:** `microsoft/testsuites/[area]/[filename].py`
- **Test Suite Class:** `[ClassName]TestSuite`
- **Test Method:** `test_[descriptive_name]`
- **Priority:** [0/1/2/3]
- **Area:** [core/network/storage/gpu/performance/...]
- **Category:** [functional/performance/stress/...]

### Test Description
[2-3 sentence description of what this test validates and why it matters]

### Platform Requirements

**Supported:**
```python
simple_requirement(
    supported_platform_type=[AZURE],
    supported_os=[Ubuntu, RedHat, ...],
    min_os_version={Ubuntu: "22.04", RedHat: "8.0"},
    supported_features=[FeatureName1, FeatureName2],
)
```

**Excluded OS & Rationale:**
- [Distro/Version] - [Specific technical reason for exclusion]

### Test Signature
```python
def test_[name](
    self,
    node: Node,  # OR environment: Environment for multi-node
    log: Logger,
) -> None:
```

**Why this signature?** [Explanation of node vs environment choice]

### Test Implementation Flow

**1. Setup (if needed)**
- [Setup step 1]
- [Setup step 2]

**2. Validation Logic**
```
Step 1: [What happens]
  - Command/operation: [specific command]
  - Expected result: [what should happen]
  
Step 2: [What happens]
  - Command/operation: [specific command]
  - Expected result: [what should happen]

Step 3: [Validation]
  - Assertion: [what we verify]
  - Error message: [what user sees on failure]
```

**3. Teardown (if needed)**
- [Cleanup step 1]
- [Cleanup step 2]

### Components Used

**LISA Tools:**
- `lisa.tools.[ToolName]` - [purpose in test]

**LISA Features:**
- `lisa.features.[FeatureName]` - [purpose in test]

**Helper Functions:**
- `[helper_name]` - [what it does] - [NEW or EXISTING]

### Pattern Compliance

**Node Cleanup Pattern:**
- [Where node.mark_dirty() is called and why]

**Feature Support Pattern:**
- [How we verify feature availability before use]

**Other Applicable Patterns:**
- [How they're applied in this test]

### Code Organization

**Option A: Extend Existing File** ✓ [OR] ❌
- File: `microsoft/testsuites/[area]/[existing_file].py`
- Reason: [Why this fits with existing tests]

**Option B: Create New File** ✓ [OR] ❌
- File: `microsoft/testsuites/[area]/[new_file].py`
- Reason: [Why new file is warranted]

**Recommendation:** [A or B] - [Reasoning]

### Success Criteria

**Test Passes When:**
1. [Success condition 1]
2. [Success condition 2]

**Test Skips When:**
1. [Skip condition - e.g., feature not supported]
2. [Skip condition - e.g., package unavailable]

**Test Fails When:**
1. [Failure condition 1]
2. [Failure condition 2]

### Example Test Run

**On Ubuntu 22.04 (Success):**
```
[Expected log output showing successful run]
```

**On Excluded OS (Skipped - if applicable):**
```
SkippedException: [Reason for skip]
```

---

## Design Approval & Next Steps

**What would you like to do?**

**A. Approve & Continue to Code Generation**
- I'll hand this specification to the code generation workflow
- Production-ready Python code will be generated
- Files created automatically

**B. Modify Design**
- Tell me which sections need changes
- I'll update and re-present

**C. Stop Here (Design Complete)**
- You have the complete specification
- Implement manually or come back later for codegen

**Choose A, B, or C.**

If you choose **A**, I'll say:
```
✅ Design approved! Switching to code generation workflow...

[Transfer to lisa-test-codegen.prompt.md with this design specification]
```

If you choose **B**, tell me what to modify:
```
Example: "Change the OS requirements - remove Debian"
Example: "Modify Step 2 to use different command"
Example: "Switch to multi-node test instead"
```

If you choose **C**, I'll say:
```
✅ Design complete! 

You now have a complete test specification. Use this when you're ready to:
1. Generate code manually
2. Return to invoke code generation workflow
3. Share with team for review

Specification saved above ⬆️
```

---

## Reference Materials

**Loaded on-demand during workflow:**

- **[LISA Patterns Library](../references/lisa-patterns.md)** - 11 core patterns
- **Official Documentation:**
  - `docs/write_test/dev_setup.rst` - Development setup
  - `docs/write_test/guidelines.rst` - Coding standards
  - `docs/write_test/write_case.rst` - Test case writing guide

---

## Tips for Best Results

**Be Specific:**
- "Test GPU persistence across reboot" is better than "test GPU"
- "Measure iperf3 latency between 2 VMs" is better than "test network"

**Provide Context:**
- Mention if you've seen similar tests
- Share known limitations or constraints
- Indicate if this is for a specific bug or feature request

**Ask Questions:**
- Not sure about OS support? Ask me to research
- Unsure about tool availability? I'll search the codebase
- Need examples? I'll find similar tests

**Iterate:**
- Design is flexible - we can refine as we go
- No need to have all answers upfront
- I'll guide you through unknowns

---

**Current Workflow:** Ideation & Requirements Gathering  
**Next Workflow:** [Code Generation](./lisa-test-codegen.prompt.md) (if you approve design)  
**Router:** [Main Menu](./write-lisa-test.prompt.md)
