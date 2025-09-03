"""
Prompt Versioning & Testing Framework
Enterprise Prompt Management System

This module provides a PromptManager class to load and version control prompts
from the filesystem, enabling scalable prompt management across business units.

Development Note: This code was generated using GitHub Copilot with strategic
prompt engineering. The prompts emphasized enterprise requirements, comprehensive
error handling, and production-ready documentation standards.
"""

import os
import re
import glob
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class PromptManager:
    """
    A class to manage versioned prompts across different business domains.
    
    This class provides functionality to:
    - Load prompts from organized directory structure
    - Version control and retrieve latest versions
    - Support A/B testing and rollback capabilities
    - Enable reuse across business units
    """
    
    def __init__(self, base_path: str = "prompts"):
        """
        Initialize the PromptManager with base directory path.
        
        Args:
            base_path (str): Base directory containing organized prompt files
        """
        self.base_path = base_path
        self._validate_base_path()
    
    def _validate_base_path(self) -> None:
        """Validate that the base path exists and is accessible."""
        if not os.path.exists(self.base_path):
            raise FileNotFoundError(f"Prompt directory not found: {self.base_path}")
        if not os.path.isdir(self.base_path):
            raise NotADirectoryError(f"Path is not a directory: {self.base_path}")
    
    def get_latest_prompt(self, domain: str, use_case: str) -> Optional[Dict]:
        """
        Get the latest version of a prompt for a given domain and use case.
        
        Args:
            domain (str): Business domain (e.g., 'wind_energy', 'customer_ops')
            use_case (str): Specific use case (e.g., 'technical_doc', 'email_response')
            
        Returns:
            Dict: Prompt metadata and content, or None if not found
        """
        # Construct the search pattern for versioned files
        domain_path = os.path.join(self.base_path, domain)
        
        if not os.path.exists(domain_path):
            print(f"Warning: Domain directory not found: {domain}")
            return None
        
        # Find all versioned files matching the use case
        pattern = os.path.join(domain_path, f"{use_case}_v*.md")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            print(f"Warning: No prompts found for {domain}/{use_case}")
            return None
        
        # Extract version numbers and find the latest
        latest_file, latest_version = self._get_latest_version_file(matching_files)
        
        if latest_file:
            # Load and parse the prompt file
            prompt_data = self._load_prompt_file(latest_file)
            prompt_data['domain'] = domain
            prompt_data['use_case'] = use_case
            prompt_data['version'] = latest_version
            prompt_data['file_path'] = latest_file
            
            return prompt_data
        
        return None
    
    def _get_latest_version_file(self, file_list: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the file with the highest version number.
        
        Args:
            file_list (List[str]): List of file paths with version numbers
            
        Returns:
            Tuple: (latest_file_path, version_string) or (None, None)
        """
        version_pattern = r'_v(\d+(?:\.\d+)?)'
        latest_file = None
        latest_version_num = -1
        latest_version_str = None
        
        for file_path in file_list:
            match = re.search(version_pattern, os.path.basename(file_path))
            if match:
                version_str = match.group(1)
                # Convert version to comparable number (handle x.y format)
                version_parts = version_str.split('.')
                version_num = float(version_parts[0])
                if len(version_parts) > 1:
                    version_num += float(version_parts[1]) / 10
                
                if version_num > latest_version_num:
                    latest_version_num = version_num
                    latest_file = file_path
                    latest_version_str = version_str
        
        return latest_file, latest_version_str
    
    def _load_prompt_file(self, file_path: str) -> Dict:
        """
        Load and parse a prompt file, extracting metadata and content.
        
        Args:
            file_path (str): Path to the prompt file
            
        Returns:
            Dict: Parsed prompt data with metadata and content
        """
        prompt_data = {
            'metadata': {},
            'content': '',
            'raw_content': '',
            'loaded_at': datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                prompt_data['raw_content'] = content
                
                # Parse metadata and content sections
                self._parse_prompt_content(content, prompt_data)
                
        except Exception as e:
            print(f"Error loading prompt file {file_path}: {e}")
            prompt_data['error'] = str(e)
        
        return prompt_data
    
    def _parse_prompt_content(self, content: str, prompt_data: Dict) -> None:
        """
        Parse the markdown content to extract metadata and prompt content.
        
        Args:
            content (str): Raw file content
            prompt_data (Dict): Dictionary to populate with parsed data
        """
        lines = content.split('\n')
        current_section = None
        prompt_content = []
        in_prompt_block = False
        
        for line in lines:
            line = line.strip()
            
            # Extract metadata fields
            if line.startswith('## ') and not line.startswith('## Prompt Content'):
                current_section = line[3:].lower().replace(' ', '_')
                continue
            elif line.startswith('# ') and current_section is None:
                prompt_data['metadata']['title'] = line[2:]
                continue
            
            # Handle prompt content section
            if line == '## Prompt Content':
                current_section = 'prompt_content'
                continue
            elif current_section == 'prompt_content':
                if line.startswith('```') and not in_prompt_block:
                    in_prompt_block = True
                    continue
                elif line.startswith('```') and in_prompt_block:
                    in_prompt_block = False
                    continue
                elif in_prompt_block:
                    prompt_content.append(line)
                    continue
            
            # Extract other metadata
            if current_section and not in_prompt_block and line:
                if current_section not in prompt_data['metadata']:
                    prompt_data['metadata'][current_section] = []
                prompt_data['metadata'][current_section].append(line)
        
        # Join prompt content
        prompt_data['content'] = '\n'.join(prompt_content)
        
        # Clean up metadata (convert single-item lists to strings)
        for key, value in prompt_data['metadata'].items():
            if isinstance(value, list) and len(value) == 1:
                prompt_data['metadata'][key] = value[0]
    
    def list_available_domains(self) -> List[str]:
        """
        List all available business domains.
        
        Returns:
            List[str]: List of domain directory names
        """
        domains = []
        try:
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                if os.path.isdir(item_path):
                    domains.append(item)
        except Exception as e:
            print(f"Error listing domains: {e}")
        
        return sorted(domains)
    
    def list_use_cases(self, domain: str) -> List[str]:
        """
        List all available use cases for a specific domain.
        
        Args:
            domain (str): Business domain name
            
        Returns:
            List[str]: List of use case names
        """
        use_cases = set()
        domain_path = os.path.join(self.base_path, domain)
        
        if not os.path.exists(domain_path):
            return []
        
        try:
            # Find all .md files and extract use case names
            pattern = os.path.join(domain_path, "*.md")
            for file_path in glob.glob(pattern):
                filename = os.path.basename(file_path)
                # Extract use case name (remove version and extension)
                match = re.match(r'(.+)_v\d+(?:\.\d+)?\.md$', filename)
                if match:
                    use_cases.add(match.group(1))
        except Exception as e:
            print(f"Error listing use cases for {domain}: {e}")
        
        return sorted(list(use_cases))
    
    def get_prompt_versions(self, domain: str, use_case: str) -> List[Dict]:
        """
        Get all available versions of a prompt.
        
        Args:
            domain (str): Business domain name
            use_case (str): Use case name
            
        Returns:
            List[Dict]: List of version information dictionaries
        """
        versions = []
        domain_path = os.path.join(self.base_path, domain)
        
        if not os.path.exists(domain_path):
            return versions
        
        # Find all versioned files
        pattern = os.path.join(domain_path, f"{use_case}_v*.md")
        matching_files = glob.glob(pattern)
        
        version_pattern = r'_v(\d+(?:\.\d+)?)'
        
        for file_path in matching_files:
            match = re.search(version_pattern, os.path.basename(file_path))
            if match:
                version_str = match.group(1)
                file_stats = os.stat(file_path)
                
                versions.append({
                    'version': version_str,
                    'file_path': file_path,
                    'created_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'modified_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    'size_bytes': file_stats.st_size
                })
        
        # Sort by version number (descending)
        versions.sort(key=lambda x: float(x['version'].replace('.', '.')), reverse=True)
        
        return versions


# Example usage and testing functions
def demo_prompt_manager():
    """Demonstrate the PromptManager functionality."""
    print("=== Enterprise Prompt Management System Demo ===\n")
    
    # Initialize the manager
    try:
        manager = PromptManager("prompts")
        print("✓ PromptManager initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize PromptManager: {e}")
        return
    
    # List available domains
    domains = manager.list_available_domains()
    print(f"Available business domains: {domains}\n")
    
    # Demonstrate prompt retrieval for each domain
    for domain in domains:
        print(f"--- {domain.upper().replace('_', ' ')} DOMAIN ---")
        use_cases = manager.list_use_cases(domain)
        print(f"Available use cases: {use_cases}")
        
        for use_case in use_cases:
            print(f"\n  Use Case: {use_case}")
            
            # Get versions
            versions = manager.get_prompt_versions(domain, use_case)
            print(f"  Available versions: {[v['version'] for v in versions]}")
            
            # Get latest prompt
            latest_prompt = manager.get_latest_prompt(domain, use_case)
            if latest_prompt:
                print(f"  Latest version: {latest_prompt['version']}")
                print(f"  Title: {latest_prompt['metadata'].get('title', 'N/A')}")
                content_preview = latest_prompt['content'][:100].replace('\n', ' ')
                print(f"  Content preview: {content_preview}...")
            else:
                print("  ✗ Failed to load latest prompt")
        
        print()


if __name__ == "__main__":
    demo_prompt_manager()
