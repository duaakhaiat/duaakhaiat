#!/usr/bin/env python3
"""Regenerates the data-driven SVGs of the profile README from real GitHub data.
Needs env: GH_TOKEN (the Actions GITHUB_TOKEN is enough) and GH_USER (login).
Run `python scripts/update_profile.py --mock` to test without network."""
import json, os, random, re, sys, urllib.request
from xml.sax.saxutils import escape as esc

NAVY="#0b1030"; CARD="#0f1749"; BORDER="#26338a"; DIM="#8fa0dd"
GOLD="#ffe9a8"; CYAN="#5ce1ff"; VIOLET="#8b6cff"; PINK="#ff6bb5"; MINT="#3ee6b0"
PALETTE=[GOLD,"#6aa8ff",MINT,PINK,"#ff8a65",CYAN,VIOLET,"#7be37b"]
FONT="'Segoe UI', Helvetica, Arial, sans-serif"
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFS='''<defs>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>
</defs>'''

QUERY="""query($login:String!){user(login:$login){name login
 repositories(ownerAffiliations:OWNER,isFork:false,first:100,orderBy:{field:STARGAZERS,direction:DESC}){totalCount
  nodes{name stargazerCount forkCount url description primaryLanguage{name}
   languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
 pinnedItems(first:3,types:REPOSITORY){nodes{...on Repository{name description stargazerCount forkCount url primaryLanguage{name}}}}
 contributionsCollection{totalCommitContributions
  contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}"""

def fetch(login, token):
    req=urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query":QUERY,"variables":{"login":login}}).encode(),
        headers={"Authorization":f"bearer {token}","Content-Type":"application/json","User-Agent":"profile-updater"})
    d=json.load(urllib.request.urlopen(req,timeout=60))
    if "errors" in d: raise SystemExit(f"GitHub API error: {d['errors']}")
    return d["data"]["user"]

def mock():
    random.seed(1)
    langs=["JavaScript","TypeScript","Python","CSS","HTML","Shell"]
    repos=[{"name":f"repo-{i}","stargazerCount":random.randint(0,30),"forkCount":random.randint(0,8),"url":f"https://github.com/me/repo-{i}",
            "description":"A mock repository used for testing the profile generator","primaryLanguage":{"name":random.choice(langs)},
            "languages":{"edges":[{"size":random.randint(1000,90000),"node":{"name":random.choice(langs)}} for _ in range(3)]}} for i in range(14)]
    weeks=[{"contributionDays":[{"contributionCount":random.choice([0,0,0,1,2,4,7,12]) } for _ in range(7)]} for _ in range(53)]
    return {"name":"Mock User","login":"mockuser","repositories":{"totalCount":14,"nodes":repos},
            "pinnedItems":{"nodes":repos[:3]},
            "contributionsCollection":{"totalCommitContributions":412,"contributionCalendar":{"totalContributions":530,"weeks":weeks}}}

def twinkles(n,w,h,seed):
    random.seed(seed); o=[]
    for _ in range(n):
        x,y=random.uniform(0,w),random.uniform(0,h); lo=random.uniform(.05,.3)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.choice([.7,1,1.4])}" fill="{random.choice(["#fff","#fff",GOLD,"#bcd0ff"])}"><animate attributeName="opacity" values="{lo:.2f};1;{lo:.2f}" dur="{random.uniform(2,6):.1f}s" begin="{random.uniform(0,6):.1f}s" repeatCount="indefinite"/></circle>')
    return "".join(o)

def write(name,w,h,body):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{DEFS}{body}</svg>'
    open(os.path.join(ROOT,name),"w",encoding="utf-8").write(s)

def short(s,n): s=(s or "").strip(); return s if len(s)<=n else s[:n-1].rstrip()+"…"
def fmt(n): return f"{n/1000:.1f}k" if n>=10000 else str(n)

def languages(repos):
    tot={}
    for r in repos:
        for e in r["languages"]["edges"]: tot[e["node"]["name"]]=tot.get(e["node"]["name"],0)+e["size"]
    items=sorted(tot.items(),key=lambda kv:-kv[1]); s=sum(v for _,v in items) or 1
    top=items[:6]; other=sum(v for _,v in items[6:])
    out=[(n,v*100/s) for n,v in top]
    if other: out.append(("Other",other*100/s))
    return out

