"""
SICO GRC Platform - Startup Data Initialization
Ensures database is populated with complete Saudi regulatory frameworks
"""

from pathlib import Path
import sys

def check_and_initialize_data():
    """
    Placeholder hook called during app startup.
    Seed data loading must be triggered manually via management scripts
    now that PostgreSQL is the only supported backend.
    """
    import logging
    logging.getLogger(__name__).info(
        "Startup data initialization skipped (run seed scripts manually)"
    )


if __name__ == "__main__":
    check_and_initialize_data()
