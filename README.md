# RsyncGitIgnore 备份工具

## 介绍
RsyncGitIgnore 是一个自动化备份工具，结合了 `rsync` 的强大功能和对 `git` 忽略文件的支持。它能够从 YAML 配置文件中读取源目录列表，并根据 `.gitignore` 文件中的规则将这些目录备份到指定的目标目录，可以包含多个子目录，如果子目录中有 `.gitignore` 也会正常生效。

## 需求
- Python 3.x
- PyYAML
- rsync（需要在系统环境中安装）

## 安装
1. 确保您的系统中已安装 Python 和 rsync。
2. 安装 PyYAML 库：

   ```bash
   pip install PyYAML
   ```

## 配置
创建一个名为 `config.yml` 的 YAML 文件，内容如下：

```yaml
paths:
  source_dirs:
    - path/to/first/source
    - path/to/second/source
    - path/to/third/source
  dest_dir: path/to/destination
```

将 `path/to/...` 替换为实际的源目录和目标目录路径。

## 使用
使用以下命令运行程序：

```bash
python main.py
```

程序将读取 `config.yml` 文件，并根据任何文件夹下 `.gitignore` 文件中的规则将源目录备份到目标目录。

![https://raw.githubusercontent.com/glwhappen/images/main/img/202312120121921.png]