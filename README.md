# TV Wallpapers

Custom photo wallpapers for Projectivy Launcher via the Overflight plugin.

## Adding photos

1. On GitHub, open `photos/`, then the collection folder you want (or make a new one:
   **Add file → Create new file**, type `my-collection/.gitkeep`, commit).
2. **Add file → Upload files**, drop your pictures in and commit.
3. Wait about a minute. A GitHub Action fixes rotation, converts HEIC/PNG to JPEG,
   shrinks anything bigger than 4K, and updates the lists below.

Any image format works: JPG, PNG, WEBP, HEIC (iPhone).

## Links for Overflight

Paste one of these into Overflight's custom URL setting:

- All photos: `https://raw.githubusercontent.com/OWNER/REPO/main/wallpapers.json`
- One collection: `https://raw.githubusercontent.com/OWNER/REPO/main/collections/<folder-name>.json`

Each entry's `location` is set to the collection name, so Overflight's keyword filter
can also narrow the full list down to one collection.
