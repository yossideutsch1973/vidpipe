# 🐙 GitHub Integration Guide - Product Analysis Agent

This guide explains how to integrate the Product Analysis Agent directly with GitHub for seamless triggering from the GitHub website and app.

## 🚀 Quick Start - GitHub Integration

### 1. Trigger from GitHub Actions Tab

1. **Navigate to your repository on GitHub**
2. **Click the "Actions" tab**
3. **Find "🔍 Product Market Analysis" workflow**
4. **Click "Run workflow"**
5. **Configure options:**
   - Project type (auto-detect, video-processing, web-framework, etc.)
   - Output format (markdown, json, both)
   - Create GitHub issue with results
   - Create PR with updated analysis

![GitHub Actions Workflow](https://via.placeholder.com/600x300?text=GitHub+Actions+Workflow+Interface)

### 2. Trigger via Issue Comments

Simply comment on any issue with:
- `@copilot analyze` 
- `@copilot product analysis`
- `/analyze`
- Any comment containing "product analysis"

The bot will respond with analysis results and links to generated reports.

### 3. Automated Triggers

- **Weekly Analysis**: Automatic runs every Sunday at midnight UTC
- **Release Analysis**: Triggered when you publish a new release
- **Manual Scheduling**: Use GitHub's workflow dispatch for on-demand runs

## 🛠️ Setup Instructions

### Step 1: Copy Files to Your Repository

```bash
# Copy the product analysis framework
cp -r product_analysis/ /path/to/your/repository/
cp product_analysis_cli.py /path/to/your/repository/
cp .github/workflows/product-analysis.yml /path/to/your/repository/.github/workflows/

# Commit and push
cd /path/to/your/repository
git add product_analysis/ product_analysis_cli.py .github/workflows/product-analysis.yml
git commit -m "Add Product Analysis Agent with GitHub integration"
git push
```

### Step 2: Configure GitHub Token (Optional)

For enhanced GitHub integration, set up a GitHub token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with permissions:
   - `repo` (for private repos) or `public_repo` (for public repos)
   - `issues:write`
   - `pull_requests:write`
3. Add as repository secret: `Settings → Secrets → Actions → New secret`
   - Name: `GITHUB_TOKEN` 
   - Value: Your token

*Note: GitHub provides a default `GITHUB_TOKEN` with basic permissions that works for most features.*

### Step 3: Enable Workflow Permissions

1. Go to `Settings → Actions → General`
2. Under "Workflow permissions":
   - Select "Read and write permissions" 
   - Check "Allow GitHub Actions to create and approve pull requests"

## 🎯 Usage Examples

### Command Line with GitHub Integration

```bash
# Basic analysis with GitHub integration
python product_analysis_cli.py . --github --verbose

# Create GitHub issue with results
python product_analysis_cli.py . --github-issue

# Create GitHub PR with analysis
python product_analysis_cli.py . --github-pr --type video-processing

# Full integration with custom output
python product_analysis_cli.py . --github --github-issue --output analysis.md --json
```

### Programmatic Usage with GitHub

```python
from product_analysis import ProductAnalysisAgent

# Enable GitHub integration
agent = ProductAnalysisAgent(
    '/path/to/repository',
    project_type='video-processing',
    enable_github=True
)

# Run analysis with GitHub features
results, report_path = agent.run_full_analysis_with_github(
    create_issue=True,
    create_pr=False
)

# Manual GitHub operations
issue_num = agent.create_github_issue("📊 Product Analysis - Custom Title")
print(f"Created issue #{issue_num}")
```

## 🔧 Workflow Configuration

### Customize Trigger Conditions

Edit `.github/workflows/product-analysis.yml`:

```yaml
# Add custom trigger patterns
issue_comment:
  types: [created]
  # Will trigger on comments matching patterns in the workflow

# Customize schedule
schedule:
  - cron: '0 9 * * 1'  # Mondays at 9 AM UTC
  - cron: '0 0 1 * *'  # Monthly on 1st at midnight
```

### Custom Project Types

Add custom project types by extending the workflow inputs:

```yaml
workflow_dispatch:
  inputs:
    project_type:
      type: choice
      options:
      - 'auto-detect'
      - 'video-processing'
      - 'blockchain'        # Custom type
      - 'mobile-app'        # Custom type
      - 'api-service'       # Custom type
```

### Environment Variables

Configure analysis behavior with environment variables:

```yaml
env:
  ANALYSIS_DEPTH: 'comprehensive'  # basic, standard, comprehensive
  INCLUDE_DEPENDENCIES: 'true'     # Analyze dependencies
  GENERATE_CHARTS: 'false'         # Generate visualization charts
```

## 📊 GitHub Integration Features

### Enhanced Data Collection

GitHub integration provides additional data:

- **Repository metrics**: Stars, forks, watchers, issues
- **Community engagement**: Contributors, activity levels  
- **Release information**: Latest releases, versions
- **Language statistics**: Detailed language breakdown
- **Traffic data**: Views, clones (requires push access)

### Automated Reporting

- **Issue Creation**: Structured analysis results as GitHub issues
- **PR Generation**: Analysis updates via pull requests  
- **Workflow Artifacts**: Downloadable reports and raw data
- **Comment Responses**: Direct responses to issue/PR comments

### Community Metrics

```yaml
Analysis includes GitHub-specific insights:
- Popularity Score: Based on stars, forks, watchers
- Activity Level: Recent commit activity assessment
- Community Engagement: Contributor and issue activity
- Repository Health: License, documentation, maintenance status
```

## 🎮 Interactive Triggers

### Issue Comment Commands

Comment on any issue to trigger analysis:

```bash
# Basic analysis
@copilot analyze

# Specific project type  
@copilot analyze --type web-framework

# With custom output
/analyze --output custom-report.md --json

# Product analysis request
"Can you run a product analysis on this repository?"
```

### Manual Workflow Triggers

Use GitHub's UI to run analysis on-demand:

1. **Go to Actions tab**
2. **Select "Product Market Analysis"**
3. **Click "Run workflow"**
4. **Configure options**:
   - Project type selection
   - Output format preferences
   - Issue/PR creation options
5. **Click "Run workflow"**

## 📈 Analysis Results Integration

### GitHub Issue Format

Analysis results are formatted as structured GitHub issues:

```markdown
## 📊 Product Market Analysis Results

**Analysis Date:** 2024-01-01T12:00:00Z
**Project Type:** video-processing  

### 🎯 Overview
- Repository: owner/repo-name
- Description: Project description
- Primary Language: Python

### 📈 Key Metrics  
- Feature Coverage: 85.2% (23/27 features)
- Critical Gaps: 2
- GitHub Stars: 1,234
- Community Engagement: High

### 🚨 Critical Gaps Identified
- GPU Acceleration Support
- Network Streaming Capabilities

### ✨ Key Strengths
- Web-based Interface
- Multi-threading Support
- Comprehensive Documentation

### 📋 Next Steps
1. Address Critical Gaps
2. Leverage Strengths  
3. Community Building
4. Strategic Planning
```

### Pull Request Integration

Analysis updates are delivered via PRs:

- **Updated analysis files**: Latest reports and data
- **Commit messages**: Structured with key metrics
- **PR descriptions**: Summary of changes and insights
- **Labels**: Automatic labeling (analysis, product-management, automated)

## 🔗 GitHub App Integration (Advanced)

For organizations wanting deeper integration:

### Create GitHub App

```json
{
  "name": "Product Analysis Agent",
  "description": "Automated product market analysis",
  "default_permissions": {
    "contents": "read",
    "issues": "write", 
    "metadata": "read",
    "pull_requests": "write"
  },
  "default_events": [
    "issues",
    "issue_comment", 
    "release",
    "push"
  ]
}
```

### Installation Benefits

- **Organization-wide deployment**: Install across all repositories
- **Webhook integration**: Real-time triggers and responses
- **Enhanced permissions**: Full GitHub API access
- **Custom integrations**: Build additional features

## 🎯 Best Practices

### Repository Setup

1. **Add workflow file**: Include `product-analysis.yml` in `.github/workflows/`
2. **Configure permissions**: Enable necessary GitHub Actions permissions
3. **Set up secrets**: Add GitHub token if needed for enhanced features
4. **Test triggers**: Verify manual and automated triggers work
5. **Customize templates**: Adapt analysis for your specific domain

### Workflow Optimization

1. **Scheduled runs**: Weekly/monthly for regular insights
2. **Release triggers**: Analyze on each release for tracking progress
3. **Comment triggers**: Enable team members to request ad-hoc analysis
4. **Artifact retention**: Configure retention period for analysis files

### Team Integration

1. **Issue labels**: Use consistent labeling for analysis issues
2. **Assignees**: Auto-assign to product managers or team leads
3. **Notifications**: Configure team notifications for analysis results
4. **Action items**: Convert analysis insights into actionable issues

## 🚀 Advanced Customization

### Custom Analysis Logic

```python
# Extend GitHub integration
from product_analysis.github_integration import GitHubAnalysisIntegration

class CustomGitHubIntegration(GitHubAnalysisIntegration):
    def collect_github_data(self):
        data = super().collect_github_data()
        # Add custom GitHub data collection
        data['custom_metrics'] = self.calculate_custom_metrics()
        return data
```

### Webhook Integration

```python
# Flask webhook handler
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    event = request.headers.get('X-GitHub-Event')
    
    if event == 'release':
        # Trigger analysis on release
        trigger_analysis(request.json['repository']['full_name'])
    
    return jsonify({'status': 'processed'})
```

### Multi-Repository Analysis

```python
# Analyze entire organization
from product_analysis import ProductAnalysisAgent

def analyze_organization(org_name, github_token):
    """Analyze all repositories in an organization"""
    github = Github(github_token)
    org = github.get_organization(org_name)
    
    for repo in org.get_repos():
        agent = ProductAnalysisAgent(
            repo.clone_url, 
            enable_github=True,
            github_token=github_token
        )
        results, report = agent.run_full_analysis_with_github(
            create_issue=True
        )
        print(f"Analyzed {repo.name}: {results['coverage_score']:.1%} coverage")
```

## 📚 Troubleshooting

### Common Issues

**Workflow not triggering:**
- Check workflow permissions in repository settings
- Verify workflow file syntax and location
- Ensure GitHub Actions is enabled

**GitHub API errors:**
- Check GitHub token permissions
- Verify repository access rights
- Review rate limiting (5000 requests/hour)

**Analysis failures:**
- Check repository structure and dependencies
- Verify Python environment and requirements
- Review workflow logs for specific errors

### Debug Mode

Enable verbose logging:

```yaml
- name: Run Analysis with Debug
  run: |
    python product_analysis_cli.py . --verbose --github
  env:
    DEBUG: 'true'
    PYTHONPATH: ${{ github.workspace }}
```

## 🌟 Success Stories

The GitHub integration transforms product analysis from a manual process into an automated, collaborative workflow:

- **Weekly insights**: Regular analysis keeps teams informed of product evolution
- **Release analysis**: Track feature completeness and market positioning over time
- **Community engagement**: GitHub issues facilitate team discussion around analysis results
- **Strategic planning**: Automated reports support data-driven product decisions

Start with basic triggers, then expand to full GitHub App integration as your needs grow!

---

## 📁 Quick Setup Checklist

- [ ] Copy product analysis framework to your repository
- [ ] Add `.github/workflows/product-analysis.yml` workflow file  
- [ ] Configure GitHub Actions permissions
- [ ] Test manual trigger from Actions tab
- [ ] Test issue comment trigger
- [ ] Configure optional GitHub token for enhanced features
- [ ] Customize workflow for your project type and needs
- [ ] Set up team notifications and integrations

**🎉 Your Product Analysis Agent is now GitHub-integrated and ready to use!**