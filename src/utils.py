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

def append_file(contents, target_file):
    # 打开源文件和目标文件
    with open(target_file, 'a') as target:
        target.write(contents)
    target.close()

def check_string_in_file(file_path, target_string):
    # 打开文件并读取内容
    with open(file_path, 'r') as file:
        content = file.read()
        # 搜索目标字符串
        if target_string not in content:
            return False
        else:
            return True
    file.close()