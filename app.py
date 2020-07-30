import dhash
from PIL import Image
import os
import shutil
import subprocess


PATH_BACKUP = os.environ['PATH_CRYPTED']
PATH_LOCAL = os.environ['PATH_LOCAL']
VERA_CRYPT = r"C:\Program Files\VeraCrypt\VeraCrypt.exe"
VDISK = r"E:\drive.vhdx"

vc_password = os.environ['VC_PASSWORD']
mount = r" /v \Device\Harddisk3\Partition1" + " /l W" + f" /p {vc_password}" + " /q"
dismount = " /d W" + " /q"

IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']


def create_folder_list(directory):
    return [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]


def create_recursive_folder_list(directory):
    folder_list = create_folder_list(directory)
    for folder in folder_list:
        path = (directory, *folder) if isinstance(folder, tuple) else (directory, folder)
        sub_folders = [(folder, sub_folder) for sub_folder in create_folder_list(os.path.join(*path))]
        if sub_folders:
            folder_list += sub_folders

    return [os.path.join(*folder) if isinstance(folder, tuple) else os.path.join(folder) for folder in folder_list]


def check_if_image(file):
    return os.path.splitext(file)[1] in IMAGE_FORMATS


def create_file_list(directory, only_images=True):
    return [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))
            and (check_if_image(os.path.join(directory, file)) or not only_images)]


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_image_hash(image_file):
    try:
        image = Image.open(image_file)
        row, col = dhash.dhash_row_col(image, size=12)
        image_hash = dhash.format_hex(row, col, size=12)
        return image_hash
    except OSError:
        print(f"Could not read image {image_file}")


def check_folder_for_duplicates(folder):
    print("Checking {}".format(folder))
    full_path = os.path.join(PATH_LOCAL, folder)
    files = create_file_list(full_path)
    print("\n   {} files found".format(len(files)))
    file_hashes = []
    duplicates = 0
    for file_num, file in enumerate(files):
        if file == 'Thumbs.db':
            pass
        else:
            print(f"   Checking file [{file_num+1}/{len(files)}]", end="\r")
            image_hash = get_image_hash(os.path.join(full_path, file))
            if image_hash:
                if image_hash in file_hashes:
                    print(f'\n   Found duplicate file {file}')
                    os.remove(os.path.join(full_path, file))
                    duplicates += 1
                else:
                    file_hashes.append(image_hash)
    print(f"\n{duplicates} duplicates deleted")
    print("=~" * 20)


def check_all_folders_for_duplicates():
    for folder in create_recursive_folder_list(PATH_LOCAL):
        check_folder_for_duplicates(folder)


def sync_folder(folder):
    print("Syncing {}".format(folder))
    full_local_path = os.path.join(PATH_LOCAL, folder)
    local_files = create_file_list(full_local_path, only_images=False)
    print("\n   {} local files found".format(len(local_files)))
    full_backup_path = os.path.join(PATH_BACKUP, folder)
    if not os.path.exists(full_backup_path):
        print("\n Backup folder not found, creating...")
        os.makedirs(full_backup_path)
    backup_files = create_file_list(full_backup_path, only_images=False)
    print("\n   {} backup files found".format(len(backup_files)))
    new_files = 0

    def copy_file_to_backup(f, new_file_name=None):
        print(f"\n   {f} not found in backup")
        shutil.copyfile(os.path.join(full_local_path, f), os.path.join(full_backup_path, new_file_name if new_file_name else f))
        return 1

    for file_num, file in enumerate(local_files):
        if file == 'Thumbs.db':
            pass
        else:
            print(f"   Checking file [{file_num}/{len(local_files)}]", end="\r")
            name, ext = os.path.splitext(os.path.join(full_local_path, file))
            if check_if_image(os.path.join(full_local_path, file)):
                image_hash = get_image_hash(os.path.join(full_local_path, file))
                if image_hash:
                    if image_hash + ext not in backup_files:
                        new_files += copy_file_to_backup(file, image_hash + ext)
                else:
                    if file not in backup_files:
                        new_files += copy_file_to_backup(file)
            else:
                if file not in backup_files:
                    new_files += copy_file_to_backup(file)
    print(f"\n{new_files} new files copied")
    print("=~" * 20)


def sync_all_folders():
    for folder in create_recursive_folder_list(PATH_LOCAL):
        sync_folder(folder)


def mount_vdisk():
    subprocess.run("mount_vdisk.bat {}".format(VDISK), shell=True)


def dismount_vdisk():
    subprocess.run("dismount_vdisk.bat {}".format(VDISK), shell=True)


def mount_veracrypt_volume():
    subprocess.run(VERA_CRYPT + mount)


def dismount_veracrypt_volume():
    subprocess.run(VERA_CRYPT + dismount)


def mount_backup():
    print("Starting mounting backup...")
    print("Mounting virtual hard drive...")
    mount_vdisk()
    print("Mounting VeraCrypt volume...")
    mount_veracrypt_volume()
    print("Backup mounted")


def dismount_backup():
    print("Dismounting VeraCrypt volume...")
    dismount_veracrypt_volume()
    print("Dismounting virtual hard drive...")
    dismount_vdisk()
    print("Backup dismounted")


if __name__ == "__main__":
    print("Check for image duplicates? (y/n)")
    if input().lower() == 'y':
        check_all_folders_for_duplicates()
    print("Start backup? (y/n)")
    if input().lower() == 'y':
        mount_backup()
        sync_all_folders()
        dismount_backup()
    else:
        exit()
