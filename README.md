# EntitlementDBExtractor

EntitlementDBExtractor is a program that allows you to extract licenses and entitlements for your digital games, DLC, themes, and other content from your `entitlement.db` file. This allows you to re-download PSN titles you've deleted from your system.
> [!IMPORTANT]
> In order for this process to work, your account should've been set as primary at the time of downloading the game in the past, and your console must not be formatted after downloading the game; otherwise this process will not work, because you will be missing the license key!

The tool will give you the links to Sony's API, so you can re-download your titles in the form of **RETAIL** PKGs from **Official Sony Servers**!

# Requirements
1. Python (v3.7+)
2. Jailbroken PS4

Run with the following command
```bash
python <path-to-db>
```

The script will create five JSON files in output/; `games.json`, `themes.json`, `additional_content.json`, `additional_license.json` and `broken.json`.
Here is an example of an entry in `games.json`:
```json
{
  "13de9468": {
    "active": [
      {
        "name": "FIFA 17",
        "icon": "...",
        "id": "EP0006-CUSA03214_00-FIFAFOOTBALL2017",
        "active": true,
        "hasRif": true,
        "size": 38.14,
        "pkg_url": "...",
        "license_expired": false,
        "is_ps_plus": false
      }
    ],
    "inactive": []
  }
}
```

# A bit of context...
The entries in the JSON are sorted by USER_ID. You need to find your USER_ID using some homebrew app like Apollo Save tool, then find your USER_ID in the entries. Again, you can only potentially install games from a list that has a matching USER_ID.  

In each USER_ID entry, you will find two arrays. One contains active titles (whose license is active) and the other contains inactive titles (whose license is expired). Games that are inactive almost certainly won't either install properly or open at all, so do not bother downloading them.

The `pkg_url` contains a JSON with multiple small pkgs. It's recommended you use a tool like JDownloader2, to easily group and combine these packages into one main package.

If the above holds, then the titles listed in the active directory are very likely to work.

## TLDR rules
1. Make sure the title is active
2. Make sure the title was originally downloaded on a ps4 with an account that was set to primary and console was not formatted
3. Make sure the title is from the list containing your USER_ID (Find your USER_ID with a homebrew app like Apollo Save Tool)
