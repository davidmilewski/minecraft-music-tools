import os
import sys
import json
import shutil
import zipfile
import math
from datetime import datetime

WORKING_DIR = "ressourcepack"  # Working folder for resource packs

def ensure_working_dir():
    if not os.path.exists(WORKING_DIR):
        os.makedirs(WORKING_DIR)

def create_pack():
    ensure_working_dir()
    pack_name = input("Enter the new pack name: ").strip()
    if not pack_name:
        print("Pack name cannot be empty.")
        return
    description = input("Enter the pack description: ").strip()
    # Use pack format 46 as default.
    pack_format = 46

    pack_folder = os.path.join(WORKING_DIR, pack_name)
    if os.path.exists(pack_folder):
        print(f"A pack named '{pack_name}' already exists.")
        return

    # Create necessary folder structure:
    # pack_folder/
    #   pack.mcmeta
    #   assets/minecraft/sounds/
    os.makedirs(pack_folder)
    assets_sounds = os.path.join(pack_folder, "assets", "minecraft", "sounds")
    os.makedirs(assets_sounds, exist_ok=True)

    # Create pack.mcmeta file
    pack_mcmeta = {
        "pack": {
            "pack_format": pack_format,
            "description": description
        }
    }
    mcmeta_path = os.path.join(pack_folder, "pack.mcmeta")
    with open(mcmeta_path, "w", encoding="utf-8") as f:
        json.dump(pack_mcmeta, f, indent=4)
    print(f"Created new resource pack '{pack_name}' in '{pack_folder}'.")
    print("Folder structure has been set up. You can now add your sound files to:")
    print(f"  {assets_sounds}")
    print("An empty sounds.json file will also be created for you to edit later.")
    # Create an empty sounds.json
    sounds_json_path = os.path.join(pack_folder, "assets", "minecraft", "sounds.json")
    with open(sounds_json_path, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)
    print("pack.mcmeta and sounds.json have been created.")

def list_existing_packs():
    ensure_working_dir()
    packs = [d for d in os.listdir(WORKING_DIR) if os.path.isdir(os.path.join(WORKING_DIR, d))]
    if not packs:
        print("No resource packs found in the working folder.")
        return []
    print("Existing resource packs:")
    for i, pack in enumerate(packs, start=1):
        print(f"  {i}. {pack}")
    return packs

def select_pack():
    packs = list_existing_packs()
    if not packs:
        return None
    try:
        choice = int(input("Enter the number of the pack to select: "))
        if 1 <= choice <= len(packs):
            return os.path.join(WORKING_DIR, packs[choice - 1])
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Please enter a valid number.")
        return None

def update_sounds_json(pack_folder):
    """
    Recursively scan the pack's assets/minecraft/sounds folder for .ogg files,
    clear the existing sounds.json file, and add new entries so that for a file located at
      assets/minecraft/sounds/world1/mycelium/full/mycelium1.ogg
    the sounds.json entry is:
      "world1/mycelium/full/mycelium1": { "sounds": ["mycelium1"] }
    That is, the key is the full relative path (without extension, using forward slashes)
    and the "sounds" array contains only the base file name.
    """
    sounds_folder = os.path.join(pack_folder, "assets", "minecraft", "sounds")
    if not os.path.exists(sounds_folder):
        print("No sounds folder found in this pack. Please ensure the structure is correct.")
        return

    sound_entries = {}
    # Walk through the sounds folder recursively
    for root, dirs, files in os.walk(sounds_folder):
        for file in files:
            if file.lower().endswith(".ogg"):
                full_path = os.path.join(root, file)
                # Compute the relative path from the sounds folder.
                rel_path = os.path.relpath(full_path, sounds_folder)  # e.g., "world1/mycelium/full/mycelium1.ogg"
                # Remove the file extension.
                base_path = os.path.splitext(rel_path)[0]  # e.g., "world1/mycelium/full/mycelium1"
                # Convert OS-specific separators to forward slashes.
                key = base_path.replace(os.sep, "/")
                # Extract the base file name (without any path)
                base_name = os.path.splitext(file)[0]
                # The "sounds" array now contains only the base file name.
                sound_entries[base_name] = {
                    "sounds": [key]
                }
    sounds_json_path = os.path.join(pack_folder, "assets", "minecraft", "sounds.json")
    # Clear any existing entries and update with our found entries.
    with open(sounds_json_path, "w", encoding="utf-8") as f:
        json.dump(sound_entries, f, indent=4)
    print(f"Cleared and updated sounds.json with {len(sound_entries)} sound entr{'y' if len(sound_entries)==1 else 'ies'}.")

def compress_pack():
    pack_folder = select_pack()
    if not pack_folder:
        return
    pack_name = os.path.basename(pack_folder)
    zip_filename = f"{pack_name}.zip"
    zip_path = os.path.join(WORKING_DIR, zip_filename)
    print(f"Compressing '{pack_name}' into '{zip_path}' with high compression...")
    # Create ZIP with high compression.
    # Instead of zipping the entire pack folder (which would put a top-level folder in the ZIP),
    # we zip the contents of the pack folder.
    try:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for root, dirs, files in os.walk(pack_folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Set archive name relative to the pack_folder so that the ZIP does not contain an extra folder.
                    arcname = os.path.relpath(full_path, pack_folder)
                    zipf.write(full_path, arcname)
        print(f"Pack compressed successfully into '{zip_path}'.")
    except Exception as e:
        print("Error compressing the pack:", e)

def main():
    print("Minecraft Resource Pack Automation Tool")
    print("---------------------------------------")
    print("1. Create a new pack")
    print("2. Edit an existing pack (update sounds.json)")
    print("3. Compress a pack")
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    if choice == "1":
        create_pack()
    elif choice == "2":
        pack_folder = select_pack()
        if pack_folder:
            update_sounds_json(pack_folder)
    elif choice == "3":
        compress_pack()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
