# Selenium Standalone Chromium Container

Custom Docker image based on `selenium/standalone-chromium` with enterprise CA certificate support and multi-architecture builds.

## Features

- Based on official Selenium standalone Chromium images
- **Multi-architecture support: AMD64 and ARM64** (Apple Silicon, AWS Graviton, etc.)
- Custom CA certificate installation for enterprise environments
- Automated version discovery and testing
- Pinned Selenium versions for reproducible builds
- Comprehensive smoke testing pipeline

## Quick Start

### Pull from Quay.io

```bash
# Latest stable version (automatically pulls correct architecture)
docker pull quay.io/rh_integration/selenium-standalone-chrome:stable

# Specific date tag
docker pull quay.io/rh_integration/selenium-standalone-chrome:20260202

# Latest build (may be unstable)
docker pull quay.io/rh_integration/selenium-standalone-chrome:latest

# Specific architecture (if needed)
docker pull --platform linux/amd64 quay.io/rh_integration/selenium-standalone-chrome:stable
docker pull --platform linux/arm64 quay.io/rh_integration/selenium-standalone-chrome:stable
```

### Run Container

```bash
docker run -d -p 4444:4444 --shm-size=2g \
  quay.io/rh_integration/selenium-standalone-chrome:stable
```

### Use with Selenium Client

```python
from selenium import webdriver

options = webdriver.ChromeOptions()
driver = webdriver.Remote(
    command_executor='http://localhost:4444',
    options=options
)

driver.get('https://www.example.com')
# Your test code here
driver.quit()
```

## Version Management

This repository uses an automated version discovery and testing system to maintain stable Selenium images.

### Version Tracking

All Selenium versions are tracked in a single organized file: `.selenium-versions/versions.yaml`

```yaml
stable:          # Current production version (manual promotion)
candidate:       # Version under evaluation (auto-discovered bi-weekly: 1st & 15th)
latest_tested:   # Most recent successfully tested version
previous_stable: # Rollback target
```

Each section contains version, updated_at, and description fields.

See [.selenium-versions/README.md](.selenium-versions/README.md) for details.

### Automated Workflows

#### Automated Discovery & Deploy (1st & 15th, 12:00 UTC)
- Automatically checks for new Selenium versions
- Updates candidate version if newer version found
- Builds multi-arch image (amd64, arm64)
- Runs comprehensive smoke tests:
  1. Container health check
  2. WebDriver connection test
  3. Real browser interaction test
- **If tests pass**: Auto-deploys as `latest` and date tag (YYYYMMDD)
- **If tests fail**: Creates GitHub issue with failure details
- Fully automated, no manual intervention needed

#### Manual Promotion to Stable
- Promotes any existing image tag (default: `latest`) to `stable`
- Re-tags and pushes as stable
- Updates version tracking and deployment log
- Creates git tag for audit trail
- Backs up previous stable version for rollback
- Run when ready for production

### Manual Operations

```bash
# Promote latest to stable (most common)
gh workflow run promote-to-stable.yaml

# Promote specific tag to stable
gh workflow run promote-to-stable.yaml -f source_tag=20260203

# Test a specific version (without auto-deploy)
gh workflow run test-and-deploy.yaml -f version=144.0-20260120

# Test and auto-deploy as latest
gh workflow run test-and-deploy.yaml -f version=144.0-20260120 -f auto_deploy=true

# Force discovery check
gh workflow run discover-selenium-version.yaml

# Manual emergency build
gh workflow run release.yaml -f release_tag=latest
```

## Building Locally

### Prerequisites

- Docker or Podman
- CA certificate file (for enterprise environments)

### Build

```bash
# Build with default stable version
docker build -t selenium-chrome .

# Build with specific Selenium version
docker build --build-arg SELENIUM_VERSION=100.0-20250525 -t selenium-chrome .

# Build with custom CA certificate
docker build --build-arg customca=./my-ca-cert.crt -t selenium-chrome .
```

### Test

```bash
# Start container
docker run -d --name selenium -p 4444:4444 --shm-size=2g selenium-chrome

# Install test dependencies
pip install -r tests/requirements.txt

# Run smoke tests
python3 tests/smoke-test.py

# Clean up
docker stop selenium && docker rm selenium
```

## CI/CD Workflows

### Automated Discovery & Deploy (1st & 15th, 12:00 UTC)
- Discovers new Selenium versions from Docker Hub
- Builds and tests automatically
- Auto-deploys as `latest` and date tag if tests pass
- Updates deployment log with latest build info
- **No manual intervention needed**

### Manual Promotion to Stable
- Promotes `latest` (or any tag) to `stable`
- Run when ready for production
- Updates version tracking and deployment log
- Backs up previous stable for rollback

### Manual Emergency Build
- Trigger via GitHub Actions for emergency builds
- Bypass normal workflow if needed
- Use for testing specific versions or urgent fixes

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── discover-selenium-version.yaml  # Auto-discover & deploy (1st & 15th)
│       ├── test-and-deploy.yaml            # Test and optionally deploy versions
│       ├── promote-to-stable.yaml          # Promote any tag to stable
│       └── release.yaml                    # Manual emergency builds
├── .selenium-versions/
│   ├── versions.yaml                       # All version tracking (stable, candidate, tested, previous)
│   ├── deployment-log.yaml                 # Current deployment status (latest, stable)
│   └── README.md                           # Version management docs
├── tests/
│   ├── smoke-test.py                       # Comprehensive test suite
│   └── requirements.txt                    # Python dependencies
├── Dockerfile                               # Image definition
└── README.md                               # This file
```

## Dockerfile Details

The Dockerfile:
1. Uses pinned Selenium Chromium version via `SELENIUM_VERSION` build arg
2. Supports multi-architecture builds (linux/amd64, linux/arm64)
3. Installs custom CA certificate from build arg
4. Updates system CA certificates
5. Adds CA to Chromium's NSS database
6. Maintains Selenium user permissions

## Troubleshooting

### Container won't start
- Ensure you have enough shared memory: `--shm-size=2g`
- Check container logs: `docker logs <container-name>`
- On ARM64: Verify you're using a compatible version (Chromium-based images support ARM64)

### Tests failing
- Verify Selenium Grid is ready: `curl http://localhost:4444/wd/hub/status`
- Check Chromium version matches ChromeDriver
- Review test artifacts in GitHub Actions

### Certificate issues
- Ensure CA certificate is valid PEM format
- Check certificate is installed: `docker exec <container> ls /usr/local/share/ca-certificates/`
- Verify Chromium trusts certificate: `docker exec <container> certutil -L -d sql:$HOME/.pki/nssdb`

### Architecture issues
- Check which architecture you're running: `docker inspect <image> | grep Architecture`
- Apple Silicon (M1/M2/M3): Uses ARM64 automatically
- AWS Graviton: Uses ARM64 automatically
- Intel/AMD processors: Uses AMD64 automatically

### Version rollback
```bash
# Check all current versions
cat .selenium-versions/versions.yaml

# Check previous stable version
yq eval '.previous_stable.version' .selenium-versions/versions.yaml

# Promote previous version back to stable
PREV_VERSION=$(yq eval '.previous_stable.version' .selenium-versions/versions.yaml)
gh workflow run promote-stable.yaml -f version=$PREV_VERSION
```

## Contributing

1. Test changes locally first
2. Run smoke tests to verify functionality
3. Update documentation if adding features
4. Create pull request with clear description

## License

Apache-2.0

## Maintainers

3scale QE Team
