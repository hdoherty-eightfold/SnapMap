# SnapMap Documentation

## Feature Specifications
All feature documentation is located in `.claude/features/`:

- **[Main Orchestrator](../.claude/features/MAIN_ORCHESTRATOR.md)** - Central coordination
- **[Upload](../.claude/features/upload/SPEC.md)** - File upload and processing
- **[Review](../.claude/features/review/SPEC.md)** - Data quality analysis
- **[Mapping](../.claude/features/mapping/SPEC.md)** - AI field mapping
- **[Export](../.claude/features/export/SPEC.md)** - Multi-format export
- **[SFTP](../.claude/features/sftp/SPEC.md)** - Secure file upload
- **[Settings](../.claude/features/settings/SPEC.md)** - App configuration
- **[Layout](../.claude/features/layout/SPEC.md)** - UI navigation

## Development
- Each feature spec contains complete functionality, API, testing, and dependency information
- Follow the safe change management protocol in MAIN_ORCHESTRATOR.md
- Test files are organized by feature in `backend/tests/features/`

## Quick Start
1. Read the feature spec for your area of work
2. Check MAIN_ORCHESTRATOR.md for dependencies
3. Make changes following feature guidelines
4. Run feature-specific tests
5. Update spec if behavior changes

---

## Documentation Index

### 1. Implementation Complete (Executive Summary)
**File**: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

**Contents**:
- Project overview and status (BETA READY)
- Complete feature list (15+ features)
- Test results summary (117 tests, 97.1% pass rate)
- Production readiness assessment
- Known limitations
- Deployment checklist
- Timeline achievement (1 day vs 3-4 weeks)

**Audience**: Executives, Project Managers, Stakeholders

**Read Time**: 15 minutes

---

### 2. User Guide (End User Documentation)
**File**: [USER_GUIDE.md](USER_GUIDE.md)

**Contents**:
- 5-minute quick start
- How to upload files (CSV, pipe-delimited, TSV, Excel)
- Understanding delimiter auto-detection
- Field mapping workflow (automatic + manual)
- Handling validation errors
- Character encoding tips (Turkish, Spanish, German, French)
- Multi-value field format (`||` separator)
- Exporting data (CSV and XML)
- SFTP upload guide
- Troubleshooting common issues (20+ scenarios)
- FAQ section

**Audience**: End Users, Business Analysts, Data Operators

**Read Time**: 30 minutes (or use as reference)

---

### 3. Developer Guide (Technical Documentation)
**File**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

**Contents**:
- Architecture overview with diagrams
- Project structure
- Key components deep-dive:
  - File Parser (delimiter detection, encoding)
  - Field Mapper (semantic matching, synonyms)
  - XML Transformer (multi-value support)
  - Data Validator (integrity checks)
- Data flow diagrams
- Core services documentation
- Database & storage (ChromaDB, in-memory)
- Extension points (adding entities, fields, validation rules)
- Development workflow
- Code examples (Python, TypeScript)
- Testing guide
- Debugging tips

**Audience**: Software Engineers, Technical Leads, Contributors

**Read Time**: 60 minutes (comprehensive)

---

### 4. API Reference (API Documentation)
**File**: [API_REFERENCE.md](API_REFERENCE.md)

**Contents**:
- Complete API specifications for all 10+ endpoints:
  - `POST /api/upload` - Enhanced with auto-detection
  - `POST /api/detect-file-format` - NEW in v2.0
  - `POST /api/auto-map` - Simplified (source_fields optional)
  - `POST /api/validate` - Data validation
  - `POST /api/transform/export` - CSV export
  - `POST /api/transform/export-xml` - XML export
  - `POST /api/sftp/upload/{id}` - SFTP upload
  - `GET /api/entities` - List entity types
  - `GET /api/schema/{entity_name}` - Get schema
- Request/response examples (JSON)
- Error codes and messages
- cURL examples for each endpoint
- Python and JavaScript code examples
- Postman collection
- Rate limiting details

**Audience**: API Consumers, Frontend Developers, Integration Engineers

**Read Time**: 45 minutes (or use as reference)

---

### 5. Deployment Guide (Operations)
**File**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Contents**:
- Prerequisites (Python 3.11+, Node 18+, dependencies)
- Development deployment (5 minutes)
- Production deployment:
  - Traditional deployment (Ubuntu/nginx)
  - Docker deployment (docker-compose)
- Environment configuration (`.env` file)
- Vector database setup (`python build_vector_db.py`)
- Security configuration (encryption keys, CORS, rate limiting)
- Performance tuning (memory, CPU, concurrent requests)
- Monitoring setup (logging, metrics, alerts)
- Backup and recovery procedures
- Scaling recommendations (vertical and horizontal)
- Troubleshooting deployment issues

**Audience**: DevOps Engineers, System Administrators, Site Reliability Engineers

**Read Time**: 45 minutes

