#!/usr/bin/env python3
"""
Digital Archaeologist CLI

Usage:
  python archaeologist.py scan ~/projects
  python archaeologist.py resurrect --top 5
"""

import argparse
import json
import sys
from pathlib import Path
from scanner import scan_projects


def cmd_scan(args):
    """Scan directory for stalled projects"""
    print(f"🔍 Scanning: {args.path}")
    print(f"   Depth: {args.depth}\n")
    
    projects = scan_projects(args.path, depth=args.depth)
    
    # Save results
    cache_file = Path.home() / '.digital-archaeologist-cache.json'
    cache_data = {
        'projects': [
            {
                'name': p.name,
                'path': p.path,
                'score': p.score,
                'days_stalled': p.days_stalled,
                'last_commit': p.last_commit.isoformat() if p.last_commit else None,
                'dependencies': p.dependencies,
            }
            for p in projects
        ]
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    # Display summary
    stalled = [p for p in projects if p.days_stalled and p.days_stalled > 180]  # 6+ months
    
    print("=" * 60)
    print(f"Scanned: {len(projects)} repos, {len(stalled)} stalled projects identified")
    print("=" * 60)
    print(f"\nResults cached to: {cache_file}")
    print(f"Run: python archaeologist.py resurrect --top 5\n")


def cmd_resurrect(args):
    """Show top resurrection candidates"""
    cache_file = Path.home() / '.digital-archaeologist-cache.json'
    
    if not cache_file.exists():
        print("Error: No scan cache found. Run 'scan' first.", file=sys.stderr)
        sys.exit(1)
    
    with open(cache_file, 'r') as f:
        data = json.load(f)
    
    projects = data['projects']
    
    # Filter stalled projects
    stalled = [p for p in projects if p.get('days_stalled') and p['days_stalled'] > 180]
    
    # Sort by score
    stalled.sort(key=lambda p: p['score'], reverse=True)
    
    # Display top N
    top = stalled[:args.top]
    
    print("\n" + "=" * 60)
    print("  TOP RESURRECTION CANDIDATES")
    print("=" * 60 + "\n")
    
    for i, project in enumerate(top, 1):
        score = project['score']
        name = project['name']
        days = project.get('days_stalled', 0)
        years = days / 365.0
        deps = project.get('dependencies', {})
        dep_count = deps.get('count', 0)
        
        print(f"{i}. [{score}/100] {name} ({years:.1f}y ago)")
        print(f"   Stalled: {days} days ago")
        print(f"   Path: {project['path']}")
        if dep_count > 0:
            print(f"   Dependencies: {dep_count}")
        
        # Resurrection hints
        if deps.get('has_package_json'):
            print(f"   Action: Check npm for updated alternatives")
        elif deps.get('has_requirements'):
            print(f"   Action: Check PyPI for updated packages")
        
        print()
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Digital Archaeologist - Project Resurrection Engine')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan directory for stalled projects')
    scan_parser.add_argument('path', help='Root directory to scan')
    scan_parser.add_argument('--depth', type=int, default=3, help='Max depth to scan (default: 3)')
    
    # Resurrect command
    res_parser = subparsers.add_parser('resurrect', help='Show top resurrection candidates')
    res_parser.add_argument('--top', type=int, default=5, help='Number of top candidates (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'scan':
        cmd_scan(args)
    elif args.command == 'resurrect':
        cmd_resurrect(args)


if __name__ == '__main__':
    main()
