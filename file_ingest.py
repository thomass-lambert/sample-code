import os
import re
import shutil


shot_regex = r"(?P<shot>(?P<sequence>[a-z]{4}\d{3})_\d{4})"
version_regex = r".+_v(?P<version>\d{3,4}).*"
file_ext = ("EXR", ".exr")

cwd = os.getcwd()
package_name = "sample_package"
package_path = os.path.join(cwd, package_name)

def detect(pkg):
    print("Scanning package: {}".format(pkg))
    package_contents = os.walk(pkg)
    for root, dirs, files in package_contents:
        for file in files:
            basename, ext = os.path.splitext(file)
            filename = re.sub(r"\..+", "", basename)
            print("\nChecking {}...".format(file))
            if ext == file_ext[1]:
                print("{} is good. Extracting shot/sequence/version.".format(file))
                file_path = os.path.join(root, file)
                m = re.search(shot_regex, filename)
                if m:
                    sequence_code = m.groupdict()['sequence']
                    shot_code = m.groupdict()['shot']
                    print("Sequence Code: {}; Shot Code: {}".format(sequence_code, shot_code))
                    vmatch = re.search(version_regex, filename)
                    if vmatch:
                        version_num = int(vmatch.groupdict()['version'])
                        print("Version Number: {:03d}".format(version_num))
                    else:
                        version_num = 1
                        print("No version number detected, using {:03d}".format(version_num))
                    yield (filename, file_path, sequence_code, shot_code, version_num)
                else:
                    print("Couldn't extract shot/sequence/version from {}".format(file))
            else:
                print("Skipping {} as it is not an {}".format(file, file_ext[0]))


def validate(detected_files):
    to_ingest = []
    for image_file in detected_files:
        print("Checking source and destination...")
        plate_name = image_file[0]
        src_file = image_file[1]
        sequence = image_file[2]
        shot = image_file[3]
        dest_dir = os.path.join(cwd, sequence, shot, plate_name)
        if os.path.exists(src_file):
            print("Source exists.")
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print("Dest doesn't exist. Creating...")
            print("Destination exists. Adding to ingest.")
            to_ingest.append(src_file)
        else:
            print("Source may no longer exist. Skipping.")
    yield (to_ingest, dest_dir)


def ingest(valid_data):
    for entry in valid_data:
        print("\nCoping files...")
        file_list = entry[0]
        dest_on_disk = entry[1]
        for file in file_list:
            shutil.copy2(file, dest_on_disk)
            print("Copied {} to {}".format(os.path.basename(file), dest_on_disk))


detection = detect(package_path)
validation = validate(detection)
ingest(validation)