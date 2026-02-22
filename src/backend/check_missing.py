import sqlite3

conn = sqlite3.connect('src/backend/sico_grc.db')
cursor = conn.cursor()

# Check for the "missing" subdomains
missing_subdomains = ['1-10', '2-10', '2-11', '2-12', '2-13', '2-14', '2-15', '2-16']

print("Checking for controls in 'missing' subdomains:\n")

for subdomain in missing_subdomains:
    cursor.execute(f"SELECT control_id FROM controls WHERE framework='ECC' AND control_id LIKE '{subdomain}%' ORDER BY control_id")
    controls = cursor.fetchall()
    
    if controls:
        print(f"✅ {subdomain}: {len(controls)} controls found")
        for ctrl in controls:
            print(f"   - {ctrl[0]}")
    else:
        print(f"❌ {subdomain}: NO CONTROLS FOUND")
    print()

conn.close()
