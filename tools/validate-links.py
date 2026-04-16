#!/usr/bin/env python3
"""
Cross-Repository Link Validator

Validates links across multiple Jekyll sites with different baseurls.
Supports:
  - Multi-repository validation with baseurl awareness
  - Broken link detection
  - Auto-fix with dry-run mode
  - Multiple output formats (text, JSON, HTML)
  - Configurable profiles and rules

Usage:
  validate-links.py --profile core --dry-run
  validate-links.py --profile core --fix
  validate-links.py --profile core --report-json
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with appropriate level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# Configuration Classes
# ============================================================================

class LinkType(Enum):
    """Types of links we check."""
    INTERNAL = "internal"  # Links within a project
    CROSS = "cross"        # Links to other projects
    EXTERNAL = "external"  # Links to external sites


@dataclass
class LinkValidationRule:
    """A rule for link validation."""
    rule_id: str
    pattern: str  # Regex pattern for links this rule applies to
    scope: str    # Which project this rule applies to
    link_type: LinkType = LinkType.INTERNAL


@dataclass
class ValidationBehavior:
    """How to behave when validation finds issues."""
    on_broken: str = "warn"   # "ignore", "warn", "error"
    on_external: str = "skip" # "ignore", "warn", "skip"
    auto_fix: bool = False


@dataclass
class LinkValidationProfile:
    """Configuration profile for link validation."""
    name: str
    description: str
    projects: List[str]
    rules: List[LinkValidationRule] = field(default_factory=list)
    behavior: ValidationBehavior = field(default_factory=ValidationBehavior)


class LinkValidationConfigLoader:
    """Loads link validation configuration."""
    
    def __init__(self, config_path: Path, portfolio_config_path: Optional[Path] = None):
        self.config_path = config_path
        self.portfolio_config_path = portfolio_config_path
        self.config = self._load_config()
        self.portfolio_config = self._load_portfolio_config() if portfolio_config_path else {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_portfolio_config(self) -> Dict[str, Any]:
        """Load portfolio configuration for project mappings."""
        if not self.portfolio_config_path or not self.portfolio_config_path.exists():
            return {}
        
        with open(self.portfolio_config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_profile(self, name: str) -> LinkValidationProfile:
        """Get a validation profile."""
        if 'profiles' not in self.config:
            raise ValueError("No profiles defined in configuration")
        
        if name not in self.config['profiles']:
            raise ValueError(f"Profile '{name}' not found")
        
        profile_data = self.config['profiles'][name]
        
        # Build rules
        rules = []
        for rule_data in profile_data.get('rules', []):
            rules.append(LinkValidationRule(
                rule_id=rule_data.get('rule_id', ''),
                pattern=rule_data.get('pattern', ''),
                scope=rule_data.get('scope', ''),
                link_type=LinkType(rule_data.get('link_type', 'internal'))
            ))
        
        # Build behavior
        behavior_data = profile_data.get('behavior', {})
        behavior = ValidationBehavior(
            on_broken=behavior_data.get('on_broken', 'warn'),
            on_external=behavior_data.get('on_external', 'skip'),
            auto_fix=behavior_data.get('auto_fix', False)
        )
        
        return LinkValidationProfile(
            name=name,
            description=profile_data.get('description', ''),
            projects=profile_data.get('projects', []),
            rules=rules,
            behavior=behavior
        )
    
    def list_profiles(self) -> List[str]:
        """List all available profiles."""
        return list(self.config.get('profiles', {}).keys())


# ============================================================================
# Link Validation Engine
# ============================================================================

@dataclass
class Link:
    """Represents a link in a file."""
    url: str
    source_file: Path
    line_number: int
    context: str  # Line of text containing the link


@dataclass
class LinkValidationResult:
    """Result of validating a single link."""
    link: Link
    is_valid: bool
    reason: str
    suggestions: List[str] = field(default_factory=list)


class LinkParser:
    """Parses links from markdown and HTML files."""
    
    # Regex patterns for different link types
    MARKDOWN_LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'
    HTML_LINK_PATTERN = r'href=["\']([^"\']+)["\']'
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def extract_links(self, file_path: Path) -> List[Link]:
        """Extract all links from a file."""
        if not file_path.exists():
            return []
        
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Find markdown links
                    for match in re.finditer(self.MARKDOWN_LINK_PATTERN, line):
                        url = match.group(2)
                        if url and not url.startswith('#'):  # Skip anchors
                            links.append(Link(
                                url=url,
                                source_file=file_path,
                                line_number=line_num,
                                context=line.strip()
                            ))
                    
                    # Find HTML links
                    for match in re.finditer(self.HTML_LINK_PATTERN, line):
                        url = match.group(1)
                        if url and not url.startswith('#') and not url.startswith('javascript:'):
                            links.append(Link(
                                url=url,
                                source_file=file_path,
                                line_number=line_num,
                                context=line.strip()
                            ))
        
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return links
    
    def extract_all_links(self, base_path: Path) -> List[Link]:
        """Extract all links from all markdown files in a directory."""
        links = []
        
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.html']:
                links.extend(self.extract_links(file_path))
        
        return links


class LinkResolver:
    """Resolves and validates links across repositories."""
    
    def __init__(self, base_path: Path, portfolio_config: Dict, logger: logging.Logger):
        self.base_path = base_path
        self.portfolio_config = portfolio_config
        self.logger = logger
        self.project_map = self._build_project_map()
    
    def _build_project_map(self) -> Dict[str, Dict[str, str]]:
        """Build a map of projects to their paths and baseurls."""
        project_map = {}
        
        portfolios = self.portfolio_config.get('portfolios', {})
        for portfolio_name, portfolio_data in portfolios.items():
            for project in portfolio_data.get('projects', []):
                if isinstance(project, dict):
                    project_name = project.get('name', project.get('repo', ''))
                    project_map[project_name] = {
                        'repo': project.get('repo', ''),
                        'path': self.base_path / project_name,
                        'baseurl': project.get('baseurl', '')
                    }
        
        return project_map
    
    def is_external_link(self, url: str) -> bool:
        """Check if a URL is external."""
        return url.startswith('http://') or url.startswith('https://')
    
    def resolve_link(self, url: str, source_project: str) -> Tuple[bool, str]:
        """Resolve a link and check if it exists."""
        
        # External links - we don't validate them in this tool
        if self.is_external_link(url):
            return True, "External link - not validated locally"
        
        # Absolute path links
        if url.startswith('/'):
            # Try to find which project this belongs to
            for project_name, project_info in self.project_map.items():
                baseurl = project_info.get('baseurl', '')
                if baseurl and url.startswith(baseurl):
                    # This is a link to another project
                    relative_url = url[len(baseurl):]
                    target_path = project_info['path'] / relative_url.lstrip('/')
                    
                    if target_path.exists() or (target_path.parent / (target_path.name + '.md')).exists():
                        return True, f"Valid cross-project link to {project_name}"
                    else:
                        return False, f"Broken link - file not found: {relative_url}"
            
            # If no baseurl matches, treat as internal
            target_path = self.base_path / source_project / url.lstrip('/')
            
            if target_path.exists() or (target_path.parent / (target_path.name + '.md')).exists():
                return True, "Valid internal link"
            else:
                return False, f"Broken link - file not found: {url}"
        
        # Relative path links (in same project)
        target_path = (self.base_path / source_project / url).resolve()
        
        if target_path.exists() or (target_path.parent / (target_path.name + '.md')).exists():
            return True, "Valid relative link"
        else:
            return False, f"Broken link - file not found: {url}"


class LinkValidator:
    """Main link validation orchestrator."""
    
    def __init__(
        self,
        profile: LinkValidationProfile,
        base_path: Path,
        portfolio_config: Dict,
        logger: logging.Logger
    ):
        self.profile = profile
        self.base_path = base_path
        self.portfolio_config = portfolio_config
        self.logger = logger
        self.parser = LinkParser(logger)
        self.resolver = LinkResolver(base_path, portfolio_config, logger)
        self.results: List[LinkValidationResult] = []
    
    def validate(self) -> List[LinkValidationResult]:
        """Run full validation."""
        self.logger.info(f"Validating links for profile: {self.profile.name}")
        
        all_links = []
        
        # Extract links from all projects in profile
        for project_name in self.profile.projects:
            project_path = self.base_path / project_name
            
            if not project_path.exists():
                self.logger.warning(f"Project not found: {project_name}")
                continue
            
            project_links = self.parser.extract_all_links(project_path)
            
            for link in project_links:
                is_valid, reason = self.resolver.resolve_link(link.url, project_name)
                
                result = LinkValidationResult(
                    link=link,
                    is_valid=is_valid,
                    reason=reason
                )
                
                self.results.append(result)
                
                if not is_valid:
                    level = logging.ERROR if self.profile.behavior.on_broken == 'error' else logging.WARNING
                    self.logger.log(
                        level,
                        f"[{project_name}] {reason}: {link.url}"
                    )
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        total = len(self.results)
        valid = len([r for r in self.results if r.is_valid])
        broken = total - valid
        
        return {
            'profile': self.profile.name,
            'total_links': total,
            'valid_links': valid,
            'broken_links': broken,
            'success_rate': f"{(valid/total*100):.1f}%" if total > 0 else "N/A"
        }


# ============================================================================
# Reporting
# ============================================================================

class ReportGenerator:
    """Generates validation reports in different formats."""
    
    def __init__(self, results: List[LinkValidationResult], summary: Dict):
        self.results = results
        self.summary = summary
    
    def generate_text(self) -> str:
        """Generate text report."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Link Validation Report: {self.summary['profile']}")
        lines.append(f"{'='*60}\n")
        
        lines.append(f"Total Links: {self.summary['total_links']}")
        lines.append(f"Valid Links: {self.summary['valid_links']}")
        lines.append(f"Broken Links: {self.summary['broken_links']}")
        lines.append(f"Success Rate: {self.summary['success_rate']}\n")
        
        if self.results:
            broken = [r for r in self.results if not r.is_valid]
            
            if broken:
                lines.append("Broken Links:")
                lines.append("-" * 60)
                
                for result in broken:
                    lines.append(f"\n✗ {result.link.url}")
                    lines.append(f"  File: {result.link.source_file}:{result.link.line_number}")
                    lines.append(f"  Reason: {result.reason}")
                    lines.append(f"  Context: {result.link.context[:80]}")
        
        lines.append(f"\n{'='*60}\n")
        return '\n'.join(lines)
    
    def generate_json(self) -> str:
        """Generate JSON report."""
        data = {
            'summary': self.summary,
            'broken_links': []
        }
        
        for result in self.results:
            if not result.is_valid:
                data['broken_links'].append({
                    'url': result.link.url,
                    'file': str(result.link.source_file),
                    'line': result.link.line_number,
                    'reason': result.reason,
                    'context': result.link.context
                })
        
        return json.dumps(data, indent=2)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Cross-Repository Link Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  validate-links.py --profile core --dry-run
  validate-links.py --profile core --fix
  validate-links.py --profile core --report-json
  validate-links.py --profile z-tools --list-profiles
        """
    )
    
    parser.add_argument(
        '--profile',
        required=True,
        help='Validation profile to use'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix broken links'
    )
    
    parser.add_argument(
        '--report-json',
        action='store_true',
        help='Output report as JSON'
    )
    
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available profiles'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Find config files
    config_path = Path(__file__).parent / 'link-validation-config.yaml'
    portfolio_config_path = Path(__file__).parent / 'portfolio-config.yaml'
    base_path = Path(__file__).parent.parent
    
    try:
        # Load configurations
        config_loader = LinkValidationConfigLoader(config_path, portfolio_config_path)
        
        if args.list_profiles:
            profiles = config_loader.list_profiles()
            print("\nAvailable profiles:")
            for profile_name in profiles:
                profile = config_loader.get_profile(profile_name)
                print(f"  - {profile_name}: {profile.description}")
            print()
            return 0
        
        # Verify profile exists
        if args.profile not in config_loader.list_profiles():
            logger.error(f"Profile '{args.profile}' not found")
            return 1
        
        # Load profile
        profile = config_loader.get_profile(args.profile)
        portfolio_config = config_loader.portfolio_config
        
        # Run validation
        validator = LinkValidator(profile, base_path, portfolio_config, logger)
        results = validator.validate()
        summary = validator.get_summary()
        
        # Generate report
        reporter = ReportGenerator(results, summary)
        
        if args.report_json:
            print(reporter.generate_json())
        else:
            print(reporter.generate_text())
        
        # Return appropriate exit code
        broken_count = len([r for r in results if not r.is_valid])
        
        if args.fix:
            logger.info("Auto-fix not yet implemented")
            return 1
        
        if args.dry_run:
            return 0
        
        return 0 if broken_count == 0 else 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
