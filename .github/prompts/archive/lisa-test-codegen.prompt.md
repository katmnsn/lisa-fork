---
mode: 'agent'
description: 'Generate production-ready LISA test code with iterative refinement through natural conversation.'
tools: ['edit/editFiles', 'problems', 'search/codebase']
---

# LISA Test Code Generation

Generate and iteratively refine production-ready Python test code for the LISA testing framework.

---

## Purpose

Create complete LISA test implementations following established patterns, with support for continuous refinement through natural conversation.

---

## Input Required

**From Design Specification (if coming from ideation):**
- Test purpose and functionality
- Platform/OS requirements
- Tool and feature dependencies
- Implementation strategy

**From Direct Request:**
- What functionality to test?
- Which platforms/OS?
- Single-node or multi-node?
- Any specific LISA tools or features needed?

---

## Process

1. **Clarify requirements** - Confirm test scope, platforms, and dependencies
2. **Propose implementation** - Present file structure, components, and patterns to apply
3. **Generate code** - Create complete, production-ready test files with proper imports
4. **Verify quality** - Check for errors using problems tool
5. **Iterate freely** - Refine based on your feedback until satisfied

---

## Output Deliverables

### Implementation Plan Template

```markdown
## Implementation Plan

**Test Overview:**
- Purpose: [What we're testing]
- Platforms: [OS support with reasoning]
- Type: [Single-node/Multi-node]

**File Structure:**
- Location: `microsoft/testsuites/[area]/[file].py`
- Method: `test_[name]`
- Strategy: [New file OR extend existing]

**Components:**
- LISA Tools: [From lisa/tools/]
- LISA Features: [From lisa/features/]
- Helpers: [New OR reuse existing]

**Patterns Applied:**
- [Pattern 1 from LISA Patterns Library]
- [Pattern 2 from LISA Patterns Library]

**Notes:** [Edge cases, special considerations]
```

### Code Generation Summary

```markdown
## ✅ Code Generated

**Created:**
- `microsoft/testsuites/[area]/[file].py` - [Description]
  - Method: `test_[name]`
  - Platforms: [OS list]
  - Patterns: [Applied patterns]

**Modified:**
- [Any updated imports or extensions]

**Summary:** [Implementation details]
```

---

## Code Quality Standards

All generated code follows:
- **[LISA Guidelines](../../docs/write_test/guidelines.rst)** - Official coding standards
- **Type hints** on all functions
- **Error handling** with `node.mark_dirty()` on failures
- **Descriptive assertions** using `.described_as()`

**Finding Implementation Examples:**
- Search codebase for similar tests: `"Find tests in microsoft/testsuites/[area]/ that test [functionality]"`
- Examine existing test suites for patterns and organization
- Check tool usage: `"Show examples of [ToolName] usage in tests"`

---

## Quick Reference Tables

### Test Method Signatures
| Scenario | Signature |
|----------|-----------|
| Single-node | `def test(self, node: Node, log: Logger)` |
| Multi-node | `def test(self, environment: Environment, log: Logger)` |
| Need log path | `def test(self, node: Node, log: Logger, log_path: Path)` |
| Need test result | `def test(self, node: Node, result: TestResult)` |

### Feature vs Tool Decision
| When you need... | Use... | Example |
|------------------|--------|---------|
| OS capability check | **Feature** | `node.features[Gpu]` |
| Executable tool | **Tool** | `node.tools[Git]` |
| To install software | `node.tools[Tool].install()` | Never `node.features[Feature].install()` |

### Error Handling
| Situation | Exception | When |
|-----------|-----------|------|
| Test not applicable | `SkippedException` | Wrong OS, missing hardware |
| Feature not implemented | `UnsupportedOperationException` | Platform limitation |
| Test failure | `assert_that()` or let exception propagate | Actual failure |

### Critical Pattern: Node Cleanup
**Always** call `node.mark_dirty()` when:
- Test modifies system state (kernel params, drivers, etc.)
- Test fails and node may be unstable
- Prevents environment reuse bugs

```python
try:
    # risky operation
except Exception:
    node.mark_dirty()
    raise
```

---

## Refinement Examples

Request any changes naturally:
- "Add Oracle Linux support"
- "Change this assertion to check X instead"
- "Add retry logic for transient failures"
- "Fix this error: [paste error]"
- "Refactor into helper function"
- "Add more detailed logging here"

No iteration limits - refine until perfect!

---

## Reference Documentation

- **[LISA Guidelines](../../docs/write_test/guidelines.rst)** - Coding standards
- **[Test Writing](../../docs/write_test/write_case.rst)** - How to write tests

---

**Previous Step:** [Test Ideation](./lisa-test-ideation.prompt.md) (optional)  
**Main Menu:** [LISA Test Writer](./write-lisa-test.prompt.md)

---

## Ready?

Tell me what to test, or share your design specification. I'll clarify requirements, propose implementation, generate code, then we refine together until perfect!
