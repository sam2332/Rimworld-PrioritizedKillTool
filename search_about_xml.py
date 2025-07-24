#!/usr/bin/env python3
"""
RimWorld Mod About.xml Search Tool

This script searches through all About.xml files in the RimWorld workshop content directory
and allows you to find mods based on various criteria like name, author, description, etc.

Usage:
    python search_about_xml.py --help
    python search_about_xml.py --name "battle"
    python search_about_xml.py --author "user"
    python search_about_xml.py --description "combat"
    python search_about_xml.py --list-all
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any
import re

# Default workshop content path for RimWorld
DEFAULT_WORKSHOP_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"

class ModInfo:
    """Container for mod information parsed from About.xml"""
    
    def __init__(self, folder_path: str, about_xml_path: str):
        self.folder_path = folder_path
        self.about_xml_path = about_xml_path
        self.mod_id = os.path.basename(folder_path)
        
        # Initialize fields
        self.name = ""
        self.author = ""
        self.description = ""
        self.package_id = ""
        self.supported_versions = []
        self.dependencies = []
        self.load_after = []
        self.load_before = []
        self.incompatible_with = []
        
        self._parse_xml()
    
    def _parse_xml(self):
        """Parse the About.xml file and extract mod information"""
        try:
            tree = ET.parse(self.about_xml_path)
            root = tree.getroot()
            
            # Extract basic info
            name_elem = root.find('name')
            if name_elem is not None:
                self.name = name_elem.text or ""
            
            author_elem = root.find('author')
            if author_elem is not None:
                self.author = author_elem.text or ""
            
            desc_elem = root.find('description')
            if desc_elem is not None:
                self.description = desc_elem.text or ""
            
            package_elem = root.find('packageId')
            if package_elem is not None:
                self.package_id = package_elem.text or ""
            
            # Extract supported versions
            versions_elem = root.find('supportedVersions')
            if versions_elem is not None:
                for li in versions_elem.findall('li'):
                    if li.text:
                        self.supported_versions.append(li.text)
            
            # Extract dependencies
            deps_elem = root.find('modDependencies')
            if deps_elem is not None:
                for li in deps_elem.findall('li'):
                    package_id = li.find('packageId')
                    if package_id is not None and package_id.text:
                        self.dependencies.append(package_id.text)
            
            # Extract load order info
            load_after_elem = root.find('loadAfter')
            if load_after_elem is not None:
                for li in load_after_elem.findall('li'):
                    if li.text:
                        self.load_after.append(li.text)
            
            load_before_elem = root.find('loadBefore')
            if load_before_elem is not None:
                for li in load_before_elem.findall('li'):
                    if li.text:
                        self.load_before.append(li.text)
            
            # Extract incompatible mods
            incompatible_elem = root.find('incompatibleWith')
            if incompatible_elem is not None:
                for li in incompatible_elem.findall('li'):
                    if li.text:
                        self.incompatible_with.append(li.text)
                        
        except ET.ParseError as e:
            print(f"Warning: Failed to parse {self.about_xml_path}: {e}")
        except Exception as e:
            print(f"Warning: Error processing {self.about_xml_path}: {e}")
    
    def matches_search(self, search_term: str, field: str = "all") -> bool:
        """Check if this mod matches the search criteria"""
        search_term = search_term.lower()
        
        if field == "all":
            # Search in all text fields
            search_text = f"{self.name} {self.author} {self.description} {self.package_id}".lower()
            return search_term in search_text
        elif field == "name":
            return search_term in self.name.lower()
        elif field == "author":
            return search_term in self.author.lower()
        elif field == "description":
            return search_term in self.description.lower()
        elif field == "package_id":
            return search_term in self.package_id.lower()
        elif field == "dependencies":
            return any(search_term in dep.lower() for dep in self.dependencies)
        
        return False
    
    def __str__(self) -> str:
        """String representation of the mod info"""
        return f"""
