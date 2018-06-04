from os import path, makedirs, getcwd, environ, listdir
from subprocess import check_call, check_output

x = 1

share_folder = path.join(environ.get('HOME'), 'KIVY_VM')  # shared folder with Kivy/Buildozer VM
base_path = path.join(share_folder, 'machinewerkz-kivy')

excluded_files = [
    'pre_build.py',
    'machinewerkz.ini',
    'screenshot.png',
    'screenshot-thumb.png',
    'README.md',
    'packages'
]

include_exts = [_.strip() for _ in check_output(
    ['grep', 'source.include_exts', 'buildozer.spec']
).strip().split('=')[1].split(',')]

include_exts.append('spec')

user_input = raw_input("Delete before building [{}] ? (Y/N)".format(share_folder))

if user_input in ["Y", "y"]:
    print('deleting', share_folder)
    x = check_call(["rm", "-rf", share_folder])
    print('creating new', share_folder)
    makedirs(base_path)

cmd = ['cp', '-rp', path.join(getcwd(), 'data'), base_path]
print(cmd)
result = check_call(cmd)
if result == 0:
    print('copied ./data/*')

included_files = [_ for _ in listdir(getcwd()) if (_ not in excluded_files) and (_.split('.')[-1] in include_exts)]

for cmd in [['cp', _, base_path] for _ in included_files]:
    result = check_call(cmd)
    if result != 0:
        print('[ERROR]', cmd)
    else:
        print("copied file", cmd[1])

result = check_call(['mv', path.join(base_path, 'build_apk.py'), share_folder])
