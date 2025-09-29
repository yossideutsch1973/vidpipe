"""
Tests for the Product Analysis Agent components

This test suite validates the functionality of the componentized
product analysis framework.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from product_analysis import (
    ProductAnalysisAgent,
    RepositoryCollector,
    ProjectMetadataCollector,
    FeatureAnalyzer,
    MarketBenchmarkAnalyzer,
    CompetitiveAnalyzer,
    MarkdownReportGenerator,
    AnalysisReportBuilder,
    get_template_for_project_type
)


class TestProductAnalysisAgent:
    """Test the main ProductAnalysisAgent orchestrator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create a minimal project structure
        (self.project_path / 'README.md').write_text('# Test Project\nA test project for analysis')
        (self.project_path / 'main.py').write_text('print("Hello, world!")')
        (self.project_path / 'requirements.txt').write_text('pytest>=6.0\nopencv-python>=4.5.0')
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = ProductAnalysisAgent(str(self.project_path))
        
        assert agent.project_path == self.project_path
        assert agent.project_type is None
        assert agent.repo_collector is not None
        assert agent.metadata_collector is not None
        
    def test_agent_with_specified_type(self):
        """Test agent initialization with specified project type"""
        agent = ProductAnalysisAgent(str(self.project_path), 'video-processing')
        
        assert agent.project_type == 'video-processing'
        
    def test_project_type_detection(self):
        """Test automatic project type detection"""
        agent = ProductAnalysisAgent(str(self.project_path))
        
        # Mock data that should trigger video-processing detection
        repo_data = {'key_files': ['video_processor.py']}
        metadata = {'dependencies': ['opencv-python>=4.5.0']}
        
        detected_type = agent._detect_project_type(repo_data, metadata)
        assert detected_type == 'video-processing'
        
    def test_web_framework_detection(self):
        """Test web framework project type detection"""
        agent = ProductAnalysisAgent(str(self.project_path))
        
        repo_data = {'key_files': ['app.js', 'index.html']}
        metadata = {
            'languages': {'JavaScript': 10, 'HTML': 5},
            'dependencies': ['react', 'webpack']
        }
        
        detected_type = agent._detect_project_type(repo_data, metadata)
        assert detected_type == 'web-framework'


class TestRepositoryCollector:
    """Test repository data collection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create test structure
        (self.project_path / 'src').mkdir()
        (self.project_path / 'tests').mkdir()
        (self.project_path / 'src' / 'main.py').write_text('# Main module')
        (self.project_path / 'tests' / 'test_main.py').write_text('# Test module')
        (self.project_path / 'README.md').write_text('# Test Project\n\n## Installation\n\n## Usage')
        (self.project_path / 'requirements.txt').write_text('pytest\nopencv-python')
        
    def test_collector_initialization(self):
        """Test collector initialization"""
        collector = RepositoryCollector(str(self.project_path))
        assert collector.project_path == self.project_path
        
    def test_directory_structure_analysis(self):
        """Test directory structure analysis"""
        collector = RepositoryCollector(str(self.project_path))
        data = collector.collect()
        
        structure = data['directory_structure']
        assert 'root' in structure
        assert 'src' in structure
        assert 'tests' in structure
        
        # Check file counts
        assert structure['src']['file_count'] == 1
        assert structure['tests']['file_count'] == 1
        
    def test_file_counting(self):
        """Test file counting by extension"""
        collector = RepositoryCollector(str(self.project_path))
        data = collector.collect()
        
        file_counts = data['file_counts']
        assert '.py' in file_counts
        assert file_counts['.py'] == 2  # main.py and test_main.py
        assert '.md' in file_counts
        assert file_counts['.md'] == 1  # README.md
        
    def test_readme_analysis(self):
        """Test README file analysis"""
        collector = RepositoryCollector(str(self.project_path))
        data = collector.collect()
        
        readme_analysis = data['readme_analysis']
        assert readme_analysis['found'] is True
        assert readme_analysis['filename'] == 'README.md'
        assert readme_analysis['has_installation_instructions'] is True
        assert readme_analysis['has_usage_examples'] is True
        
    def test_test_structure_detection(self):
        """Test detection of testing structure"""
        collector = RepositoryCollector(str(self.project_path))
        data = collector.collect()
        
        test_structure = data['test_structure']
        assert test_structure['has_testing'] is True
        assert len(test_structure['test_directories']) == 1
        assert 'tests' in test_structure['test_directories'][0]


class TestProjectMetadataCollector:
    """Test project metadata collection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
    def test_python_metadata_collection(self):
        """Test Python project metadata collection"""
        # Create pyproject.toml
        pyproject_content = '''
[project]
name = "test-project"
description = "A test project"
version = "1.0.0"
dependencies = ["pytest>=6.0", "opencv-python>=4.5.0"]
'''
        (self.project_path / 'pyproject.toml').write_text(pyproject_content)
        
        collector = ProjectMetadataCollector(str(self.project_path))
        data = collector.collect()
        
        assert data['project_name'] == 'test-project'
        assert data['description'] == 'A test project'
        assert data['version'] == '1.0.0'
        
    def test_node_metadata_collection(self):
        """Test Node.js project metadata collection"""
        package_json = {
            "name": "test-node-project",
            "version": "2.1.0",
            "description": "A test Node.js project",
            "dependencies": {
                "react": "^18.0.0",
                "webpack": "^5.0.0"
            }
        }
        
        (self.project_path / 'package.json').write_text(json.dumps(package_json))
        
        collector = ProjectMetadataCollector(str(self.project_path))
        data = collector.collect()
        
        assert data['project_name'] == 'test-node-project'
        assert data['description'] == 'A test Node.js project'
        assert data['version'] == '2.1.0'
        
    def test_language_detection(self):
        """Test programming language detection"""
        # Create files with different extensions
        (self.project_path / 'main.py').write_text('# Python file')
        (self.project_path / 'script.js').write_text('// JavaScript file')
        (self.project_path / 'style.css').write_text('/* CSS file */')
        
        collector = ProjectMetadataCollector(str(self.project_path))
        data = collector.collect()
        
        languages = data['languages']
        assert 'Python' in languages
        assert 'JavaScript' in languages
        assert 'CSS' in languages
        assert languages['Python'] == 1
        assert languages['JavaScript'] == 1


