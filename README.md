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
stable:          # Current production version (scheduled builds: 1st & 15th)
candidate:       # Version under evaluation (auto-discovered weekly)
latest_tested:   # Most recent successfully tested version
previous_stable: # Rollback target
```

Each section contains version, updated_at, and description fields.

See [.selenium-versions/README.md](.selenium-versions/README.md) for details.

### Automated Workflows

#### Discovery (Saturdays, 12:00 UTC)
- Automatically checks for new Selenium versions
- Updates candidate version if newer version available
- Triggers automated testing

#### Testing
- Builds candidate image
- Runs comprehensive smoke tests:
  1. Container health check
  2. WebDriver connection test
  3. Real browser interaction test
- On success: tags as `tested-<version>`
- On failure: creates GitHub issue

#### Promotion (Manual)
- Promotes tested version to stable
- Rebuilds and pushes with `stable` tag
- Creates git tag for audit trail
- Backs up previous version for rollback

### Manual Operations

```bash
# Promote latest tested version to stable
gh workflow run promote-stable.yaml

# Promote specific version
gh workflow run promote-stable.yaml -f version=100.0-20250525

# Test a specific version
gh workflow run test-candidate.yaml -f version=100.0-20250525

# Force discovery check
gh workflow run discover-selenium-version.yaml
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

### Scheduled Build (1st and 15th of each month, 00:00 UTC)
- Builds image with stable Selenium version
- Pushes to Quay.io with date tag
- Used for regular production releases

### Manual Release
- Trigger via GitHub Actions
- Specify custom release tag
- Useful for emergency builds or custom tags

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── discover-selenium-version.yaml  # Auto-discover new versions
│       ├── test-candidate.yaml             # Test candidate versions
│       ├── promote-stable.yaml             # Promote to stable
│       └── release.yaml                    # Scheduled/manual builds
├── .selenium-versions/
│   ├── versions.yaml                       # All version tracking (stable, candidate, tested, previous)
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
