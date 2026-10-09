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
colors = ['#71ddff', '#a78bfa', '#f0abfc', '#57e0bd']
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="180" viewBox="0 0 1000 180">',
    '<rect width="1000" height="180" rx="18" fill="#0b1020" stroke="#293452"/>',
    '<text x="500" y="26" text-anchor="middle" fill="#aeb7d4" font-family="monospace" font-size="10" letter-spacing="3">GITHUB SNAPSHOT</text>',
]
for i, (value, label) in enumerate(values):
    x = 20 + i * 245
    color = colors[i]
    parts.append(
        f'<rect x="{x}" y="40" width="230" height="94" rx="14" fill="#111a35" stroke="#293452"/>'
        f'<rect x="{x + 1}" y="41" width="228" height="2" rx="1" fill="{color}" opacity=".7">'
        f'<animate attributeName="opacity" values=".25;.85;.25" dur="4s" begin="{i * 0.45}s" repeatCount="indefinite"/></rect>'
        f'<text x="{x + 115}" y="91" text-anchor="middle" fill="#f8fafc" font-family="Arial" font-size="34" font-weight="bold">{value}</text>'
        f'<text x="{x + 115}" y="116" text-anchor="middle" fill="{color}" font-family="monospace" font-size="10" letter-spacing="1.5">{label}</text>'
    )
parts.append(f'<text x="500" y="160" text-anchor="middle" fill="#7f8aaa" font-family="monospace" font-size="10">Authorized repository scope · updated {datetime.date.today().isoformat()}</text></svg>')
Path('assets').mkdir(exist_ok=True)
Path('assets/stats.svg').write_text(''.join(parts))
