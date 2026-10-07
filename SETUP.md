# Install your profile

1. Create a PUBLIC repository named duaakhaiat in your duaakhaiat account.
2. Extract this ZIP. Upload README.md and the assets folder to that repository.
3. For automatic statistics, also commit .github/workflows/profile-stats.yml and scripts/update-stats.py. A local Git client or GitHub's file editor can create these paths.

## Include private repository statistics

The public preview cannot read your private repositories. It never invents private totals.

Create a fine-grained personal access token at GitHub Settings > Developer settings > Personal access tokens. Set resource owner to duaakhaiat, select ALL repositories (or only those you want counted), and grant read-only repository Metadata access. No write access is needed for this token. Its selected repository scope determines the total; selecting only some will only count those repositories. Give it an expiry and renew it before expiry.

In your profile repository, open Settings > Secrets and variables > Actions > New repository secret. Name it PROFILE_TOKEN and paste your token there. NEVER paste it into your README, code, a URL, or this app.

Open Actions > Update profile statistics > Run workflow. The action uses your secret to count repositories you own (public and private) and their stars/forks; it publishes ONLY aggregate totals, not private repository names, code or languages. The workflow runs daily. This deliberately makes your PRIVATE REPOSITORY COUNT public: enable it only if you want to disclose that aggregate.

The built-in GITHUB_TOKEN writes the generated stats file; PROFILE_TOKEN only reads repository metadata. If your organization blocks tokens or workflows, resolve that in GitHub first.

## Private contributions

On your GitHub profile, above the contribution calendar, choose Contribution settings > Private contributions. GitHub displays anonymized private activity, not private repository details. The bundled activity image is a dated public snapshot, not a live or private-inclusive graph. Enable the GitHub setting for a live native profile graph.

LinkedIn and Instagram are included in the profile links.
