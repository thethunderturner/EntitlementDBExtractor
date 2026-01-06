# EntitlementDBExtractor

EntitlementDBExtractor is a program that allows you to extract licenses and entitlements for your digital games, DLC, themes, and other content. This allows the user to potentially re-download old deleted PSN titles.

Run with the following command
```bash
python <path-to-db>
```

The script will create two JSON files in output/; `games.json` and `themes.json`
An example:
```json
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
```

# A bit of context...
The `pkg_url` contains a JSON with multiple small pkgs. It's recommended you use a tool like JDownloader2, to easily group and combine these packages into one main package.\
> [!IMPORTANT]
> In order for this process to work, your account should've been set as primary at the time of downloading the game in the past; otherwise this process will not work, because you will be missing the license key!

If the above holds, then games listed in the active directory are very likely to work. Games that are inactive almost certainly won't either install properly or open at all, because their licenses are expired.