class TestTemplates:
    """Test analysis templates"""
    
    def test_video_processing_template(self):
        """Test video processing template"""
        template = get_template_for_project_type('video-processing')
        
        assert template.name == "Video Processing Framework"
        assert 'Core Language & Runtime' in template.feature_categories
        assert 'Video Sources' in template.feature_categories
        assert len(template.benchmark_criteria) > 0
        assert 'Direct Competitors' in template.competitor_categories
        
    def test_web_framework_template(self):
        """Test web framework template"""
        template = get_template_for_project_type('web-framework')
        
        assert template.name == "Web Framework"
        assert 'Core Framework' in template.feature_categories
        assert 'Performance' in template.feature_categories
        
    def test_generic_template_fallback(self):
        """Test fallback to generic template"""
        template = get_template_for_project_type('unknown-type')
        
        assert template.name == "Generic Software"
        assert 'Core Features' in template.feature_categories


class TestFeatureAnalyzer:
    """Test feature analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        template = get_template_for_project_type('video-processing')
        self.analyzer = FeatureAnalyzer(template.feature_categories)
        
    def test_feature_detection(self):
        """Test feature presence detection"""
        repo_data = {
            'key_files': ['gui_main.py', 'web_server.py'],
            'file_counts': {'.py': 10, '.html': 3}
        }
        metadata = {
            'dependencies': ['PyQt6', 'flask', 'opencv-python']
        }
        
        # Test CLI detection
        cli_present = self.analyzer._detect_feature_presence(
            'Command Line Interface', repo_data, metadata
        )
        # Should detect CLI from main.py pattern
        
        # Test GUI detection  
        gui_present = self.analyzer._detect_feature_presence(
            'Desktop GUI Editor', repo_data, metadata
        )
        assert gui_present is True  # Should detect from PyQt6 dependency
        
        # Test web interface detection
        web_present = self.analyzer._detect_feature_presence(
            'Web-based Editor', repo_data, metadata
        )
        assert web_present is True  # Should detect from flask + html files
        
    def test_market_standard_detection(self):
        """Test market standard feature identification"""
        # CLI should be considered market standard
        assert self.analyzer._is_market_standard('Command Line Interface') is True
        
        # GPU acceleration might not be standard everywhere
        assert self.analyzer._is_market_standard('GPU Acceleration') is False


class TestAnalysisReportBuilder:
    """Test analysis report building"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.builder = AnalysisReportBuilder()
        self.template = get_template_for_project_type('video-processing')
        
        # Mock analysis results
        self.analysis_results = {
            'timestamp': '2024-01-01T00:00:00',
            'project_path': '/test/project',
            'project_type': 'video-processing',
            'repository_data': {
                'file_counts': {'.py': 15, '.md': 3}
            },
            'project_metadata': {
                'project_name': 'test-vidpipe',
                'description': 'A test video processing library',
                'languages': {'Python': 15}
            },
            'feature_analysis': {
                'summary': {
                    'total_features': 20,
                    'present_features': 15,
                    'coverage_score': 0.75,
                    'critical_gaps': ['GPU Acceleration', 'Network Streaming'],
                    'key_strengths': ['Real-time Processing', 'Multi-threading Support']
                }
            },
            'competitive_analysis': {
                'market_niche': 'Programmable real-time video processing',
                'differentiation_opportunities': ['Web-based editor', 'Functional syntax']
            }
        }
        
    def test_report_building(self):
        """Test building structured report"""
        report = self.builder.build_report(self.analysis_results, self.template)
        
        assert 'metadata' in report
        assert 'overview' in report  
        assert 'benchmark' in report
        assert 'gaps' in report
        assert 'competitive' in report
        assert 'roadmap' in report
        
    def test_metadata_section(self):
        """Test metadata section building"""
        metadata = self.builder._build_metadata_section(self.analysis_results)
        
        assert metadata['project_name'] == 'test-vidpipe'
        assert metadata['project_type'] == 'video-processing'
        assert metadata['primary_language'] == 'Python'
        assert metadata['total_files'] == 18  # 15 .py + 3 .md
        
    def test_gaps_section(self):
        """Test gaps section building"""
        gaps = self.builder._build_gaps_section(self.analysis_results)
        
        assert 'critical_gaps' in gaps
        assert 'key_strengths' in gaps
        assert 'GPU Acceleration' in gaps['critical_gaps']
        assert 'Real-time Processing' in gaps['key_strengths']


