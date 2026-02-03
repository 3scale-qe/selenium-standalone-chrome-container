# Selenium Version Tracking

This directory contains version tracking for the Selenium standalone-chromium base image (multi-arch: amd64, arm64).

## Version File

All version information is stored in a single file: **versions.yaml**

### Structure

**versions.yaml** - Version tracking for discovery and testing:
```yaml
stable:
  version: "144.0-20260120"
  updated_at: "2026-02-03"
  description: "Production version"

candidate:
  version: "144.0-20260120"
  updated_at: "2026-02-03"
  description: "Version under evaluation"

latest_tested:
  version: "144.0-20260120"
  updated_at: "2026-02-03"
  description: "Most recent tested version"

previous_stable:
  version: "144.0-20260120"
  updated_at: "2026-02-03"
  description: "Rollback target"
```

**deployment-log.yaml** - Current deployment tracking:
```yaml
latest:
  selenium_version: "144.0-20260120"
  deployed_at: "2026-02-03"
  image_tag: "latest"
  description: "Current latest build (auto-deployed after testing)"

stable:
  selenium_version: "144.0-20260120"
  deployed_at: "2026-02-03"
  image_tag: "stable"
  description: "Current production stable build"
```

### Version Sections

**stable** - Current production version
- Updated only through the "Promote to Stable" workflow (manual)
- Should always point to a tested, verified version
- Used for production deployments

**candidate** - Version under evaluation
- Auto-updated by the "Discover Selenium Version" workflow (1st & 15th of month)
- Triggers automatic testing when updated
- May not be tested or stable

**latest_tested** - Most recent tested version
- Updated automatically when test-and-deploy workflow succeeds
- Default target for promotion to stable
- Safe to promote, but awaits manual approval

**previous_stable** - Rollback version
- Updated when a new version is promoted to stable
- Used for rollback if issues are discovered
- Provides safety net for quick recovery

## Workflows

### 1. Automated Discovery & Deploy (1st & 15th of month, 12:00 UTC)
- Queries Docker Hub for latest selenium/standalone-chromium version
- If newer version found:
  - Updates candidate version
  - Builds multi-arch image (amd64, arm64)
  - Runs comprehensive smoke tests
  - **If tests pass**: Auto-deploys as `latest` and date tag
  - **If tests fail**: Creates GitHub issue
- Fully automated, no manual intervention

### 2. Manual Promote to Stable
- Takes any existing image tag (default: `latest`)
- Re-tags as `stable`
- Backs up current stable to previous_stable
- Updates version tracking and deployment log
- Use when ready for production

## Version Format

Versions follow the format: `X.Y.Z-YYYYMMDD`

Example: `100.0-20250525`
- `100.0` = Selenium Grid version
- `20250525` = Image build date (May 25, 2025)

## Accessing Version Information

### Current Versions
```bash
# Read stable version
yq eval '.stable.version' .selenium-versions/versions.yaml

# Read candidate version
yq eval '.candidate.version' .selenium-versions/versions.yaml

# Read latest tested version
yq eval '.latest_tested.version' .selenium-versions/versions.yaml
```

### Deployment Status
```bash
# Check what's currently deployed as latest
yq eval '.latest' .selenium-versions/deployment-log.yaml

# Check what's currently deployed as stable
yq eval '.stable' .selenium-versions/deployment-log.yaml
```

## Typical Workflow

```
1st & 15th at 12:00 UTC
  ↓
Discovery finds new version
  ↓
Updates candidate version → Triggers test
  ↓
Tests pass → Auto-deploy as latest + date tag
  ↓
Updates latest_tested version
  ↓
Manual review
  ↓
Promote to stable (manual workflow)
```

## Manual Operations

### Promote Latest to Stable
```bash
gh workflow run promote-to-stable.yaml
```

### Promote Specific Tag to Stable
```bash
gh workflow run promote-to-stable.yaml -f source_tag=20260203
```

### Test Specific Version
```bash
gh workflow run test-and-deploy.yaml -f version=144.0-20260120
```

### Rollback to Previous Version
```bash
# Check previous version
yq eval '.previous_stable.version' .selenium-versions/versions.yaml

# Promote it
gh workflow run promote-stable.yaml -f version=$(yq eval '.previous_stable.version' .selenium-versions/versions.yaml)
```

## Local Testing

To test a specific version locally:

```bash
# Build with specific version
docker build --build-arg SELENIUM_VERSION=100.0-20250525 -t test-selenium .

# Run container
docker run -d --name selenium --shm-size=2g -p 4444:4444 test-selenium

# Run smoke tests
pip install selenium requests
python3 tests/smoke-test.py

# Clean up
docker stop selenium
docker rm selenium
```
