"""
GitHub Integration for Product Analysis Agent

This module provides GitHub-specific functionality for the product analysis agent,
including repository data collection via GitHub API, issue/PR integration, and
automated reporting capabilities.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


class GitHubAnalysisIntegration:
    """
    GitHub integration for the product analysis agent
    
    Provides GitHub-specific enhancements including:
    - Repository data collection via GitHub API
    - Issue/PR creation with analysis results
    - GitHub Actions integration
    - Repository insights and metrics
    """
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub integration
        
        Args:
            token: GitHub token (defaults to GITHUB_TOKEN env var)
            repo_name: Repository name in format "owner/repo" (auto-detected if None)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repo_name = repo_name or self._detect_repository()
        self.github = None
        self.repo = None
        
        if self.token and GITHUB_AVAILABLE:
            try:
                self.github = Github(self.token)
                if self.repo_name:
                    self.repo = self.github.get_repo(self.repo_name)
            except Exception as e:
                print(f"Warning: GitHub API initialization failed: {e}")
                
    def _detect_repository(self) -> Optional[str]:
        """Detect GitHub repository from environment or git config"""
        # Try GitHub Actions environment
        repo_name = os.getenv('GITHUB_REPOSITORY')
        if repo_name:
            return repo_name
            
        # Try git remote origin
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse GitHub URL formats
                patterns = [
                    r'https://github\.com/([^/]+/[^/]+)(?:\.git)?',
                    r'git@github\.com:([^/]+/[^/]+)(?:\.git)?'
                ]
                for pattern in patterns:
                    match = re.match(pattern, url)
                    if match:
                        return match.group(1).rstrip('.git')
        except Exception:
            pass
            
        return None
        
    def collect_github_data(self) -> Dict[str, Any]:
        """
        Collect additional repository data from GitHub API
        
        Returns:
            Dictionary with GitHub-specific repository data
        """
        if not self.repo:
            return {'github_available': False}
            
        try:
            # Basic repository information
            repo_data = {
                'github_available': True,
                'name': self.repo.name,
                'full_name': self.repo.full_name,
                'description': self.repo.description,
                'stars': self.repo.stargazers_count,
                'forks': self.repo.forks_count,
                'watchers': self.repo.watchers_count,
                'open_issues': self.repo.open_issues_count,
                'language': self.repo.language,
                'languages': dict(self.repo.get_languages()),
                'topics': self.repo.get_topics(),
                'created_at': self.repo.created_at.isoformat() if self.repo.created_at else None,
                'updated_at': self.repo.updated_at.isoformat() if self.repo.updated_at else None,
                'default_branch': self.repo.default_branch,
                'license': self.repo.license.name if self.repo.license else None,
                'archived': self.repo.archived,
                'private': self.repo.private
            }
            
            # Recent activity
            try:
                commits = list(self.repo.get_commits()[:10])
                repo_data['recent_commits'] = len(commits)
                repo_data['last_commit_date'] = commits[0].commit.author.date.isoformat() if commits else None
            except Exception:
                repo_data['recent_commits'] = 0
                repo_data['last_commit_date'] = None
                
            # Release information
            try:
                releases = list(self.repo.get_releases()[:5])
                repo_data['releases_count'] = len(releases)
                repo_data['latest_release'] = {
                    'tag_name': releases[0].tag_name,
                    'published_at': releases[0].published_at.isoformat(),
                    'prerelease': releases[0].prerelease
                } if releases else None
            except Exception:
                repo_data['releases_count'] = 0
                repo_data['latest_release'] = None
                
            # Contributors
            try:
                contributors = list(self.repo.get_contributors()[:10])
                repo_data['contributors_count'] = len(contributors)
                repo_data['top_contributors'] = [
                    {'login': c.login, 'contributions': c.contributions}
                    for c in contributors[:5]
                ]
            except Exception:
                repo_data['contributors_count'] = 0
                repo_data['top_contributors'] = []
                
            # Repository traffic (requires push access)
            try:
                views = self.repo.get_views_traffic()
                repo_data['views'] = {
                    'count': views['count'],
                    'uniques': views['uniques']
                }
            except Exception:
                repo_data['views'] = None
                
            return repo_data
            
        except Exception as e:
            return {
                'github_available': False,
                'error': str(e)
            }
            
    def enhance_analysis_with_github_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance analysis results with GitHub-specific data
        
        Args:
            analysis_results: Original analysis results
            
        Returns:
            Enhanced analysis results with GitHub data
        """
        github_data = self.collect_github_data()
        
        if github_data.get('github_available'):
            # Add GitHub data to project metadata
            analysis_results.setdefault('project_metadata', {}).update({
                'github_stars': github_data.get('stars', 0),
                'github_forks': github_data.get('forks', 0),
                'github_watchers': github_data.get('watchers', 0),
                'github_issues': github_data.get('open_issues', 0),
                'github_topics': github_data.get('topics', []),
                'github_license': github_data.get('license'),
                'github_created': github_data.get('created_at'),
                'github_updated': github_data.get('updated_at')
            })
            
            # Enhance competitive analysis with community metrics
            competitive = analysis_results.setdefault('competitive_analysis', {})
            competitive['community_metrics'] = {
                'popularity_score': self._calculate_popularity_score(github_data),
                'activity_level': self._assess_activity_level(github_data),
                'community_engagement': self._assess_community_engagement(github_data)
            }
            
            # Add GitHub-specific recommendations
            gaps = analysis_results.setdefault('feature_analysis', {}).setdefault('summary', {})
            github_recommendations = self._generate_github_recommendations(github_data)
            gaps.setdefault('github_recommendations', []).extend(github_recommendations)
            
        analysis_results['github_integration'] = github_data
        return analysis_results
        
    def create_analysis_issue(self, analysis_results: Dict[str, Any], title: str = None) -> Optional[int]:
        """
        Create a GitHub issue with analysis results
        
        Args:
            analysis_results: Analysis results to include in issue
            title: Custom issue title
            
        Returns:
            Issue number if created successfully, None otherwise
        """
        if not self.repo:
            print("Warning: Cannot create issue - GitHub repository not available")
            return None
            
        try:
            # Generate issue title
            if not title:
                project_name = analysis_results.get('project_metadata', {}).get('project_name', 'Project')
                title = f"📊 Product Market Analysis - {project_name}"
                
            # Generate issue body
            body = self._generate_issue_body(analysis_results)
            
            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=['analysis', 'product-management', 'documentation']
            )
            
            print(f"✅ Created GitHub issue #{issue.number}: {title}")
            return issue.number
            
        except Exception as e:
            print(f"❌ Failed to create GitHub issue: {e}")
            return None
            
    def create_analysis_pr(self, analysis_results: Dict[str, Any], 
                          report_file: str, title: str = None) -> Optional[int]:
        """
        Create a pull request with analysis results
        
        Args:
            analysis_results: Analysis results
            report_file: Path to the generated report file
            title: Custom PR title
            
        Returns:
            PR number if created successfully, None otherwise
        """
        if not self.repo:
            print("Warning: Cannot create PR - GitHub repository not available")
            return None
            
        try:
            # This is a simplified example - in practice, you'd need to:
            # 1. Create a new branch
            # 2. Commit the report file
            # 3. Create the PR
            
            print("📝 PR creation requires additional Git operations")
            print("   Use the GitHub Actions workflow for automated PR creation")
            return None
            
        except Exception as e:
            print(f"❌ Failed to create GitHub PR: {e}")
            return None
            
    def _calculate_popularity_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate a popularity score based on GitHub metrics"""
        stars = github_data.get('stars', 0)
        forks = github_data.get('forks', 0)
        watchers = github_data.get('watchers', 0)
        
        # Simple popularity scoring
        score = (stars * 1.0) + (forks * 2.0) + (watchers * 0.5)
        return min(score / 1000.0, 1.0)  # Normalize to 0-1 range
        
    def _assess_activity_level(self, github_data: Dict[str, Any]) -> str:
        """Assess repository activity level"""
        commits = github_data.get('recent_commits', 0)
        last_commit = github_data.get('last_commit_date')
        
        if not last_commit:
            return 'inactive'
            
        try:
            from datetime import datetime, timezone
            last_date = datetime.fromisoformat(last_commit.replace('Z', '+00:00'))
            days_since = (datetime.now(timezone.utc) - last_date).days
            
            if days_since <= 7:
                return 'very_active'
            elif days_since <= 30:
                return 'active'
            elif days_since <= 90:
                return 'moderate'
            else:
                return 'low'
        except Exception:
            return 'unknown'
            
    def _assess_community_engagement(self, github_data: Dict[str, Any]) -> str:
        """Assess community engagement level"""
        stars = github_data.get('stars', 0)
        forks = github_data.get('forks', 0)
        contributors = github_data.get('contributors_count', 0)
        issues = github_data.get('open_issues', 0)
        
        engagement_score = 0
        if stars > 100: engagement_score += 1
        if stars > 1000: engagement_score += 1
        if forks > 20: engagement_score += 1
        if contributors > 5: engagement_score += 1
        if issues > 0: engagement_score += 1  # Active issues indicate engagement
        
        levels = ['minimal', 'low', 'moderate', 'good', 'high', 'excellent']
        return levels[min(engagement_score, len(levels) - 1)]
        
    def _generate_github_recommendations(self, github_data: Dict[str, Any]) -> List[str]:
        """Generate GitHub-specific recommendations"""
        recommendations = []
        
        stars = github_data.get('stars', 0)
        forks = github_data.get('forks', 0)
        topics = github_data.get('topics', [])
        description = github_data.get('description', '')
        license = github_data.get('license')
        
        if stars < 10:
            recommendations.append("Consider promoting the repository to increase visibility and stars")
            
        if not topics:
            recommendations.append("Add GitHub topics to improve discoverability")
            
        if not description:
            recommendations.append("Add a clear repository description")
            
        if not license:
            recommendations.append("Add a license to clarify usage terms")
            
        if forks < (stars * 0.1):
            recommendations.append("Low fork ratio suggests limited contribution activity")
            
        return recommendations
        
    def _generate_issue_body(self, analysis_results: Dict[str, Any]) -> str:
        """Generate GitHub issue body from analysis results"""
        metadata = analysis_results.get('project_metadata', {})
        feature_summary = analysis_results.get('feature_analysis', {}).get('summary', {})
        competitive = analysis_results.get('competitive_analysis', {})
        github_data = analysis_results.get('github_integration', {})
        
        body = f"""## 📊 Product Market Analysis Results

