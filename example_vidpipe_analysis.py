#!/usr/bin/env python3
"""
Example: Using the Product Analysis Agent on VidPipe

This script demonstrates how to use the componentized product analysis 
agent to analyze the VidPipe repository itself, showing how the framework
can be applied to generate the kind of analysis that was done manually before.
"""

import sys
import json
from pathlib import Path

# Add the current directory to Python path to import product_analysis
sys.path.insert(0, str(Path(__file__).parent))

from product_analysis import ProductAnalysisAgent


def main():
    """
    Demonstrate the product analysis agent on VidPipe
    """
    print("🎯 Product Analysis Agent - VidPipe Example")
    print("=" * 50)
    
    # Get the current directory (should be the VidPipe repo root)
    repo_path = Path(__file__).parent
    print(f"📁 Analyzing repository: {repo_path}")
    
    try:
        # Initialize the analysis agent for video processing project
        print("\n🔧 Initializing analysis agent...")
        agent = ProductAnalysisAgent(str(repo_path), project_type='video-processing')
        
        # Run the complete analysis
        print("🔍 Running comprehensive analysis...")
        results, report_path = agent.run_full_analysis()
        
        print(f"\n✅ Analysis complete!")
        print(f"📄 Report generated: {report_path}")
        
        # Show a summary of the results
        print("\n" + "="*50)
        print("📊 ANALYSIS SUMMARY")
        print("="*50)
        
        # Project information
        metadata = results.get('project_metadata', {})
        print(f"🎯 Project Name: {metadata.get('project_name', 'Unknown')}")
        print(f"🏷️  Project Type: {results.get('project_type', 'Unknown')}")
        print(f"🗣️  Primary Language: {agent.report_builder._get_primary_language(metadata)}")
        
        # Feature analysis summary
        feature_analysis = results.get('feature_analysis', {})
        summary = feature_analysis.get('summary', {})
        
        total_features = summary.get('total_features', 0)
        present_features = summary.get('present_features', 0)
        coverage_score = summary.get('coverage_score', 0.0)
        
        print(f"\n📈 Feature Coverage: {present_features}/{total_features} ({coverage_score:.1%})")
        
        # Critical gaps
        critical_gaps = summary.get('critical_gaps', [])
        if critical_gaps:
            print(f"\n🚨 Critical Gaps ({len(critical_gaps)}):")
            for i, gap in enumerate(critical_gaps[:5], 1):
                print(f"   {i}. {gap}")
                
        # Key strengths  
        strengths = summary.get('key_strengths', [])
        if strengths:
            print(f"\n✨ Key Strengths ({len(strengths)}):")
            for i, strength in enumerate(strengths[:5], 1):
                print(f"   {i}. {strength}")
                
        # Competitive positioning
        competitive = results.get('competitive_analysis', {})
        market_niche = competitive.get('market_niche', 'Unknown')
        print(f"\n🏢 Market Niche: {market_niche}")
        
        differentiators = competitive.get('differentiation_opportunities', [])
        if differentiators:
            print(f"\n🎯 Key Differentiators:")
            for i, diff in enumerate(differentiators[:3], 1):
                print(f"   {i}. {diff}")
                
        # Benchmark score
        benchmark = results.get('benchmark_analysis', {})
        overall_score = benchmark.get('overall_score', 0.0)
        print(f"\n📊 Overall Benchmark Score: {overall_score:.1%}")
        
        # Show some example feature assessments
        print(f"\n📋 Sample Feature Assessments:")
        assessments = feature_analysis.get('feature_assessments', {})
        
        # Show a few key features from different categories
        sample_features = []
        for category, features in list(assessments.items())[:3]:  # First 3 categories
            if features:
                feature = features[0]  # First feature in category
                status = "✅" if feature.present else "❌"
                sample_features.append(f"   • {feature.name} ({category}): {status}")
                
        for feature in sample_features[:5]:
            print(feature)
            
        print(f"\n💾 For complete details, see: {report_path}")
        
        # Optionally save raw data for further analysis
        json_path = Path(report_path).with_suffix('.json')
        print(f"📊 Saving raw analysis data to: {json_path}")
        
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        print("\n🎉 Analysis complete! Use the generated report to understand")
        print("   VidPipe's market position and development priorities.")
        
        return results, report_path
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def demonstrate_customization():
    """
    Show how to customize the analysis for specific needs
    """
    print("\n" + "="*50)
    print("🔧 CUSTOMIZATION EXAMPLE")
    print("="*50)
    
    repo_path = Path(__file__).parent
    
    # Example 1: Custom feature detection
    print("Example 1: Custom Feature Detection")
    
    from product_analysis.analyzers import FeatureAnalyzer
    from product_analysis.templates import get_template_for_project_type
    
    template = get_template_for_project_type('video-processing')
    
    class CustomFeatureAnalyzer(FeatureAnalyzer):
        def _detect_feature_presence(self, feature, repo_data, metadata):
            # Custom logic for VidPipe-specific features
            if feature == "Functional Pipeline Syntax":
                # Check for DSL-related files
                key_files = repo_data.get('key_files', [])
                return any('parser' in f.lower() or 'lexer' in f.lower() or 'ast' in f.lower() 
                          for f in key_files)
            elif feature == "Multi-interface Support":
                # Check for CLI, GUI, and web interfaces
                files = repo_data.get('key_files', [])
                has_cli = any('cli' in f.lower() for f in files)
                has_gui = any('gui' in f.lower() for f in files) 
                has_web = any('web' in f.lower() for f in files)
                return sum([has_cli, has_gui, has_web]) >= 2
                
            return super()._detect_feature_presence(feature, repo_data, metadata)
    
    print("   ✓ Custom analyzer with VidPipe-specific feature detection")
    
    # Example 2: Custom report formatting
    print("Example 2: Custom Report Builder")
    
    from product_analysis.generators import AnalysisReportBuilder
    
    class VidPipeReportBuilder(AnalysisReportBuilder):
        def _generate_value_proposition(self, results):
            # Custom value prop for VidPipe
            return ("VidPipe is a composable functional pipeline language and runtime "
                   "for building real-time video processing workflows in Python. "
                   "It features a domain-specific language (DSL) that combines "
                   "functional programming concepts with computer vision operations.")
    
    print("   ✓ Custom report builder with VidPipe-specific formatting")
    
    # Example 3: Multiple project analysis
    print("Example 3: Batch Analysis Capability")
    
    def analyze_multiple_projects(project_paths):
        """Analyze multiple repositories"""
        results = {}
        for path in project_paths:
            if Path(path).exists():
                agent = ProductAnalysisAgent(str(path))
                project_results = agent.analyze()
                results[path] = {
                    'coverage_score': project_results.get('feature_analysis', {})
                                    .get('summary', {}).get('coverage_score', 0),
                    'project_type': project_results.get('project_type'),
                    'critical_gaps_count': len(project_results.get('feature_analysis', {})
                                              .get('summary', {}).get('critical_gaps', []))
                }
        return results
    
    print("   ✓ Batch analysis function for comparing multiple projects")
    print("\n🎯 These examples show how the componentized framework")
    print("   can be extended and customized for specific needs!")


if __name__ == '__main__':
    # Run the main analysis
    results, report_path = main()
    
    if results:
        # Show customization examples
        demonstrate_customization()
        
        print("\n" + "="*50)
        print("🚀 NEXT STEPS")
        print("="*50)
        print("1. Review the generated analysis report")
        print("2. Use insights to prioritize development work")
        print("3. Apply the framework to other repositories")
        print("4. Customize templates for your specific domain")
        print("5. Integrate into CI/CD for ongoing analysis")
    else:
        print("❌ Analysis failed - check error messages above")
        sys.exit(1)