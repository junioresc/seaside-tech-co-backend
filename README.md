# Seaside Tech Co Backend

Backend stack: Django + DRF, Postgres, Redis, Celery, Stripe, MinIO, SES/SNS.

## Quickstart (Dev)

1. Copy envs

```bash
cp config/env.example config/env.dev
```

2. Build and start services

```bash
make build && make up
```

3. Open devcontainer and install deps

```bash
# inside api container
pip install -r backend/requirements-dev.txt
python manage.py migrate
```

4. Run server (compose already starts it)

```bash
open http://localhost:8000/health/
open http://localhost:8025 # MailHog
open http://localhost:9001 # MinIO console (minio:minioadmin)
```

## Tests

```bash
make test
```

## CI/CD Pipeline

### Quality Checks

The CI pipeline runs automated quality checks on every pull request:
- **Black** - Code formatting (100 char line length)
- **isort** - Import sorting
- **flake8** - Linting and style checking
- **mypy** - Type checking

### Docker Build Pipeline

Production-ready Docker images are automatically built and pushed to GitHub Container Registry (GHCR) when code is merged to `main`.

**Build Workflow:**
- Triggers automatically after CI workflow completes successfully on `main` branch
- Uses multi-stage Dockerfile for optimized image size (< 500MB)
- Builds complete in < 10 minutes
- Docker layer caching reduces rebuild time by ~50%

**Image Tagging Strategy:**
- `sha-XXXXXXX` - Tagged with short commit SHA for version tracking
- `latest` - Latest successful build from main branch

**Pulling Images:**

```bash
# Pull latest image
docker pull ghcr.io/YOUR_ORG/YOUR_REPO/backend:latest

# Pull specific version by commit SHA
docker pull ghcr.io/YOUR_ORG/YOUR_REPO/backend:sha-abc1234

# Run production image locally
docker run -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=seaside.settings.prod \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  ghcr.io/YOUR_ORG/YOUR_REPO/backend:latest
```

**Local Build Testing:**

```bash
# Build production image
docker build -f backend/Dockerfile.prod -t seaside-backend:test .

# Verify image size (should be < 500MB)
docker images seaside-backend:test --format "{{.Size}}"

# Test image runs correctly
docker run --rm -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=seaside.settings.prod \
  seaside-backend:test

# Verify non-root user
docker run --rm seaside-backend:test whoami
# Output: app

# Check health endpoint
curl http://localhost:8000/health/
```

**Image Optimization Techniques:**

1. **Multi-Stage Build**
   - Builder stage: Installs build dependencies and compiles packages
   - Runtime stage: Contains only production runtime dependencies
   - Excludes build tools (gcc, build-essential) from final image

2. **Layer Caching**
   - GitHub Actions cache stores Docker layers
   - Requirements.txt changes invalidate cache appropriately
   - Cached builds are ~50% faster

3. **Security Best Practices**
   - Runs as non-root user (app, UID 1000)
   - Python 3.12-slim base image (minimal attack surface)
   - No secrets or sensitive data in image layers
   - Health check endpoint configured

4. **Size Optimization**
   - `--no-cache-dir` flag for pip installations
   - Cleanup of apt package lists
   - Minimal system packages only
   - Multi-stage pattern excludes build artifacts

### Branch Strategy

**CI Triggers:**
- Push to `main` or `develop` branches → Full CI pipeline runs
- Pull requests to any branch → Full CI pipeline runs

**Docker Build Triggers:**
- Push to `main` branch (after CI passes) → Build and push Docker image

**Why not all branches?**  
Running CI on every feature branch push (without a PR) is expensive and usually unnecessary. The current strategy ensures:
- All code going into main/develop is validated ✅
- All pull requests are checked before merge ✅
- Production images built only from main branch ✅
- Developers can push WIP commits to feature branches without triggering CI
- CI resources are used efficiently

**Recommendation:** Create a pull request early (even as draft) to get continuous CI feedback during development.

### Local Quality Checks

Run quality checks locally before pushing:

```bash
# Format code
black backend/
isort backend/

# Check quality
flake8 backend/
mypy backend/

# Run tests
pytest backend/tests/
```

## Docs

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
