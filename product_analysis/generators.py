"""
Report Generators

This module contains classes responsible for generating various types
of analysis reports from the collected data and analysis results.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .templates import AnalysisTemplate
from .analyzers import FeatureAssessment, BenchmarkResult


class AnalysisReportBuilder:
    """
    Builds structured analysis reports from raw analysis data
    """
    
    def build_report(self, analysis_results: Dict[str, Any], template: AnalysisTemplate) -> Dict[str, Any]:
        """
        Build a structured report from analysis results
        
        Args:
            analysis_results: Raw analysis results from the agent
            template: Analysis template used
            
        Returns:
            Structured report data
        """
        return {
            'metadata': self._build_metadata_section(analysis_results),
            'overview': self._build_overview_section(analysis_results, template),
            'benchmark': self._build_benchmark_section(analysis_results),
            'gaps': self._build_gaps_section(analysis_results),
            'competitive': self._build_competitive_section(analysis_results),
            'roadmap': self._build_roadmap_section(analysis_results, template)
        }
        
    def _build_metadata_section(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build the metadata section of the report"""
        repo_data = results.get('repository_data', {})
        project_metadata = results.get('project_metadata', {})
        
        return {
            'analysis_timestamp': results.get('timestamp', datetime.now().isoformat()),
            'project_name': project_metadata.get('project_name', 'Unknown Project'),
            'project_type': results.get('project_type', 'unknown'),
            'template_used': results.get('template_used', 'generic'),
            'repository_path': results.get('project_path', ''),
            'description': project_metadata.get('description', 'No description available'),
            'primary_language': self._get_primary_language(project_metadata),
            'total_files': sum(repo_data.get('file_counts', {}).values()),
            'has_tests': repo_data.get('test_structure', {}).get('has_testing', False)
        }
        
    def _build_overview_section(self, results: Dict[str, Any], template: AnalysisTemplate) -> Dict[str, Any]:
        """Build the product overview section"""
        project_metadata = results.get('project_metadata', {})
        competitive_analysis = results.get('competitive_analysis', {})
        
        return {
            'value_proposition': self._generate_value_proposition(results),
            'target_audience': self._identify_target_audience(results),
            'key_differentiators': competitive_analysis.get('differentiation_opportunities', []),
            'market_niche': competitive_analysis.get('market_niche', 'Unknown niche')
        }
        
    def _build_benchmark_section(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build the market benchmarking section"""
        feature_analysis = results.get('feature_analysis', {})
        benchmark_analysis = results.get('benchmark_analysis', {})
        
        assessments = feature_analysis.get('feature_assessments', {})
        summary = feature_analysis.get('summary', {})
        
        # Convert assessments to benchmark table format
        benchmark_table = []
        for category, features in assessments.items():
            for feature in features:
                benchmark_table.append({
                    'feature': feature.name,
                    'category': category,
                    'market_standard': '✅' if feature.market_standard else '❌',
                    'present': '✅' if feature.present else '❌',
                    'notes': feature.notes,
                    'opportunity': feature.opportunity_level
                })
                
        return {
            'feature_coverage_score': summary.get('coverage_score', 0.0),
            'total_features_assessed': summary.get('total_features', 0),
            'features_present': summary.get('present_features', 0),
            'benchmark_table': benchmark_table,
            'overall_benchmark_score': benchmark_analysis.get('overall_score', 0.0)
        }
        
    def _build_gaps_section(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build the gaps and opportunities section"""
        feature_analysis = results.get('feature_analysis', {})
        benchmark_analysis = results.get('benchmark_analysis', {})
        
        summary = feature_analysis.get('summary', {})
        
        return {
            'critical_gaps': summary.get('critical_gaps', []),
            'key_strengths': summary.get('key_strengths', []),
            'benchmark_recommendations': benchmark_analysis.get('recommendations', []),
            'innovation_opportunities': self._identify_innovation_opportunities(results)
        }
        
    def _build_competitive_section(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build the competitive landscape section"""
        competitive_analysis = results.get('competitive_analysis', {})
        
        return {
            'competitors': competitive_analysis.get('competitors', {}),
            'positioning': competitive_analysis.get('positioning', {}),
            'competitive_threats': competitive_analysis.get('competitive_threats', []),
            'market_position_summary': self._generate_market_position_summary(results)
        }
        
    def _build_roadmap_section(self, results: Dict[str, Any], template: AnalysisTemplate) -> Dict[str, Any]:
        """Build the suggested roadmap section"""
        feature_analysis = results.get('feature_analysis', {})
        summary = feature_analysis.get('summary', {})
        
        critical_gaps = summary.get('critical_gaps', [])
        
        return {
            'priority_framework': template.roadmap_priorities,
            'immediate_priorities': critical_gaps[:5],  # Top 5 critical gaps
            'suggested_phases': self._generate_roadmap_phases(results, template)
        }
        
    def _get_primary_language(self, metadata: Dict[str, Any]) -> str:
        """Get the primary programming language"""
        languages = metadata.get('languages', {})
        if not languages:
            return 'Unknown'
            
        # Return language with most files
        return max(languages.items(), key=lambda x: x[1])[0]
        
    def _generate_value_proposition(self, results: Dict[str, Any]) -> str:
        """Generate a value proposition based on analysis"""
        project_metadata = results.get('project_metadata', {})
        description = project_metadata.get('description', '')
        
        if description:
            return description
            
        # Generate based on project characteristics
        project_name = project_metadata.get('project_name', 'This project')
        project_type = results.get('project_type', 'software tool')
        
        return f"{project_name} is a {project_type} that provides specialized functionality for developers."
        
    def _identify_target_audience(self, results: Dict[str, Any]) -> str:
        """Identify the target audience based on project characteristics"""
        project_type = results.get('project_type', '')
        
        audience_map = {
            'video-processing': 'developers and researchers working with video processing and computer vision',
            'web-framework': 'web developers and frontend engineers',
            'ml-library': 'data scientists and machine learning engineers',
            'cli-tool': 'developers and system administrators',
            'generic-software': 'software developers'
        }
        
        return audience_map.get(project_type, 'software developers and technical users')
        
    def _identify_innovation_opportunities(self, results: Dict[str, Any]) -> List[str]:
        """Identify opportunities for innovation beyond baseline features"""
        opportunities = []
        
        project_type = results.get('project_type', '')
        
        if project_type == 'video-processing':
            opportunities.extend([
                "AI-powered pipeline optimization",
                "Collaborative pipeline development",
                "Visual pipeline debugger", 
                "Auto-generated pipelines based on ML"
            ])
        elif project_type == 'web-framework':
            opportunities.extend([
                "AI-assisted component generation",
                "Real-time collaborative development",
                "Advanced performance insights"
            ])
        else:
            opportunities.extend([
                "Enhanced automation capabilities",
                "Improved developer experience",
                "Advanced integration options"
            ])
            
        return opportunities
        
    def _generate_market_position_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary of market position"""
        competitive_analysis = results.get('competitive_analysis', {})
        niche = competitive_analysis.get('market_niche', 'specialized tool')
        
        return f"Positioned as a {niche} with unique approach to solving domain-specific challenges."
        
    def _generate_roadmap_phases(self, results: Dict[str, Any], template: AnalysisTemplate) -> List[Dict[str, Any]]:
        """Generate suggested roadmap phases"""
        feature_analysis = results.get('feature_analysis', {})
        summary = feature_analysis.get('summary', {})
        critical_gaps = summary.get('critical_gaps', [])
        
        phases = []
        
        # Phase 1: Critical gaps
        if critical_gaps:
            phases.append({
                'phase': 'Phase 1: Address Critical Market Gaps',
                'description': 'Focus on features that are market standards but currently missing',
                'items': critical_gaps[:3]
            })
            
        # Phase 2: Differentiation
        phases.append({
            'phase': 'Phase 2: Enhance Differentiation',
            'description': 'Build on unique strengths and develop competitive advantages',
            'items': ['Advanced feature development', 'User experience improvements', 'Performance optimization']
        })
        
        # Phase 3: Growth
        phases.append({
            'phase': 'Phase 3: Position for Growth',
            'description': 'Scale and expand market reach',
            'items': ['Enterprise features', 'Ecosystem development', 'Market expansion']
        })
        
        return phases


class MarkdownReportGenerator:
    """
    Generates markdown reports from structured analysis data
    """
    
    def generate(self, report_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate a markdown report file
        
        Args:
            report_data: Structured report data from AnalysisReportBuilder
            output_path: Path where to save the report
            
        Returns:
            Path to the generated report file
        """
        markdown_content = self._build_markdown_content(report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return output_path
        
    def _build_markdown_content(self, data: Dict[str, Any]) -> str:
        """Build the complete markdown content"""
        sections = []
        
        # Title and metadata
        sections.append(self._build_header(data))
        
        # Product Overview
        sections.append(self._build_overview_section(data.get('overview', {}), data.get('metadata', {})))
        
        # Market Benchmarking  
        sections.append(self._build_benchmarking_section(data.get('benchmark', {})))
        
        # Gap Analysis
        sections.append(self._build_gaps_section(data.get('gaps', {})))
        
        # Competitive Landscape
        sections.append(self._build_competitive_section(data.get('competitive', {})))
        
        # Roadmap
        sections.append(self._build_roadmap_section(data.get('roadmap', {})))
        
        return '\n\n'.join(sections)
        
    def _build_header(self, data: Dict[str, Any]) -> str:
        """Build the report header"""
        metadata = data.get('metadata', {})
        
        return f"""# 📊 Product Market Analysis Report

*Generated on {metadata.get('analysis_timestamp', 'Unknown date')}*

**Project:** {metadata.get('project_name', 'Unknown Project')}  
**Type:** {metadata.get('project_type', 'Unknown').replace('-', ' ').title()}  
**Template:** {metadata.get('template_used', 'Generic')}  

---"""

    def _build_overview_section(self, overview: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Build the product overview section"""
        return f"""## 1. Product Overview

- **Repository Name:** `{metadata.get('project_name', 'Unknown Project')}`
- **Current Value Proposition:**  
  {overview.get('value_proposition', 'No description available')}

- **Target Audience:** {overview.get('target_audience', 'Unknown')}
- **Market Niche:** {overview.get('market_niche', 'Unknown niche')}

**Key Differentiators:**
{self._format_list(overview.get('key_differentiators', []))}

---"""

    def _build_benchmarking_section(self, benchmark: Dict[str, Any]) -> str:
        """Build the market benchmarking section"""
        table_rows = []
        
        # Group features by category for better organization
        features_by_category = {}
        for feature in benchmark.get('benchmark_table', []):
            category = feature['category']
            if category not in features_by_category:
                features_by_category[category] = []
            features_by_category[category].append(feature)
            
        # Build table
        table_rows.append("| Feature | Market Standard? | Present in Repo? | Notes / Opportunity |")
        table_rows.append("|---------|------------------|------------------|---------------------|")
        
        for category, features in features_by_category.items():
            table_rows.append(f"| **{category}** |  |  |  |")
            for feature in features:
                notes = feature['notes'].replace('–', '-')  # Handle em dashes
                table_rows.append(f"| {feature['feature']} | {feature['market_standard']} | {feature['present']} | {notes} |")
                
        benchmark_table = '\n'.join(table_rows)
        
        coverage_score = benchmark.get('feature_coverage_score', 0.0)
        coverage_percent = int(coverage_score * 100)
        
        return f"""## 2. Market Benchmarking

**Feature Coverage Score:** {coverage_percent}% ({benchmark.get('features_present', 0)}/{benchmark.get('total_features_assessed', 0)} features)

{benchmark_table}

---"""

    def _build_gaps_section(self, gaps: Dict[str, Any]) -> str:
        """Build the gaps and opportunities section"""
        return f"""## 3. Gap & Opportunity Report

**Strengths (what we already do well):**
{self._format_list(gaps.get('key_strengths', []))}

**Critical Missing Features (baseline expectations):**
{self._format_list(gaps.get('critical_gaps', []))}

**Opportunities for Innovation (go beyond baseline):**
{self._format_list(gaps.get('innovation_opportunities', []))}

**Recommendations:**
{self._format_list(gaps.get('benchmark_recommendations', []))}

---"""

    def _build_competitive_section(self, competitive: Dict[str, Any]) -> str:
        """Build the competitive landscape section"""
        competitors = competitive.get('competitors', {})
        positioning = competitive.get('positioning', {})
        
        competitor_sections = []
        for category, comp_list in competitors.items():
            competitor_sections.append(f"**{category}:**")
            for competitor in comp_list:
                competitor_sections.append(f"- **{competitor.split(' - ')[0]}**: {competitor.split(' - ', 1)[1] if ' - ' in competitor else competitor}")
        
        return f"""## 4. Competitive Landscape

{chr(10).join(competitor_sections)}

**Market Position:**
{competitive.get('market_position_summary', 'Unknown position')}

**Positioning Characteristics:**
{self._format_dict_as_list(positioning)}

---"""

    def _build_roadmap_section(self, roadmap: Dict[str, Any]) -> str:
        """Build the suggested roadmap section"""
        phases = roadmap.get('suggested_phases', [])
        
        phase_sections = []
        for i, phase in enumerate(phases, 1):
            items = self._format_list(phase.get('items', []))
            phase_sections.append(f"{i}. **{phase.get('phase', f'Phase {i}')}**: \n   {phase.get('description', '')}\n   {items}")
            
        return f"""## 5. Suggested Roadmap Priorities

{chr(10).join(phase_sections)}

---"""

    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as markdown bullet points"""
        if not items:
            return "- None identified"
        return '\n'.join(f"- {item}" for item in items)
        
    def _format_dict_as_list(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as markdown bullet points"""
        if not data:
            return "- No specific positioning characteristics identified"
        return '\n'.join(f"- **{key}**: {value}" for key, value in data.items())