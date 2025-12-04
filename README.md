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

### Security Scanning Pipeline

Automated security vulnerability scanning is integrated into the CI pipeline to identify and prevent security issues.

**Security Scanning Workflow:**
- Triggers on every push and pull request (after code quality checks, before tests)
- Completes in < 2 minutes
- High-severity issues fail the workflow and block merging
- Medium/low severity issues logged as warnings

**Security Tools:**

#### 1. Bandit Python Security Linter

Scans Python code for common security vulnerabilities.

**What it detects:**
- SQL injection vulnerabilities
- Hardcoded passwords or secrets
- Insecure cryptographic usage (MD5, SHA1)
- Use of `eval()` or `exec()` (arbitrary code execution)
- Pickle usage (insecure deserialization)
- Shell injection vulnerabilities
- Path traversal vulnerabilities
- XML external entity (XXE) vulnerabilities

**Severity Levels:**
- **HIGH** → Workflow FAILS (blocks merge)
- **MEDIUM** → Warning only (workflow continues)
- **LOW** → Informational (workflow continues)

**Run Bandit Locally:**

```bash
# Install Bandit
pip install bandit

# Scan backend directory
bandit -r backend/ -f json -o bandit-report.json

# View report
cat bandit-report.json
```

**View Security Reports:**
1. Navigate to GitHub Actions → CI Pipeline workflow
2. Click on a workflow run
3. Scroll to "Artifacts" section
4. Download `bandit-security-report` artifact
5. Reports retained for 90 days

#### 2. Dependabot Dependency Scanning

Automatically scans Python dependencies for known vulnerabilities (CVEs) and creates pull requests to update vulnerable packages.

**Configuration:**
- Scans: `backend/requirements.txt` and `backend/requirements-dev.txt`
- Schedule: Daily at 00:00 UTC
- Automatic PR creation for security updates
- Groups critical/high severity updates together

**Reviewing Dependabot PRs:**
1. Check PR description for vulnerability details (CVE links, severity)
2. Review changelog and breaking changes
3. Verify tests pass in CI
4. Merge promptly (especially for critical/high severity)

**Monitor Dependabot:**
- GitHub UI → Settings → Security → Dependabot
- View open security alerts
- Check PR update schedule

#### 3. GitHub Secret Scanning

Prevents accidental exposure of secrets (API keys, passwords, tokens) in commits.

**Enabling Secret Scanning:**

1. Navigate to repository Settings → Security
2. Enable "Secret scanning"
3. Enable "Push protection" (blocks commits containing secrets)
4. Enable "Dependabot alerts"

**Note:** GitHub Advanced Security may be required for private repositories.

**What it detects:**
- API keys (AWS, Stripe, etc.)
- Database connection strings
- Django `SECRET_KEY`
- OAuth tokens
- Private SSH/TLS keys
- Password literals

**If a secret is exposed:**
1. **Revoke the secret immediately** (rotate API key, change password)
2. Remove the secret from code
3. Add to `.env` file (gitignored) for local development
4. Use GitHub Secrets for CI/CD
5. Use AWS Secrets Manager for production runtime

### Security Best Practices

**Never commit secrets to the repository:**

```bash
# ❌ NEVER do this
DATABASE_URL = "postgresql://user:password@host/db"
STRIPE_SECRET_KEY = "sk_live_abc123..."

# ✅ DO THIS instead
# In code
DATABASE_URL = os.environ.get("DATABASE_URL")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

# In local development (.env file, gitignored)
DATABASE_URL=postgresql://user:password@localhost/db
STRIPE_SECRET_KEY=sk_test_abc123

# In CI/CD (GitHub Secrets)
# Settings → Secrets → Actions → New repository secret

# In production (AWS Secrets Manager)
aws secretsmanager create-secret \
  --name staging/backend/stripe-secret-key \
  --secret-string "sk_live_abc123..."
```

