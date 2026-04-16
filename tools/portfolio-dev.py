#!/usr/bin/env python3
"""
Portfolio Development Orchestrator

Manages multi-repository portfolio projects with plugin architecture.
Supports operations like setup, status, branching, commits, and link validation
across multiple projects and portfolios.

Plugin Architecture:
  - Core portfolios (core, all) are built-in
  - External portfolios can provide custom orchestration via portfolio-orchestrator.py
  - Each portfolio lead can have customized behavior while maintaining standard interface
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
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

@dataclass
class Project:
    """Represents a single project in a portfolio."""
    repo: str
    name: Optional[str] = None
    language: Optional[str] = None
    role: Optional[str] = None  # 'lead' for portfolio leads
    path: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            self.name = self.repo.split('/')[-1]


@dataclass
class PortfolioConfig:
    """Configuration for a portfolio."""
    name: str
    description: str
    portfolio_type: str  # 'builtin' or 'plugin'
    projects: List[Project]
    plugin_path: Optional[str] = None


class ConfigLoader:
    """Loads and parses portfolio configuration."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load portfolio configuration from YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_portfolio(self, name: str) -> PortfolioConfig:
        """Get a specific portfolio configuration."""
        if 'portfolios' not in self.config:
            raise ValueError("No portfolios defined in configuration")
        
        if name not in self.config['portfolios']:
            raise ValueError(f"Portfolio '{name}' not found in configuration")
        
        portfolio_data = self.config['portfolios'][name]
        projects = [
            Project(**proj) if isinstance(proj, dict) else Project(repo=proj)
            for proj in portfolio_data.get('projects', [])
        ]
        
        return PortfolioConfig(
            name=name,
            description=portfolio_data.get('description', ''),
            portfolio_type=portfolio_data.get('type', 'builtin'),
            projects=projects,
            plugin_path=portfolio_data.get('plugin_path')
        )
    
    def list_portfolios(self) -> List[str]:
        """List all available portfolios."""
        return list(self.config.get('portfolios', {}).keys())
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a global setting."""
        return self.config.get('settings', {}).get(key, default)


# ============================================================================
# Plugin System
# ============================================================================

class PluginInterface:
    """Base interface that all portfolio plugins must implement."""
    
    def __init__(self, config: PortfolioConfig, shared_logger: logging.Logger):
        """Initialize plugin with portfolio config and logger."""
        self.config = config
        self.logger = shared_logger
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """Validate that setup is possible. Returns (is_valid, list_of_errors)."""
        raise NotImplementedError
    
    def setup(self) -> bool:
        """Execute setup. Return success."""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Return status dict with all project statuses."""
        raise NotImplementedError
    
    def new_branch(self, branch_name: str) -> bool:
        """Create new branch across all projects. Return success."""
        raise NotImplementedError
    
    def commit_all(self, message: str) -> bool:
        """Commit all changes across all projects. Return success."""
        raise NotImplementedError
    
    def push(self) -> bool:
        """Push all changes across all projects. Return success."""
        raise NotImplementedError
    
    def get_projects(self) -> List[Project]:
        """Return list of projects in this portfolio."""
        return self.config.projects


