# Selenium Version Tracking

This directory contains version tracking for the Selenium standalone-chromium base image (multi-arch: amd64, arm64).

## Version File

All version information is stored in a single file: **versions.yaml**

### Structure

```yaml
stable:
  version: "100.0-20250525"
  updated_at: "2026-02-02"
  description: "Production version used by release.yaml workflow"

candidate:
  version: "144.0-20260120"
  updated_at: "2026-02-02"
  description: "Version under evaluation, triggers automatic testing"

latest_tested:
  version: "100.0-20250525"
  updated_at: "2026-02-02"
  description: "Most recent version that passed all smoke tests"

previous_stable:
  version: "100.0-20250525"
  updated_at: "2026-02-02"
  description: "Backup of previous stable for rollback"
```

### Version Sections

**stable** - Current production version
- Used by the scheduled 1st and 15th builds (release.yaml)
- Updated only through the "Promote Stable" workflow
- Should always point to a tested, verified version

**candidate** - Version under evaluation
- Auto-updated by the "Discover Selenium Version" workflow (Saturdays)
- Triggers automatic testing when updated
- May not be tested or stable

**latest_tested** - Most recent tested version
- Updated automatically when test-candidate workflow succeeds
- Default target for promotion to stable
- Safe to promote, but awaits manual approval

**previous_stable** - Rollback version
- Updated when a new version is promoted to stable
- Used for rollback if issues are discovered
- Provides safety net for quick recovery

## Workflows

### 1. Discover Selenium Version (Saturdays, 12:00 UTC)
- Queries Docker Hub for latest selenium/standalone-chromium version
- Compares with current candidate version
- If newer: updates candidate and triggers testing

### 2. Test Candidate
- Builds multi-arch image (amd64, arm64) with candidate version
- Runs comprehensive smoke tests
- On success: tags as `tested-<version>` and updates latest_tested
- On failure: creates GitHub issue with details

### 3. Promote Stable (Manual)
- Promotes tested version to stable
- Backs up current stable to previous_stable
- Rebuilds multi-arch image and pushes with `stable` and date tags
- Creates git tag and announcement issue

## Version Format

Versions follow the format: `X.Y.Z-YYYYMMDD`

Example: `100.0-20250525`
- `100.0` = Selenium Grid version
- `20250525` = Image build date (May 25, 2025)

## Accessing Versions

```bash
# Read stable version
yq eval '.stable.version' .selenium-versions/versions.yaml

# Read candidate version
yq eval '.candidate.version' .selenium-versions/versions.yaml

# Read latest tested version
yq eval '.latest_tested.version' .selenium-versions/versions.yaml

# Read previous stable version
yq eval '.previous_stable.version' .selenium-versions/versions.yaml
```

## Typical Workflow

```
Saturday 12:00 UTC
  ↓
Discovery finds new version
  ↓
Updates candidate.yaml → Triggers test
  ↓
Tests pass → Tag as tested-<version>
  ↓
Manual review
  ↓
Promote to stable
  ↓
1st and 15th 00:00 UTC
  ↓
Scheduled build uses stable version
```

## Manual Operations

### Promote Latest Tested Version
```bash
gh workflow run promote-stable.yaml
```

### Promote Specific Version
```bash
gh workflow run promote-stable.yaml -f version=100.0-20250525
```

### Test Specific Version
```bash
gh workflow run test-candidate.yaml -f version=100.0-20250525
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
