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

### Branch Strategy

**CI Triggers:**
- Push to `main` or `develop` branches → Full CI pipeline runs
- Pull requests to any branch → Full CI pipeline runs

**Why not all branches?**  
Running CI on every feature branch push (without a PR) is expensive and usually unnecessary. The current strategy ensures:
- All code going into main/develop is validated ✅
- All pull requests are checked before merge ✅
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