**Regularly update dependencies:**

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements file
pip freeze > backend/requirements.txt
```

**Review security findings promptly:**
- Check Dependabot PRs daily
- Investigate Bandit high-severity findings immediately
- Review secret scanning alerts within 24 hours

**Follow secure coding practices:**
- Use parameterized queries (prevent SQL injection)
- Validate and sanitize user input
- Use Django's built-in security features (CSRF, XSS protection)
- Keep dependencies up to date
- Use HTTPS everywhere
- Implement proper authentication and authorization

### Remediation Procedures

#### Fixing Bandit Security Findings

1. **Review the finding:**
   - Download `bandit-security-report` artifact from GitHub Actions
   - Identify: file, line number, issue type, severity

2. **Common fixes:**

   **Hardcoded password:**
   ```python
   # ❌ Before
   password = "admin123"
   
   # ✅ After
   password = os.environ.get("ADMIN_PASSWORD")
   ```

   **SQL injection vulnerability:**
   ```python
   # ❌ Before
   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
   
   # ✅ After
   cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
   ```

   **Insecure cryptography:**
   ```python
   # ❌ Before
   import hashlib
   hashlib.md5(password.encode())
   
   # ✅ After
   from django.contrib.auth.hashers import make_password
   make_password(password)
   ```

3. **Verify fix:**
   ```bash
   bandit -r backend/ -f json -o bandit-report.json
   # Check that issue is resolved
   ```

4. **Commit and push** - CI will re-scan automatically

#### Handling Exposed Secrets

1. **Immediate action:**
   - **Revoke/rotate the secret NOW** (don't wait)
   - Exposed secrets should be considered compromised

2. **Remove from code:**
   ```bash
   # Remove secret from current commit
   git reset HEAD~1
   # Edit file to remove secret
   # Commit without secret
   
   # If already pushed, rewrite history (coordinate with team)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (⚠️ coordinate with team)
   git push origin --force --all
   ```

3. **Use proper secret management:**
   - Local: `.env` file (add to `.gitignore`)
   - CI/CD: GitHub Secrets
   - Production: AWS Secrets Manager

#### Updating Vulnerable Dependencies

1. **Review Dependabot PR:**
   - Check vulnerability details (CVE link, severity)
   - Review changelog for breaking changes
   - Check if tests pass

2. **Update locally (if needed):**
   ```bash
   # Update specific package
   pip install --upgrade package-name==X.Y.Z
   
   # Update requirements
   pip freeze > backend/requirements.txt
   
   # Run tests
   pytest backend/tests/
   ```

3. **Merge Dependabot PR** - tests pass + no breaking changes

4. **Monitor deployment** - verify staging environment after update

### Security Resources

- **Bandit Documentation:** https://bandit.readthedocs.io/
- **Dependabot Documentation:** https://docs.github.com/en/code-security/dependabot
- **GitHub Secret Scanning:** https://docs.github.com/en/code-security/secret-scanning
- **Django Security:** https://docs.djangoproject.com/en/stable/topics/security/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/

### Production Deployment Pipeline

Controlled deployment to production environment requiring manual approval and semantic version tags.

**Deployment Workflow:**
- Triggers on semantic version tag push (e.g., `v1.0.0`, `v2.1.3`)
- Requires manual approval from designated reviewers (GitHub Environment protection)
- Creates RDS database snapshot before migrations
- Runs database migrations
- Deploys with blue-green strategy (zero downtime)
- Performs health checks with automatic rollback on failure
- Completes in < 15 minutes (excluding approval wait time)

**Deployment Steps:**
1. **Tag Validation** - Verify semantic versioning format (v*.*.*)
2. **Manual Approval** - Designated reviewers approve deployment (24-hour timeout)
3. **Database Backup** - RDS snapshot created automatically (30-day retention)
4. **Update Task Definition** - New Docker image (version-tagged) registered to ECS
5. **Run Migrations** - Django migrations executed as one-off task
6. **Service Update** - ECS service updated with circuit breaker enabled
7. **Health Check** - /health/ endpoint validated (10 retries, 30s intervals)
8. **Rollback** - Automatic revert to previous version on failure

**How to Deploy to Production:**

1. **Create and push semantic version tag:**

   ```bash
   # Create a release tag (semantic versioning)
   git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
   
   # Push tag to GitHub (triggers deployment workflow)
   git push origin v1.0.0
   ```

2. **Approve deployment:**
   - Navigate to: Actions → Production Deployment → Pending approval
   - Review deployment details
   - Click "Review deployments" → Select "production" → "Approve and deploy"
   - Deployment proceeds automatically after approval

3. **Monitor deployment:**

   ```bash
   # View deployment logs in GitHub Actions
   # Navigate to: Actions → Production Deployment → Latest run
   
   # Monitor ECS service status (via AWS CLI)
   aws ecs describe-services \
     --cluster seaside-backend-cluster \
     --services seaside-backend-prod \
     --query 'services[0].events[:5]' \
     --output table
   
   # Check health endpoint
   curl https://api.seasidetech.co/health/
   ```

**GitHub Environment Setup (One-Time Configuration):**

To enable manual approval gate, configure the `production` environment in GitHub:

1. **Create Environment:**
   - Navigate to: Settings → Environments → New Environment
   - Name: `production`
   - Click "Configure environment"

2. **Add Protection Rules:**
   - Enable "Required reviewers"
   - Add reviewers: PM, lead dev, or backend-team
   - Set wait timer (optional): 5 minutes cooldown before allowing approval
   - Enable "Prevent administrators from bypassing configured protection rules"

3. **Add Environment Secrets (if needed):**
   - Add production-specific secrets (if different from repository secrets)
   - Example: `PRODUCTION_DATABASE_URL` (reference to AWS Secrets Manager ARN)

**AWS Infrastructure Requirements:**

```yaml
# GitHub Repository Secrets Required
AWS_ACCESS_KEY_ID: <IAM user access key for production>
AWS_SECRET_ACCESS_KEY: <IAM user secret key for production>
AWS_REGION: <region, e.g., us-west-2>
```

**ECS Task Definition:**
- Task: `seaside-backend-prod`
- CPU: 2048 (2 vCPU)
- Memory: 4096 MB (4 GB)
- Network Mode: awsvpc
- Port: 8000
- Launch Type: Fargate
- Desired Count: 2+ tasks minimum

**RDS Configuration:**
- Instance: `seaside-backend-prod`
- Engine: PostgreSQL 16
- Snapshot retention: 30 days minimum
- Automated backups: Enabled

**Environment Variables (AWS Secrets Manager):**
- `DATABASE_URL` → Secret: `production/backend/database-url`
- `REDIS_URL` → Secret: `production/backend/redis-url`
- `DJANGO_SECRET_KEY` → Secret: `production/backend/django-secret-key`
- `DJANGO_SETTINGS_MODULE=seaside.settings.prod`
- `AWS_S3_BUCKET_NAME` → Secret: `production/backend/s3-bucket-name`
- `STRIPE_SECRET_KEY` → Secret: `production/backend/stripe-secret-key`

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
        "rds:CreateDBSnapshot",
        "rds:DescribeDBSnapshots",
        "rds:ModifyDBSnapshot",
        "secretsmanager:GetSecretValue",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:FilterLogEvents",
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
- Desired Count: 2+ tasks minimum
- Circuit Breaker: Enabled with automatic rollback
- Health Check Grace Period: 5 minutes

**Health Check Configuration:**
- Endpoint: `GET https://api.seasidetech.co/health/`
- Expected Response: 200 OK with `{"status": "ok"}`
- Retries: 10 attempts
- Interval: 30 seconds between retries
- Timeout: 5 seconds per attempt

