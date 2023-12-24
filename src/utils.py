import os
import getpass

def get_shell_type():
    shell = os.environ.get('SHELL')
    
    if shell:
        if 'fish' in shell:
            return 'Fish'
        elif 'zsh' in shell:
            return 'Zsh'
        elif 'bash' in shell:
            return 'Bash'
    
    return 'Unknown'

def get_curr_username():
    return getpass.getuser()

def append_file(source_file, target_file):
    # 打开源文件和目标文件
    with open(source_file, 'r') as source, open(target_file, 'a') as target:
        # 读取源文件的内容
        content = source.read()
        
        # 将源文件的内容追加到目标文件的末尾
        target.write(content)
        
    # 关闭源文件和目标文件
    source.close()
    target.close()

# 指定源文件和目标文件的路径
source_file_path = 'path/to/source/file.txt'
target_file_path = 'path/to/target/file.txt'