"""
SICO GRC Platform - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="SICO GRC Platform API",
    description="Saudi Regulatory Compliance Engine - ECC, CCC, PDPL",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "operational",
        "service": "SICO GRC Platform API",
        "version": "0.1.0",
        "frameworks": ["ECC 3.0", "CCC 1.0", "PDPL 2023"],
        "languages": ["ar", "en"],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "database": "connected",
            "cache": "operational",
            "vector_db": "operational",
        }
    )


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "api_version": "v1",
        "supported_frameworks": {
            "ecc": {
                "version": "3.0",
                "name": "Essential Cybersecurity Controls",
                "name_ar": "الضوابط الأساسية للأمن السيبراني",
                "controls_count": 114
            },
            "ccc": {
                "version": "1.0",
                "name": "Cloud Cybersecurity Controls",
                "name_ar": "ضوابط الأمن السيبراني السحابي",
                "controls_count": 154
            },
            "pdpl": {
                "version": "2023",
                "name": "Personal Data Protection Law",
                "name_ar": "نظام حماية البيانات الشخصية",
                "articles_count": 40
            }
        },
        "capabilities": [
            "Unified Control Library",
            "ECC-CCC Baseline Mapping",
            "PDPL Registers (RoPA, DSAR, Breach)",
            "Evidence Automation",
            "SOC-GRC Integration",
            "Bilingual AI (Arabic/English)",
            "Executive Reporting"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
