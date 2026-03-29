# PaytollControl — Agent Configuration

## Current state (Phase 1)

No sub-agents needed. The project is small enough for a single agent to handle all tasks.

## When to add agents

Consider adding specialized agents when:
- **Feature count > 3**: A feature-builder agent that scaffolds new feature subpackages
- **Test suite > 30s**: A test-runner agent that runs tests in parallel
- **Multiple LLM providers**: An LLM-testing agent that validates responses across providers
