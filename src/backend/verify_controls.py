"""Quick verification of loaded controls"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sico_grc.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get counts by framework
cursor.execute("SELECT framework, COUNT(*) FROM controls GROUP BY framework")
results = cursor.fetchall()

print("\n" + "="*60)
print("📊 CONTROL LIBRARY VERIFICATION")
print("="*60)

total = 0
for fw, count in results:
    print(f"   {fw}: {count:>3} controls")
    total += count

print(f"   {'─'*50}")
print(f"   TOTAL: {total:>3} controls")

# Get sample from each framework
print("\n📋 Sample Controls by Framework:")
print("="*60)

for framework in ['ECC', 'CCC', 'PDPL']:
    cursor.execute(f"""
        SELECT control_id, title_en 
        FROM controls 
        WHERE framework = '{framework}' 
        LIMIT 3
    """)
    samples = cursor.fetchall()
    
    print(f"\n{framework}:")
    for cid, title in samples:
        print(f"   • {cid}: {title[:70]}...")

conn.close()

print("\n" + "="*60)
print("✅ Verification Complete!")
print("="*60 + "\n")
