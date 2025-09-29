"""
Analysis Components

This module contains specialized analyzers that examine different aspects
of a project's market position and competitive landscape.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass 
class FeatureAssessment:
    """Assessment of a single feature"""
    name: str
    present: bool
    market_standard: bool
    notes: str
    opportunity_level: str  # 'critical', 'high', 'medium', 'low'


@dataclass
class BenchmarkResult:
    """Result of benchmarking against market standards"""
    category: str
    features: List[FeatureAssessment]
    score: float  # 0.0 to 1.0
    gaps: List[str]
    strengths: List[str]


class FeatureAnalyzer:
    """
    Analyzes project features against defined categories
    """
    
    def __init__(self, feature_categories: Dict[str, List[str]]):
        self.feature_categories = feature_categories
        
    def analyze(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project features across all categories
        
        Args:
            repo_data: Repository data from collector
            metadata: Project metadata from collector
            
        Returns:
            Dictionary containing feature analysis results
        """
        assessments = {}
        
        for category, features in self.feature_categories.items():
            category_assessments = []
            
            for feature in features:
                assessment = self._assess_feature(feature, repo_data, metadata)
                category_assessments.append(assessment)
                
            assessments[category] = category_assessments
            
        return {
            'feature_assessments': assessments,
            'summary': self._generate_feature_summary(assessments)
        }
        
    def _assess_feature(self, feature: str, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> FeatureAssessment:
        """
        Assess whether a specific feature is present in the project
        
        Args:
            feature: Name of the feature to assess
            repo_data: Repository data
            metadata: Project metadata
            
        Returns:
            FeatureAssessment for the feature
        """
        # Feature detection logic based on patterns
        present = self._detect_feature_presence(feature, repo_data, metadata)
        market_standard = self._is_market_standard(feature)
        notes = self._generate_feature_notes(feature, present, repo_data, metadata)
        opportunity_level = self._assess_opportunity_level(feature, present, market_standard)
        
        return FeatureAssessment(
            name=feature,
            present=present,
            market_standard=market_standard,
            notes=notes,
            opportunity_level=opportunity_level
        )
        
    def _detect_feature_presence(self, feature: str, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """
        Detect if a feature is present based on repository analysis
        
        This uses pattern matching against file structures, dependencies, and content
        """
        feature_lower = feature.lower()
        
        # Check dependencies
        dependencies = metadata.get('dependencies', [])
        dep_text = ' '.join(dependencies).lower()
        
        # Check file structure
        key_files = repo_data.get('key_files', [])
        files_text = ' '.join(key_files).lower()
        
        # Check directory structure
        dirs = []
        structure = repo_data.get('directory_structure', {})
        for path, info in structure.items():
            dirs.extend(info.get('subdirectories', []))
        dir_text = ' '.join(dirs).lower()
        
        # Feature-specific detection patterns
        detection_patterns = {
            'command line interface': ['cli', 'main.py', 'argparse', 'click', 'typer'],
            'desktop gui editor': ['gui', 'qt', 'pyqt', 'tkinter', 'wx'],
            'web-based editor': ['web', 'flask', 'django', 'fastapi', 'html', 'javascript'],
            'api/sdk integration': ['api', 'sdk', 'rest', 'graphql'],
            'real-time processing': ['threading', 'asyncio', 'queue', 'real-time', 'stream'],
            'multi-threading support': ['thread', 'multiprocess', 'concurrent', 'parallel'],
            'gpu acceleration': ['cuda', 'opencl', 'gpu', 'tensorflow-gpu'],
            'machine learning integration': ['tensorflow', 'pytorch', 'sklearn', 'ml', 'ai'],
            'webcam/camera input': ['opencv', 'cv2', 'camera', 'webcam', 'capture'],
            'video recording': ['record', 'encode', 'video', 'mp4', 'avi'],
            'network streaming': ['rtsp', 'rtmp', 'webrtc', 'stream', 'broadcast'],
            'testing framework': ['test', 'pytest', 'unittest', 'jest'],
            'documentation': ['docs/', 'readme', '.md', 'sphinx'],
            'docker/container support': ['dockerfile', 'docker-compose', 'container'],
            'configuration management': ['config', 'settings', 'yaml', 'json', 'toml'],
            'version control integration': ['git', '.git/', 'version'],
            'package manager distribution': ['pyproject.toml', 'setup.py', 'package.json'],
            'cross-platform support': ['windows', 'linux', 'macos', 'platform']
        }
        
        # Check for patterns
        patterns = detection_patterns.get(feature_lower, [])
        for pattern in patterns:
            if pattern in dep_text or pattern in files_text or pattern in dir_text:
                return True
                
        # Special case: check for specific feature indicators in file counts
        file_counts = repo_data.get('file_counts', {})
        if 'web-based' in feature_lower and ('.html' in file_counts or '.js' in file_counts):
            return True
        if 'gui' in feature_lower and '.ui' in file_counts:
            return True
            
        return False
        
    def _is_market_standard(self, feature: str) -> bool:
        """
        Determine if a feature is considered a market standard
        
        This could be made configurable per template in the future
        """
        market_standards = {
            'command line interface', 'documentation/tutorials', 'version control integration',
            'real-time processing', 'multi-threading support', 'testing framework',
            'package manager distribution', 'cross-platform support', 'configuration management'
        }
        
        return feature.lower() in market_standards
        
    def _generate_feature_notes(self, feature: str, present: bool, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generate descriptive notes about the feature assessment"""
        if present:
            return f"Present – detected in project structure"
        else:
            if self._is_market_standard(feature):
                return f"Missing – considered market standard"
            else:
                return f"Missing – opportunity for differentiation"
                
    def _assess_opportunity_level(self, feature: str, present: bool, market_standard: bool) -> str:
        """Assess the opportunity level for a missing feature"""
        if present:
            return "satisfied"
            
        if market_standard:
            return "critical"
        else:
            return "medium"
            
    def _generate_feature_summary(self, assessments: Dict[str, List[FeatureAssessment]]) -> Dict[str, Any]:
        """Generate a summary of feature analysis"""
        total_features = 0
        present_features = 0
        critical_gaps = []
        strengths = []
        
        for category, features in assessments.items():
            for feature in features:
                total_features += 1
                if feature.present:
                    present_features += 1
                    if feature.market_standard:
                        strengths.append(f"{feature.name} ({category})")
                else:
                    if feature.opportunity_level == "critical":
                        critical_gaps.append(f"{feature.name} ({category})")
                        
        coverage_score = present_features / total_features if total_features > 0 else 0
        
        return {
            'total_features': total_features,
            'present_features': present_features,
            'coverage_score': coverage_score,
            'critical_gaps': critical_gaps,
            'key_strengths': strengths[:10]  # Top 10 strengths
        }


class MarketBenchmarkAnalyzer:
    """
    Analyzes project against market benchmarks and standards
    """
    
    def __init__(self, benchmark_criteria: List[Dict[str, Any]]):
        self.benchmark_criteria = benchmark_criteria
        
    def analyze(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project against market benchmarks
        
        Args:
            repo_data: Repository data from collector
            metadata: Project metadata from collector
            
        Returns:
            Dictionary containing benchmark analysis results
        """
        results = []
        
        for criteria in self.benchmark_criteria:
            result = self._benchmark_category(criteria, repo_data, metadata)
            results.append(result)
            
        return {
            'benchmark_results': results,
            'overall_score': self._calculate_overall_score(results),
            'recommendations': self._generate_recommendations(results)
        }
        
    def _benchmark_category(self, criteria: Dict[str, Any], repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> BenchmarkResult:
        """Benchmark a specific category against market standards"""
        category = criteria['category']
        weight = criteria.get('weight', 'medium')
        examples = criteria.get('examples', [])
        
        # This is a simplified benchmark - in practice, you'd have more sophisticated scoring
        features_in_category = self._get_category_features(category, repo_data, metadata)
        
        gaps = []
        strengths = []
        
        # Analyze gaps and strengths (simplified)
        if 'Machine Learning' in category and not self._has_ml_support(repo_data, metadata):
            gaps.append("No ML framework integration detected")
        elif 'Machine Learning' in category:
            strengths.append("ML framework support detected")
            
        if 'Performance' in category and not self._has_performance_features(repo_data, metadata):
            gaps.append("Limited performance optimization features")
        elif 'Performance' in category:
            strengths.append("Performance optimization features present")
            
        # Calculate score based on gaps
        score = max(0.0, 1.0 - (len(gaps) * 0.3))
        
        return BenchmarkResult(
            category=category,
            features=features_in_category,
            score=score,
            gaps=gaps,
            strengths=strengths
        )
        
    def _get_category_features(self, category: str, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> List[FeatureAssessment]:
        """Get features for a specific category (simplified implementation)"""
        # This would be more sophisticated in practice
        return []
        
    def _has_ml_support(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Check if project has ML support"""
        dependencies = metadata.get('dependencies', [])
        ml_libs = ['tensorflow', 'pytorch', 'sklearn', 'onnx', 'keras']
        return any(ml_lib in ' '.join(dependencies).lower() for ml_lib in ml_libs)
        
    def _has_performance_features(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Check if project has performance features"""
        dependencies = metadata.get('dependencies', [])
        files = repo_data.get('key_files', [])
        
        perf_indicators = ['threading', 'multiprocess', 'asyncio', 'cython', 'numba']
        text = ' '.join(dependencies + files).lower()
        
        return any(indicator in text for indicator in perf_indicators)
        
    def _calculate_overall_score(self, results: List[BenchmarkResult]) -> float:
        """Calculate overall benchmark score"""
        if not results:
            return 0.0
            
        return sum(result.score for result in results) / len(results)
        
    def _generate_recommendations(self, results: List[BenchmarkResult]) -> List[str]:
        """Generate recommendations based on benchmark results"""
        recommendations = []
        
        for result in results:
            if result.score < 0.7:  # Below threshold
                for gap in result.gaps:
                    recommendations.append(f"Address {gap} in {result.category}")
                    
        return recommendations[:5]  # Top 5 recommendations


class CompetitiveAnalyzer:
    """
    Analyzes competitive landscape and positioning
    """
    
    def __init__(self, competitor_categories: Dict[str, List[str]]):
        self.competitor_categories = competitor_categories
        
    def analyze(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitive landscape
        
        Args:
            repo_data: Repository data from collector  
            metadata: Project metadata from collector
            
        Returns:
            Dictionary containing competitive analysis results
        """
        positioning = self._analyze_positioning(repo_data, metadata)
        differentiation = self._identify_differentiation_opportunities(repo_data, metadata)
        threats = self._assess_competitive_threats()
        
        return {
            'competitors': self.competitor_categories,
            'positioning': positioning,
            'differentiation_opportunities': differentiation,
            'competitive_threats': threats,
            'market_niche': self._identify_market_niche(repo_data, metadata)
        }
        
    def _analyze_positioning(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, str]:
        """Analyze project's market positioning"""
        languages = metadata.get('languages', {})
        dependencies = metadata.get('dependencies', [])
        
        # Determine positioning based on technical characteristics
        positioning = {}
        
        if 'Python' in languages:
            positioning['language_focus'] = "Python-centric, developer-friendly"
            
        if any('web' in dep.lower() for dep in dependencies):
            positioning['interface'] = "Multi-interface (CLI, GUI, Web)"
        else:
            positioning['interface'] = "Traditional command-line focused"
            
        return positioning
        
    def _identify_differentiation_opportunities(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> List[str]:
        """Identify opportunities for differentiation"""
        opportunities = []
        
        # Check for unique features
        key_files = repo_data.get('key_files', [])
        if any('web' in f.lower() for f in key_files):
            opportunities.append("Web-based interface - ahead of market trend")
            
        # Check for functional programming approach
        readme_analysis = repo_data.get('readme_analysis', {})
        if readme_analysis.get('found') and 'functional' in str(readme_analysis):
            opportunities.append("Functional programming approach - unique in domain")
            
        return opportunities
        
    def _assess_competitive_threats(self) -> List[str]:
        """Assess competitive threats"""
        threats = []
        
        # Generic threats based on competitor categories
        if "Direct Competitors" in self.competitor_categories:
            threats.append("Established players with large user bases")
            
        if "Emerging Competition" in self.competitor_categories:
            threats.append("New entrants with modern approaches")
            
        return threats
        
    def _identify_market_niche(self, repo_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Identify the project's market niche"""
        description = metadata.get('description', '')
        
        if 'video' in description.lower():
            return "Programmable real-time video processing for developers"
        elif 'web' in description.lower():
            return "Modern web development framework"
        elif 'ml' in description.lower() or 'machine learning' in description.lower():
            return "Machine learning tools and utilities"
        else:
            return "Specialized developer tool"