class TestMarkdownReportGenerator:
    """Test markdown report generation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = MarkdownReportGenerator()
        
        # Mock report data
        self.report_data = {
            'metadata': {
                'project_name': 'test-project',
                'project_type': 'video-processing',
                'analysis_timestamp': '2024-01-01T00:00:00'
            },
            'overview': {
                'value_proposition': 'A test video processing library',
                'target_audience': 'developers and researchers',
                'key_differentiators': ['Web interface', 'Functional syntax']
            },
            'benchmark': {
                'feature_coverage_score': 0.75,
                'features_present': 15,
                'total_features_assessed': 20,
                'benchmark_table': [
                    {
                        'feature': 'Real-time Processing',
                        'category': 'Core',
                        'market_standard': '✅',
                        'present': '✅', 
                        'notes': 'Present - detected in project'
                    }
                ]
            },
            'gaps': {
                'critical_gaps': ['GPU Acceleration'],
                'key_strengths': ['Multi-threading'],
                'innovation_opportunities': ['AI-powered optimization']
            },
            'competitive': {
                'competitors': {
                    'Direct Competitors': ['OpenCV - Powerful library']
                },
                'market_position_summary': 'Unique positioning'
            },
            'roadmap': {
                'suggested_phases': [
                    {
                        'phase': 'Phase 1',
                        'description': 'Address critical gaps',
                        'items': ['Add GPU support']
                    }
                ]
            }
        }
        
    def test_markdown_generation(self):
        """Test markdown content generation"""
        content = self.generator._build_markdown_content(self.report_data)
        
        assert '# 📊 Product Market Analysis Report' in content
        assert '## 1. Product Overview' in content
        assert '## 2. Market Benchmarking' in content
        assert 'test-project' in content
        assert '75%' in content  # Coverage percentage
        
    def test_benchmark_table_generation(self):
        """Test benchmark table generation"""
        benchmark_section = self.generator._build_benchmarking_section(
            self.report_data['benchmark']
        )
        
        assert '| Feature | Market Standard? | Present in Repo? |' in benchmark_section
        assert 'Real-time Processing' in benchmark_section
        assert '75%' in benchmark_section


@pytest.fixture
def sample_repository(tmp_path):
    """Create a sample repository for testing"""
    # Create basic structure
    (tmp_path / 'src').mkdir()
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'docs').mkdir()
    
    # Create files
    (tmp_path / 'README.md').write_text('# Sample Project\n\n## Installation\n\n## Usage')
    (tmp_path / 'main.py').write_text('#!/usr/bin/env python\nprint("Hello")')
    (tmp_path / 'src' / 'core.py').write_text('# Core module')
    (tmp_path / 'tests' / 'test_core.py').write_text('# Tests')
    
    # Create pyproject.toml
    pyproject = '''
[project]
name = "sample-project"
description = "A sample project for testing"
version = "0.1.0"
dependencies = ["pytest>=6.0"]
'''
    (tmp_path / 'pyproject.toml').write_text(pyproject)
    
    return tmp_path


def test_full_integration(sample_repository):
    """Integration test of the complete analysis flow"""
    agent = ProductAnalysisAgent(str(sample_repository))
    
    # Run analysis
    results = agent.analyze()
    
    # Verify results structure
    assert 'repository_data' in results
    assert 'project_metadata' in results
    assert 'feature_analysis' in results
    assert 'benchmark_analysis' in results
    assert 'competitive_analysis' in results
    
    # Verify project detection
    assert results['project_type'] in ['generic-software', 'cli-tool']  # Could be either
    
    # Generate report
    report_path = agent.generate_report()
    assert Path(report_path).exists()
    
    # Verify report content
    content = Path(report_path).read_text()
    assert '# 📊 Product Market Analysis Report' in content
    assert 'sample-project' in content