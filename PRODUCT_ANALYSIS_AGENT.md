# Product Analysis Agent - Componentized Framework

A reusable framework for conducting comprehensive product market analysis of software repositories. This componentized system can be used across different projects to generate structured analysis reports covering market positioning, feature gaps, and strategic recommendations.

## 🏗️ Architecture

The product analysis agent is built with a modular architecture that allows for easy customization and reuse:

```
product_analysis/
├── __init__.py          # Main package exports
├── core.py              # ProductAnalysisAgent orchestrator
├── collectors.py        # Data collection from repositories
├── analyzers.py         # Feature, benchmark, and competitive analysis
├── templates.py         # Project-type specific analysis templates
└── generators.py        # Report building and markdown generation
```

### Core Components

1. **ProductAnalysisAgent** - Main orchestrator that coordinates the analysis process
2. **Data Collectors** - Gather repository structure, metadata, and project information
3. **Analyzers** - Specialized analysis for features, benchmarks, and competition
4. **Templates** - Domain-specific analysis criteria for different project types
5. **Report Generators** - Convert analysis results into structured markdown reports

## 🚀 Quick Start

### Basic Usage

```python
from product_analysis import ProductAnalysisAgent

# Initialize for a repository
agent = ProductAnalysisAgent('/path/to/repository')

# Run complete analysis and generate report
results, report_path = agent.run_full_analysis()

print(f"Analysis complete! Report saved to: {report_path}")
```

### Command Line Interface

```bash
# Analyze current directory with auto-detection
python product_analysis_cli.py .

# Analyze specific project type  
python product_analysis_cli.py /path/to/repo --type video-processing

# Custom output location
python product_analysis_cli.py . --output my-analysis.md --verbose
```

## 🎯 Supported Project Types

The framework includes built-in templates for different project types:

- **`video-processing`** - Video processing and computer vision tools
- **`web-framework`** - Web development frameworks and libraries  
- **`ml-library`** - Machine learning and data science tools
- **`cli-tool`** - Command-line applications
- **`generic-software`** - General software projects (fallback)

## 🔧 Customization

### Adding Custom Project Types

1. **Create a new template:**

```python
def _get_my_custom_template() -> AnalysisTemplate:
    return AnalysisTemplate(
        name="My Custom Project Type",
        description="Analysis template for my specific domain",
        feature_categories={
            "Core Features": [
                "Feature 1",
                "Feature 2",
                # ... more features
            ],
            "Integration": [
                "API Support",
                "Third-party Integration"
            ]
            # ... more categories
        },
        benchmark_criteria=[
            {
                "category": "Core Features",
                "market_standard": True,
                "weight": "high",
                "examples": ["Industry Tool 1", "Tool 2"]
            }
        ],
        competitor_categories={
            "Direct Competitors": [
                "Competitor 1 - Description",
                "Competitor 2 - Description"
            ]
        },
        roadmap_priorities=[
            "Priority 1",
            "Priority 2"
        ]
    )
```

2. **Register the template:**

```python
# In templates.py, add to get_template_for_project_type():
templates = {
    # ... existing templates
    'my-custom-type': _get_my_custom_template(),
}
```

### Custom Analysis Logic

You can override specific analyzers for specialized analysis:

```python
from product_analysis.analyzers import FeatureAnalyzer

class CustomFeatureAnalyzer(FeatureAnalyzer):
    def _detect_feature_presence(self, feature, repo_data, metadata):
        # Custom feature detection logic
        if feature == "My Special Feature":
            return self._check_for_special_feature(repo_data)
        return super()._detect_feature_presence(feature, repo_data, metadata)

# Use custom analyzer
agent = ProductAnalysisAgent('/path/to/repo')
agent.feature_analyzer = CustomFeatureAnalyzer(template.feature_categories)
```

## 📊 Analysis Output

The framework generates comprehensive reports with the following sections:

1. **Product Overview** - Value proposition, target audience, key differentiators
2. **Market Benchmarking** - Feature-by-feature comparison against market standards  
3. **Gap & Opportunity Report** - Strengths, critical gaps, and innovation opportunities
4. **Competitive Landscape** - Competitor analysis and market positioning
5. **Suggested Roadmap** - Prioritized development recommendations

### Example Output Structure

