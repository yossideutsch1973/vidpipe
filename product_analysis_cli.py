#!/usr/bin/env python3
"""
Product Analysis Agent CLI

Command-line interface for running product market analysis on repositories
"""

import argparse
import sys
from pathlib import Path

from product_analysis import ProductAnalysisAgent


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze a repository's product market position",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory with auto-detection
  %(prog)s .
  
  # Analyze specific project type
  %(prog)s /path/to/repo --type video-processing
  
  # Specify custom output location
  %(prog)s . --output my-analysis.md
  
  # Available project types:
  - video-processing: Video processing and computer vision tools
  - web-framework: Web development frameworks and libraries  
  - ml-library: Machine learning and data science tools
  - cli-tool: Command-line applications
  - generic-software: General software projects (default)
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to the repository to analyze'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['video-processing', 'web-framework', 'ml-library', 'cli-tool', 'generic-software'],
        help='Project type (auto-detected if not specified)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (defaults to PRODUCT_MARKET_ANALYSIS.md in project root)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Also output raw analysis results as JSON'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate path
    project_path = Path(args.path).resolve()
    if not project_path.exists():
        print(f"Error: Path '{project_path}' does not exist", file=sys.stderr)
        sys.exit(1)
        
    if not project_path.is_dir():
        print(f"Error: Path '{project_path}' is not a directory", file=sys.stderr)
        sys.exit(1)
        
    try:
        # Initialize the analysis agent
        agent = ProductAnalysisAgent(str(project_path), args.type)
        
        # Run analysis and generate report
        print(f"🎯 Analyzing repository: {project_path}")
        if args.type:
            print(f"📋 Using project type: {args.type}")
        else:
            print("🔍 Auto-detecting project type...")
            
        results, report_path = agent.run_full_analysis(args.output)
        
        print(f"✅ Analysis complete!")
        print(f"📄 Report generated: {report_path}")
        
        # Output JSON if requested
        if args.json:
            import json
            json_path = Path(report_path).with_suffix('.json')
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📊 Raw data saved: {json_path}")
            
        # Show summary if verbose
        if args.verbose:
            print("\n" + "="*50)
            print("ANALYSIS SUMMARY")
            print("="*50)
            
            feature_analysis = results.get('feature_analysis', {})
            summary = feature_analysis.get('summary', {})
            
            print(f"Project Type: {results.get('project_type', 'Unknown')}")
            print(f"Features Assessed: {summary.get('total_features', 0)}")
            print(f"Features Present: {summary.get('present_features', 0)}")
            print(f"Coverage Score: {summary.get('coverage_score', 0.0):.1%}")
            
            critical_gaps = summary.get('critical_gaps', [])
            if critical_gaps:
                print(f"\nCritical Gaps ({len(critical_gaps)}):")
                for gap in critical_gaps[:5]:
                    print(f"  • {gap}")
                    
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()