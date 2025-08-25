#!/usr/bin/env python3
"""
MultiPosti - Main CLI Application
Multi-platform social media video uploader
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import argparse
import logging
from core import PlatformManager

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def list_platforms(manager: PlatformManager):
    """List all available platforms"""
    print("Available Platforms:")
    print("=" * 20)
    
    status = manager.get_all_platform_status()
    for name, info in status.items():
        auth_status = "OK" if info['authenticated'] else "NO"
        print(f"{name.title():<15} [{auth_status}] {'Authenticated' if info['authenticated'] else 'Not authenticated'}")
    
    print()

def authenticate_platform(manager: PlatformManager, platform: str):
    """Authenticate with a specific platform"""
    print(f"Authenticating with {platform.title()}...")
    
    success = manager.authenticate_platform(platform)
    if success:
        print(f"SUCCESS: {platform.title()} authentication successful!")
    else:
        print(f"FAILED: {platform.title()} authentication failed!")
    
    return success

def upload_video(manager: PlatformManager, platforms: list, video_path: str, 
                title: str, description: str, **kwargs):
    """Upload video to specified platforms"""
    print(f"Uploading video: {video_path}")
    print(f"Title: {title}")
    print(f"Platforms: {', '.join(platforms)}")
    print()
    
    results = manager.upload_video_to_multiple_platforms(
        platforms, video_path, title, description, **kwargs
    )
    
    print("Upload Results:")
    print("=" * 15)
    
    for platform, result in results.items():
        if result['success']:
            print(f"SUCCESS {platform.title()}: Upload completed")
            if 'video_url' in result:
                print(f"  URL: {result['video_url']}")
        else:
            print(f"FAILED {platform.title()}: {result.get('error', 'Unknown error')}")
    
    print()

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="MultiPosti - Multi-platform social media video uploader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List platforms command
    list_parser = subparsers.add_parser('list', help='List available platforms')
    
    # Authenticate command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with platform')
    auth_parser.add_argument('platform', choices=['youtube', 'facebook', 'tiktok'],
                           help='Platform to authenticate with')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload video to platforms')
    upload_parser.add_argument('video_path', help='Path to video file')
    upload_parser.add_argument('--platforms', '-p', nargs='+', 
                             choices=['youtube', 'facebook', 'tiktok'],
                             default=['youtube'], help='Target platforms')
    upload_parser.add_argument('--title', '-t', required=True, help='Video title')
    upload_parser.add_argument('--description', '-d', default='', help='Video description')
    upload_parser.add_argument('--tags', nargs='*', help='Video tags (YouTube)')
    upload_parser.add_argument('--privacy', choices=['private', 'public', 'unlisted'],
                             default='private', help='Privacy setting (YouTube)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show platform status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Initialize platform manager
    print("Initializing MultiPosti...")
    manager = PlatformManager()
    print(f"Loaded platforms: {', '.join(manager.get_available_platforms())}")
    print()
    
    # Execute command
    if args.command == 'list':
        list_platforms(manager)
    
    elif args.command == 'auth':
        authenticate_platform(manager, args.platform)
    
    elif args.command == 'upload':
        # Prepare upload parameters
        upload_kwargs = {
            'tags': args.tags or [],
            'privacy': args.privacy
        }
        
        upload_video(manager, args.platforms, args.video_path, 
                    args.title, args.description, **upload_kwargs)
    
    elif args.command == 'status':
        list_platforms(manager)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)