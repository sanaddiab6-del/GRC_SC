import sqlite3
import sys

try:
    conn = sqlite3.connect('sico_grc.db')
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]

    print(f"✅ عدد الجداول في قاعدة البيانات: {len(tables)}\n")
    print("📊 قائمة الجداول:")
    for i, table in enumerate(sorted(tables), 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {i:2d}. {table:30s} ({count:5d} سجل)")

    conn.close()
    print("\n✅ تم الفحص بنجاح")
except Exception as e:
    print(f"❌ خطأ: {e}")
    sys.exit(1)