**Automatic Rollback (on health check failure):**

If health checks fail after deployment:
1. Workflow automatically reverts ECS service to previous task definition
2. CloudWatch Logs captured and uploaded as workflow artifact
3. Deployment marked as FAILED in GitHub Actions
4. Database snapshot available for manual rollback if needed
5. Rollback notification sent

**Manual Rollback Procedures:**

If you need to rollback to a previous version:

1. **Trigger Rollback Workflow:**

   ```bash
   # Via GitHub Actions UI:
   # 1. Navigate to: Actions → Production Rollback → Run workflow
   # 2. Select branch: main
   # 3. Enter target version (e.g., v1.0.0)
   # 4. Select database rollback option (if migrations need reverting)
   # 5. Click "Run workflow"
   ```

2. **Approve Rollback:**
   - Same approval process as deployment
   - Designated reviewers must approve rollback

3. **Rollback completes automatically:**
   - ECS service reverted to target version
   - Health checks validated
   - Rollback notification sent

**Database Rollback (Manual - if needed):**

If database migrations need to be rolled back:

**Option 1: Restore from RDS Snapshot**

```bash
# 1. Identify snapshot for target version
aws rds describe-db-snapshots \
  --db-instance-identifier seaside-backend-prod \
  --query 'DBSnapshots[?contains(DBSnapshotIdentifier, `v1.0.0`)]' \
  --output table

# 2. Restore from snapshot (creates new instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier seaside-backend-prod-restored \
  --db-snapshot-identifier prod-db-backup-v1.0.0-20250203-120000

# 3. Wait for restore to complete
aws rds wait db-instance-available \
  --db-instance-identifier seaside-backend-prod-restored

# 4. Update ECS task definition to point to restored instance
# 5. OR: Rename restored instance to replace production instance
```

