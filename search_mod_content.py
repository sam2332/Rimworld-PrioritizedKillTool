#!/usr/bin/env python3
"""
Enhanced RimWorld Mod Content Search Tool
Searches through About.xml, Defs, Textures, and other mod content
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from collections import defaultdict

class ModContentSearcher:
    def __init__(self, workshop_path):
        self.workshop_path = Path(workshop_path)
        self.mods = []
        
    def load_mods(self):
        """Load all mod directories and their About.xml files"""
        print("Loading mod information...")
        about_files = list(self.workshop_path.rglob("About/About.xml"))
        print(f"Found {len(about_files)} About.xml files")
        
        for about_file in about_files:
            try:
                mod_data = self.parse_about_xml(about_file)
                if mod_data:
                    mod_data['path'] = about_file.parent.parent
                    self.mods.append(mod_data)
            except Exception as e:
                print(f"Error parsing {about_file}: {e}")
                
        print(f"Loaded {len(self.mods)} mods")
        
    def parse_about_xml(self, about_file):
        """Parse About.xml file and extract mod information"""
        try:
            tree = ET.parse(about_file)
            root = tree.getroot()
            
            mod_data = {
                'name': '',
                'author': '',
                'description': '',
                'package_id': '',
                'supported_versions': [],
                'dependencies': [],
                'load_after': [],
                'mod_id': about_file.parent.parent.name
            }
            
            # Extract basic info
            name_elem = root.find('name')
            if name_elem is not None:
                mod_data['name'] = name_elem.text or ''
                
            author_elem = root.find('author')
            if author_elem is not None:
                mod_data['author'] = author_elem.text or ''
                
            desc_elem = root.find('description')
            if desc_elem is not None:
                mod_data['description'] = desc_elem.text or ''
                
            package_elem = root.find('packageId')
            if package_elem is not None:
                mod_data['package_id'] = package_elem.text or ''
                
            # Extract supported versions
            versions_elem = root.find('supportedVersions')
            if versions_elem is not None:
                for li in versions_elem.findall('li'):
                    if li.text:
                        mod_data['supported_versions'].append(li.text)
                        
            # Extract dependencies
            deps_elem = root.find('modDependencies')
            if deps_elem is not None:
                for li in deps_elem.findall('li'):
                    package_id = li.find('packageId')
                    if package_id is not None and package_id.text:
                        mod_data['dependencies'].append(package_id.text)
                        
            # Extract load after
            load_after_elem = root.find('loadAfter')
            if load_after_elem is not None:
                for li in load_after_elem.findall('li'):
                    if li.text:
                        mod_data['load_after'].append(li.text)
                        
            return mod_data
            
        except Exception as e:
            print(f"Error parsing {about_file}: {e}")
            return None
            
    def search_defs(self, search_term, mod_path):
        """Search through all Defs files in a mod"""
        results = []
        defs_path = mod_path / "Defs"
        
        if not defs_path.exists():
            return results
            
        for def_file in defs_path.rglob("*.xml"):
            try:
                with open(def_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(search_term, content, re.IGNORECASE):
                        # Try to parse XML to get more details
                        try:
                            tree = ET.parse(def_file)
                            root = tree.getroot()
                            defs_found = []
                            
                            for def_elem in root:
                                if def_elem.tag == 'Defs':
                                    for item in def_elem:
                                        if self._matches_def(item, search_term):
                                            defs_found.append(self._extract_def_info(item))
                                else:
                                    if self._matches_def(def_elem, search_term):
                                        defs_found.append(self._extract_def_info(def_elem))
                                        
                            if defs_found:
                                results.append({
                                    'file': def_file,
                                    'defs': defs_found
                                })
                        except:
                            # If XML parsing fails, just record the file match
                            results.append({
                                'file': def_file,
                                'defs': [{'type': 'unknown', 'defName': 'unknown', 'label': 'XML parse failed'}]
                            })
                            
            except Exception as e:
                continue
                
        return results
        
    def _matches_def(self, def_elem, search_term):
        """Check if a def element matches the search term"""
        # Check defName
        def_name = def_elem.get('Name') or def_elem.get('defName')
        if def_name and re.search(search_term, def_name, re.IGNORECASE):
            return True
            
        # Check label
        label_elem = def_elem.find('label')
        if label_elem is not None and label_elem.text:
            if re.search(search_term, label_elem.text, re.IGNORECASE):
                return True
                
        # Check description
        desc_elem = def_elem.find('description')
        if desc_elem is not None and desc_elem.text:
            if re.search(search_term, desc_elem.text, re.IGNORECASE):
                return True
                
        return False
        
    def _extract_def_info(self, def_elem):
        """Extract information from a def element"""
        info = {
            'type': def_elem.tag,
            'defName': def_elem.get('Name') or def_elem.get('defName') or 'unknown',
            'label': '',
            'description': ''
        }
        
        label_elem = def_elem.find('label')
        if label_elem is not None and label_elem.text:
            info['label'] = label_elem.text
            
        desc_elem = def_elem.find('description')
        if desc_elem is not None and desc_elem.text:
            info['description'] = desc_elem.text[:100] + "..." if len(desc_elem.text) > 100 else desc_elem.text
            
        return info
        
    def search_textures(self, search_term, mod_path):
        """Search through texture files in a mod"""
        results = []
        textures_path = mod_path / "Textures"
        
        if not textures_path.exists():
            return results
            
        for texture_file in textures_path.rglob("*"):
            if texture_file.is_file() and re.search(search_term, texture_file.name, re.IGNORECASE):
                results.append({
                    'file': texture_file,
                    'relative_path': texture_file.relative_to(textures_path)
                })
                
        return results
        
    def search_assemblies(self, search_term, mod_path):
        """Search for assembly files"""
        results = []
        assemblies_path = mod_path / "Assemblies"
        
        if not assemblies_path.exists():
            return results
            
        for assembly_file in assemblies_path.rglob("*.dll"):
            if re.search(search_term, assembly_file.name, re.IGNORECASE):
                results.append(assembly_file)
                
        return results
        
    def search_all_content(self, search_term, search_type='all'):
        """Search through all mod content"""
        matching_mods = []
        
        for mod in self.mods:
            mod_matches = {
                'mod_info': mod,
                'about_match': False,
                'def_matches': [],
                'texture_matches': [],
                'assembly_matches': []
            }
            
            # Check About.xml content
            if search_type in ['all', 'about']:
                searchable_text = f"{mod['name']} {mod['author']} {mod['description']} {mod['package_id']}".lower()
                if search_term.lower() in searchable_text:
                    mod_matches['about_match'] = True
                    
            # Search Defs
            if search_type in ['all', 'defs']:
                mod_matches['def_matches'] = self.search_defs(search_term, mod['path'])
                
            # Search Textures
            if search_type in ['all', 'textures']:
                mod_matches['texture_matches'] = self.search_textures(search_term, mod['path'])
                
            # Search Assemblies
            if search_type in ['all', 'assemblies']:
                mod_matches['assembly_matches'] = self.search_assemblies(search_term, mod['path'])
                
            # Add to results if any matches found
            if (mod_matches['about_match'] or 
                mod_matches['def_matches'] or 
                mod_matches['texture_matches'] or 
                mod_matches['assembly_matches']):
                matching_mods.append(mod_matches)
                
        return matching_mods
        
    def print_results(self, results, search_term):
        """Print search results in a formatted way"""
        if not results:
            print(f"No matches found for '{search_term}'")
            return
            
        print(f"\nFound {len(results)} mods with matches for '{search_term}':")
        print("=" * 80)
        
        for i, mod_result in enumerate(results, 1):
            mod = mod_result['mod_info']
            print(f"\nMatch #{i}")
            print("=" * 60)
            print(f"Mod ID: {mod['mod_id']}")
            print(f"Name: {mod['name']}")
            print(f"Author: {mod['author']}")
            print(f"Package ID: {mod['package_id']}")
            print(f"Path: {mod['path']}")
            
            if mod_result['about_match']:
                print("✓ Found in About.xml")
                
            if mod_result['def_matches']:
                print(f"✓ Found in {len(mod_result['def_matches'])} Def files:")
                for def_match in mod_result['def_matches']:
                    print(f"   - {def_match['file'].relative_to(mod['path'])}")
                    for def_info in def_match['defs']:
                        print(f"     • {def_info['type']}: {def_info['defName']} ({def_info['label']})")
                        
            if mod_result['texture_matches']:
                print(f"✓ Found {len(mod_result['texture_matches'])} texture files:")
                for texture_match in mod_result['texture_matches']:
                    print(f"   - {texture_match['relative_path']}")
                    
            if mod_result['assembly_matches']:
                print(f"✓ Found {len(mod_result['assembly_matches'])} assembly files:")
                for assembly in mod_result['assembly_matches']:
                    print(f"   - {assembly.name}")

def main():
    parser = argparse.ArgumentParser(
        description="Search through RimWorld mod content (About.xml, Defs, Textures, Assemblies)"
    )
    
    parser.add_argument(
        '--workshop-path',
        default=r"C:\Program Files (x86)\Steam\steamapps\workshop\content\294100",
        help="Path to the workshop content directory"
    )
    
    parser.add_argument(
        'search_term',
        help="Term to search for"
    )
    
    parser.add_argument(
        '--type',
        choices=['all', 'about', 'defs', 'textures', 'assemblies'],
        default='all',
        help="Type of content to search"
    )
    
    parser.add_argument(
        '--count',
        action='store_true',
        help="Only show count of matches"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.workshop_path):
        print(f"Error: Workshop path does not exist: {args.workshop_path}")
        sys.exit(1)
        
    searcher = ModContentSearcher(args.workshop_path)
    searcher.load_mods()
    
    results = searcher.search_all_content(args.search_term, args.type)
    
    if args.count:
        print(f"Found {len(results)} mods with matches for '{args.search_term}'")
    else:
        searcher.print_results(results, args.search_term)

if __name__ == "__main__":
    main()