Mod ID: {self.mod_id}
Name: {self.name}
Author: {self.author}
Package ID: {self.package_id}
Supported Versions: {', '.join(self.supported_versions)}
Dependencies: {', '.join(self.dependencies) if self.dependencies else 'None'}
Load After: {', '.join(self.load_after) if self.load_after else 'None'}
Description: {self.description[:200]}{'...' if len(self.description) > 200 else ''}
Path: {self.folder_path}
""".strip()

def find_about_xml_files(workshop_path: str) -> List[str]:
    """Find all About.xml files in the workshop directory"""
    about_files = []
    
    if not os.path.exists(workshop_path):
        print(f"Error: Workshop path does not exist: {workshop_path}")
        return about_files
    
    print(f"Searching for About.xml files in: {workshop_path}")
    
    for mod_folder in os.listdir(workshop_path):
        mod_path = os.path.join(workshop_path, mod_folder)
        if os.path.isdir(mod_path):
            about_xml_path = os.path.join(mod_path, "About", "About.xml")
            if os.path.exists(about_xml_path):
                about_files.append((mod_path, about_xml_path))
    
    print(f"Found {len(about_files)} About.xml files")
    return about_files

def parse_all_mods(workshop_path: str) -> List[ModInfo]:
    """Parse all About.xml files and return ModInfo objects"""
    about_files = find_about_xml_files(workshop_path)
    mods = []
    
    for mod_path, about_xml_path in about_files:
        try:
            mod_info = ModInfo(mod_path, about_xml_path)
            mods.append(mod_info)
        except Exception as e:
            print(f"Error parsing {about_xml_path}: {e}")
    
    return mods

def search_mods(mods: List[ModInfo], search_term: str, field: str = "all") -> List[ModInfo]:
    """Search mods based on criteria"""
    return [mod for mod in mods if mod.matches_search(search_term, field)]

def main():
    parser = argparse.ArgumentParser(
        description="Search RimWorld mod About.xml files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python search_about_xml.py --list-all
  python search_about_xml.py --name "battle"
  python search_about_xml.py --author "user"
  python search_about_xml.py --description "combat"
  python search_about_xml.py --package-id "user.battlestations"
  python search_about_xml.py --dependencies "core"
  python search_about_xml.py --search "weapon" --field all
        """
    )
    
    parser.add_argument(
        "--workshop-path",
        default=DEFAULT_WORKSHOP_PATH,
        help=f"Path to workshop content directory (default: {DEFAULT_WORKSHOP_PATH})"
    )
    
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all mods found"
    )
    
    parser.add_argument(
        "--name",
        help="Search by mod name"
    )
    
    parser.add_argument(
        "--author",
        help="Search by author name"
    )
    
    parser.add_argument(
        "--description",
        help="Search in mod description"
    )
    
    parser.add_argument(
        "--package-id",
        help="Search by package ID"
    )
    
    parser.add_argument(
        "--dependencies",
        help="Search by dependencies"
    )
    
    parser.add_argument(
        "--search",
        help="General search term"
    )
    
    parser.add_argument(
        "--field",
        choices=["all", "name", "author", "description", "package_id", "dependencies"],
        default="all",
        help="Field to search in (use with --search)"
    )
    
    parser.add_argument(
        "--count",
        action="store_true",
        help="Only show count of results"
    )
    
    args = parser.parse_args()
    
    # Parse all mods
    print("Loading mod information...")
    mods = parse_all_mods(args.workshop_path)
    
    if not mods:
        print("No mods found!")
        return
    
    print(f"Loaded {len(mods)} mods")
    
    # Determine search criteria
    results = mods
    search_performed = False
    
    if args.name:
        results = search_mods(results, args.name, "name")
        search_performed = True
        print(f"Searching for name containing: '{args.name}'")
    
    if args.author:
        results = search_mods(results, args.author, "author")
        search_performed = True
        print(f"Searching for author containing: '{args.author}'")
    
    if args.description:
        results = search_mods(results, args.description, "description")
        search_performed = True
        print(f"Searching for description containing: '{args.description}'")
    
    if args.package_id:
        results = search_mods(results, args.package_id, "package_id")
        search_performed = True
        print(f"Searching for package ID containing: '{args.package_id}'")
    
    if args.dependencies:
        results = search_mods(results, args.dependencies, "dependencies")
        search_performed = True
        print(f"Searching for dependencies containing: '{args.dependencies}'")
    
    if args.search:
        results = search_mods(results, args.search, args.field)
        search_performed = True
        print(f"Searching for '{args.search}' in field '{args.field}'")
    
    # Display results
    if args.count:
        print(f"\nFound {len(results)} matching mods")
    elif args.list_all or not search_performed:
        print(f"\nShowing all {len(results)} mods:")
        for i, mod in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"Mod #{i}")
            print(mod)
    else:
        print(f"\nFound {len(results)} matching mods:")
        for i, mod in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"Match #{i}")
            print(mod)

if __name__ == "__main__":
    main()