**Option 2: Run Reverse Migrations**

```bash
# Connect to production database and run reverse migration:
# Find the migration you want to revert to:
python manage.py showmigrations

# Revert to specific migration:
python manage.py migrate <app_name> <migration_number>

# Example:
python manage.py migrate repairs 0005_add_line_items
```

**Recovery Time Objectives (RTO):**
- Automatic Rollback: ~5-10 minutes (automatic)
- Manual ECS Rollback: ~10-15 minutes (workflow-based)
- Database Snapshot Restore: ~15-30 minutes (manual)
- Reverse Migrations: ~5-10 minutes (depends on migration complexity)

**Deployment Best Practices:**

1. **Test in Staging First:**
   - Always deploy and test in staging before production
   - Verify migrations run successfully
   - Validate health checks pass

2. **Create Meaningful Release Tags:**
   ```bash
   # Good release tag messages
   git tag -a v1.0.0 -m "Release v1.0.0: Initial production release with core features"
   git tag -a v1.1.0 -m "Release v1.1.0: Add payment processing and invoicing"
   git tag -a v1.1.1 -m "Release v1.1.1: Hotfix for invoice PDF generation bug"
   ```

3. **Monitor After Deployment:**
   - Check CloudWatch Logs for errors
   - Monitor ECS service metrics (CPU, memory, task count)
   - Verify health endpoint responds correctly
   - Monitor application-level metrics

4. **Have Rollback Plan Ready:**
   - Know the previous stable version
   - Have communication plan for rollback
   - Document any manual steps needed

### Branch Strategy

**CI Triggers:**
- Push to `main` or `develop` branches → Full CI pipeline runs
- Pull requests to any branch → Full CI pipeline runs

**Docker Build Triggers:**
- Push to `main` branch (after CI passes) → Build and push Docker image

**Deployment Triggers:**
- Docker build completes on `main` branch → Deploy to staging
- Semantic version tag push (v*.*.*) → Deploy to production (with manual approval)

**Why not all branches?**  
Running CI on every feature branch push (without a PR) is expensive and usually unnecessary. The current strategy ensures:
- All code going into main/develop is validated ✅
- All pull requests are checked before merge ✅
- Production images built only from main branch ✅
- Staging deployment automatic on main merge ✅
- Production deployment requires semantic version tags and manual approval ✅
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
