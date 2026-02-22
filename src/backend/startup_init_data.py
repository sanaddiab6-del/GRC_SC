"""
SICO GRC Platform - Startup Data Initialization
Ensures database is populated with complete Saudi regulatory frameworks
"""

import sqlite3
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent / "sico_grc.db"

def check_and_initialize_data():
    """Check if database has data, populate with complete control libraries if needed"""
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if controls exist
        cursor.execute("SELECT COUNT(*) FROM controls")
        control_count = cursor.fetchone()[0]
        
        # Check if risks exist  
        cursor.execute("SELECT COUNT(*) FROM risks")
        risk_count = cursor.fetchone()[0]
        
        # Check if evidence exists
        cursor.execute("SELECT COUNT(*) FROM evidences")
        evidence_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Database Status:")
        print(f"   - Controls: {control_count}")
        print(f"   - Risks: {risk_count}")
        print(f"   - Evidence: {evidence_count}")
        
        # If database has fewer than 400 controls, load complete libraries (ECC, CCC, PDPL)
        if control_count < 400:
            print(f"⚠️ Database has only {control_count} controls - loading COMPLETE control libraries...")
            
            # Import and run complete control libraries loader
            from load_complete_control_libraries import main as load_complete
            load_complete()
            
            print("✅ Complete Saudi control libraries loaded (ECC, CCC, PDPL)")
        else:
            print(f"✅ Database already has {control_count} controls - skipping control library load")
        
        if risk_count == 0:
            print("⚠️ No risks in database - loading sample data...")
            from load_enterprise_sample_data import load_enterprise_sample_data
            load_enterprise_sample_data()
            print("✅ Sample enterprise data loaded")
        
        if evidence_count < 5:
            print("⚠️ Insufficient evidence records - loading evidence data...")
            from load_evidence_data import load_evidence_data
            load_evidence_data()
            print("✅ Evidence records loaded")
        
        print("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_and_initialize_data()
