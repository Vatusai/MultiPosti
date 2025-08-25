#!/usr/bin/env python3
"""
Test script to verify the new modular structure works correctly
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("Testing imports...")
    
    try:
        from core import CredentialsManager, PlatformManager, BaseSocialPlatform
        print("✓ Core modules imported successfully")
        
        from platforms.youtube import YouTubePlatform
        print("✓ YouTube platform imported successfully")
        
        # Test importing placeholder platforms
        from platforms.facebook.facebook_platform import FacebookPlatform
        from platforms.tiktok.tiktok_platform import TikTokPlatform
        print("✓ Placeholder platforms imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_credentials_manager():
    """Test credentials manager functionality"""
    print("\nTesting CredentialsManager...")
    
    try:
        manager = CredentialsManager()
        
        # Test platform path creation
        youtube_path = manager.get_platform_path('youtube')
        print(f"✓ YouTube credentials path: {youtube_path}")
        
        # Test file listing
        files = manager.list_platform_files('youtube')
        print(f"✓ YouTube files: {files}")
        
        return True
        
    except Exception as e:
        print(f"✗ CredentialsManager error: {e}")
        return False

def test_platform_manager():
    """Test platform manager functionality"""
    print("\nTesting PlatformManager...")
    
    try:
        manager = PlatformManager()
        
        # Test platform listing
        platforms = manager.get_available_platforms()
        print(f"✓ Available platforms: {platforms}")
        
        # Test platform status
        status = manager.get_all_platform_status()
        print("✓ Platform status:")
        for name, info in status.items():
            auth_status = "authenticated" if info['authenticated'] else "not authenticated"
            print(f"   {name}: {auth_status}")
        
        return True
        
    except Exception as e:
        print(f"✗ PlatformManager error: {e}")
        return False

def test_youtube_platform():
    """Test YouTube platform specifically"""
    print("\nTesting YouTube Platform...")
    
    try:
        from core import CredentialsManager
        from platforms.youtube.youtube_platform import YouTubePlatform
        
        credentials_manager = CredentialsManager()
        youtube = YouTubePlatform(credentials_manager)
        
        print(f"✓ YouTube platform created: {youtube}")
        print(f"✓ Platform name: {youtube.get_platform_name()}")
        print(f"✓ Credentials path: {youtube.get_credentials_path()}")
        print(f"✓ Supported formats: {youtube.get_supported_formats()}")
        
        # Check if client secret exists
        client_secret_path = youtube.get_credentials_path() / 'client_secret.json'
        if client_secret_path.exists():
            print("✓ Client secret file found")
        else:
            print("⚠️  Client secret file not found (expected for fresh setup)")
        
        return True
        
    except Exception as e:
        print(f"✗ YouTube platform error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== MultiPosti Modular Structure Test ===")
    print()
    
    all_tests_passed = True
    
    # Run tests
    tests = [
        test_imports,
        test_credentials_manager,
        test_platform_manager,
        test_youtube_platform
    ]
    
    for test in tests:
        if not test():
            all_tests_passed = False
    
    print("\n" + "=" * 45)
    
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The new modular structure is working correctly.")
        print()
        print("Next steps:")
        print("1. Run: python src/platforms/youtube/setup_auth.py")
        print("2. Run: python scripts/main.py list")
        print("3. Upload a test video!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above and fix the issues.")

if __name__ == '__main__':
    main()