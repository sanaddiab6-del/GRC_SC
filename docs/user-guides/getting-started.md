# SICO GRC Platform - Getting Started

## Welcome to SICO GRC Platform

SICO GRC Platform is a comprehensive Saudi regulatory compliance engine that helps organizations achieve and maintain compliance with:

- **ECC (Essential Cybersecurity Controls)** - 114 controls by NCA
- **CCC (Cloud Cybersecurity Controls)** - 180 controls by NCA  
- **PDPL (Personal Data Protection Law)** - 42 controls by SDAIA

## Quick Start

### Option 1: Docker (Recommended)

The fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Start all services
docker-compose -f deployment/docker-compose.yml up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

For development:

```bash
# Clone the repository
git clone https://github.com/sonaiso/sanadcom.git
cd sanadcom

# Run the setup script
bash scripts/setup.sh

# Start backend (Terminal 1)
cd src/backend
source venv/bin/activate
uvicorn main:app --reload

# Start frontend (Terminal 2)
cd src/frontend
npm run dev
```

## What's Included

### 1. Comprehensive Control Library
- All ECC, CCC, and PDPL controls
- Bilingual support (English/Arabic)
- Implementation guidance
- Evidence requirements

### 2. Control Mappings
- ECC ↔ CCC baseline mapping
- Cross-framework relationships
- Unified implementation approach

### 3. Assessment Tools
- Compliance scoring
- Gap analysis
- Progress tracking
- Dashboard views

### 4. Evidence Management
- Evidence catalog
- Document templates
- Audit trail
- Export capabilities

### 5. API & Integration
- RESTful API
- OpenAPI documentation
- Easy integration
- Webhook support (coming soon)

## Key Features

### 🎯 Framework Support
- **ECC 2.0**: Full 114-control implementation
- **CCC 1.0**: Complete 180-control coverage
- **PDPL 2021**: All 42 requirements

### 🌐 Bilingual
- Full Arabic and English support
- RTL interface ready
- Localized content

### 📊 Compliance Dashboard
- Real-time compliance scores
- Gap analysis
- Priority recommendations
- Executive reporting

### 🤖 AI-Powered (Coming Soon)
- RAG-based Q&A
- Citation-backed answers
- Bilingual knowledge base
- Custom BERT adapters

## Next Steps

1. **Explore the Dashboard**
   - Navigate to http://localhost:3000
   - Review compliance overview
   - Check framework status

2. **Review Controls**
   - Browse control library
   - Understand requirements
   - Check implementation status

3. **Start an Assessment**
   - Create new assessment
   - Answer control questions
   - Track progress

4. **Generate Reports**
   - Export compliance data
   - Create executive summaries
   - Share with stakeholders

## Documentation

- [Installation Guide](installation.md)
- [Architecture Overview](../architecture/overview.md)
- [API Documentation](../api/README.md)
- [User Manual](user-manual.md) (coming soon)

## Support

For questions or issues:
- Check the documentation
- Review API docs at http://localhost:8000/api/docs
- Contact the project owner

## License

MIT License - See LICENSE file for details

---

**Built with ❤️ for Saudi Regulatory Compliance Excellence**
