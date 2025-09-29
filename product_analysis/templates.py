"""
Analysis Templates

This module contains templates that define how different types of projects
should be analyzed. Templates specify feature categories, benchmark criteria,
and competitive landscapes specific to different domains.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class AnalysisTemplate:
    """
    Template defining how to analyze a specific type of project
    """
    name: str
    description: str
    feature_categories: Dict[str, List[str]]
    benchmark_criteria: List[Dict[str, Any]]
    competitor_categories: Dict[str, List[str]]
    roadmap_priorities: List[str]
    

def get_template_for_project_type(project_type: str) -> AnalysisTemplate:
    """
    Get the appropriate analysis template for a project type
    
    Args:
        project_type: The type of project to analyze
        
    Returns:
        AnalysisTemplate instance for the project type
    """
    templates = {
        'video-processing': _get_video_processing_template(),
        'web-framework': _get_web_framework_template(),
        'ml-library': _get_ml_library_template(),
        'cli-tool': _get_cli_tool_template(),
        'generic-software': _get_generic_software_template()
    }
    
    return templates.get(project_type, templates['generic-software'])


def _get_video_processing_template() -> AnalysisTemplate:
    """Template for video processing projects like VidPipe"""
    return AnalysisTemplate(
        name="Video Processing Framework",
        description="Analysis template for video processing and computer vision libraries",
        feature_categories={
            "Core Language & Runtime": [
                "Visual/Node-based Editor",
                "Functional Pipeline Syntax", 
                "Real-time Processing",
                "Multi-threading Support",
                "Pipeline Definition/Reuse"
            ],
            "Development Interfaces": [
                "Command Line Interface",
                "Desktop GUI Editor", 
                "Web-based Editor",
                "API/SDK Integration"
            ],
            "Video Sources": [
                "Webcam/Camera Input",
                "File Input (Video/Image)",
                "Network Streams (RTSP/HTTP)",
                "Screen Capture",
                "Multiple Camera Support"
            ],
            "Processing Capabilities": [
                "Basic Filters (blur, edge, etc.)",
                "Color Space Conversions",
                "Geometric Transforms",
                "Feature Detection", 
                "Machine Learning Integration",
                "Custom Filter Plugins"
            ],
            "Output & Recording": [
                "Live Display Windows",
                "Video Recording",
                "Image Sequence Export",
                "Network Streaming Output",
                "Multi-format Export"
            ],
            "Performance & Scalability": [
                "GPU Acceleration",
                "Parallel Pipeline Execution",
                "Memory Management",
                "Batch Processing"
            ],
            "Enterprise Features": [
                "Configuration Management",
                "Version Control Integration", 
                "Monitoring/Logging",
                "REST API",
                "Docker/Container Support"
            ],
            "Distribution & Installation": [
                "Package Manager Distribution",
                "Binary/Executable Releases",
                "Cross-platform Support",
                "Documentation/Tutorials"
            ]
        },
        benchmark_criteria=[
            {
                "category": "Core Language & Runtime",
                "market_standard": True,
                "weight": "high",
                "examples": ["GStreamer", "OpenCV", "FFmpeg"]
            },
            {
                "category": "Performance & Scalability", 
                "market_standard": True,
                "weight": "high",
                "examples": ["CUDA acceleration", "Real-time processing"]
            },
            {
                "category": "Machine Learning Integration",
                "market_standard": True,
                "weight": "critical",
                "examples": ["YOLO", "TensorFlow", "ONNX Runtime"]
            }
        ],
        competitor_categories={
            "Direct Competitors": [
                "GStreamer - Industry standard, pipeline-based, but C-focused and complex syntax",
                "OpenCV Python - Powerful but requires manual threading and pipeline management", 
                "FFmpeg - Command-line video processing, limited real-time capabilities"
            ],
            "Adjacent Competitors": [
                "OBS Studio - User-friendly GUI, focused on streaming/recording, not programmable",
                "Node-RED - Visual flow programming, general-purpose but not video-optimized",
                "TouchDesigner - Node-based visual programming, expensive, creative industry focus"
            ],
            "Emerging Competition": [
                "Browser-based tools - Online video editors (Canva, etc.) but not real-time/programmable",
                "AI Platforms - RunwayML, Replicate - focus on ML models, not pipeline construction"
            ]
        },
        roadmap_priorities=[
            "Close critical market gaps (ML Integration, Network Streaming, GPU Acceleration)",
            "Enhance differentiation (Advanced Web Editor, Performance Profiler, Smart Templates)",
            "Position for future growth (Cloud Integration, Enterprise Features, Mobile/IoT Extensions)"
        ]
    )


def _get_web_framework_template() -> AnalysisTemplate:
    """Template for web frameworks and libraries"""
    return AnalysisTemplate(
        name="Web Framework",
        description="Analysis template for web frameworks and development tools",
        feature_categories={
            "Core Framework": [
                "Component Architecture",
                "State Management", 
                "Routing System",
                "Server-Side Rendering",
                "Static Site Generation"
            ],
            "Developer Experience": [
                "Hot Reload/Fast Refresh",
                "TypeScript Support",
                "CLI Tools",
                "IDE Integration",
                "Debugging Tools"
            ],
            "Performance": [
                "Bundle Size Optimization",
                "Code Splitting",
                "Lazy Loading",
                "Tree Shaking",
                "Performance Monitoring"
            ],
            "Ecosystem": [
                "Plugin Architecture",
                "Third-party Integration",
                "Community Packages",
                "Documentation Quality",
                "Learning Resources"
            ],
            "Production Features": [
                "Testing Framework",
                "Build System",
                "Deployment Tools",
                "Monitoring Integration",
                "Security Features"
            ]
        },
        benchmark_criteria=[
            {
                "category": "Core Framework",
                "market_standard": True,
                "weight": "high", 
                "examples": ["React", "Vue", "Angular"]
            },
            {
                "category": "Performance",
                "market_standard": True,
                "weight": "high",
                "examples": ["Fast initial load", "Small bundle size"]
            }
        ],
        competitor_categories={
            "Direct Competitors": [
                "React - Dominant market share, large ecosystem",
                "Vue - Growing popularity, gentle learning curve", 
                "Angular - Enterprise-focused, comprehensive framework"
            ],
            "Adjacent Competitors": [
                "Svelte - Compile-time optimization approach",
                "Next.js - React-based with additional features",
                "Nuxt.js - Vue-based framework with conventions"
            ]
        },
        roadmap_priorities=[
            "Performance optimization and bundle size reduction",
            "Developer experience improvements",
            "Ecosystem growth and third-party integrations"
        ]
    )


def _get_ml_library_template() -> AnalysisTemplate:
    """Template for machine learning libraries"""
    return AnalysisTemplate(
        name="Machine Learning Library",
        description="Analysis template for ML frameworks and tools",
        feature_categories={
            "Core ML Capabilities": [
                "Model Training",
                "Model Inference",
                "Pre-trained Models",
                "Transfer Learning",
                "Model Optimization"
            ],
            "Algorithms & Methods": [
                "Deep Learning",
                "Classical ML",
                "Reinforcement Learning",
                "Computer Vision",
                "Natural Language Processing"
            ],
            "Performance": [
                "GPU Acceleration",
                "Distributed Training",
                "Model Quantization",
                "ONNX Support",
                "Edge Deployment"
            ],
            "Developer Experience": [
                "Python API",
                "Jupyter Integration",
                "Visualization Tools",
                "Documentation",
                "Example Notebooks"
            ],
            "Production Features": [
                "Model Serving",
                "Monitoring",
                "A/B Testing",
                "Version Control",
                "MLOps Integration"
            ]
        },
        benchmark_criteria=[
            {
                "category": "Core ML Capabilities",
                "market_standard": True,
                "weight": "critical",
                "examples": ["TensorFlow", "PyTorch", "Scikit-learn"]
            }
        ],
        competitor_categories={
            "Direct Competitors": [
                "TensorFlow - Google's comprehensive ML platform",
                "PyTorch - Facebook's research-focused framework",
                "Scikit-learn - Traditional ML algorithms"
            ]
        },
        roadmap_priorities=[
            "Core algorithm implementation and optimization",
            "Performance and scalability improvements",
            "Production deployment capabilities"
        ]
    )


def _get_cli_tool_template() -> AnalysisTemplate:
    """Template for command-line tools"""
    return AnalysisTemplate(
        name="CLI Tool",
        description="Analysis template for command-line applications",
        feature_categories={
            "Core Functionality": [
                "Command Structure",
                "Argument Parsing",
                "Configuration Files",
                "Error Handling",
                "Output Formatting"
            ],
            "User Experience": [
                "Help Documentation",
                "Auto-completion",
                "Interactive Mode",
                "Progress Indicators",
                "Color Output"
            ],
            "Integration": [
                "Shell Integration",
                "Pipe Support",
                "Exit Codes",
                "Environment Variables",
                "Config File Format"
            ],
            "Distribution": [
                "Package Manager Support",
                "Binary Distribution",
                "Cross-platform Support",
                "Installation Scripts",
                "Update Mechanism"
            ]
        },
        benchmark_criteria=[
            {
                "category": "User Experience", 
                "market_standard": True,
                "weight": "high",
                "examples": ["Git", "Docker", "AWS CLI"]
            }
        ],
        competitor_categories={
            "Similar Tools": ["Tools in the same domain"]
        },
        roadmap_priorities=[
            "User experience improvements",
            "Cross-platform compatibility",
            "Integration capabilities"
        ]
    )


def _get_generic_software_template() -> AnalysisTemplate:
    """Generic template for software projects"""
    return AnalysisTemplate(
        name="Generic Software",
        description="Generic analysis template for software projects",
        feature_categories={
            "Core Features": [
                "Primary Functionality",
                "API Design",
                "Configuration",
                "Error Handling"
            ],
            "Quality Assurance": [
                "Testing Coverage",
                "Code Quality",
                "Documentation",
                "Examples"
            ],
            "Performance": [
                "Speed",
                "Memory Usage", 
                "Scalability",
                "Resource Management"
            ],
            "Usability": [
                "Ease of Use",
                "Learning Curve",
                "Integration",
                "Customization"
            ],
            "Maintenance": [
                "Code Structure",
                "Dependency Management",
                "Version Control",
                "Release Process"
            ]
        },
        benchmark_criteria=[
            {
                "category": "Core Features",
                "market_standard": True,
                "weight": "high",
                "examples": ["Industry standard tools"]
            }
        ],
        competitor_categories={
            "Competitors": ["Similar projects in the domain"]
        },
        roadmap_priorities=[
            "Core functionality completion",
            "Performance optimization",
            "User experience improvements"
        ]
    )