**Analysis Date:** {analysis_results.get('timestamp', datetime.now().isoformat())}
**Project Type:** {analysis_results.get('project_type', 'Unknown')}

### 🎯 Overview
- **Repository:** {github_data.get('full_name', metadata.get('project_name', 'Unknown'))}
- **Description:** {github_data.get('description', metadata.get('description', 'No description available'))}
- **Primary Language:** {github_data.get('language', 'Unknown')}

### 📈 Key Metrics
- **Feature Coverage:** {feature_summary.get('coverage_score', 0):.1%} ({feature_summary.get('present_features', 0)}/{feature_summary.get('total_features', 0)} features)
- **Critical Gaps:** {len(feature_summary.get('critical_gaps', []))}
- **GitHub Stars:** {github_data.get('stars', 'N/A')}
- **Community Engagement:** {competitive.get('community_metrics', {}).get('community_engagement', 'Unknown')}

### 🚨 Critical Gaps Identified
"""
        
        critical_gaps = feature_summary.get('critical_gaps', [])
        if critical_gaps:
            for gap in critical_gaps[:5]:  # Show top 5
                body += f"- {gap}\n"
        else:
            body += "- No critical gaps identified\n"
            
        body += f"""
### ✨ Key Strengths
"""
        
        strengths = feature_summary.get('key_strengths', [])
        if strengths:
            for strength in strengths[:5]:  # Show top 5
                body += f"- {strength}\n"
        else:
            body += "- Analysis in progress\n"
            
        body += f"""
