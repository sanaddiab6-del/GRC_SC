"""
Quick fix script to add 'await' before all db.execute() calls in enterprise_router.py
"""

import re

# Read the file
with open('enterprise_router.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: db.execute(...).fetchone() -> await db.execute(...).fetchone()
content = re.sub(
    r'(\s+)result = db\.execute\(',
    r'\1result = await db.execute(',
    content
)

# Pattern 2: db.execute(...) standalone assignments
content = re.sub(
    r'(\s+)total = db\.execute\(',
    r'\1total = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)critical = db\.execute\(',
    r'\1critical = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)high = db\.execute\(',
    r'\1high = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)within_appetite = db\.execute\(',
    r'\1within_appetite = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)open_findings = db\.execute\(',
    r'\1open_findings = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)overdue = db\.execute\(',
    r'\1overdue = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)open_cases = db\.execute\(',
    r'\1open_cases = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)in_progress = db\.execute\(',
    r'\1in_progress = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)data_processors = db\.execute\(',
    r'\1data_processors = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)high_risk = db\.execute\(',
    r'\1high_risk = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)total_ropa = db\.execute\(',
    r'\1total_ropa = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)total_dsar = db\.execute\(',
    r'\1total_dsar = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)overdue_dsar = db\.execute\(',
    r'\1overdue_dsar = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)total_breaches = db\.execute\(',
    r'\1total_breaches = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)sdaia_notified = db\.execute\(',
    r'\1sdaia_notified = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)total_risks = db\.execute\(',
    r'\1total_risks = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)critical_risks = db\.execute\(',
    r'\1critical_risks = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)overdue_findings = db\.execute\(',
    r'\1overdue_findings = (await db.execute(',
    content
)

# Pattern 3: latest_XXX = db.execute (multi-line pattern)
content = re.sub(
    r'(\s+)latest_ecc = db\.execute\(',
    r'\1latest_ecc = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)latest_ccc = db\.execute\(',
    r'\1latest_ccc = (await db.execute(',
    content
)
content = re.sub(
    r'(\s+)latest_pdpl = db\.execute\(',
    r'\1latest_pdpl = (await db.execute(',
    content
)

content = re.sub(
    r'(\s+)active = db\.execute\(',
    r'\1active = (await db.execute(',
    content
)

# Fix closing parentheses for lines that now have ( await
content = re.sub(
    r'\(await db\.execute\(text\("SELECT COUNT\(\*\) FROM [^"]+"\)\)\.fetchone\(\)\[0\]',
    lambda m: m.group(0) + ')',
    content
)
content = re.sub(
    r'\(await db\.execute\(text\("SELECT [^"]+"\)\)\.fetchone\(\)',
    lambda m: m.group(0) + ')',
    content
)

# Write back
with open('enterprise_router.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all db.execute() calls with await")
