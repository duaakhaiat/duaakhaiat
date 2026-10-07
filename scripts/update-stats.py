import json, os, urllib.request, datetime
from pathlib import Path
token = os.environ.get('PROFILE_TOKEN')
if not token:
    raise RuntimeError('Add PROFILE_TOKEN as an Actions repository secret first')
repos = []
page = 1
while True:
    request = urllib.request.Request(f'https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}', headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request) as response:
        batch = json.load(response)
    repos.extend(r for r in batch if r['owner']['login'].lower() == 'duaakhaiat')
    if len(batch) < 100:
        break
    page += 1
values = [(len(repos), 'REPOSITORIES'), (sum(r['private'] for r in repos), 'PRIVATE REPOS'), (sum(r['stargazers_count'] for r in repos), 'STARS'), (sum(r['forks_count'] for r in repos), 'FORKS')]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="160" viewBox="0 0 1000 160"><rect width="1000" height="160" rx="8" fill="#ffffff"/>']
for i, (value, label) in enumerate(values):
    x = 125 + i * 250
    parts.append(f'<text x="{x}" y="72" text-anchor="middle" fill="#24292f" font-family="Arial" font-size="38" font-weight="bold">{value}</text><text x="{x}" y="106" text-anchor="middle" fill="#0969da" font-family="monospace" font-size="12" letter-spacing="2">{label}</text>')
parts.append(f'<text x="500" y="143" text-anchor="middle" fill="#57606a" font-family="monospace" font-size="10">Authorized repository scope · updated {datetime.date.today().isoformat()}</text></svg>')
Path('assets').mkdir(exist_ok=True)
Path('assets/stats.svg').write_text(''.join(parts))
