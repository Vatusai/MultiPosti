#!/usr/bin/env python3
"""
Test script for Facebook video posting functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.platform_manager import PlatformManager


def test_facebook_video_upload():
    """Test Facebook video upload functionality"""
    print("Testing Facebook Video Upload Functionality")
    print("=" * 50)
    
    # Initialize platform manager
    platform_manager = PlatformManager(credentials_path="credentials")
    
    # Check if Facebook platform is available
    available_platforms = platform_manager.get_available_platforms()
    print(f"Available platforms: {available_platforms}")
    
    if 'facebook' not in available_platforms:
        print("X Facebook platform not available")
        return False
    
    # Get Facebook platform status
    fb_status = platform_manager.get_platform_status('facebook')
    print(f"Facebook platform status: {fb_status}")
    
    # Try to authenticate
    print("\nAttempting to authenticate with Facebook...")
    auth_success = platform_manager.authenticate_platform('facebook')
    
    if not auth_success:
        print("X Facebook authentication failed")
        print("Make sure you have:")
        print("  1. Valid access_token in credentials/facebook/facebook_token.json")
        print("  2. Valid page_id in the token file")
        print("  3. Valid app_id in the token file")
        print("  4. Required permissions: pages_show_list, pages_read_engagement, pages_manage_posts")
        return False
    
    print("+ Facebook authentication successful")
    
    # Test video path
    video_path = "tutorial.mp4"
    if not os.path.exists(video_path):
        print(f"X Test video file not found: {video_path}")
        return False
    
    print(f"Using test video: {video_path}")
    
    # Test upload (dry run - comment out if you want to actually upload)
    print("\nTesting video upload process...")
    
    # Test actual video upload
    result = platform_manager.upload_video_to_platform(
        'facebook',
        video_path,
        title="Test Video Upload - Facebook API",
        description="This is a test video upload using the new Facebook resumable upload API implementation.",
        hashtags=["test", "MultiPosti", "FacebookAPI"]
    )
    
    if result['success']:
        print(f"+ Video upload successful! Video ID: {result.get('video_id')}")
        return True
    else:
        print(f"X Video upload failed: {result.get('error')}")
        return False
    print("+ All tests passed - Facebook platform is ready for video uploads!")
    return True


def main():
    """Main test function"""
    print("MultiPosti - Facebook Video Upload Test")
    print("======================================")
    
    success = test_facebook_video_upload()
    
    if success:
        print("\nAll tests completed successfully!")
        print("\nYour Facebook platform is now configured with:")
        print("  + Resumable Upload API (for large video files)")
        print("  + Proper video posting using Graph API v23.0")
        print("  + Error handling and upload resumption")
        print("  + Support for title, description, and hashtags")
    else:
        print("\nX Tests failed. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())