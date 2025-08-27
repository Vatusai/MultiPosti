# Facebook Page Setup Guide

## Current Status ✅❌
- ✅ **App ID Found**: `1438267127386307`
- ✅ **Access Token Valid**: Has all required permissions
- ✅ **User Account**: `Fabian Orozco González` (ID: `10238533643543614`)
- ❌ **Missing Facebook Page**: You need to create or get admin access to a Facebook page

## Why You Need a Facebook Page

Facebook videos must be posted to **Pages**, not personal profiles. Personal user accounts cannot post videos via the API.

## Step 1: Create a Facebook Page

1. **Go to**: https://www.facebook.com/pages/create
2. **Choose a page type**: 
   - Business or Brand
   - Community or Public Figure
3. **Fill in details**:
   - Page Name: (e.g., "MultiPosti Content", "Your Business Name")
   - Category: (e.g., "Software Company", "Content Creator") 
   - Description: Brief description of what the page is for
4. **Click "Create Page"**

## Step 2: Get Your Page ID

After creating the page, you can get the Page ID in several ways:

### Method A: From Page URL
- Visit your page
- Look at the URL: `facebook.com/YourPageName-123456789`
- The numbers at the end are your Page ID

### Method B: Using Graph API (Recommended)
Run this script after creating your page:

```bash
python get_facebook_credentials.py
```

This will show all your managed pages with their IDs.

### Method C: Page Info Section
- Go to your page
- Click "About" 
- Scroll to "Page Info"
- You'll see the Page ID listed

## Step 3: Update Credentials

Once you have your Page ID, update `credentials/facebook/facebook_token.json`:

```json
{
  "access_token": "your_current_token",
  "app_id": "1438267127386307",
  "page_id": "YOUR_NEW_PAGE_ID_HERE",
  "user_id": "10238533643543614",
  "user_name": "Fabian Orozco González",
  "created_at": 1699999999
}
```

## Step 4: Test the Setup

Run the test script to verify everything works:

```bash
python test_facebook_video.py
```

## Alternative: Use Existing Page

If you already manage a Facebook page for your business or project:
1. Make sure you're an admin of that page
2. Run `python get_facebook_credentials.py` to get the Page ID
3. Update the credentials file with that Page ID

## Troubleshooting

**Q: I created a page but it's not showing in managed pages**
- Wait a few minutes and run the script again
- Make sure you're logged into the same Facebook account

**Q: Page shows but I get permission errors**
- Make sure you're an admin (not just editor) of the page
- Check that your access token hasn't expired

**Q: Still having issues?**
- Try generating a new access token with page permissions
- Visit: https://developers.facebook.com/tools/explorer/