import os
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import GeoIP2 for production-grade IP geolocation
GEOIP_AVAILABLE = False
geoip2_reader = None

try:
    import geoip2.database
    import geoip2.errors
    
    # Check if GeoLite2 database exists
    GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "/usr/share/GeoIP/GeoLite2-Country.mmdb")
    if os.path.exists(GEOIP_DB_PATH):
        geoip2_reader = geoip2.database.Reader(GEOIP_DB_PATH)
        GEOIP_AVAILABLE = True
        logger.info(f"GeoIP2 database loaded successfully from {GEOIP_DB_PATH}")
    else:
        logger.warning(f"GeoIP2 database not found at {GEOIP_DB_PATH}. Using fallback IP ranges.")
except ImportError:
    logger.warning("geoip2 library not installed. Using fallback IP ranges for Saudi IP validation.")
except Exception as e:
    logger.error(f"Error loading GeoIP2 database: {e}")

    Check if IP address is from Saudi Arabia.
    Uses GeoIP2 MaxMind database if available, falls back to known IP ranges.
        True if Saudi IP, False otherwise
        
    Note:
        For production use, download GeoLite2-Country database from:
        https://dev.maxmind.com/geoip/geoip2/geolite2/
        Set GEOIP_DB_PATH environment variable to database path.
    # Production: Use GeoIP2 MaxMind database
    if GEOIP_AVAILABLE and geoip2_reader:
        try:
            response = geoip2_reader.country(ip)
            # Saudi Arabia ISO code
            return response.country.iso_code == "SA"
        except geoip2.errors.AddressNotFoundError:
            logger.debug(f"IP {ip} not found in GeoIP database")
            return False
        except Exception as e:
            logger.error(f"GeoIP lookup error for {ip}: {e}")
            # Fall through to fallback method
    
    # Fallback: Known Saudi Arabia IP ranges (partial list for demonstration)
    # Note: This is not comprehensive - production should use GeoIP database
    saudi_ip_ranges = [
        # Saudi Telecom Company (STC)
        "213.130.", "213.131.", "212.26.", "212.27.",
        # Mobily
        "212.26.", "212.72.", "212.73.",
        # Zain Saudi Arabia
        "212.72.", "212.73.",
        # Government networks
        "195.229.",
        # Additional major ISPs
        "46.242.", "31.9.", "31.13.",
    return any(ip.startswith(prefix) for prefix in saudi_ip_ranges)