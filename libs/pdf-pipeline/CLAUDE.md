# pdf-pipeline — Claude Code Instructions

## Overview

Generic PDF-to-JSON extraction pipeline via LLM. Domain-agnostic — consumers provide prompts and parse results.

## Structure

```
src/pdf_pipeline/
  abstractions/     ABCs for all swappable components (LanguageModel, DataExtractor, OcrEngine, ...)
  core/             Pipeline orchestration (FeaturePipeline, ExcelPipeline) and FeatureRegistry
  implementations/  Concrete classes (Gemini, Cloud Vision OCR, image preprocessing, caching, ...)
  config/           Settings (DPI, chunk size, model names) and pricing
```

## Key Files

| File | Role |
|------|------|
| `abstractions/language_model.py` | LanguageModel ABC — implement to add a new LLM provider |
| `abstractions/data_extractor.py` | DataExtractor ABC — implement in consumer features |
| `core/pipeline.py` | FeaturePipeline — main orchestration loop |
| `core/feature_registry.py` | FeatureRegistry, FeatureConfig, ExcelFeatureConfig |
| `implementations/gemini_model.py` | GeminiModel — current LLM implementation |

## Dependency Rule

```
core/            → abstractions/ only
implementations/ → abstractions/ + config/
```

**core/ and implementations/ NEVER import from each other.**

## Rules

1. Never import from consumer applications — no domain-specific code
2. Never depend on a specific data schema — receive a prompt, return raw LLM text
3. New preprocessing steps go behind the `PreparationStep` ABC
4. New LLM providers go behind the `LanguageModel` ABC
5. Default chunk size: 40 pages — always send in chunks, never per-page

## Commands

- Run tests: `python -m pytest tests/ -v`
- Install (editable): `pip install -e .`
