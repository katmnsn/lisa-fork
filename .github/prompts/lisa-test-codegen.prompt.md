---
mode: 'agent'
description: 'LISA test code generation - iterative, production-ready Python test code with continuous refinement support.'
tools: ['edit/editFiles', 'problems', 'search/codebase']
---

# LISA Test Code Generation

Generate and iteratively refine production-ready LISA test code through natural conversation.

---

## Phase 1: Understand & Plan

### Gather Requirements

If from **ideation workflow**: Use provided design specification.

If **direct generation**: Ask:
- What functionality to test?
- Which OS/platforms?
- Single-node or multi-node?
- Required tools/features?

### Propose Implementation

```
## Implementation Plan

**Test Overview:**
- Purpose: [What we're testing]
- Platforms: [OS support with reasoning]
- Type: [Single-node/Multi-node]

**File Structure:**
- Location: `microsoft/testsuites/[area]/[file].py`
- Method: `test_[name]`
- Strategy: [New file OR extend existing - reason]

**Components:**
- LISA Tools: [From lisa/tools/]
- LISA Features: [From lisa/features/]
- Helpers: [New OR reuse]

**Patterns Applied:**
- Node cleanup on failures
- Feature support checks
- [Other patterns from LISA Patterns Library]

**Notes:** [Edge cases, special considerations]

Ready to generate? (Yes/Modify/Details)
```

---

## Phase 2: Generate Code

### Standards

Code follows:
- **[LISA Patterns](../references/lisa-patterns.md)** - 11 core patterns
- **[LISA Guidelines](../../docs/write_test/guidelines.rst)** - Official standards
- **Type hints** on all functions
- **Error handling** with `node.mark_dirty()`
- **Assertions** with `.described_as()`

### File Creation

Use `edit/editFiles` to:
1. Create new files with complete code
2. Update existing files (imports, extensions)
3. Verify with `problems` tool
4. Report changes

### Output Format

```
## ✅ Code Generated

**Created:**
- `microsoft/testsuites/[area]/[file].py` - [Description]
  - Method: `test_[name]`
  - Platforms: [OS list]
  - Patterns: [Applied patterns]

**Modified:**
- `microsoft/testsuites/[area]/__init__.py` - Added import

**Summary:** [Brief description of implementation]

Next: Review code, request refinements, or validate
```

---

## Phase 3: Refine Iteratively

**Key feature**: Continuous improvement through conversation.

### Refinement Options

**1. Modify Implementation**
- Add Oracle Linux support
- Change assertion to check specific value
- Add retry logic here
- Refactor into helper function

**2. Fix Issues**
- Share error from Nox/pytest
- Share VS Code Problems panel errors
- I'll analyze and fix

**3. Improve Quality**
- Clarify this error message
- Add detailed logging
- Handle edge case X

**4. Extend Functionality**
- Add test case for Y
- Create multi-node variant
- Add before_case setup

### Iteration Process

```
You: Request change
  ↓
Me: Analyze + implement using edit/editFiles
  ↓
Me: Verify with problems tool
  ↓
Me: Report changes
  ↓
You: Review → More changes OR Done
```

**No iteration limits** - refine until satisfied!

---

## Pattern Quick Reference

All code follows these patterns (details in [lisa-patterns.md](../references/lisa-patterns.md)):

1. **Node Cleanup** - `node.mark_dirty()` in exception handlers
2. **Feature Support** - Check before use, skip gracefully
3. **Helper Naming** - `_private`, `__internal` conventions
4. **Lifecycle Hooks** - `before_case`, `after_case` for setup/teardown
5. **Multi-Node** - `min_count`, `environment.nodes.list()`
6. **Retry Logic** - `@retry` decorator for transient failures
7. **Timeout Protection** - `func_timeout()` for cleanup
8. **Logging** - DEBUG for details, INFO for key events
9. **Error Messages** - WHAT + WHY + HOW format
10. **Code Comments** - Explain business logic, not code
11. **Assertions** - `.described_as()` with clear messages

---

## Validation (Minimal)

After satisfied with code:

```powershell
# Activate venv (if not active)
.\.venv\Scripts\Activate.ps1

# Run all checks
nox -vrt all
```

**If errors:**
- **Option 1**: Share error → I'll fix
- **Option 2**: See `docs/write_test/dev_setup.rst`

---

## Common Workflows

**From Ideation:**
1. Ideation provides design spec
2. Generate code from spec
3. Iterate to refine
4. Validate

**Direct Generation:**
1. Describe what to test
2. I clarify requirements
3. Generate code
4. Iterate to refine
5. Validate

**Fix Existing:**
1. Share error/issue
2. I analyze and propose fix
3. Iterate if needed
4. Validate

**Extend Existing:**
1. Request new test case
2. I analyze existing patterns
3. Generate matching style
4. Iterate to refine
5. Validate

---

## Tips

**Be Conversational:**
- Add Oracle Linux support
- This error is confusing
- Make this a helper

**Iterate Freely:**
- Start simple
- Refine incrementally
- Fix issues as found

**Share Context:**
- Error messages verbatim
- Point to related code
- Explain reasoning

---

## Reference Documentation

- **[LISA Patterns](../references/lisa-patterns.md)** - Implementation patterns
- **[Guidelines](../../docs/write_test/guidelines.rst)** - Coding standards
- **[Test Writing](../../docs/write_test/write_case.rst)** - How to write tests
- **[Dev Setup](../../docs/write_test/dev_setup.rst)** - Nox and validation

---

**Current Workflow:** Code Generation & Iterative Refinement  
**Previous:** [Ideation](./lisa-test-ideation.prompt.md) (optional)  
**Router:** [Main Menu](./write-lisa-test.prompt.md)

---

## Ready?

Tell me what to test, or share your design specification!

I'll clarify requirements, propose implementation, generate code, then we refine together until perfect.
