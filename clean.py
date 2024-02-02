import re
import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i",
               "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")


TRANS = {}

images = list()
videos = list()
documents = list()
music = list()
folders = list()
archives = list()
others = list()
unknown = set()
extensions = set()


registered_extensions = {
    'JPEG': images,
    'JPG': images,
    'PNG': images,
    'SVG': images,
    'AVI': videos,
    'MP4': videos,
    'MOV': videos,
    'MKV': videos,
    'DOC': documents,
    'DOCX': documents,
    'TXT': documents,
    'PDF': documents,
    'XLSX': documents,
    'PPTX': documents,
    'MP3': music,
    'OGG': music,
    'WAV': music,
    'AMR': music,
    'ZIP': archives,
    'GZ': archives,
    'TAR': archives
}

for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name):
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', "_", new_name)
    return f"{new_name}.{'.'.join(extension)}"


def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'music', 'documents', 'videos', 'images'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)
   


def handle_file(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))


def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name.replace(
        ".zip", "").replace(".gz", "").replace(".tar", ""))

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()),
                              str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return

    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def get_folder_objects(root_path):
    for folder in root_path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
            try:
                folder.rmdir()
            except OSError:
                pass

def process_files(files, folder_path, destination):
    for file in files:
        handle_file(file, folder_path, destination)

def process_archives(archives, folder_path, destination):
    for archive in archives:
        handle_archive(archive, folder_path, destination)

def main():
    path = sys.argv[1]
    print(f"Start in {path}")
    folder_path = Path(path)
    scan(folder_path)

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Передача роботи для обробки файлів в окремому потоці
        executor.submit(process_files, images, folder_path, "images")
        executor.submit(process_files, videos, folder_path, "videos")
        executor.submit(process_files, documents, folder_path, "documents")
        executor.submit(process_files, music, folder_path, "music")
        executor.submit(process_files, others, folder_path, "others")

        # Передача роботи для обробки архівів в окремому потоці
        executor.submit(process_archives, archives, folder_path, "archives")

    get_folder_objects(folder_path)

if __name__ == '__main__':
    main()


