import os
import shutil
import re
import urllib.request

def get_current_streak(username="Firojpaudel"):
    url = f"https://github-readme-streak-stats-sigma-two.vercel.app?user={username}&theme=merko&hide_border=true&card_height=175&exclude_days=Sat"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
        idx = content.find("Current Streak big number")
        if idx != -1:
            snippet = content[idx:idx + 500]
            m = re.search(r'>\s*(\d+)\s*<', snippet)
            if m:
                return int(m.group(1))
    except Exception as e:
        print("Error fetching streak:", e)
    return 1  # Default to active on failure

def main():
    username = os.environ.get("GITHUB_REPOSITORY_OWNER", "Firojpaudel")
    streak = get_current_streak(username)
    print(f"Current detected streak for {username}: {streak}")

    src = "assets/sama_streaks.gif" if streak > 0 else "assets/sama_popcorn.gif"
    dst = "assets/current_streak_avatar.gif"

    # Only copy if file changed or does not exist
    if not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read():
        shutil.copyfile(src, dst)
        print(f"Updated {dst} -> {src}")
    else:
        print(f"No change needed ({src} is already active).")

if __name__ == "__main__":
    main()
