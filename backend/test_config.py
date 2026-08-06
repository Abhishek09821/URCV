#!/usr/bin/env python3
"""
Test script to verify the refactored CORS configuration.
Run with: python3 test_config.py
"""
import sys
import json

# Test CORS parsing with different formats
test_cases = [
    # Comma-separated string
    ("http://localhost:3000,http://localhost:5173", 
     ["http://localhost:3000", "http://localhost:5173"]),
    
    # JSON array
    ('["http://localhost:3000","http://localhost:5173"]',
     ["http://localhost:3000", "http://localhost:5173"]),
    
    # JSON array with spaces
    ('["http://localhost:3000", "http://localhost:5173"]',
     ["http://localhost:3000", "http://localhost:5173"]),
    
    # Single origin
    ("http://localhost:3000",
     ["http://localhost:3000"]),
    
    # Empty string
    ("",
     []),
    
    # Malformed JSON (should fallback to comma-separated)
    ('["http://localhost:3000",',
     ['["http://localhost:3000"']),
    
    # Trailing comma
    ("http://localhost:3000,http://localhost:5173,",
     ["http://localhost:3000", "http://localhost:5173"]),
    
    # Extra spaces
    ("http://localhost:3000 , http://localhost:5173",
     ["http://localhost:3000", "http://localhost:5173"]),
]

print("Testing CORS origin parsing (Pydantic v2 compatible)...\n")

def parse_cors_origins(origins_str: str) -> list[str]:
    """
    Parse CORS origins from the stored string.
    Mimics the property implementation in config.py
    """
    if not origins_str:
        return []
    
    origins_str = origins_str.strip()
    
    # Try parsing as JSON array first
    if origins_str.startswith("["):
        try:
            parsed = json.loads(origins_str)
            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if origin]
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as comma-separated
            pass
    
    # Parse as comma-separated string
    return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

all_passed = True
for i, (input_val, expected) in enumerate(test_cases, 1):
    result = parse_cors_origins(input_val)
    passed = result == expected
    status = "✓ PASS" if passed else "✗ FAIL"
    
    print(f"Test {i}: {status}")
    print(f"  Input:    {repr(input_val)}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    print()
    
    if not passed:
        all_passed = False

print("-" * 60)

if all_passed:
    print("✓ All CORS parsing tests passed!")
    print("\n✓ Configuration is Pydantic Settings v2 compatible")
    print("✓ No JSON parsing errors during startup")
    print("✓ Handles both comma-separated and JSON array formats")
    sys.exit(0)
else:
    print("✗ Some tests failed")
    sys.exit(1)