class PluginLoader:
    """Dynamically loads portfolio plugins."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.loaded_plugins: Dict[str, PluginInterface] = {}
    
    def load_plugin(
        self,
        portfolio_config: PortfolioConfig,
        shared_logger: logging.Logger
    ) -> PluginInterface:
        """Load a portfolio plugin from file."""
        
        if not portfolio_config.plugin_path:
            raise ValueError(
                f"Portfolio '{portfolio_config.name}' has no plugin path"
            )
        
        plugin_file = self.base_path / portfolio_config.plugin_path
        
        if not plugin_file.exists():
            raise FileNotFoundError(
                f"Plugin file not found: {plugin_file}"
            )
        
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(
            f"plugin_{portfolio_config.name}",
            plugin_file
        )
        
        if not spec or not spec.loader:
            raise ImportError(f"Failed to load plugin from {plugin_file}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get the plugin class
        if not hasattr(module, 'PortfolioOrchestrator'):
            raise ImportError(
                f"Plugin {plugin_file} must define 'PortfolioOrchestrator' class"
            )
        
        PluginClass = module.PortfolioOrchestrator
        
        # Verify it implements the interface
        if not issubclass(PluginClass, PluginInterface):
            raise TypeError(
                f"Plugin {plugin_file} PortfolioOrchestrator must inherit "
                "from PluginInterface"
            )
        
        return PluginClass(portfolio_config, shared_logger)


# ============================================================================
# Built-in Portfolio Implementations
# ============================================================================

class GitOperations:
    """Shared git operations utilities."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def run_git_command(
        self,
        cmd: List[str],
        cwd: Path,
        check: bool = True
    ) -> Tuple[bool, str, str]:
        """Run a git command in a directory."""
        try:
            result = subprocess.run(
                ['git'] + cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            self.logger.error(f"Git command failed: {e}")
            return False, '', str(e)
    
    def get_status(self, cwd: Path) -> Dict[str, Any]:
        """Get git status for a directory."""
        success, stdout, _ = self.run_git_command(
            ['status', '--porcelain'],
            cwd
        )
        
        if not success:
            return {'status': 'error', 'changes': 0}
        
        changes = len([line for line in stdout.strip().split('\n') if line])
        
        # Get current branch
        branch_success, branch, _ = self.run_git_command(
            ['rev-parse', '--abbrev-ref', 'HEAD'],
            cwd
        )
        current_branch = branch.strip() if branch_success else 'unknown'
        
        return {
            'status': 'clean' if changes == 0 else 'dirty',
            'changes': changes,
            'current_branch': current_branch
        }
    
    def create_branch(self, branch_name: str, cwd: Path) -> bool:
        """Create a new branch."""
        success, _, _ = self.run_git_command(
            ['checkout', '-b', branch_name],
            cwd
        )
        return success
    
    def commit_changes(self, message: str, cwd: Path) -> bool:
        """Commit changes in a directory."""
        # Check if there are changes
        success, stdout, _ = self.run_git_command(
            ['status', '--porcelain'],
            cwd
        )
        
        if not success or not stdout.strip():
            self.logger.info(f"No changes to commit in {cwd}")
            return True
        
        # Stage all changes
        success, _, _ = self.run_git_command(['add', '-A'], cwd)
        if not success:
            return False
        
        # Commit
        success, _, _ = self.run_git_command(
            ['commit', '-m', message],
            cwd
        )
        return success
    
    def push(self, cwd: Path) -> bool:
        """Push changes."""
        success, _, _ = self.run_git_command(['push'], cwd)
        return success


class ProjectStatus:
    """Utilities for checking project status."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.git_ops = GitOperations(logger)
    
    def check_project(self, project: Project, base_path: Path) -> Dict[str, Any]:
        """Check status of a single project."""
        project_path = base_path / project.name
        
        if not project_path.exists():
            return {
                'name': project.name,
                'repo': project.repo,
                'exists': False,
                'cloned': False
            }
        
        git_status = self.git_ops.get_status(project_path)
        
        return {
            'name': project.name,
            'repo': project.repo,
            'exists': True,
            'cloned': True,
            **git_status
        }


class BootstrapChecker:
    """Checks if projects can be set up."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check that all required tools are available."""
        errors = []
        
        # Check git
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("git is not installed or not in PATH")
        
        # Check Python
        try:
            subprocess.run(
                [sys.executable, '--version'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append("Python is not available")
        
        return len(errors) == 0, errors


class CorePortfolioPlugin(PluginInterface):
    """Built-in implementation for core portfolio (main site + blog + CV)."""
    
    def __init__(self, config: PortfolioConfig, shared_logger: logging.Logger):
        super().__init__(config, shared_logger)
        self.git_ops = GitOperations(shared_logger)
        self.bootstrap = BootstrapChecker(shared_logger)
        self.status_checker = ProjectStatus(shared_logger)
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """Validate that setup is possible."""
        is_valid, errors = self.bootstrap.check_prerequisites()
        
        if not is_valid:
            return False, errors
        
        return True, []
    
    def setup(self) -> bool:
        """Set up all projects in the portfolio."""
        self.logger.info(f"Setting up portfolio: {self.config.name}")
        
        is_valid, errors = self.validate_setup()
        if not is_valid:
            self.logger.error("Setup validation failed:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False
        
        self.logger.info("Setup validation passed")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all projects."""
        # Use current directory as base
        base_path = Path.cwd()
        
        statuses = {
            'portfolio': self.config.name,
            'projects': []
        }
        
        for project in self.config.projects:
            project_status = self.status_checker.check_project(project, base_path)
            statuses['projects'].append(project_status)
        
        return statuses
    
    def new_branch(self, branch_name: str) -> bool:
        """Create a new branch in all projects."""
        self.logger.info(
            f"Creating branch '{branch_name}' in portfolio {self.config.name}"
        )
        
        base_path = Path.cwd()
        all_success = True
        
        for project in self.config.projects:
            project_path = base_path / project.name
            
            if not project_path.exists():
                self.logger.warning(f"Project {project.name} not found, skipping")
                all_success = False
                continue
            
            success = self.git_ops.create_branch(branch_name, project_path)
            
            if success:
                self.logger.info(f"✓ Created branch in {project.name}")
            else:
                self.logger.error(f"✗ Failed to create branch in {project.name}")
                all_success = False
        
        return all_success
    
    def commit_all(self, message: str) -> bool:
        """Commit all changes across all projects."""
        self.logger.info(
            f"Committing all projects in portfolio {self.config.name}: {message}"
        )
        
        base_path = Path.cwd()
        all_success = True
        
        for project in self.config.projects:
            project_path = base_path / project.name
            
            if not project_path.exists():
                self.logger.warning(f"Project {project.name} not found, skipping")
                all_success = False
                continue
            
            success = self.git_ops.commit_changes(message, project_path)
            
            if success:
                self.logger.info(f"✓ Committed changes in {project.name}")
            else:
                self.logger.error(f"✗ Failed to commit in {project.name}")
                all_success = False
        
        return all_success
    
    def push(self) -> bool:
        """Push all changes across all projects."""
        self.logger.info(f"Pushing portfolio {self.config.name}")
        
        base_path = Path.cwd()
        all_success = True
        
        for project in self.config.projects:
            project_path = base_path / project.name
            
            if not project_path.exists():
                self.logger.warning(f"Project {project.name} not found, skipping")
                all_success = False
                continue
            
            success = self.git_ops.push(project_path)
            
            if success:
                self.logger.info(f"✓ Pushed {project.name}")
            else:
                self.logger.error(f"✗ Failed to push {project.name}")
                all_success = False
        
        return all_success


class AllPortfolioPlugin(PluginInterface):
    """Built-in implementation for 'all' portfolio."""
    
    def __init__(self, config: PortfolioConfig, shared_logger: logging.Logger):
        super().__init__(config, shared_logger)
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """Validate setup for all portfolios."""
        return True, []
    
    def setup(self) -> bool:
        """Setup is handled by aggregating all portfolios."""
        self.logger.info("'all' is a meta-portfolio and delegates to component portfolios")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get status from all portfolios."""
        return {
            'portfolio': self.config.name,
            'message': "Use individual portfolio names for full status"
        }
    
    def new_branch(self, branch_name: str) -> bool:
        """Create branch in all portfolios."""
        self.logger.info("This operation must be performed per-portfolio")
        return False
    
    def commit_all(self, message: str) -> bool:
        """Commit across all portfolios."""
        self.logger.info("This operation must be performed per-portfolio")
        return False
    
    def push(self) -> bool:
        """Push across all portfolios."""
        self.logger.info("This operation must be performed per-portfolio")
        return False


# ============================================================================
# Portfolio Registry
# ============================================================================

class PortfolioRegistry:
    """Registry for all available portfolios and their plugins."""
    
    def __init__(self, config_loader: ConfigLoader, base_path: Path):
        self.config_loader = config_loader
        self.base_path = base_path
        self.plugin_loader = PluginLoader(base_path)
        self.logger = logging.getLogger(__name__)
        self._plugin_cache: Dict[str, PluginInterface] = {}
    
    def get_portfolio(self, name: str) -> PluginInterface:
        """Get a portfolio plugin by name."""
        
        # Check cache first
        if name in self._plugin_cache:
            return self._plugin_cache[name]
        
        # Load configuration
        config = self.config_loader.get_portfolio(name)
        
        # Get appropriate plugin
        if config.portfolio_type == 'builtin':
            if name == 'core':
                plugin = CorePortfolioPlugin(config, self.logger)
            elif name == 'all':
                plugin = AllPortfolioPlugin(config, self.logger)
            else:
                raise ValueError(
                    f"Unknown built-in portfolio: {name}"
                )
        elif config.portfolio_type == 'plugin':
            plugin = self.plugin_loader.load_plugin(config, self.logger)
        else:
            raise ValueError(
                f"Unknown portfolio type: {config.portfolio_type}"
            )
        
        # Cache it
        self._plugin_cache[name] = plugin
        return plugin
    
    def list_portfolios(self) -> List[str]:
        """List all available portfolios."""
        return self.config_loader.list_portfolios()


# ============================================================================
# Command Router & Main Interface
# ============================================================================

class CommandRouter:
    """Routes commands to appropriate portfolio plugin."""
    
    def __init__(self, registry: PortfolioRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    def execute_setup(self, portfolio_name: str) -> bool:
        """Execute setup command."""
        plugin = self.registry.get_portfolio(portfolio_name)
        return plugin.setup()
    
    def execute_status(self, portfolio_name: str) -> Dict[str, Any]:
        """Execute status command."""
        plugin = self.registry.get_portfolio(portfolio_name)
        return plugin.get_status()
    
    def execute_new_branch(self, portfolio_name: str, branch_name: str) -> bool:
        """Execute new-branch command."""
        plugin = self.registry.get_portfolio(portfolio_name)
        return plugin.new_branch(branch_name)
    
    def execute_commit_all(self, portfolio_name: str, message: str) -> bool:
        """Execute commit-all command."""
        plugin = self.registry.get_portfolio(portfolio_name)
        return plugin.commit_all(message)
    
    def execute_push(self, portfolio_name: str) -> bool:
        """Execute push command."""
        plugin = self.registry.get_portfolio(portfolio_name)
        return plugin.push()
    
    def execute_validate(
        self,
        portfolio_name: str,
        dry_run: bool = False,
        fix: bool = False
    ) -> bool:
        """Execute link validation command."""
        self.logger.info(
            f"Link validation for portfolio '{portfolio_name}' "
            f"(dry-run={dry_run}, fix={fix})"
        )
        
        # This will integrate validate-links.py later
        self.logger.info("Link validation not yet implemented")
        return False
    
    def execute_list(self, verbose: bool = False) -> None:
        """List all available portfolios."""
        portfolios = self.registry.list_portfolios()
        
        print("\nAvailable portfolios:")
        for portfolio_name in portfolios:
            config = self.registry.config_loader.get_portfolio(portfolio_name)
            
            if verbose:
                print(f"\n  {portfolio_name}:")
                print(f"    Description: {config.description}")
                print(f"    Type: {config.portfolio_type}")
                print(f"    Projects: {len(config.projects)}")
                for proj in config.projects:
                    print(f"      - {proj.name} ({proj.repo})")
            else:
                print(f"  - {portfolio_name}: {config.description}")
        
        print()


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main entry point."""
    
    # Argument parsing
    parser = argparse.ArgumentParser(
        description="Portfolio Development Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  portfolio-dev.py list
  portfolio-dev.py list --verbose
  portfolio-dev.py core --setup
  portfolio-dev.py core --status
  portfolio-dev.py core --new-branch feature/new-feature
  portfolio-dev.py core --commit-all "your commit message"
  portfolio-dev.py core --push
  portfolio-dev.py core --validate --dry-run
  portfolio-dev.py core --validate --fix
        """
    )
    
    parser.add_argument(
        'portfolio',
        nargs='?',
        help='Portfolio name to operate on (or "list" to see all)'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Setup the portfolio'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show portfolio status'
    )
    
    parser.add_argument(
        '--new-branch',
        metavar='BRANCH_NAME',
        help='Create a new branch in all projects'
    )
    
    parser.add_argument(
        '--commit-all',
        metavar='MESSAGE',
        help='Commit all changes with message'
    )
    
    parser.add_argument(
        '--push',
        action='store_true',
        help='Push all changes'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate cross-project links'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry-run mode (for validation)'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Auto-fix issues (for validation)'
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
    
    # Find config file
    config_path = Path(__file__).parent / 'portfolio-config.yaml'
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return 1
    
    try:
        # Load configuration
        config_loader = ConfigLoader(config_path)
        base_path = Path(__file__).parent.parent
        
        # Create registry and router
        registry = PortfolioRegistry(config_loader, base_path)
        router = CommandRouter(registry)
        
        # Default to 'list' if no portfolio specified
        if not args.portfolio:
            args.portfolio = 'list'
        
        # Route commands
        if args.portfolio == 'list':
            router.execute_list(args.verbose)
            return 0
        
        # Verify portfolio exists
        if args.portfolio not in registry.list_portfolios():
            logger.error(f"Portfolio '{args.portfolio}' not found")
            return 1
        
        # Execute commands
        if args.setup:
            success = router.execute_setup(args.portfolio)
            return 0 if success else 1
        
        elif args.status:
            status = router.execute_status(args.portfolio)
            print(json.dumps(status, indent=2))
            return 0
        
        elif args.new_branch:
            success = router.execute_new_branch(args.portfolio, args.new_branch)
            return 0 if success else 1
        
        elif args.commit_all:
            success = router.execute_commit_all(args.portfolio, args.commit_all)
            return 0 if success else 1
        
        elif args.push:
            success = router.execute_push(args.portfolio)
            return 0 if success else 1
        
        elif args.validate:
            success = router.execute_validate(
                args.portfolio,
                dry_run=args.dry_run,
                fix=args.fix
            )
            return 0 if success else 1
        
        else:
            # No command specified
            print("No command specified. Use --help for usage information.")
            return 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