```markdown
# 📊 Product Market Analysis Report

## 1. Product Overview
- Repository Name: `project-name`
- Current Value Proposition: [Generated description]
- Target Audience: [Identified audience]

## 2. Market Benchmarking

| Feature | Market Standard? | Present in Repo? | Notes / Opportunity |
|---------|------------------|------------------|---------------------|
| Core Feature 1 | ✅ | ✅ | Matches market baseline |
| Advanced Feature | ✅ | ❌ | Critical gap – needed for production |

## 3. Gap & Opportunity Report
**Critical Missing Features:**
- Feature X (Category Y)
- Feature Z (Category A)

## 4. Competitive Landscape
**Direct Competitors:**
- Competitor A: Description and positioning
- Competitor B: Description and positioning

## 5. Suggested Roadmap Priorities
1. **Address Critical Gaps**: Focus on missing market standards
2. **Enhance Differentiation**: Build on unique strengths  
3. **Position for Growth**: Scale and expand market reach
```

## 🔍 Analysis Methodology

### Feature Detection

The framework uses pattern matching to detect features:

- **File structure analysis** - Looks for key directories and files
- **Dependency analysis** - Examines package requirements
- **Configuration analysis** - Checks build and deployment configs
- **Documentation analysis** - Scans README and docs for indicators

### Benchmarking Approach

Features are assessed against market standards:

- **Market Standard** - Whether the feature is expected in the domain
- **Present** - Whether the feature is detected in the project
- **Opportunity Level** - Critical, high, medium, or low priority
- **Notes** - Contextual information about the assessment

### Competitive Analysis

Competitive positioning is determined by:

- **Direct competitors** - Projects solving the same problem
- **Adjacent competitors** - Related tools in the broader space
- **Emerging competition** - New approaches or technologies
- **Market niche identification** - Unique positioning opportunities

## 🎯 Use Cases

### Repository Owners
- Understand market positioning and competitive landscape  
- Identify critical feature gaps and development priorities
- Get data-driven roadmap recommendations
- Compare against industry standards

### Product Managers  
- Conduct competitive analysis across multiple projects
- Generate standardized product assessments
- Track feature coverage and market alignment
- Support strategic planning with consistent analysis

### Open Source Maintainers
- Assess project maturity and completeness
- Identify areas for community contribution
- Understand differentiation opportunities
- Plan sustainable development roadmaps

## 🔄 Integration Examples

### CI/CD Integration

```yaml
name: Product Analysis
on: 
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run Product Analysis
      run: |
        python product_analysis_cli.py . --output analysis.md
    - name: Create PR with Analysis
      # ... create PR with updated analysis
```

### Multi-Repository Analysis

```python
import glob
from product_analysis import ProductAnalysisAgent

# Analyze multiple repositories
repositories = glob.glob('/projects/*/') 

for repo_path in repositories:
    print(f"Analyzing {repo_path}...")
    agent = ProductAnalysisAgent(repo_path)
    results, report_path = agent.run_full_analysis()
    print(f"Report: {report_path}")
```

### Custom Report Generation

```python
from product_analysis import ProductAnalysisAgent
from product_analysis.generators import AnalysisReportBuilder

agent = ProductAnalysisAgent('/path/to/repo')
results = agent.analyze()

# Custom report builder
builder = AnalysisReportBuilder()
report_data = builder.build_report(results, agent.template)

# Generate custom format (e.g., JSON, HTML, etc.)
import json
with open('analysis.json', 'w') as f:
    json.dump(report_data, f, indent=2)
```

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run specific test categories
pytest tests/ -m "not slow"  # Skip slow tests
```

### Adding New Features

1. Implement new analyzer logic in `analyzers.py`
2. Add corresponding template updates in `templates.py`  
3. Update report generation in `generators.py`
4. Add tests in `tests/test_product_analysis.py`

### Code Quality

The framework follows standard Python practices:

- Type hints throughout
- Comprehensive docstrings
- Modular, testable design
- Configurable and extensible architecture

## 📈 Future Enhancements

Planned improvements to the framework:

- **Plugin System** - Easy third-party extensions
- **Web Dashboard** - Interactive analysis reports
- **API Integration** - GitHub/GitLab data collection
- **ML-Powered Analysis** - Automated feature detection
- **Collaborative Analysis** - Team-based assessments
- **Historical Tracking** - Analysis over time