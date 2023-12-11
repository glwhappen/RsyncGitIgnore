import os
import subprocess
import pathspec

def load_gitignore_rules(gitignore_file_path):
    with open(gitignore_file_path, 'r') as file:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', file)
    return spec

def apply_gitignore(root, dirs, files, spec, exclude_list):
    for name in dirs + files:
        if spec.match_file(os.path.join(root, name)):
            exclude_list.add(f'/{os.path.relpath(os.path.join(root, name), start=root)}')
            if name in dirs:
                dirs.remove(name)  # 从遍历列表中移除被忽略的目录

def main():
    source_dir = "/path/to/source"  # 设置你的源目录
    dest_dir = "/path/to/destination"  # 设置你的目标目录
    exclude_list = set()

    # 遍历 SOURCE_DIR
    for root, dirs, files in os.walk(source_dir):
        gitignore_path = os.path.join(root, '.gitignore')
        if os.path.isfile(gitignore_path):
            spec = load_gitignore_rules(gitignore_path)
            apply_gitignore(root, dirs, files, spec, exclude_list)

    # 构建 rsync 命令
    rsync_command = ["rsync", "-av"]
    for item in exclude_list:
        rsync_command.extend(["--exclude", item])
    rsync_command.extend([source_dir, dest_dir])

    # 执行 rsync
    subprocess.run(rsync_command)

if __name__ == "__main__":
    main()