### 🏢 Market Positioning
**Market Niche:** {competitive.get('market_niche', 'To be determined')}

**Differentiation Opportunities:**
"""
        
        diff_opps = competitive.get('differentiation_opportunities', [])
        if diff_opps:
            for opp in diff_opps:
                body += f"- {opp}\n"
        else:
            body += "- Analysis in progress\n"
            
        body += """
### 📋 Next Steps
Based on this analysis, consider:

1. **Address Critical Gaps**: Focus development on missing market-standard features
2. **Leverage Strengths**: Build marketing and positioning around existing advantages  
3. **Community Building**: Enhance GitHub presence and community engagement
4. **Strategic Planning**: Use insights for product roadmap and resource allocation

### 📄 Full Report
The complete analysis report contains detailed benchmarking, competitive analysis, and strategic recommendations. Check the workflow artifacts or generated files for the full report.

---
*This analysis was generated automatically by the Product Analysis Agent*
"""
        
        return body


def create_github_app_manifest() -> Dict[str, Any]:
    """
    Create a GitHub App manifest for the Product Analysis Agent
    
    Returns:
        GitHub App manifest configuration
    """
    return {
        "name": "Product Analysis Agent",
        "url": "https://github.com/yossideutsch1973/vidpipe",
        "hook_attributes": {
            "url": "https://your-domain.com/webhook"
        },
        "redirect_url": "https://your-domain.com/auth/callback",
        "description": "Automated product market analysis for software repositories",
        "public": True,
        "default_events": [
            "issues",
            "issue_comment",
            "release",
            "push",
            "repository"
        ],
        "default_permissions": {
            "contents": "read",
            "issues": "write",
            "metadata": "read",
            "pull_requests": "write",
            "repository_projects": "read"
        },
        "setup_url": "https://your-domain.com/setup",
        "setup_on_update": True
    }