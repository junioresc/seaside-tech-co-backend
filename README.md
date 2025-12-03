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

### Staging Deployment Pipeline

Automatic deployment to AWS ECS Fargate staging environment when code is merged to `main`.

**Deployment Workflow:**
- Triggers automatically after Docker build completes successfully on `main` branch
- Runs database migrations before service update
- Deploys with blue-green strategy (zero downtime)
- Performs health checks with automatic rollback on failure
- Completes in < 15 minutes

**Deployment Steps:**
1. **Update Task Definition** - New Docker image (sha-tagged) registered to ECS
2. **Run Migrations** - Django migrations executed as one-off task
3. **Service Update** - ECS service updated with circuit breaker enabled
4. **Health Check** - /health/ endpoint validated (10 retries, 30s intervals)
5. **Rollback** - Automatic revert to previous version on failure

**AWS Infrastructure Requirements:**

```yaml
# GitHub Secrets Required
AWS_ACCESS_KEY_ID: <IAM user access key>
AWS_SECRET_ACCESS_KEY: <IAM user secret key>
AWS_REGION: <region, e.g., us-east-1>
ECS_CLUSTER_STAGING: <staging cluster name, e.g., staging-cluster>
```

**ECS Task Definition:**
- Task: `backend-api-staging`
- CPU: 512 (0.5 vCPU)
- Memory: 1024 MB (1 GB)
- Network Mode: awsvpc
- Port: 8000
- Launch Type: Fargate

**Environment Variables (AWS Secrets Manager):**
- `DATABASE_URL` → Secret: `staging/backend/database-url`
- `REDIS_URL` → Secret: `staging/backend/redis-url`
- `DJANGO_SECRET_KEY` → Secret: `staging/backend/django-secret-key`
- `DJANGO_SETTINGS_MODULE=seaside.settings.staging`
- `AWS_S3_BUCKET_NAME` → Secret: `staging/backend/s3-bucket-name`

**IAM Permissions Required:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:RunTask",
        "ecs:DescribeTasks",
        "secretsmanager:GetSecretValue",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "elbv2:DescribeTargetGroups",
        "elbv2:DescribeLoadBalancers"
      ],
      "Resource": "*"
    }
  ]
}
```

**Blue-Green Deployment Configuration:**
- Minimum Healthy Percent: 100 (keeps all tasks running during deployment)
- Maximum Percent: 200 (allows new tasks alongside old)
- Desired Count: 2 tasks minimum
- Circuit Breaker: Enabled with automatic rollback
- Old tasks kept for 5 minutes post-switch

**Health Check Configuration:**
- Endpoint: `GET /health/`
- Expected Response: 200 OK with `{"status": "ok"}`
- Retries: 10 attempts
- Interval: 30 seconds between retries
- Timeout: 5 seconds per attempt

**Monitoring Deployment:**

```bash
# View deployment logs in GitHub Actions
# Navigate to: Actions → Deploy to Staging → Latest run

# Monitor ECS service status (via AWS CLI)
aws ecs describe-services \
  --cluster staging-cluster \
  --services backend-api-staging \
  --query 'services[0].events[:5]' \
  --output table

# Check health endpoint
curl https://staging.example.com/health/
```

**Manual Rollback (if needed):**

```bash
# Get previous task definition revision
aws ecs list-task-definitions \
  --family-prefix backend-api-staging \
  --sort DESC \
  --max-items 5

# Revert service to previous revision
aws ecs update-service \
  --cluster staging-cluster \
  --service backend-api-staging \
  --task-definition backend-api-staging:<PREVIOUS_REVISION>
```

### Branch Strategy

**CI Triggers:**
- Push to `main` or `develop` branches → Full CI pipeline runs
- Pull requests to any branch → Full CI pipeline runs

**Docker Build Triggers:**
- Push to `main` branch (after CI passes) → Build and push Docker image

**Deployment Triggers:**
- Docker build completes on `main` branch → Deploy to staging

**Why not all branches?**  
Running CI on every feature branch push (without a PR) is expensive and usually unnecessary. The current strategy ensures:
- All code going into main/develop is validated ✅
- All pull requests are checked before merge ✅
- Production images built only from main branch ✅
- Staging deployment automatic on main merge ✅
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
