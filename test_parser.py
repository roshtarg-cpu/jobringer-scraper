#!/usr/bin/env python3
"""Test the parser with the saved HTML."""
import sys
sys.path.insert(0, 'src')

from parser import parse_job_listing

# Read the saved HTML
with open('/home/roshtarg/.hermes/cache/browser-use/workspace/sa-0-071af705/jobringer_job.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Test the parser
url = 'https://jobringer.com/job/sales-coordinator/3f73042a'
job_data = parse_job_listing(html, url)

# Print results
print("Extraction Test Results:")
print("=" * 60)
for key, value in job_data.items():
    if key != 'description' or not value:
        print(f"{key:15s}: {value}")
    else:
        print(f"{key:15s}: {value[:100]}...")

# Validation
print("\n" + "=" * 60)
print("VALIDATION:")
required_fields = ['jobTitle', 'company', 'location', 'experience', 'jobType']
missing = []
for field in required_fields:
    if not job_data.get(field):
        missing.append(field)
        print(f"❌ MISSING: {field}")
    else:
        print(f"✓ FOUND: {field} = {job_data[field]}")

if missing:
    print(f"\n⚠️  Parser would fail - missing {len(missing)} required fields")
    sys.exit(1)
else:
    print("\n✓ Parser extracts all required fields successfully!")
    sys.exit(0)
