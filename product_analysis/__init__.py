"""
Product Market Analysis Agent - A componentized framework for analyzing repositories

This package provides a reusable framework for conducting comprehensive product market analysis
of software repositories. It can be used across different projects to generate structured
analysis reports covering market positioning, feature gaps, and strategic recommendations.
"""

from .core import ProductAnalysisAgent
from .collectors import RepositoryCollector, ProjectMetadataCollector
from .analyzers import FeatureAnalyzer, MarketBenchmarkAnalyzer, CompetitiveAnalyzer
from .generators import MarkdownReportGenerator, AnalysisReportBuilder
from .templates import get_template_for_project_type

__version__ = "1.0.0"
__all__ = [
    "ProductAnalysisAgent",
    "RepositoryCollector", 
    "ProjectMetadataCollector",
    "FeatureAnalyzer",
    "MarketBenchmarkAnalyzer", 
    "CompetitiveAnalyzer",
    "MarkdownReportGenerator",
    "AnalysisReportBuilder",
    "get_template_for_project_type"
]