---

### 6. Changelog (Version History)
**File**: [CHANGELOG.md](CHANGELOG.md)

**Contents**:
- Version 2.0.0 (Current - PRODUCTION READY)
  - Added features (15+)
  - Changed functionality
  - Fixed bugs
  - Security improvements
  - Performance optimizations
  - Known issues
  - Migration guide from v1.0
- Version 1.0.0 (Deprecated - MVP)
- Planned releases (v2.1, v3.0)
- Upgrade path

**Audience**: All Users, Developers, Managers

**Read Time**: 10 minutes

---

### 7. Testing Guide
**File**: [TESTING_GUIDE.md](TESTING_GUIDE.md)

**Contents**:
- Test suite overview (117 tests)
- Running tests (pytest commands)
- Test coverage (97.1% pass rate)
- Test modules:
  - Character encoding (12 tests)
  - Data loss validation (15 tests)
  - Delimiter detection (14 tests)
  - Field mapping accuracy (10 tests)
  - Multi-value fields (8 tests)
- Writing new tests (best practices)
- CI/CD integration (GitHub Actions)
- Performance testing (Locust, benchmarks)
- Load testing recommendations

**Audience**: QA Engineers, Developers, DevOps Engineers

**Read Time**: 30 minutes

---

### 8. Troubleshooting Guide
**File**: [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)

**Contents**:
- Quick diagnosis commands
- Common issues with solutions (30+ scenarios):
  - Upload errors
  - Mapping errors
  - Validation errors
  - Export errors
  - SFTP errors
  - Backend won't start
  - High memory usage
  - Slow performance
- Backend troubleshooting
- Frontend troubleshooting
- Database troubleshooting
- Getting help (support contact)

**Audience**: All Users, Developers, Support Team

**Read Time**: 20 minutes (or use as reference when needed)

---

### 9. Security Guide
**File**: [SECURITY_GUIDE.md](SECURITY_GUIDE.md)

**Contents**:
- Security features implemented:
  - Rate limiting (100 req/min)
  - Security headers (HSTS, CSP, X-Frame-Options)
  - CORS protection
  - Input sanitization
  - Credential encryption (AES-256)
- OWASP Top 10 compliance
- Security best practices
- Penetration testing guidelines
- Incident response procedures
- Compliance considerations (GDPR, HIPAA)
- Vulnerability disclosure policy
- Security checklist

**Audience**: Security Engineers, Compliance Officers, DevOps Engineers

**Read Time**: 25 minutes

---

### 10. Performance Guide
**File**: [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md)

**Contents**:
- Performance benchmarks:
  - File processing (15,000 rows/sec)
  - Field mapping (<1ms per field)
  - Export (10,000 rows/sec)
- Optimization techniques
- Resource requirements (min, recommended, high-perf)
- Monitoring metrics (KPIs, system metrics)
- Performance tuning:
  - Backend (FastAPI/Uvicorn)
  - Frontend (React)
  - Database (ChromaDB)
  - nginx
- Load testing (Locust, Apache Bench)
- Scalability (vertical, horizontal)
- Troubleshooting performance issues

**Audience**: DevOps Engineers, Performance Engineers, System Architects

**Read Time**: 25 minutes

---

## Documentation Structure

```
docs/
├── README.md (this file)
├── IMPLEMENTATION_COMPLETE.md
├── USER_GUIDE.md
├── DEVELOPER_GUIDE.md
├── API_REFERENCE.md
├── DEPLOYMENT_GUIDE.md
├── CHANGELOG.md
├── TESTING_GUIDE.md
├── TROUBLESHOOTING_GUIDE.md
├── SECURITY_GUIDE.md
└── PERFORMANCE_GUIDE.md
```

---

## Reading Paths

### For Different Audiences

