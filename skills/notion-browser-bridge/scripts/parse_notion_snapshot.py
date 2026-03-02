#!/usr/bin/env python3
"""
Parse Notion snapshot data from OpenClaw browser tool.

This script helps extract structured data from Notion page snapshots,
particularly useful for tables and lists.
"""

import json
import sys
from typing import Dict, List, Any, Optional


def extract_tables(snapshot_data: Dict) -> List[Dict]:
    """
    Extract tables from snapshot data.
    
    Args:
        snapshot_data: The snapshot JSON from browser tool
        
    Returns:
        List of tables with rows and cells
    """
    tables = []
    
    def traverse(node: Dict, path: str = ""):
        # Check if this is a table
        if isinstance(node, dict):
            # Look for table elements
            if node.get("type") == "table" or "table" in str(node.get("role", "")):
                table_data = {
                    "ref": node.get("ref", ""),
                    "rows": []
                }
                
                # Try to find rows
                if "children" in node:
                    for child in node["children"]:
                        if isinstance(child, dict):
                            # Look for row elements
                            if "row" in str(child.get("role", "")) or child.get("type") == "row":
                                row_data = {
                                    "ref": child.get("ref", ""),
                                    "cells": []
                                }
                                
                                # Extract cell content
                                if "children" in child:
                                    for cell in child["children"]:
                                        if isinstance(cell, dict):
                                            cell_text = extract_text(cell)
                                            row_data["cells"].append({
                                                "ref": cell.get("ref", ""),
                                                "text": cell_text
                                            })
                                
                                table_data["rows"].append(row_data)
                
                tables.append(table_data)
            
            # Recursively traverse children
            if "children" in node:
                for child in node["children"]:
                    traverse(child, f"{path}.{node.get('ref', '')}")
    
    traverse(snapshot_data)
    return tables


def extract_links(snapshot_data: Dict) -> List[Dict]:
    """
    Extract links from snapshot data.
    
    Args:
        snapshot_data: The snapshot JSON from browser tool
        
    Returns:
        List of links with URLs and text
    """
    links = []
    
    def traverse(node: Dict):
        if isinstance(node, dict):
            # Look for link elements
            if node.get("type") == "link" or "link" in str(node.get("role", "")):
                link_data = {
                    "ref": node.get("ref", ""),
                    "text": extract_text(node),
                    "url": node.get("url", node.get("/url", ""))
                }
                links.append(link_data)
            
            # Recursively traverse children
            if "children" in node:
                for child in node["children"]:
                    traverse(child)
    
    traverse(snapshot_data)
    return links


def extract_headings(snapshot_data: Dict) -> List[Dict]:
    """
    Extract headings from snapshot data.
    
    Args:
        snapshot_data: The snapshot JSON from browser tool
        
    Returns:
        List of headings with level and text
    """
    headings = []
    
    def traverse(node: Dict):
        if isinstance(node, dict):
            # Look for heading elements
            if node.get("type") == "heading" or "heading" in str(node.get("role", "")):
                heading_data = {
                    "ref": node.get("ref", ""),
                    "text": extract_text(node),
                    "level": node.get("level", 1)
                }
                headings.append(heading_data)
            
            # Recursively traverse children
            if "children" in node:
                for child in node["children"]:
                    traverse(child)
    
    traverse(snapshot_data)
    return headings


def extract_text(node: Dict) -> str:
    """
    Extract text content from a node and its children.
    
    Args:
        node: The node to extract text from
        
    Returns:
        Concatenated text content
    """
    text_parts = []
    
    def collect_text(n: Dict):
        if isinstance(n, dict):
            # Add text property if present
            if "text" in n:
                text_parts.append(str(n["text"]))
            elif "name" in n:
                text_parts.append(str(n["name"]))
            
            # Recursively collect from children
            if "children" in n:
                for child in n["children"]:
                    collect_text(child)
        elif isinstance(n, str):
            text_parts.append(n)
    
    collect_text(node)
    return " ".join(text_parts).strip()


def parse_notion_snapshot(snapshot_file: str) -> Dict[str, Any]:
    """
    Parse a Notion snapshot file and extract structured data.
    
    Args:
        snapshot_file: Path to JSON file containing snapshot data
        
    Returns:
        Dictionary with extracted tables, links, headings, etc.
    """
    with open(snapshot_file, 'r') as f:
        snapshot_data = json.load(f)
    
    result = {
        "tables": extract_tables(snapshot_data),
        "links": extract_links(snapshot_data),
        "headings": extract_headings(snapshot_data),
        "text_content": extract_text(snapshot_data)
    }
    
    return result


def main():
    """Command-line interface for parsing Notion snapshots."""
    if len(sys.argv) < 2:
        print("Usage: python parse_notion_snapshot.py <snapshot_json_file>")
        print("Example: python parse_notion_snapshot.py snapshot.json")
        sys.exit(1)
    
    snapshot_file = sys.argv[1]
    
    try:
        data = parse_notion_snapshot(snapshot_file)
        
        print("=== Notion Snapshot Analysis ===")
        print(f"Tables found: {len(data['tables'])}")
        print(f"Links found: {len(data['links'])}")
        print(f"Headings found: {len(data['headings'])}")
        
        # Print tables in a readable format
        for i, table in enumerate(data["tables"]):
            print(f"\nTable {i + 1} (ref: {table['ref']}):")
            for j, row in enumerate(table["rows"]):
                cell_texts = [cell["text"] for cell in row["cells"]]
                print(f"  Row {j + 1}: {' | '.join(cell_texts)}")
        
        # Print links
        if data["links"]:
            print(f"\nLinks:")
            for link in data["links"]:
                print(f"  - {link['text']}: {link['url']}")
        
        # Print headings
        if data["headings"]:
            print(f"\nHeadings:")
            for heading in data["headings"]:
                level_prefix = "#" * heading["level"]
                print(f"  {level_prefix} {heading['text']}")
        
        # Optionally save to file
        output_file = f"{snapshot_file}.parsed.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nFull analysis saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{snapshot_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{snapshot_file}' is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
