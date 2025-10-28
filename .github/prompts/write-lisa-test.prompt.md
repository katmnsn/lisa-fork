---
mode: 'agent'
description: 'LISA test generation router - routes users to ideation, code generation, or both workflows. CRITICAL: ALWAYS ask user to choose A/B/C before proceeding.'
tools: ['search', 'search/codebase', 'edit/editFiles', 'problems', 'runCommands', 'fetch', 'changes']
---

# LISA Test Generator

> **Simple router for AI-assisted LISA test development**

---

## ⚠️ CRITICAL INSTRUCTION ⚠️

**You MUST ask the user to choose A, B, or C before proceeding.**

Do NOT:
- Auto-select a workflow based on the user's message
- Start asking detailed questions before getting their choice
- Assume which workflow they need

---

## Choose Your Workflow

**A. Plan the test (Requirements & Design)**
- Gather functional requirements
- Analyze existing infrastructure
- Design test strategy
- Propose implementation plan
- **STOPS before code generation**

**B. Generate code (Skip Planning)**  
- Provide brief summary of what you want
- Get production-ready test code immediately
- Files created automatically
- **SKIPS requirements gathering**

**C. Full workflow (Plan → Code)**
- Requirements gathering
- Design proposal
- Code generation
- **Complete end-to-end**

---

**👉 Choose A, B, or C to begin.**

---

## Implementation

Once user chooses A, B, or C:

### **Choice A: Ideation Only**
Route to: `lisa-test-ideation.prompt.md`

Workflow:
1. Ask clarifying questions (purpose, platforms, requirements)
2. Search codebase for existing tools/features/tests
3. Propose test design with OS requirements and implementation plan
4. **STOP** - User reviews before proceeding

### **Choice B: Code Generation Only**
Route to: `lisa-test-codegen.prompt.md`

Workflow:
1. Get brief summary of test requirements
2. Automatically create production-ready Python test files
3. **STOP** - User handles validation

**Note:** Files are created automatically using `runCommands` tool.

### **Choice C: Full Workflow (A → B)**
Execute both prompts in sequence:

1. **First:** Run ideation workflow (lisa-test-ideation.prompt.md)
2. **Get approval:** User reviews proposed design
3. **Then:** Run code generation workflow (lisa-test-codegen.prompt.md)
4. **Done:** User handles validation using Nox

---

## Post-Generation: Validation

After code generation (paths B or C), validate before committing:

```bash
nox -vrt all  # Format, lint, type check, and test
```

**Resources:**
- Setup guide: `docs/write_test/dev_setup.rst`
- Debugging: Use Copilot chat with error messages
- Quality: Copilot checks code automatically during generation

---

## Reference Materials

Used by sub-workflows on-demand:

- **[LISA Patterns Library](../references/lisa-patterns.md)** - 11 core patterns with examples
- **[LISA Commands Reference](../references/lisa-commands.md)** - Development commands
