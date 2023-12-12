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

def check_rsync_available():
    try:
        # 尝试执行 'rsync --version'
        subprocess.run(["rsync", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 'rsync' 命令执行失败或未找到
        return False

# 检查 'rsync' 是否可用
if not check_rsync_available():
    print("错误：未找到 'rsync' 命令。请确保 'rsync' 已安装并在 PATH 中。")
    logging.error("错误：未找到 'rsync' 命令。请确保 'rsync' 已安装并在 PATH 中。")
    input("按回车键退出程序。")
    exit(1)

# 检查配置文件是否存在
if not os.path.exists('config.yml'):
    print(f"错误：配置文件 '{'config.yml'}' 不存在。请确保配置文件位于正确的位置。")
    logging.error(f"错误：配置文件 '{'config.yml'}' 不存在。请确保配置文件位于正确的位置。")
    input("按回车键退出程序。")
    exit(1)  # 终止程序

# Load the YAML configuration file
with open('config.yml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

def confirm_deletion(dest_dir):
    confirmation = input(f"您将要执行包含 --delete 的 rsync 命令，这可能会删除 {dest_dir} 目录中的文件。请输入 'yes' 来确认: ")
    return confirmation == 'yes'


def read_backup_list():
    source_dirs = config['paths']['source_dirs']
    dest_dir = config['paths']['dest_dir']

    # 在调用 rsync 命令之前
    if config['config']['delete'] and not confirm_deletion(dest_dir):
        print("操作已取消。")
        return

    # Now you can iterate over the source directories
    for source_dir in source_dirs:
        
        # Your backup logic here...
        if os.path.exists(source_dir) and os.path.isdir(dest_dir):
            print(f"Backing up {source_dir} to {dest_dir}")
            rsync_backup(source_dir, dest_dir)
        else:
            print(f"Not Found {source_dir} or {dest_dir}")
            logging.error(f"请确保两个目录都存在 {source_dir} or {dest_dir}")
            input("按回车键退出程序。")



def rsync_backup(source_dir, dest_dir):
    exclude_list = set()
    print("正在计算 .gitignore 中需要排除的文件")
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
    rsync_command = ["rsync", "-avh"]
    if config['config']['progress']:
        rsync_command.append("--progress")
    if config['config']['delete']:
        rsync_command.append("--delete")

    for item in exclude_list:
        rsync_command.extend(["--exclude", item])
    rsync_command.extend([cygwin_source_dir, cygwin_dest_dir])
    print(f"排除了{len(exclude_list)}个文件或文件夹")
    # print(rsync_command)
    logging.info('Executing command: %s', ' '.join(rsync_command))
    # 执行 rsync
    subprocess.run(rsync_command)

if __name__ == "__main__":
    read_backup_list()
