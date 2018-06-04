from subprocess import check_call, check_output, call
from os import chdir, path
from datetime import datetime

app_name = "MachineWerkz"
app_dist = "debug"
share_folder = "/media/sf_KIVY_VM"  # shared folder with Kivy/Buildozer VM

build_log = open('log.txt', 'w')
app_source = path.join(share_folder, "machinewerkz-kivy")
print("SOURCE : ", app_source)
chdir(path.join(app_source))
build_dir = path.join(app_source,
                      check_output(
                          ['grep', 'build_dir', path.join(app_source, 'buildozer.spec')]
                      ).strip().split('=')[1].split(',')[0].strip())
print("BUILD : ", build_dir)
dist_bin = '/'.join([build_dir, "android/platform/build/dists", app_name.lower(), 'bin'])  # may not yet exist

print("OUTPUT: ", dist_bin)

try:
    app_ver = str(
        check_output(["grep", "__version__", "{}/main.py".format(app_source)]).split('"')[1]
    )
    _major, _minor, _revision = app_ver.split('.')
    build_log.write("[{}] - [{}] - VERSION : MAJOR {} MINOR {} REVISION {}\n".format(
        str(datetime.now()), app_name, int(_major), int(_minor), int(_revision)))
except Exception as e:
    raise e

try:
    assert path.isdir(share_folder)
    assert path.isdir(app_source)
    assert isinstance(app_name, str)
except AssertionError as e:
    raise e

apk_file = "{}-{}-{}.apk".format(app_name, app_ver, app_dist)
apk_fqpn = '/'.join([dist_bin, apk_file])
build_log.write(apk_fqpn)
build_log.write('\n')
build_log.write("buildozer is packaging {}\n".format(apk_file))
build_log.write("cleaning build environment\n")
result = check_call(['buildozer', 'android', 'clean'])
if result != 0:
    build_log.write('BUILDOZER CLEAN : RETURNED ERROR : {}\n'.format(result))
    raise AttributeError("Should have returned 0. Are you in the Kivy/Buildozer VM?")

done = 1

build_log.write("buildozer, building...\n")
print("Please wait while buildozer packages {}".format(apk_file))
call(['buildozer', 'android', 'debug'])
try:
    print("Copying {} to {}\n".format(apk_fqpn, share_folder))
    build_log.write("copying {} to {}\n".format(apk_fqpn, share_folder))
    done = check_call(['cp', apk_fqpn, share_folder])
except AssertionError as e:
    build_log.write(e)

build_log.close()
exit(done)
