# Test Code Coverage Reports

This folder maintains comprehensive code coverage analysis and reports for the VisionCrafterAI backend.

## Folder Structure

```
coverage_reports/
├── README.md                              # This file
├── COVERAGE_TRACKING.md                   # Coverage trends & history
│
├── reports/                               # Generated HTML & PDF coverage reports
│   ├── 2026-04-03_coverage_report.html    # Latest HTML report (from --cov-report=html)
│   ├── VisionCrafterAI_Coverage_Report.docx # Professional Word document
│   └── coverage_archive/                  # Historical reports by date
│       └── 2026-04/
│
├── data/                                  # Raw coverage data & JSON exports
│   ├── coverage.json                      # Latest JSON coverage data (from --cov-report=json)
│   ├── coverage_data.csv                  # Csv format for spreadsheet analysis
│   └── historical/                        # Previous coverage snapshots
│       └── 2026-04-03_coverage.json
│
├── configs/                               # Coverage configuration files
│   ├── pytest.ini                         # Pytest configuration with coverage settings
│   ├── .coveragerc                        # Coverage.py configuration
│   └── conftest.py                        # Pytest fixtures and configuration
│
├── analysis/                              # Coverage analysis & reports
│   ├── missing_coverage_analysis.md       # Detailed gaps & recommendations
│   ├── module_coverage_breakdown.json     # Per-module coverage statistics
│   └── coverage_trends.json               # Historical coverage trends
│
└── scripts/
    ├── run_coverage.sh                    # Script to run coverage with standard settings
    ├── generate_coverage_report.py        # Generate Word document from data
    └── track_coverage_trend.py            # Track coverage over time
```

## Quick Start

### Generate Coverage Report
```bash
# From project root
source .venv/bin/activate

# Run tests with coverage
pytest testOutputs/tests/ --cov=app --cov-report=term-missing --cov-report=html:testOutputs/coverage_reports/reports/coverage_html --cov-report=json:testOutputs/coverage_reports/data/coverage.json

# Generate HTML report (opens in browser)
open testOutputs/coverage_reports/reports/coverage_html/index.html
```

### View Latest Report
```bash
open testOutputs/coverage_reports/VisionCrafterAI_Coverage_Report.docx
```

## Coverage Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Overall Coverage | 94.53% | ✅ Excellent |
| Total Statements | 1,042 | |
| Covered Statements | 985 | |
| Missing Statements | 57 | |
| Test Cases | 48 | All Passing ✅ |

## Key Coverage Areas

- **Authentication (auth.py)**: 95.17% ✅
- **Project Management (project.py)**: 93.68% ✅
- **Security Utils (security.py)**: 94.87% ✅
- **ImageKit Integration (imagekit.py)**: 94.87% ✅
- **User Models (user.py)**: 100.00% ✅
- **Database (database.py)**: 91.18% 🟡 (Connection & transaction edge cases)

## Coverage Gaps

See `analysis/missing_coverage_analysis.md` for detailed info on:
- Which lines are not covered
- Why they're not tested
- Recommended test cases to add

## CI/CD Integration

Add to your GitHub Actions:

```yaml
- name: Run coverage tests
  run: |
    pytest --cov=app --cov-report=json:coverage.json --cov-fail-under=85
```

This ensures:
- Coverage reports are generated every build
- Build fails if coverage drops below 85%
- JSON reports are archived for trend analysis

## Best Practices

1. **Run coverage regularly**: Before each commit or PR
2. **Track trends**: Use `scripts/track_coverage_trend.py` to monitor progress
3. **Fix gaps**: Address missing coverage items from the gap analysis
4. **Archive reports**: Save reports before merging major features
5. **Review with team**: Include coverage metrics in code review process

## Tools Used

- **pytest**: Python testing framework
- **pytest-cov**: Coverage plugin for pytest
- **coverage.py**: Core coverage measurement
- **python-docx**: Generate Word documents

## Related Documents

- `../unit_test_cases.docx` - Test case documentation
- `../test_visioncrafter.py` - Consolidated test suite
- `../../app/` - Application source code
