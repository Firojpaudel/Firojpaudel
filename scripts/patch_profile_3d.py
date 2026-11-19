import os
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

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


def patch_svg(filepath, dock_filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found, skipping.")
        return

    tree = ET.parse(filepath)
    root = tree.getroot()

    # 1. Update <svg> viewBox and height to cropped dimensions
    root.attrib["width"] = "1280"
    root.attrib["height"] = "735"
    root.attrib["viewBox"] = "0 115 1280 735"

    # 2. Update background <rect> dimensions and remove fill so it stays transparent
    for child in root:
        if child.tag.endswith("rect") and "fill-bg" in child.attrib.get("class", ""):
            child.attrib["x"] = "0"
            child.attrib["y"] = "115"
            child.attrib["width"] = "1280"
            child.attrib["height"] = "735"
            child.attrib["fill"] = "none"

    # 3. Locate radar chart, donut chart, stats footer, and date text
    radar_elem = None
    donut_elem = None
    footer_elem = None
    date_text_elem = None
    existing_dock = None

    for child in list(root):
        tag = child.tag.replace(f"{{{SVG_NS}}}", "")
        attrib = child.attrib
        trans = attrib.get("transform", "")

        if attrib.get("id") == "tech-stack-dock":
            existing_dock = child
            continue

        if tag == "g":
            # Radar chart: generated at (980, 284.5) or previously moved to (210, 640)
            if "980" in trans or "210, 640" in trans:
                radar_elem = child
            # Donut chart: generated at (40, 520)
            elif "520" in trans:
                donut_elem = child
            else:
                # Find the footer group with the date text
                for sub in child.iter():
                    if sub.tag.endswith("text") and sub.text and (" / " in sub.text or sub.text.startswith("202")):
                        date_text_elem = sub
                        footer_elem = child
                        break

    # 4. Move Radar Chart to bottom-left (x=210, y=640) so top-right is open for the tech dock
    if radar_elem is not None:
        radar_elem.attrib["transform"] = "translate(210, 640)"

    # 5. Remove the donut chart
    if donut_elem is not None:
        root.remove(donut_elem)

    # 6. Simplify footer: keep only the date string, positioned at bottom-right (y=830)
    if footer_elem is not None and date_text_elem is not None:
        root.remove(footer_elem)
        date_text_elem.attrib["x"] = "1260"
        date_text_elem.attrib["y"] = "830"
        date_text_elem.attrib["dominant-baseline"] = "auto"
        date_text_elem.attrib["text-anchor"] = "end"
        date_text_elem.attrib["class"] = "fill-weak"

        new_footer = ET.Element(f"{{{SVG_NS}}}g")
        new_footer.append(date_text_elem)
        root.append(new_footer)

    # 7. Remove existing dock if present, then inject fresh dock in top-right
    if existing_dock is not None:
        root.remove(existing_dock)

    with open(dock_filepath, "r", encoding="utf-8") as f:
        dock_elem = ET.fromstring(f.read().strip())
    root.append(dock_elem)

    # 8. Write back clean SVG
    tree.write(filepath, encoding="utf-8", xml_declaration=False)
    print(f"Successfully patched: {os.path.basename(filepath)}")


def main():
    print("Patching 3D contribution SVGs with custom layout and tech dock...")
    for filename, dock_path in TARGET_FILES.items():
        svg_path = os.path.join(PROFILE_DIR, filename)
        patch_svg(svg_path, dock_path)
    print("Done!")


if __name__ == "__main__":
    main()
