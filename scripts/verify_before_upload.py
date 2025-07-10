#!/usr/bin/env python3
"""
Pre-upload verification script for Zero Vector 4
This script checks for potential security issues before uploading to GitHub
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

class SecurityChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues: List[Tuple[str, str, str]] = []  # (severity, file, issue)
        
        # Patterns to look for in files
        self.secret_patterns = {
            'api_key': re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?'),
            'password': re.compile(r'(?i)password\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?'),
            'secret': re.compile(r'(?i)secret[_-]?key\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?'),
            'token': re.compile(r'(?i)token\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?'),
            'private_key': re.compile(r'-----BEGIN (?:RSA |EC |)PRIVATE KEY-----'),
            'connection_string': re.compile(r'(?i)(postgres|mysql|mongodb)://[^/]+:[^@]+@'),
        }
        
        # Files that should definitely not exist
        self.forbidden_files = [
            '.env',
            'zero_vector_4.db',
            'config.local.py',
            'secrets.py',
            'credentials.py'
        ]
        
        # Directories that should not exist
        self.forbidden_dirs = [
            'zv4-env',
            'venv',
            'env',
            '.venv',
            'logs',
            '__pycache__',
            '.pytest_cache',
            'node_modules'
        ]

    def check_forbidden_files(self):
        """Check for files that should not be uploaded"""
        for forbidden in self.forbidden_files:
            file_path = self.project_root / forbidden
            if file_path.exists():
                self.issues.append(("CRITICAL", str(file_path), f"Forbidden file exists: {forbidden}"))

    def check_forbidden_directories(self):
        """Check for directories that should not be uploaded"""
        for forbidden in self.forbidden_dirs:
            dir_path = self.project_root / forbidden
            if dir_path.exists() and dir_path.is_dir():
                self.issues.append(("CRITICAL", str(dir_path), f"Forbidden directory exists: {forbidden}"))

    def scan_file_for_secrets(self, file_path: Path):
        """Scan a single file for potential secrets"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern_name, pattern in self.secret_patterns.items():
                matches = pattern.findall(content)
                for match in matches:
                    # Skip obvious placeholders
                    if isinstance(match, tuple):
                        value = match[1] if len(match) > 1 else match[0]
                    else:
                        value = match
                    
                    if not self._is_placeholder(value):
                        self.issues.append(("HIGH", str(file_path), f"Potential {pattern_name}: {value[:20]}..."))
                        
        except Exception as e:
            self.issues.append(("WARNING", str(file_path), f"Could not scan file: {e}"))

    def _is_placeholder(self, value: str) -> bool:
        """Check if a value is likely a placeholder rather than real secret"""
        placeholders = [
            'your-api-key', 'your_api_key', 'api-key-here', 'your-secret',
            'dev-secret-key', 'change-me', 'placeholder', 'example',
            'localhost', '127.0.0.1', 'password', 'secret', 'key'
        ]
        return any(placeholder in value.lower() for placeholder in placeholders)

    def check_gitignore_exists(self):
        """Check if .gitignore file exists"""
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            self.issues.append(("HIGH", str(gitignore_path), ".gitignore file is missing"))

    def scan_source_files(self):
        """Scan source code files for potential secrets"""
        source_extensions = ['.py', '.js', '.ts', '.json', '.yml', '.yaml', '.md', '.txt']
        
        for ext in source_extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                # Skip files in common ignore directories
                if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'logs'] 
                       for part in file_path.parts):
                    continue
                
                if file_path.is_file():
                    self.scan_file_for_secrets(file_path)

    def check_env_example(self):
        """Check if .env.example exists and .env doesn't"""
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if not env_example.exists():
            self.issues.append(("MEDIUM", str(env_example), ".env.example file is missing"))
        
        if env_file.exists():
            self.issues.append(("CRITICAL", str(env_file), ".env file should not be uploaded"))

    def run_all_checks(self):
        """Run all security checks"""
        print("🔍 Running pre-upload security checks...")
        print(f"📁 Scanning directory: {self.project_root.absolute()}")
        print()
        
        self.check_forbidden_files()
        self.check_forbidden_directories()
        self.check_gitignore_exists()
        self.check_env_example()
        self.scan_source_files()

    def report_results(self) -> bool:
        """Report results and return True if safe to upload"""
        if not self.issues:
            print("✅ All checks passed! Safe to upload to GitHub.")
            return True
        
        # Group issues by severity
        critical_issues = [i for i in self.issues if i[0] == "CRITICAL"]
        high_issues = [i for i in self.issues if i[0] == "HIGH"]
        medium_issues = [i for i in self.issues if i[0] == "MEDIUM"]
        warning_issues = [i for i in self.issues if i[0] == "WARNING"]
        
        print("🚨 SECURITY ISSUES FOUND:")
        print()
        
        if critical_issues:
            print("❌ CRITICAL ISSUES (Must fix before upload):")
            for severity, file_path, issue in critical_issues:
                print(f"   {file_path}: {issue}")
            print()
        
        if high_issues:
            print("⚠️  HIGH PRIORITY ISSUES:")
            for severity, file_path, issue in high_issues:
                print(f"   {file_path}: {issue}")
            print()
        
        if medium_issues:
            print("📝 MEDIUM PRIORITY ISSUES:")
            for severity, file_path, issue in medium_issues:
                print(f"   {file_path}: {issue}")
            print()
        
        if warning_issues:
            print("ℹ️  WARNINGS:")
            for severity, file_path, issue in warning_issues:
                print(f"   {file_path}: {issue}")
            print()
        
        # Determine if safe to upload
        safe_to_upload = len(critical_issues) == 0
        
        if not safe_to_upload:
            print("🛑 DO NOT UPLOAD TO GITHUB until critical issues are resolved!")
        elif high_issues:
            print("⚠️  Review high priority issues before uploading.")
        
        return safe_to_upload

def main():
    """Main function"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    checker = SecurityChecker(project_root)
    checker.run_all_checks()
    
    safe = checker.report_results()
    
    if not safe:
        print("\n📋 RECOMMENDED ACTIONS:")
        print("1. Remove .env file: rm .env")
        print("2. Remove database files: rm *.db")
        print("3. Remove virtual environment: rm -rf zv4-env/")
        print("4. Remove logs: rm -rf logs/")
        print("5. Review and sanitize any flagged source files")
        print("6. Run this script again to verify")
        
        sys.exit(1)
    else:
        print("\n🎉 Ready for GitHub upload!")
        sys.exit(0)

if __name__ == "__main__":
    main()