def build_stats(u):
    repos=u["repositories"]["nodes"]
    vals=[(fmt(sum(r["stargazerCount"] for r in repos)),"STARS",GOLD),(fmt(sum(r["forkCount"] for r in repos)),"FORKS",CYAN),
          (fmt(u["repositories"]["totalCount"]),"REPOS",PINK),(fmt(u["contributionsCollection"]["totalCommitContributions"]),"COMMITS",MINT)]
    st=[]
    for i,(v,l,c) in enumerate(vals):
        cx=125+i*250
        st.append(f'''<ellipse cx="{cx}" cy="82" rx="90" ry="34" fill="{c}" opacity=".14" filter="url(#soft)"><animate attributeName="opacity" values=".06;.22;.06" dur="{4+i}s" begin="{i*.6}s" repeatCount="indefinite"/></ellipse>
<text x="{cx}" y="92" text-anchor="middle" font-family="{FONT}" font-size="46" font-weight="800" fill="#fff">{esc(v)}<animate attributeName="opacity" values=".8;1;.8" dur="{3+i}s" repeatCount="indefinite"/></text>
<text x="{cx}" y="122" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="6" fill="{c}">{l}</text>
<line x1="{cx-40}" y1="136" x2="{cx+40}" y2="136" stroke="{c}" stroke-opacity=".6" stroke-width="2" stroke-dasharray="80" stroke-dashoffset="80"><animate attributeName="stroke-dashoffset" values="80;0;0;80" keyTimes="0;.3;.7;1" dur="5s" begin="{i*.5}s" repeatCount="indefinite"/></line>''')
    write("stats.svg",1000,170,f'<rect width="1000" height="170" fill="{NAVY}"/><line x1="40" y1="20" x2="960" y2="20" stroke="{BORDER}" stroke-opacity=".7"/><line x1="40" y1="150" x2="960" y2="150" stroke="{BORDER}" stroke-opacity=".7"/>{twinkles(16,1000,170,5)}{"".join(st)}')

