# 🧩 Componentized Product Analysis Agent - Usage Guide

This guide demonstrates how to use the componentized product analysis agent across different types of repositories and projects.

## 🎯 Quick Start Examples

### Analyze Any Repository

```bash
# Clone this framework to any repository
cp -r product_analysis/ /path/to/target/repo/
cp product_analysis_cli.py /path/to/target/repo/

# Run analysis
cd /path/to/target/repo
python product_analysis_cli.py . --verbose
```

### Programmatic Usage

```python
from product_analysis import ProductAnalysisAgent

# Auto-detect project type
agent = ProductAnalysisAgent('/path/to/repository')
results, report_path = agent.run_full_analysis()

# Specific project type  
agent = ProductAnalysisAgent('/path/to/repo', 'web-framework')
results = agent.analyze()
```

## 🏗️ Framework Structure

```
your-repository/
├── product_analysis/           # Copy this framework
│   ├── __init__.py
│   ├── core.py                # Main orchestrator
│   ├── collectors.py          # Repository data collection
│   ├── analyzers.py           # Feature & competitive analysis
│   ├── templates.py           # Domain-specific templates
│   └── generators.py          # Report generation
├── product_analysis_cli.py    # Command-line interface
└── PRODUCT_MARKET_ANALYSIS.md # Generated report
```

## 📊 Supported Analysis Types

### 1. Video Processing Projects (like VidPipe)

```python
agent = ProductAnalysisAgent('/path/to/video-project', 'video-processing')
```

**Analyzes:**
- Real-time processing capabilities
- Video I/O support (webcam, files, streaming)  
- Processing pipelines and filters
- GPU acceleration features
- Multi-interface support (CLI, GUI, Web)

**Example projects:** OpenCV applications, GStreamer pipelines, video processing libraries

### 2. Web Frameworks

```python
agent = ProductAnalysisAgent('/path/to/web-project', 'web-framework')
```

**Analyzes:**
- Component architecture
- Performance optimization features
- Developer experience tools
- Build and deployment systems
- Ecosystem integration

**Example projects:** React libraries, Vue components, Angular applications

### 3. Machine Learning Libraries

```python
agent = ProductAnalysisAgent('/path/to/ml-project', 'ml-library')
```

**Analyzes:**
- Model training and inference
- Algorithm implementations
- Performance optimization (GPU, distributed)
- Integration with ML ecosystems
- Production deployment features

**Example projects:** PyTorch extensions, TensorFlow libraries, scikit-learn tools

### 4. CLI Tools

```python
agent = ProductAnalysisAgent('/path/to/cli-project', 'cli-tool')
```

**Analyzes:**
- Command structure and usability
- Configuration and integration
- Cross-platform support
- Installation and distribution
- Documentation quality

**Example projects:** Development tools, system utilities, automation scripts

### 5. Generic Software

```python
agent = ProductAnalysisAgent('/path/to/any-project')  # Auto-detects or uses generic
```

**Analyzes:**
- Core functionality completeness
- Code quality and testing
- Documentation and examples  
- Performance characteristics
- Maintainability factors

## 🎛️ Customization Options

### Custom Feature Detection

```python
from product_analysis.analyzers import FeatureAnalyzer

class MyCustomAnalyzer(FeatureAnalyzer):
    def _detect_feature_presence(self, feature, repo_data, metadata):
        # Your custom detection logic
        if feature == "My Special Feature":
            return self._check_special_conditions(repo_data)
        return super()._detect_feature_presence(feature, repo_data, metadata)

# Use with agent
agent = ProductAnalysisAgent('/path/to/repo')
template = agent.template
agent.feature_analyzer = MyCustomAnalyzer(template.feature_categories)
```

### Custom Templates

```python
from product_analysis.templates import AnalysisTemplate

def create_blockchain_template():
    return AnalysisTemplate(
        name="Blockchain Project",
        description="Analysis for blockchain and DeFi projects",
        feature_categories={
            "Consensus": ["Proof of Work", "Proof of Stake", "Delegated PoS"],
            "Smart Contracts": ["Solidity Support", "Vyper Support", "Contract Verification"],
            "DeFi": ["DEX Integration", "Lending Protocols", "Yield Farming"],
            # ... more categories
        },
        benchmark_criteria=[
            {
                "category": "Security",
                "market_standard": True,
                "weight": "critical",
                "examples": ["Formal Verification", "Audit Reports"]
            }
        ],
        competitor_categories={
            "Layer 1": ["Ethereum", "Solana", "Cardano"],
            "Layer 2": ["Polygon", "Arbitrum", "Optimism"]
        },
        roadmap_priorities=["Security first", "Scalability", "Ecosystem growth"]
    )

# Register and use
from product_analysis.templates import get_template_for_project_type
# Add to templates.py or inject dynamically
```

### Custom Report Formats

```python
from product_analysis.generators import AnalysisReportBuilder

class JSONReportBuilder(AnalysisReportBuilder):
    def export_json(self, analysis_results, template, output_path):
        import json
        report_data = self.build_report(analysis_results, template)
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        return output_path

class HTMLReportGenerator:
    def generate_html(self, report_data, output_path):
        # Convert report_data to HTML
        html_content = self._build_html(report_data)
        with open(output_path, 'w') as f:
            f.write(html_content)
        return output_path
```

## 🔄 Integration Patterns

### CI/CD Pipeline Integration

