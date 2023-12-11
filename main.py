import os
import re
import subprocess
import pathspec

def windows_to_cygwin_path(path):
    """ 将 Windows 风格的路径转换为 Cygwin 风格的路径 """
    if re.match(r'[a-zA-Z]:\\', path):
        drive = path[0].lower()
        return f'/cygdrive/{drive}' + path[2:].replace('\\', '/')
    return path

def load_gitignore_rules(gitignore_file_path):
    with open(gitignore_file_path, 'r', encoding='utf-8') as file:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', file)

    # 打印 spec 中的规则的字符串表示
    print("Loaded .gitignore rules from", gitignore_file_path)
    for pattern in spec.patterns:
        print("  Rule:", pattern.pattern)

    return spec



def apply_gitignore(root, dirs, files, spec, exclude_list, source_dir):
    # os.chdir(root)  # 切换到 .gitignore 文件所在目录
    print(root, dirs)
    for name in dirs + files:
        full_path = os.path.join(root, name)
        print("full_path", full_path)
        # 将完整路径转换为相对于源目录的路径
        relative_path_to_source = os.path.relpath(full_path, start=source_dir)
        # 将完整路径转换为相对于当前 .gitignore 文件所在目录的路径
        relative_path_to_gitignore = os.path.relpath(full_path, start=root)
        print("relative_path_to_source", relative_path_to_source, spec.match_file(relative_path_to_source))
        print("relative_path_to_gitignore", relative_path_to_gitignore, spec.match_file(relative_path_to_gitignore + '/'))
        # relative_path_to_gitignore_unix = relative_path_to_gitignore.replace('\\', '/')

        # 如果是目录，则在路径末尾添加斜杠
        if os.path.isdir(full_path):
            relative_path_to_gitignore += '/'
        is_ignored = spec.match_file(relative_path_to_gitignore)

        
        # print("relative_path_to_gitignore_unix", relative_path_to_gitignore_unix, spec.match_file(relative_path_to_gitignore_unix))

        # 使用相对于 .gitignore 文件的路径进行匹配
        # is_ignored = spec.match_file(relative_path_to_gitignore)
        # print()
        if is_ignored:
            exclude_list.add(windows_to_cygwin_path(relative_path_to_source).replace('\\', '/'))

            if name in dirs:
                dirs.remove(name)  # 从遍历列表中移除被忽略的目录

# def apply_gitignore(root, dirs, files, spec, exclude_list, source_dir):
#     for name in dirs + files:
#         full_path = os.path.join(root, name)
#         relative_path_to_source = os.path.relpath(full_path, start=source_dir).replace('\\', '/')
#         relative_path_to_gitignore = os.path.relpath(full_path, start=root).replace('\\', '/')
#         print(relative_path_to_gitignore, spec.match_file(relative_path_to_gitignore))
#         is_ignored = spec.match_file(relative_path_to_gitignore)
#         if is_ignored:
#             exclude_list.add(relative_path_to_source)





def main():
    # 使用 Windows 路径格式
    source_dir = "C:\\happen\\code\\模拟备份"
    dest_dir = "C:\\happen\\code\\备份"
    
    exclude_list = set()

    # 遍历 SOURCE_DIR
    for root, dirs, files in os.walk(source_dir):
        gitignore_path = os.path.join(root, '.gitignore')
        # print(gitignore_path)
        if os.path.isfile(gitignore_path):
            # 让python切换到gitignore_path所在的目录
            

            spec = load_gitignore_rules(gitignore_path)
            # print(spec)
            
            apply_gitignore(root, dirs, files, spec, exclude_list, source_dir)


    # 转换为 Cygwin 路径格式用于 rsync 命令
    cygwin_source_dir = windows_to_cygwin_path(source_dir)
    cygwin_dest_dir = windows_to_cygwin_path(dest_dir)

    # 构建 rsync 命令
    rsync_command = ["rsync", "-av"]
    for item in exclude_list:
        rsync_command.extend(["--exclude", item])
    rsync_command.extend([cygwin_source_dir, cygwin_dest_dir])

    print(rsync_command)
    # 执行 rsync
    subprocess.run(rsync_command)

if __name__ == "__main__":
    main()