import os
import re
import subprocess
import pathspec
import yaml # pip install PyYAML

import logging
logging.basicConfig(filename='backup.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s', encoding='utf-8')

def windows_to_cygwin_path(path):
    """ 将 Windows 风格的路径转换为 Cygwin 风格的路径 """
    if re.match(r'[a-zA-Z]:\\', path):
        drive = path[0].lower()
        return f'/cygdrive/{drive}' + path[2:].replace('\\', '/')
    return path

def load_gitignore_rules(gitignore_file_path):
    with open(gitignore_file_path, 'r', encoding='utf-8') as file:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', file)
    return spec


def apply_gitignore(root, dirs, files, spec, exclude_list, source_dir):
    # os.chdir(root)  # 切换到 .gitignore 文件所在目录
    # print(root, dirs)
    for name in dirs + files:
        full_path = os.path.join(root, name)
        # print("full_path", full_path)
        # 将完整路径转换为相对于源目录的路径
        relative_path_to_source = os.path.relpath(full_path, start=source_dir)
        # 将完整路径转换为相对于当前 .gitignore 文件所在目录的路径
        relative_path_to_gitignore = os.path.relpath(full_path, start=root)

        # 如果是目录，则在路径末尾添加斜杠
        if os.path.isdir(full_path):
            relative_path_to_gitignore += '/'
        is_ignored = spec.match_file(relative_path_to_gitignore)

        if is_ignored:
            exclude_list.add(windows_to_cygwin_path(relative_path_to_source).replace('\\', '/'))

            if name in dirs:
                dirs.remove(name)  # 从遍历列表中移除被忽略的目录


# Load the YAML configuration file
with open('config.yml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


def read_backup_list():
    source_dirs = config['paths']['source_dirs']
    dest_dir = config['paths']['dest_dir']

    # Now you can iterate over the source directories
    for source_dir in source_dirs:
        
        # Your backup logic here...
        if os.path.exists(source_dir):
            print(f"Backing up {source_dir} to {dest_dir}")
            rsync_backup(source_dir, dest_dir)
        else:
            print(f"Not Found {source_dir}")

def rsync_backup(source_dir, dest_dir):
    exclude_list = set()

    # 遍历 SOURCE_DIR
    for root, dirs, files in os.walk(source_dir):
        gitignore_path = os.path.join(root, '.gitignore')
        # print(gitignore_path)
        if os.path.isfile(gitignore_path):
            spec = load_gitignore_rules(gitignore_path)
            apply_gitignore(root, dirs, files, spec, exclude_list, source_dir)

    # 转换为 Cygwin 路径格式用于 rsync 命令
    cygwin_source_dir = windows_to_cygwin_path(source_dir)
    cygwin_dest_dir = windows_to_cygwin_path(dest_dir)

    # 构建 rsync 命令
    rsync_command = ["rsync", "-av"]

    if config['config']['delete']:
        rsync_command.append("--delete")

    for item in exclude_list:
        rsync_command.extend(["--exclude", item])
    rsync_command.extend([cygwin_source_dir, cygwin_dest_dir])

    print(rsync_command)
    logging.info('Executing command: %s', ' '.join(rsync_command))
    # 执行 rsync
    subprocess.run(rsync_command)

if __name__ == "__main__":
    read_backup_list()
