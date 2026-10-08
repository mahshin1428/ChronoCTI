# Upload ChronoCTI to GitHub (code only)

The root `.gitignore` excludes local datasets, reports, generated features,
trained models, embeddings, checkpoints, installed dependencies, environment
files, and release archives. These files remain on your computer.
Source code, documentation, dependency manifests, training configuration,
frontend configuration, and small technique/asset label mappings are included.
This checkout has already been initialized as a Git repository on `main`.

## First upload

1. On GitHub, create an **empty** repository named `ChronoCTI`. Choose your
   preferred visibility. Do not initialize it with a README, license, or
   `.gitignore`; this project already supplies those files.
2. Open a terminal and run:

   ```sh
   cd "/Users/mahshinislam/ChronoCTI Resource/ChronoCTI-main"
   git add .
   git diff --cached --stat
   git status --short
   git commit -m "Initial code-only release of ChronoCTI"
   git remote add origin https://github.com/mahshin1428/ChronoCTI.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` with your GitHub username. Authenticate with GitHub
   when requested; HTTPS authentication uses a personal access token or a
   credential manager, rather than your account password. If Git asks for your
   commit identity, set it for this repository and repeat the commit:

   ```sh
   git config user.name "Your Name"
   git config user.email "YOUR_GITHUB_EMAIL_OR_NOREPLY_ADDRESS"
   ```

Use these Git commands instead of dragging the whole project into the browser:
the `.gitignore` controls Git's file selection, not browser file uploads.
The destination for this checkout is `https://github.com/mahshin1428/ChronoCTI`.
Once `origin` is configured, skip `git remote add origin` and use `git push -u origin main`.

## Later updates

```sh
git add .
git diff --cached --stat
git commit -m "Describe your code changes"
git push
```

Do not force-add ignored files. `.gitignore` does not remove files that were
already committed; this repository starts without previous history.
New JSON files are excluded by default because this project stores datasets,
predictions, and serialized models in JSON. For a new code configuration file,
add an explicit `!path/to/config.json` exception to `.gitignore` after review.

## Running a code-only checkout

This is source code, not a self-contained trained pipeline. Supply datasets and
train or obtain models separately at the paths expected by the scripts.
Install dependencies from the component manifests. Installed TreeTagger and
MALLET directories and NLP statistical dictionaries are excluded; reinstall
the required external tools/resources using the TimeML documentation and
installation scripts. The web frontend source is included; build it using
`web-server/README.md` to recreate the excluded compiled static files.

`temporal-learner-code/classify_ttps_using_embeddings.py` now reads
`OPENAI_API_KEY` and optional `OPENAI_ORG_ID` from environment variables.
The hardcoded key was removed; revoke/rotate the old key if it is still active.

Official instructions:
[Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).