#### End Users / Business Analysts
1. [Implementation Complete](IMPLEMENTATION_COMPLETE.md) - Overview
2. [User Guide](USER_GUIDE.md) - How to use the system
3. [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) - When issues arise
4. [FAQ](USER_GUIDE.md#faq) - Common questions

**Total Time**: ~50 minutes

---

#### Developers / Engineers
1. [Implementation Complete](IMPLEMENTATION_COMPLETE.md) - Overview
2. [Developer Guide](DEVELOPER_GUIDE.md) - Architecture and code
3. [API Reference](API_REFERENCE.md) - API specifications
4. [Testing Guide](TESTING_GUIDE.md) - How to test
5. [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) - Debugging

**Total Time**: ~2.5 hours

---

#### DevOps / System Administrators
1. [Implementation Complete](IMPLEMENTATION_COMPLETE.md) - Overview
2. [Deployment Guide](DEPLOYMENT_GUIDE.md) - How to deploy
3. [Security Guide](SECURITY_GUIDE.md) - Security configuration
4. [Performance Guide](PERFORMANCE_GUIDE.md) - Optimization
5. [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) - Operational issues

**Total Time**: ~2 hours

---

#### Project Managers / Stakeholders
1. [Implementation Complete](IMPLEMENTATION_COMPLETE.md) - Full overview
2. [Changelog](CHANGELOG.md) - What's new
3. [User Guide - Quick Start](USER_GUIDE.md#getting-started) - Capabilities demo
4. [Deployment Guide - Checklist](DEPLOYMENT_GUIDE.md#deployment-checklist) - Rollout plan

**Total Time**: ~30 minutes

---

## Document Conventions

### Formatting

**Code Blocks**:
```python
# Python code
def example():
    return "Hello"
```

```bash
# Shell commands
cd backend && python main.py
```

**Inline Code**: `variable_name`, `function_name()`, `/api/endpoint`

**File Paths**: `backend/app/services/file_parser.py`

**Emphasis**:
- **Bold**: Important concepts
- *Italic*: New terms
- ✅ Success indicators
- ❌ Failure indicators
- ⚠️ Warnings

### Icons

- 🎯 Goals / Objectives
- 🚀 Performance / Speed
- 🧠 Intelligence / AI
- 🔒 Security
- 🌍 International / Localization
- 📊 Data / Analytics
- 📚 Documentation / Resources
- ✨ New Features

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-11-07 | Complete documentation package |
| 1.0.0 | 2025-11-01 | Initial basic documentation |

---

## Contributing to Documentation

### How to Update Docs

1. **Clone repository**:
   ```bash
   git clone https://github.com/your-org/snapmap.git
   cd snapmap/docs
   ```

2. **Edit Markdown files**:
   - Use any text editor
   - Follow existing formatting conventions
   - Add examples where helpful

3. **Submit changes**:
   ```bash
   git checkout -b docs/update-user-guide
   git add USER_GUIDE.md
   git commit -m "docs: Update user guide with new examples"
   git push origin docs/update-user-guide
   ```

4. **Create Pull Request**:
   - Describe changes
   - Tag as "documentation"
   - Request review

### Documentation Standards

- **Clarity**: Write for the target audience
- **Completeness**: Cover all important aspects
- **Conciseness**: Be thorough but not verbose
- **Examples**: Include code examples and screenshots
- **Up-to-date**: Update with code changes
- **Cross-references**: Link to related documentation

---

## Additional Resources

### Internal Documentation
- **Code Comments**: See inline code documentation
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **GitHub Issues**: Known issues and feature requests

### External Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **React Documentation**: https://react.dev/

---

## Support

### Getting Help

**Documentation Issues**:
- GitHub Issues (tag: documentation)
- Email: docs@yourcompany.com

**Technical Support**:
- Email: support@yourcompany.com
- Response Time: Within 24 hours

**Community**:
- Slack: #snapmap-support
- GitHub Discussions

---

## Acknowledgments

This comprehensive documentation package was created to support the production-ready v2.0.0 release of SnapMap. Special thanks to:

- **Development Team**: For building an amazing product
- **QA Team**: For thorough testing (117 tests!)
- **Early Users**: For valuable feedback
- **Claude Code**: For AI-assisted development and documentation

---

## License

This documentation is licensed under MIT License - see LICENSE file for details.

---

## Feedback

We value your feedback on this documentation!

**Was this documentation helpful?** Please let us know:
- Email: docs@yourcompany.com
- GitHub: Create an issue with "documentation" tag
- What worked well?
- What could be improved?
- What's missing?

Your feedback helps us improve documentation for everyone.

---

**Documentation Package Version**: 2.0.0
**Last Updated**: November 7, 2025
**Total Pages**: ~150 pages across 10 documents
**Estimated Reading Time**: 5 hours (complete read) or use as reference

---

## Quick Reference Card

**Most Common Tasks**:

| Task | Documentation | Section |
|------|---------------|---------|
| Upload a file | [User Guide](USER_GUIDE.md) | Uploading Files |
| Map fields | [User Guide](USER_GUIDE.md) | Field Mapping |
| Fix validation errors | [User Guide](USER_GUIDE.md) | Validation & Error Handling |
| Export data | [User Guide](USER_GUIDE.md) | Exporting Data |
| Deploy to production | [Deployment Guide](DEPLOYMENT_GUIDE.md) | Production Deployment |
| Call API from code | [API Reference](API_REFERENCE.md) | Code Examples |
| Add new entity type | [Developer Guide](DEVELOPER_GUIDE.md) | Extension Points |
| Write tests | [Testing Guide](TESTING_GUIDE.md) | Writing New Tests |
| Fix slow performance | [Performance Guide](PERFORMANCE_GUIDE.md) | Troubleshooting |
| Configure security | [Security Guide](SECURITY_GUIDE.md) | Security Configuration |

---

Thank you for choosing SnapMap!

*Happy transforming! 🚀*
