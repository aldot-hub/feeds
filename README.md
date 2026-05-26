# AL.com YouTube Feed Merger

Automatically merges the Alabama Crimson Tide and Auburn Tigers AL.com YouTube channel RSS feeds into a single MRSS feed, sorted newest to oldest. Runs every 15 minutes via GitHub Actions and is served via GitHub Pages.

## Feeds included

- [Alabama Crimson Tide on AL.com](https://www.youtube.com/channel/UCXovZWLiLAQwhc07L_TuHYQ)
- [Auburn Tigers on AL.com](https://www.youtube.com/channel/UC2JSgw37hwXBA-4PVeVlwAg)

## Setup instructions

### 1. Create the repository

1. Go to [github.com](https://github.com) and create a new **public** repository (e.g. `alcom-sports-feed`)
2. Upload all files from this project into the repository

### 2. Enable GitHub Pages

1. Go to your repository → **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Set branch to `main` and folder to `/docs`
4. Click **Save**

GitHub will give you a URL like:
```
https://yourusername.github.io/alcom-sports-feed/feed.xml
```

That is the feed URL you give to ex.co.

### 3. Trigger the first run

1. Go to your repository → **Actions** tab
2. Click **Merge YouTube Feeds** in the left sidebar
3. Click **Run workflow** → **Run workflow**

This generates the initial `docs/feed.xml`. After that, it runs automatically every 15 minutes.

### 4. Give the feed URL to ex.co

Once GitHub Pages is enabled and the first run has completed, your feed URL will be:
```
https://[your-github-username].github.io/[your-repo-name]/feed.xml
```

Use this as the MRSS feed URL in ex.co.

## How it works

- `merge_feeds.py` fetches both YouTube channel RSS feeds, merges all videos, sorts them newest to oldest, and writes a combined MRSS-compatible XML file to `docs/feed.xml`
- `.github/workflows/merge-feeds.yml` runs the script on a 15-minute schedule and commits the updated file back to the repository
- GitHub Pages serves `docs/feed.xml` as a public URL

## Modifying channels

To add or remove channels, edit the `FEEDS` list at the top of `merge_feeds.py`.
