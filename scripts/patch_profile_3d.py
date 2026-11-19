import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_DIR = os.path.join(REPO_ROOT, "profile-3d-contrib")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

DARK_DOCK_PATH = os.path.join(ASSETS_DIR, "dock-dark.xml")
LIGHT_DOCK_PATH = os.path.join(ASSETS_DIR, "dock-light.xml")

TARGET_FILES = {
    "firoj-dark.svg": DARK_DOCK_PATH,
    "firoj-dark-lime.svg": DARK_DOCK_PATH,
    "firoj-light.svg": LIGHT_DOCK_PATH,
}


def load_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def save_file(filepath, content):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def patch_svg(filepath, dock_filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found, skipping.")
        return

    content = load_file(filepath)
    dock_xml = load_file(dock_filepath).strip()

    # If dock is already present, remove it first so we can cleanly re-inject
    content = re.sub(r'<g id="tech-stack-dock">.*?</g>\s*(?=</svg>)', "", content, flags=re.DOTALL)

    # 1. Update <svg ...> tag to cropped viewBox starting at y=115, height=735
    content = re.sub(
        r'<svg\s+xmlns="http://www.w3.org/2000/svg"\s+width="1280"\s+height="\d+"\s+viewBox="[^"]+">',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="735" viewBox="0 115 1280 735">',
        content,
    )

    # 2. Update background <rect> to match the new cropped dimensions
    content = re.sub(
        r'<rect x="0" y="\d+" width="1280" height="\d+" class="fill-bg"[^>]*></rect>',
        '<rect x="0" y="115" width="1280" height="735" class="fill-bg" fill="none"></rect>',
        content,
    )

    # 3. Move date text from top (y=20, which is cropped out) to bottom right footer (y=830)
    content = re.sub(
        r'<text style="font-size: 16px;" x="1260" y="20" dominant-baseline="hanging" text-anchor="end" class="fill-weak">([^<]+)</text>',
        r'<text style="font-size: 16px;" x="1260" y="830" dominant-baseline="auto" text-anchor="end" class="fill-weak">\1</text>',
        content,
    )

    # 4. Inject dock before </svg>
    svg_close_idx = content.rfind("</svg>")
    if svg_close_idx != -1:
        content = content[:svg_close_idx] + dock_xml + "\n</svg>"
    else:
        print(f"Warning: </svg> closing tag not found in {filepath}!")

    save_file(filepath, content)
    print(f"Successfully patched: {os.path.basename(filepath)}")


def main():
    print("Patching 3D contribution SVGs with custom tech dock...")
    for filename, dock_path in TARGET_FILES.items():
        svg_path = os.path.join(PROFILE_DIR, filename)
        patch_svg(svg_path, dock_path)
    print("Done!")


if __name__ == "__main__":
    main()