def build_stack(u):
    items=languages(u["repositories"]["nodes"]) or [("No data",100)]
    x=40; seg=[]; tot=920-3*(len(items)-1)
    for i,(n,p) in enumerate(items):
        c=PALETTE[i%len(PALETTE)]; w_=tot*p/100
        seg.append(f'<rect x="{x:.1f}" y="62" height="10" width="0" fill="{c}"><animate attributeName="width" from="0" to="{w_:.1f}" dur="1.2s" begin="{i*.35:.2f}s" fill="freeze"/></rect>'); x+=w_+3
    leg=[]
    for i,(n,p) in enumerate(items):
        c=PALETTE[i%len(PALETTE)]; lx=40+(i%4)*230; ly=108+(i//4)*34
        leg.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".6s" begin="{.4+i*.2:.1f}s" fill="freeze"/><circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{c}"/><text x="{lx+18}" y="{ly}" font-family="{FONT}" font-size="14" font-weight="600" fill="#e6ecff">{esc(n)}</text><text x="{lx+112}" y="{ly}" font-family="{FONT}" font-size="12" fill="{DIM}">{p:.0f}%</text></g>')
    write("stack.svg",1000,200,f'''<rect width="1000" height="200" fill="{NAVY}"/>{twinkles(14,1000,200,31)}
<text x="40" y="40" font-family="{FONT}" font-size="13" font-weight="700" letter-spacing="6" fill="{CYAN}">STACK ANALYTICS</text>
<clipPath id="bar"><rect x="40" y="62" width="920" height="10" rx="5"/></clipPath>
<rect x="40" y="62" width="920" height="10" rx="5" fill="#141d52"/><g clip-path="url(#bar)">{"".join(seg)}
<rect x="-80" y="62" width="70" height="10" fill="#fff" opacity=".35"><animate attributeName="x" values="-80;1000" dur="4s" begin="3s" repeatCount="indefinite"/></rect></g>{"".join(leg)}''')

def build_chips(u):
    names=[n for n,_ in languages(u["repositories"]["nodes"]) if n!="Other"][:8] or ["GitHub"]
    pw=[len(n)*9.4+34 for n in names]; gap=12; x=(1000-(sum(pw)+gap*(len(names)-1)))/2; ch=[]
    for i,(n,w_) in enumerate(zip(names,pw)):
        c=PALETTE[i%len(PALETTE)]
        ch.append(f'''<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-4;0,0" dur="{3+i%3}s" begin="{i*.3:.1f}s" repeatCount="indefinite"/>
<rect x="{x:.0f}" y="26" width="{w_:.0f}" height="32" rx="16" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-opacity=".75"><animate attributeName="stroke-opacity" values=".35;1;.35" dur="{2.5+i%3}s" begin="{i*.25:.1f}s" repeatCount="indefinite"/></rect>
<text x="{x+w_/2:.0f}" y="47" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{c}">{esc(n)}</text></g>'''); x+=w_+gap
    write("chips.svg",1000,84,f'<rect width="1000" height="84" fill="{NAVY}"/>{twinkles(14,1000,84,12)}{"".join(ch)}')

def build_activity(u):
    cal=u["contributionsCollection"]["contributionCalendar"]; weeks=cal["weeks"][-46:]
    mx=max([d["contributionCount"] for w in weeks for d in w["contributionDays"]] or [1]) or 1
    lv=["#15215f","#1f3d92","#2f72dc",CYAN,"#ffffff"]; random.seed(4); cells=[]
    for c,w in enumerate(weeks):
        for r,d in enumerate(w["contributionDays"]):
            n=d["contributionCount"]; k=0 if n==0 else min(4,max(1,-(-n*4//mx)))
            x=40+c*20; y=70+r*20; an=""
            if k>=2 and random.random()<.5: an=f'<animate attributeName="opacity" values="1;.35;1" dur="{random.uniform(2,5):.1f}s" begin="{random.uniform(0,4):.1f}s" repeatCount="indefinite"/>'
            cells.append(f'<rect x="{x}" y="{y}" width="16" height="16" rx="3" fill="{lv[k]}">{an}</rect>')
    write("activity.svg",1000,250,f'''<rect width="1000" height="250" fill="{NAVY}"/>
<defs><linearGradient id="wave" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".45"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient><clipPath id="grid"><rect x="36" y="66" width="928" height="156" rx="6"/></clipPath></defs>
<text x="40" y="40" font-family="{FONT}" font-size="13" font-weight="700" letter-spacing="6" fill="{CYAN}">ACTIVITY PULSE</text>
<text x="960" y="40" text-anchor="end" font-family="{FONT}" font-size="12" font-weight="700" fill="{GOLD}">{cal["totalContributions"]} contributions</text>
{"".join(cells)}<g clip-path="url(#grid)"><rect x="-120" y="66" width="120" height="156" fill="url(#wave)"><animate attributeName="x" values="-120;1000" dur="6s" repeatCount="indefinite"/></rect></g>''')

def build_cards(u):
    cards=[r for r in u["pinnedItems"]["nodes"] if r][:3]
    if len(cards)<3:
        for r in u["repositories"]["nodes"]:
            if r["name"] not in [c["name"] for c in cards] and len(cards)<3: cards.append(r)
    urls=[]
    for i,r in enumerate(cards,1):
        lang=(r.get("primaryLanguage") or {}).get("name","—"); c=PALETTE[(i-1)%len(PALETTE)]
        urls.append(r["url"])
        write(f"project-{i}.svg",330,190,f'''<rect width="330" height="190" fill="{NAVY}"/>{twinkles(8,330,190,60+i)}
<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-5;0,0" dur="{4+i}s" begin="{i*.6:.1f}s" repeatCount="indefinite"/>
<rect x="10" y="14" width="310" height="160" rx="16" fill="{CARD}" stroke="{BORDER}" stroke-width="1.4"><animate attributeName="stroke" values="{BORDER};{c};{BORDER}" dur="{5+i}s" repeatCount="indefinite"/></rect>
<text x="28" y="52" font-family="{FONT}" font-size="19" font-weight="700" fill="#fff">{esc(short(r["name"],22))}</text>
<text x="300" y="50" text-anchor="end" font-family="{FONT}" font-size="18" fill="{c}">↗<animate attributeName="opacity" values=".4;1;.4" dur="2.5s" repeatCount="indefinite"/></text>
<text x="28" y="84" font-family="{FONT}" font-size="13" fill="{DIM}">{esc(short(r.get("description") or "No description yet",42))}</text>
<line x1="28" y1="116" x2="302" y2="116" stroke="{BORDER}" stroke-opacity=".7"/>
<circle cx="34" cy="143" r="5" fill="{c}"><animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/></circle>
<text x="46" y="148" font-family="{FONT}" font-size="12" font-weight="600" fill="#e6ecff">{esc(lang)}</text>
<text x="302" y="148" text-anchor="end" font-family="{FONT}" font-size="12" fill="{DIM}">stars {r["stargazerCount"]}  ·  forks {r["forkCount"]}</text></g>''')
    return urls

def patch_text(u, urls):
    p=os.path.join(ROOT,"README.md")
    if os.path.exists(p):
        t=open(p,encoding="utf-8").read()
        for i,url in enumerate(urls,1):
            t=re.sub(rf'<a href="[^"]*">(<img src="project-{i}\.svg")',lambda m:f'<a href="{url}">{m.group(1)}',t)
        t=t.replace("YOUR_USERNAME",u["login"]); open(p,"w",encoding="utf-8").write(t)
    p=os.path.join(ROOT,"header.svg")
    if os.path.exists(p):
        t=open(p,encoding="utf-8").read()
        t=t.replace("YOUR_USERNAME",u["login"]).replace("YOUR NAME",esc((u.get("name") or u["login"]).upper()))
        open(p,"w",encoding="utf-8").write(t)

if __name__=="__main__":
    if "--mock" in sys.argv: u=mock()
    else:
        tok,login=os.environ.get("GH_TOKEN"),os.environ.get("GH_USER")
        if not tok or not login: raise SystemExit("Set GH_TOKEN and GH_USER")
        u=fetch(login,tok)
    build_stats(u); build_stack(u); build_chips(u); build_activity(u); urls=build_cards(u); patch_text(u,urls)
    print("updated for",u["login"])
