import dhash
from PIL import Image
import os
import shutil
import subprocess


PATH_BACKUP = os.environ['PATH_CRYPTED']
PATH_LOCAL = os.environ['PATH_LOCAL']
VERA_CRYPT = r"C:\Program Files\VeraCrypt\VeraCrypt.exe"

vc_password = os.environ['VC_PASSWORD']
mount = r" /v \Device\Harddisk3\Partition1" + " /l W" + f" /p {vc_password}" + " /q"
dismount = " /d W" + " /q"


def create_file_list(directory):
    return [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_image_hash(image_file):
    image = Image.open(image_file)
    row, col = dhash.dhash_row_col(image)
    image_hash = dhash.format_hex(row, col)
    return image_hash


def check_directory_for_duplicates(directory):
    files = create_file_list(directory)
    file_hashes = []
    duplicates = 0
    for file_num, file in enumerate(files):
        if file == 'Thumbs.db':
            pass
        else:
            print(f"Checking file [{file_num}/{len(files)}]")
            image_hash = get_image_hash(os.path.join(directory, file))
            if image_hash in file_hashes:
                print(f'Found duplicate file {file}')
                os.remove(os.path.join(directory, file))
                duplicates += 1
            else:
                file_hashes.append(image_hash)
        cls()
        print(f"{duplicates} duplicates deleted")


def compare_directories(local_directory, backup_directory):
    local_files = create_file_list(local_directory)
    backup_files = create_file_list(backup_directory)
    new_files = 0
    for file_num, file in enumerate(local_files):
        if file == 'Thumbs.db':
            pass
        else:
            print(f"Checking file [{file_num}/{len(local_files)}]")
            name, ext = os.path.splitext(os.path.join(local_directory, file))
            image_hash = get_image_hash(os.path.join(local_directory, file))
            if image_hash + ext not in backup_files:
                print(f"{file} not found in backup")
                shutil.copyfile(os.path.join(local_directory, file), os.path.join(backup_directory, image_hash + ext))
                new_files += 1
        cls()
        print(f"{new_files} new files copied")


def mount_backup():
    subprocess.run(VERA_CRYPT + mount)
    print("Backup mounted")


def dismount_backup():
    subprocess.run(VERA_CRYPT + dismount)
    print("Backup dismounted")


if __name__ == "__main__":
    print("Check for duplicates? (y/n)")
    if input().lower() == 'y':
        check_directory_for_duplicates(PATH_LOCAL)
    print("Start backup? (y/n)")
    if input().lower() == 'y':
        mount_backup()
        compare_directories(PATH_LOCAL, PATH_BACKUP)
        dismount_backup()
    else:
        exit()
