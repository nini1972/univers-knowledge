"""Integration test for the Math Engine."""
import sys
sys.path.insert(0, 'src')

# Test 1: index_utils parse_concept_md now includes math fields
from index_utils import parse_concept_md
from pathlib import Path

test_files = list(Path('knowledge_base/level_1_fundamental_physics').glob('*.md'))
if test_files:
    r = parse_concept_md(test_files[0], 'level_1_fundamental_physics')
    print(f'parse_concept_md test: {test_files[0].name}')
    print(f'  id: {r["id"]}')
    print(f'  status: {r["status"]}')
    print(f'  math_status: {r["math_status"]}')
    print(f'  math_score: {r["math_score"]}')
    assert 'math_status' in r, 'math_status missing from concept dict'
    assert 'math_score' in r, 'math_score missing from concept dict'
    print('  PASS')
else:
    print('No level 1 files found to test')

# Test 2: workflow_contracts all functions importable
from workflow_contracts import (
    parse_student_decision, normalize_markdown_output, validate_concept_markdown,
    parse_skeptic_checklist_score, parse_math_score, parse_math_status,
    check_level2_prerequisites
)
print('workflow_contracts imports: PASS')

# Test 3: parse_math_score
s, t = parse_math_score('**Math Score:** 4/4')
assert s == 4 and t == 4, f'Expected 4/4 got {s}/{t}'
print(f'parse_math_score bold fmt: PASS ({s}/{t})')

s2, t2 = parse_math_score('Math Score: 3/4')
assert s2 == 3, f'Expected 3 got {s2}'
print(f'parse_math_score plain fmt: PASS ({s2}/{t2})')

# Test 4: parse_math_status
for label in ['MATH_PROVEN', 'MATH_CONSISTENT', 'MATH_TOPOLOGICAL', 'MATH_CONJECTURED', 'MATH_FLAWED', 'MATH_PENDING']:
    result = parse_math_status(f'Status: [{label}]')
    assert result == label, f'Expected {label} got {result}'
print('parse_math_status: PASS (all 6 statuses)')

# Test 5: tools all importable
from tools.math_tools import get_tier1_math_tools, get_tier2_math_tools
t1 = get_tier1_math_tools()
t2 = get_tier2_math_tools()
print(f'Tier 1 tools: {[type(t).__name__ for t in t1]}')
print(f'Tier 2 tools: {[type(t).__name__ for t in t2]}')

# Test 6: validate_concept_markdown with math warnings (non-blocking)
from workflow_contracts import validate_concept_markdown
sample_md = """---
title: "Test Concept"
level: 1
status: "[VERIFIED]"
sources:
  - source1
  - source2
  - source3
---

# Test Concept

## 1. Overview
Overview text.

## 2. Detailed Explanation
Explanation.

## 3. Mathematical Framework
Math.

## 4. Skeptical Perspectives & Alternative Hypotheses
Skeptic.

## 5. Verification & Skeptic's Notes
Notes.

## 6. Visual Representation
Visual.

## 7. Related Concepts
- [Related](other.md)
"""
is_valid, errors = validate_concept_markdown(sample_md)
assert is_valid, f'Expected valid: {errors}'
print(f'validate_concept_markdown (no math sections): PASS (valid={is_valid}, errors={errors})')

print()
print('ALL INTEGRATION TESTS PASSED')
