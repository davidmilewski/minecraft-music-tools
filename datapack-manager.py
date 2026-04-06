import os
import json
import re
import shutil  # for removing existing directories


# Ensures the main datapack folder exists
def ensure_datapack_folder():
    if not os.path.exists('datapack'):
        os.makedirs('datapack')


# Creates a new datapack based on user inputs
def create_datapack():
    name = input('Enter datapack name: ').strip()
    version = input('Enter datapack version (default 46): ').strip() or '46'
    description = input('Enter datapack description: ').strip()

    pack_folder = os.path.join('datapack', name)
    data_folder = os.path.join(pack_folder, 'data')

    # Check if datapack already exists
    if os.path.exists(pack_folder):
        print('Datapack already exists!')
        return

    os.makedirs(data_folder)

    pack_mcmeta = {
        "pack": {
            "pack_format": int(version),
            "description": description
        }
    }

    # Write the pack.mcmeta file
    with open(os.path.join(pack_folder, 'pack.mcmeta'), 'w') as f:
        json.dump(pack_mcmeta, f, indent=4)

    print(f'Datapack \"{name}\" created successfully.')


# Lists existing datapacks
def list_datapacks():
    ensure_datapack_folder()
    packs = [name for name in os.listdir('datapack') if os.path.isdir(os.path.join('datapack', name))]
    if not packs:
        print('No datapacks found.')
        return []

    print('Available datapacks:')
    for i, pack in enumerate(packs, 1):
        print(f'{i}. {pack}')
    return packs


def natural_sort_key(s: str):
    """
    Splits the string into alphanumeric chunks, converting numeric parts
    to integers so they sort in true numerical order (e.g. 1,2,10,11).
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s) if text]


# Generates mcfunction files based on .ogg files in the output folder
def generate_mcfunction_files(datapack_folder, song_folder_name, delay):
    # Points to the external output folder, where .ogg files live
    output_folder = os.path.join('output', song_folder_name)
    namespace_folder = os.path.join(datapack_folder, 'data', song_folder_name, 'function')

    # If this folder already exists, remove it before recreating
    if os.path.exists(namespace_folder):
        shutil.rmtree(namespace_folder)

    # Recreate the folder and subfolders (full, fadein, fadeout)
    for subfolder in ['full', 'fadein', 'fadeout']:
        os.makedirs(os.path.join(namespace_folder, subfolder), exist_ok=True)

    # We'll only create .mcfunction files for .ogg files in the "full" folder
    full_folder = os.path.join(output_folder, 'full')
    ogg_files = [f for f in os.listdir(full_folder) if f.endswith('.ogg')]
    ogg_files.sort(key=natural_sort_key)

    # Iterate over each .ogg file in a natural sorted order
    for idx, ogg_file in enumerate(ogg_files):
        mcfunction_path = os.path.join(namespace_folder, 'full', f'{idx}.mcfunction')

        with open(mcfunction_path, 'w') as file:
            # Conditional scoreboard check + playsound
            file.write(
                f'execute as @a at @s if score YesNo ambienceToggle matches 1 run '
                f'playsound minecraft:{ogg_file[:-4]} ambient @s ~ ~ ~ 1 1 1\n'
            )

            # If this is NOT the last segment, schedule the next function
            if idx + 1 < len(ogg_files):
                next_segment = f'{idx + 1}'
                file.write(
                    f'execute if score YesNo ambienceToggle matches 1 run '
                    f'schedule function {song_folder_name}:full/{next_segment} {delay}s\n'
                )

            # Simple tellraw message
            file.write(
                f'tellraw @a[tag=dbg,tag=music] ["[AmbienceDebug] Now playing {ogg_file}"]\n'
            )


# Select and work on an existing datapack
def select_datapack():
    packs = list_datapacks()
    if not packs:
        return

    try:
        pack_choice = int(input('Select a datapack by number: '))
        if 1 <= pack_choice <= len(packs):
            selected_pack = packs[pack_choice - 1]

            # Look for available song folders in the 'output' directory
            song_folders = [
                name for name in os.listdir('output')
                if os.path.isdir(os.path.join('output', name))
            ]
            if not song_folders:
                print('No song folders found in output.')
                return

            print('Available song folders:')
            for i, folder in enumerate(song_folders, 1):
                print(f'{i}. {folder}')

            song_choice = int(input('Select a song folder by number: '))
            if 1 <= song_choice <= len(song_folders):
                selected_song = song_folders[song_choice - 1]
                delay = input('Enter delay between segments (default 12): ').strip() or '12'

                # Generate the .mcfunction files
                generate_mcfunction_files(
                    os.path.join('datapack', selected_pack),
                    selected_song,
                    delay
                )

                print('Mcfunction files generated successfully.')
            else:
                print('Invalid song selection.')
        else:
            print('Invalid datapack selection.')
    except ValueError:
        print('Please enter a valid number.')


# Main loop for user interaction
def main():
    ensure_datapack_folder()

    while True:
        print('\nMinecraft Datapack Manager')
        print('1. Create new datapack')
        print('2. Select existing datapack to work on')
        print('3. Exit')

        option = input('Choose an option: ').strip()

        if option == '1':
            create_datapack()
        elif option == '2':
            select_datapack()
        elif option == '3':
            print('Exiting.')
            break
        else:
            print('Invalid option, please try again.')


if __name__ == '__main__':
    main()
