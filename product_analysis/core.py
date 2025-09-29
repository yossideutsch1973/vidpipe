"""
Core Product Analysis Agent

This module contains the main ProductAnalysisAgent class that orchestrates
the analysis process by coordinating data collection, analysis, and report generation.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import os
from datetime import datetime

from .collectors import RepositoryCollector, ProjectMetadataCollector
from .analyzers import FeatureAnalyzer, MarketBenchmarkAnalyzer, CompetitiveAnalyzer
from .generators import MarkdownReportGenerator, AnalysisReportBuilder
from .templates import get_template_for_project_type, AnalysisTemplate


class ProductAnalysisAgent:
    """
    Main orchestrator for product market analysis
    
    This class coordinates the entire analysis process:
    1. Collects repository and project metadata
    2. Runs various analyzers to assess market position
    3. Generates comprehensive reports
    """
    
    def __init__(self, project_path: str, project_type: Optional[str] = None):
        """
        Initialize the analysis agent
        
        Args:
            project_path: Path to the project repository
            project_type: Type of project (e.g., 'video-processing', 'web-framework', 'ml-library')
                         If None, will attempt to auto-detect
        """
        self.project_path = Path(project_path)
        self.project_type = project_type
        
        # Initialize components
        self.repo_collector = RepositoryCollector(project_path)
        self.metadata_collector = ProjectMetadataCollector(project_path)
        
        # Analysis components will be initialized after template selection
        self.template: Optional[AnalysisTemplate] = None
        self.feature_analyzer: Optional[FeatureAnalyzer] = None
        self.benchmark_analyzer: Optional[MarketBenchmarkAnalyzer] = None
        self.competitive_analyzer: Optional[CompetitiveAnalyzer] = None
        
        self.report_builder = AnalysisReportBuilder()
        self.report_generator = MarkdownReportGenerator()
        
        # Analysis results storage
        self.analysis_results: Dict[str, Any] = {}
        
    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete analysis process
        
        Returns:
            Dictionary containing all analysis results
        """
        print("🔍 Starting Product Market Analysis...")
        
        # Step 1: Collect repository data
        print("📊 Collecting repository data...")
        repo_data = self.repo_collector.collect()
        project_metadata = self.metadata_collector.collect()
        
        # Step 2: Determine project type and load appropriate template
        if not self.project_type:
            self.project_type = self._detect_project_type(repo_data, project_metadata)
        
        print(f"🎯 Detected project type: {self.project_type}")
        self.template = get_template_for_project_type(self.project_type)
        
        # Step 3: Initialize analyzers with template
        self.feature_analyzer = FeatureAnalyzer(self.template.feature_categories)
        self.benchmark_analyzer = MarketBenchmarkAnalyzer(self.template.benchmark_criteria)
        self.competitive_analyzer = CompetitiveAnalyzer(self.template.competitor_categories)
        
        # Step 4: Run analyses
        print("⚡ Running feature analysis...")
        feature_analysis = self.feature_analyzer.analyze(repo_data, project_metadata)
        
        print("📈 Running market benchmark analysis...")
        benchmark_analysis = self.benchmark_analyzer.analyze(repo_data, project_metadata)
        
        print("🏢 Running competitive analysis...")
        competitive_analysis = self.competitive_analyzer.analyze(repo_data, project_metadata)
        
        # Step 5: Compile results
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'project_type': self.project_type,
            'repository_data': repo_data,
            'project_metadata': project_metadata,
            'feature_analysis': feature_analysis,
            'benchmark_analysis': benchmark_analysis,
            'competitive_analysis': competitive_analysis,
            'template_used': self.template.name
        }
        
        print("✅ Analysis complete!")
        return self.analysis_results
        
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a markdown report from analysis results
        
        Args:
            output_path: Path to save the report. If None, saves to project root
            
        Returns:
            Path to the generated report file
        """
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analyze() first.")
            
        print("📝 Building analysis report...")
        report_content = self.report_builder.build_report(self.analysis_results, self.template)
        
        if not output_path:
            output_path = self.project_path / "PRODUCT_MARKET_ANALYSIS.md"
        else:
            output_path = Path(output_path)
            
        print(f"💾 Generating report: {output_path}")
        report_path = self.report_generator.generate(report_content, output_path)
        
        print("✅ Report generated successfully!")
        return str(report_path)
        
    def run_full_analysis(self, output_path: Optional[str] = None) -> tuple[Dict[str, Any], str]:
        """
        Convenience method to run analysis and generate report in one step
        
        Args:
            output_path: Path to save the report
            
        Returns:
            Tuple of (analysis_results, report_path)
        """
        results = self.analyze()
        report_path = self.generate_report(output_path)
        return results, report_path
        
    def _detect_project_type(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """
        Auto-detect project type based on repository characteristics
        
        Args:
            repo_data: Repository data from collector
            metadata: Project metadata from collector
            
        Returns:
            Detected project type string
        """
        # Check for common patterns to determine project type
        languages = metadata.get('languages', {})
        dependencies = metadata.get('dependencies', [])
        files = repo_data.get('key_files', [])
        
        # Video processing indicators
        if any('opencv' in dep.lower() for dep in dependencies) or \
           any('video' in f.lower() for f in files):
            return 'video-processing'
            
        # Web framework indicators
        if any(lang in languages for lang in ['JavaScript', 'TypeScript']) and \
           any('react' in dep.lower() or 'vue' in dep.lower() or 'angular' in dep.lower() 
               for dep in dependencies):
            return 'web-framework'
            
        # ML library indicators  
        if any('tensorflow' in dep.lower() or 'pytorch' in dep.lower() or 'sklearn' in dep.lower()
               for dep in dependencies):
            return 'ml-library'
            
        # CLI tool indicators
        if 'Python' in languages and any('cli' in f.lower() for f in files):
            return 'cli-tool'
            
        # Default fallback
        return 'generic-software'