```yaml
# .github/workflows/product-analysis.yml
name: Product Market Analysis
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -e .  # Your project
        # Install analysis framework dependencies
        
    - name: Run Product Analysis
      run: |
        python product_analysis_cli.py . --output analysis-$(date +%Y%m%d).md --json
        
    - name: Create Analysis PR
      uses: peter-evans/create-pull-request@v5
      with:
        commit-message: 'Update product market analysis'
        title: 'Product Analysis Update'
        body: 'Automated product market analysis update'
        branch: analysis-update
```

### Multi-Repository Analysis

```python
#!/usr/bin/env python3
"""
Batch analysis across multiple repositories
"""

import os
import json
from pathlib import Path
from product_analysis import ProductAnalysisAgent

def analyze_organization_repos(org_path, output_dir):
    """Analyze all repositories in an organization"""
    results_summary = {}
    
    for repo_dir in os.listdir(org_path):
        repo_path = Path(org_path) / repo_dir
        if not repo_path.is_dir() or repo_dir.startswith('.'):
            continue
            
        print(f"Analyzing {repo_dir}...")
        
        try:
            agent = ProductAnalysisAgent(str(repo_path))
            results = agent.analyze()
            
            # Generate individual report
            report_path = agent.generate_report(
                Path(output_dir) / f"{repo_dir}_analysis.md"
            )
            
            # Collect summary data
            feature_summary = results.get('feature_analysis', {}).get('summary', {})
            results_summary[repo_dir] = {
                'project_type': results.get('project_type'),
                'coverage_score': feature_summary.get('coverage_score', 0),
                'critical_gaps_count': len(feature_summary.get('critical_gaps', [])),
                'report_path': str(report_path)
            }
            
        except Exception as e:
            print(f"Error analyzing {repo_dir}: {e}")
            results_summary[repo_dir] = {'error': str(e)}
    
    # Generate summary report
    summary_path = Path(output_dir) / "organization_analysis_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"Organization analysis complete. Summary: {summary_path}")
    return results_summary

# Usage
if __name__ == '__main__':
    results = analyze_organization_repos(
        org_path='/path/to/organization/repos',
        output_dir='./analysis_reports'
    )
```

### Dashboard Integration

```python
"""
Web dashboard for analysis results
"""

from flask import Flask, render_template, jsonify
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Load analysis results from multiple projects
    results = []
    for analysis_file in Path('analysis_results').glob('*.json'):
        with open(analysis_file) as f:
            data = json.load(f)
            results.append({
                'name': analysis_file.stem,
                'coverage': data.get('feature_analysis', {}).get('summary', {}).get('coverage_score', 0),
                'type': data.get('project_type', 'unknown'),
                'gaps': len(data.get('feature_analysis', {}).get('summary', {}).get('critical_gaps', []))
            })
    
    return render_template('dashboard.html', projects=results)

@app.route('/api/analysis/<project>')
def get_analysis(project):
    analysis_file = Path('analysis_results') / f"{project}.json"
    if analysis_file.exists():
        with open(analysis_file) as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Analysis not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
```

## 📈 Analysis Workflow Examples

### Development Team Workflow

1. **Weekly Analysis**: Run automated analysis in CI/CD
2. **Feature Planning**: Use gap analysis for sprint planning  
3. **Competitive Review**: Monitor competitive positioning
4. **Progress Tracking**: Track coverage score improvements

### Product Management Workflow  

1. **Market Assessment**: Analyze multiple products in portfolio
2. **Strategic Planning**: Use roadmap recommendations
3. **Competitive Intelligence**: Track competitor feature development
4. **Investment Decisions**: Prioritize based on analysis insights

### Open Source Maintenance

1. **Project Health**: Regular analysis of project completeness
2. **Contributor Guidance**: Use gap analysis for contributor tasks
3. **Roadmap Planning**: Data-driven feature prioritization
4. **Community Communication**: Share analysis results with community

## 🎯 Best Practices

### Template Design

- **Domain-specific**: Create templates for your specific domain
- **Comprehensive**: Include all relevant feature categories
- **Balanced**: Mix market standards with innovation opportunities
- **Maintainable**: Keep templates updated with market evolution

### Feature Detection

- **Pattern-based**: Use file patterns, dependencies, and structure
- **Flexible**: Allow for different implementation approaches  
- **Accurate**: Validate detection logic with known projects
- **Extensible**: Design for easy addition of new patterns

### Report Usage

- **Actionable**: Focus on actionable insights and recommendations
- **Regular**: Run analysis regularly to track progress
- **Collaborative**: Share results with relevant stakeholders
- **Iterative**: Use feedback to improve analysis accuracy

### Integration Strategy

- **Gradual**: Start with one project, expand gradually
- **Automated**: Integrate into existing CI/CD workflows
- **Standardized**: Use consistent analysis across organization
- **Customized**: Adapt templates and logic for your domain

## 🔮 Future Enhancements

The componentized framework is designed for extensibility. Planned improvements:

- **Plugin Architecture**: Easy third-party extensions
- **ML-Powered Detection**: Automated feature recognition
- **Real-time Dashboards**: Live analysis monitoring
- **API Integration**: Direct GitHub/GitLab data collection
- **Collaborative Analysis**: Team-based assessment tools

## 📚 Additional Resources

- **Template Examples**: See `templates.py` for built-in templates
- **Analyzer Patterns**: Review `analyzers.py` for detection logic
- **Extension Points**: Check `core.py` for customization hooks
- **Test Examples**: See `tests/test_product_analysis.py` for usage patterns