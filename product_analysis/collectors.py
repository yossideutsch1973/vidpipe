"""
Data Collectors

This module contains classes responsible for collecting data about repositories
and projects to feed into the analysis process.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess


class RepositoryCollector:
    """
    Collects data from the repository structure and files
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def collect(self) -> Dict[str, Any]:
        """
        Collect comprehensive repository data
        
        Returns:
            Dictionary containing repository analysis data
        """
        return {
            'directory_structure': self._analyze_directory_structure(),
            'file_counts': self._get_file_counts(),
            'key_files': self._identify_key_files(),
            'readme_analysis': self._analyze_readme(),
            'documentation_files': self._find_documentation_files(),
            'test_structure': self._analyze_test_structure(),
            'build_configuration': self._analyze_build_config(),
            'git_info': self._get_git_info()
        }
        
    def _analyze_directory_structure(self) -> Dict[str, Any]:
        """Analyze the overall directory structure"""
        structure = {}
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == '.':
                rel_path = 'root'
                
            structure[rel_path] = {
                'subdirectories': dirs.copy(),
                'file_count': len(files),
                'key_files': [f for f in files if self._is_key_file(f)]
            }
            
        return structure
        
    def _get_file_counts(self) -> Dict[str, int]:
        """Count files by extension"""
        file_counts = {}
        
        for root, _, files in os.walk(self.project_path):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'node_modules', '.pytest_cache']):
                continue
                
            for file in files:
                ext = Path(file).suffix.lower()
                if ext:
                    file_counts[ext] = file_counts.get(ext, 0) + 1
                    
        return file_counts
        
    def _identify_key_files(self) -> List[str]:
        """Identify important configuration and documentation files"""
        key_patterns = [
            'README*', 'readme*',
            'requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg',
            'package.json', 'package-lock.json',
            'Dockerfile', 'docker-compose.yml',
            'Makefile', 'makefile',
            '.github/workflows/*',
            'LICENSE*', 'license*',
            '*.md'
        ]
        
        key_files = []
        for root, _, files in os.walk(self.project_path):
            if '.git' in root:
                continue
                
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                for pattern in key_patterns:
                    if self._match_pattern(file, pattern) or self._match_pattern(rel_path, pattern):
                        key_files.append(rel_path)
                        break
                        
        return sorted(set(key_files))
        
    def _analyze_readme(self) -> Dict[str, Any]:
        """Analyze README file content"""
        readme_files = []
        for file in os.listdir(self.project_path):
            if file.lower().startswith('readme'):
                readme_files.append(file)
                
        if not readme_files:
            return {'found': False}
            
        readme_path = self.project_path / readme_files[0]
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'found': True,
                'filename': readme_files[0],
                'length': len(content),
                'sections': self._extract_markdown_sections(content),
                'has_installation_instructions': 'install' in content.lower(),
                'has_usage_examples': any(keyword in content.lower() for keyword in ['usage', 'example', 'getting started']),
                'has_contributing_guide': 'contribut' in content.lower(),
                'badge_count': len(re.findall(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', content))
            }
        except Exception:
            return {'found': True, 'filename': readme_files[0], 'error': 'Could not read file'}
            
    def _analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze testing setup and structure"""
        test_dirs = []
        test_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Look for test directories
            for dir_name in dirs:
                if any(test_pattern in dir_name.lower() for test_pattern in ['test', 'spec']):
                    rel_path = os.path.relpath(os.path.join(root, dir_name), self.project_path)
                    test_dirs.append(rel_path)
                    
            # Look for test files
            for file in files:
                if any(test_pattern in file.lower() for test_pattern in ['test_', '_test', '.test.', '.spec.']):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                    test_files.append(rel_path)
                    
        return {
            'test_directories': test_dirs,
            'test_files': test_files,
            'test_file_count': len(test_files),
            'has_testing': len(test_dirs) > 0 or len(test_files) > 0
        }
        
    def _analyze_build_config(self) -> Dict[str, Any]:
        """Analyze build and configuration files"""
        config_files = {}
        
        config_patterns = {
            'python': ['pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt'],
            'node': ['package.json', 'package-lock.json', 'yarn.lock'],
            'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
            'ci_cd': ['.github/workflows/*.yml', '.github/workflows/*.yaml', '.travis.yml', 'circle.yml'],
            'build': ['Makefile', 'makefile', 'CMakeLists.txt', 'build.gradle']
        }
        
        for category, patterns in config_patterns.items():
            found_files = []
            for pattern in patterns:
                if '*' in pattern:
                    # Handle wildcard patterns
                    for root, _, files in os.walk(self.project_path):
                        dir_path = Path(root)
                        pattern_dir = self.project_path / pattern.split('*')[0].rstrip('/')
                        if dir_path == pattern_dir.parent:
                            matching_files = [f for f in files if f.endswith(pattern.split('*')[1])]
                            found_files.extend([str(pattern_dir / f) for f in matching_files])
                else:
                    file_path = self.project_path / pattern
                    if file_path.exists():
                        found_files.append(str(file_path.relative_to(self.project_path)))
                        
            config_files[category] = found_files
            
        return config_files
        
    def _get_git_info(self) -> Dict[str, Any]:
        """Get basic git repository information"""
        try:
            # Check if it's a git repository
            git_dir = self.project_path / '.git'
            if not git_dir.exists():
                return {'is_git_repo': False}
                
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            commit_count = len(result.stdout.strip().split('\n')) if result.returncode == 0 else 0
            
            return {
                'is_git_repo': True,
                'recent_commit_count': commit_count,
                'has_recent_activity': commit_count > 0
            }
        except Exception:
            return {'is_git_repo': True, 'error': 'Could not read git info'}
            
    def _is_key_file(self, filename: str) -> bool:
        """Check if a file is considered important"""
        key_files = [
            'readme', 'license', 'changelog', 'contributing',
            'dockerfile', 'makefile', 'requirements.txt',
            'package.json', 'pyproject.toml', 'setup.py'
        ]
        return any(key in filename.lower() for key in key_files)
        
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """Simple pattern matching with * wildcard support"""
        if '*' not in pattern:
            return text.lower() == pattern.lower()
        return re.match(pattern.lower().replace('*', '.*'), text.lower()) is not None
        
    def _extract_markdown_sections(self, content: str) -> List[str]:
        """Extract section headers from markdown content"""
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return headers
        
    def _find_documentation_files(self) -> List[str]:
        """Find documentation files and directories"""
        doc_files = []
        doc_patterns = ['docs/', 'doc/', 'documentation/', '*.md', '*.rst']
        
        for root, dirs, files in os.walk(self.project_path):
            if '.git' in root:
                continue
                
            # Check directories
            for dir_name in dirs:
                if any(pattern.rstrip('/') in dir_name.lower() for pattern in doc_patterns if pattern.endswith('/')):
                    rel_path = os.path.relpath(os.path.join(root, dir_name), self.project_path)
                    doc_files.append(f"{rel_path}/")
                    
            # Check files
            for file in files:
                if any(file.lower().endswith(pattern.lstrip('*')) for pattern in doc_patterns if pattern.startswith('*')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_path)
                    doc_files.append(rel_path)
                    
        return sorted(set(doc_files))


class ProjectMetadataCollector:
    """
    Collects project metadata from configuration files and package managers
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def collect(self) -> Dict[str, Any]:
        """
        Collect project metadata from various sources
        
        Returns:
            Dictionary containing project metadata
        """
        return {
            'python_metadata': self._collect_python_metadata(),
            'node_metadata': self._collect_node_metadata(),
            'languages': self._detect_languages(),
            'dependencies': self._collect_dependencies(),
            'project_name': self._extract_project_name(),
            'description': self._extract_description(),
            'version': self._extract_version()
        }
        
    def _collect_python_metadata(self) -> Dict[str, Any]:
        """Collect Python project metadata"""
        metadata = {}
        
        # Check pyproject.toml
        pyproject_path = self.project_path / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                # Try tomllib (Python 3.11+) first, then fallback to tomli
                try:
                    import tomllib
                    with open(pyproject_path, 'rb') as f:
                        data = tomllib.load(f)
                except ImportError:
                    try:
                        import tomli
                        with open(pyproject_path, 'rb') as f:
                            data = tomli.load(f)
                    except ImportError:
                        # Fallback to basic text parsing
                        with open(pyproject_path, 'r') as f:
                            content = f.read()
                        # Simple extraction of project name and description
                        import re
                        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                        data = {
                            'project': {
                                'name': name_match.group(1) if name_match else None,
                                'description': desc_match.group(1) if desc_match else None
                            }
                        }
                metadata['pyproject'] = data.get('project', {})
            except Exception:
                metadata['pyproject'] = {'found': True, 'error': 'Could not parse TOML'}
                
        # Check setup.py
        setup_py_path = self.project_path / 'setup.py'
        if setup_py_path.exists():
            metadata['setup_py'] = {'found': True}
            
        # Check requirements.txt
        req_path = self.project_path / 'requirements.txt'
        if req_path.exists():
            try:
                with open(req_path, 'r') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                metadata['requirements'] = requirements
            except Exception:
                metadata['requirements'] = {'error': 'Could not read requirements.txt'}
                
        return metadata
        
    def _collect_node_metadata(self) -> Dict[str, Any]:
        """Collect Node.js project metadata"""
        package_json_path = self.project_path / 'package.json'
        if not package_json_path.exists():
            return {}
            
        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception:
            return {'found': True, 'error': 'Could not parse package.json'}
            
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages by file extensions"""
        language_extensions = {
            'Python': ['.py'],
            'JavaScript': ['.js', '.mjs'],
            'TypeScript': ['.ts', '.tsx'],
            'Java': ['.java'],
            'C++': ['.cpp', '.cxx', '.cc'],
            'C': ['.c'],
            'Go': ['.go'],
            'Rust': ['.rs'],
            'Shell': ['.sh', '.bash'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css'],
            'Markdown': ['.md', '.markdown']
        }
        
        language_counts = {}
        
        for root, _, files in os.walk(self.project_path):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                ext = Path(file).suffix.lower()
                for lang, extensions in language_extensions.items():
                    if ext in extensions:
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                        break
                        
        return language_counts
        
    def _collect_dependencies(self) -> List[str]:
        """Collect all project dependencies from various sources"""
        dependencies = []
        
        # Python dependencies
        python_meta = self._collect_python_metadata()
        if 'requirements' in python_meta and isinstance(python_meta['requirements'], list):
            dependencies.extend(python_meta['requirements'])
        if 'pyproject' in python_meta and isinstance(python_meta['pyproject'], dict):
            deps = python_meta['pyproject'].get('dependencies', [])
            if isinstance(deps, list):
                dependencies.extend(deps)
                
        # Node.js dependencies
        node_meta = self._collect_node_metadata()
        if isinstance(node_meta, dict):
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                if dep_type in node_meta:
                    dependencies.extend(node_meta[dep_type].keys())
                    
        return dependencies
        
    def _extract_project_name(self) -> Optional[str]:
        """Extract project name from various sources"""
        # Try pyproject.toml
        python_meta = self._collect_python_metadata()
        if 'pyproject' in python_meta and isinstance(python_meta['pyproject'], dict):
            name = python_meta['pyproject'].get('name')
            if name:
                return name
                
        # Try package.json
        node_meta = self._collect_node_metadata()
        if isinstance(node_meta, dict) and 'name' in node_meta:
            return node_meta['name']
            
        # Try directory name
        return self.project_path.name
        
    def _extract_description(self) -> Optional[str]:
        """Extract project description from various sources"""
        # Try pyproject.toml
        python_meta = self._collect_python_metadata()
        if 'pyproject' in python_meta and isinstance(python_meta['pyproject'], dict):
            desc = python_meta['pyproject'].get('description')
            if desc:
                return desc
                
        # Try package.json
        node_meta = self._collect_node_metadata()
        if isinstance(node_meta, dict) and 'description' in node_meta:
            return node_meta['description']
            
        return None
        
    def _extract_version(self) -> Optional[str]:
        """Extract project version from various sources"""
        # Try pyproject.toml
        python_meta = self._collect_python_metadata()
        if 'pyproject' in python_meta and isinstance(python_meta['pyproject'], dict):
            version = python_meta['pyproject'].get('version')
            if version:
                return version
                
        # Try package.json
        node_meta = self._collect_node_metadata()
        if isinstance(node_meta, dict) and 'version' in node_meta:
            return node_meta['version']
            
        return None