'''Print the words and their frequencies in this file'''

import os
import subprocess

def main():
    '''Program entry point'''

    #TODO - pass these in via the command line?
    storageaccountname= ""
    storageaccountkey= ""
    storageaccountsuffix= ""

    mount_point = "/mnt/nyc"
    file_mount_command = [
        'mount',
        '-t',
        'cifs',
        '//{}.file.core.windows.net/data'.format(storageaccountname),
        '{}'.format(mount_point),
        '-o',
        'vers=3.0,username={},password={},dir_mode=0777,file_mode=0777'.format(
            storageaccountname,
            storageaccountkey
        )]

    print("Create mount directory: {}".format(mount_point))
    if not os.path.exists(mount_point):
        os.makedirs(mount_point);

    print("Mounting azure file share with command: '{}'".format(file_mount_command));
    result = subprocess.run(file_mount_command, stdout=subprocess.PIPE)
    print(result.stdout)

    if (os.path.exists(mount_point)):
        files = [f for f in os.listdir(mount_point)]    
        for root, dirs, files2 in os.walk(mount_point):
            path = root.split(os.sep)
            print((len(path) - 1) * '---', os.path.basename(root))
            for file in files2:
                print(len(path) * '---', file)

        # if (os.path.exists(mount_point + '/capacity')):
        #     print("reading capacity data...")
        #     with open(mount_point + '/capacity/capacity_data_jan_to_march_2017.csv', 'r') as cap_data:
        #         #lines = [cap_data.readline() for i in range(1)] # Header
        #         lines = cap_data.readlines()

        #     for line in lines:
        #         print(line)

    else:
        print("Could not find mounted drive '{}'".format(mount_point))

if __name__ == "__main__":
    main()

#sed -i -e '/Defaults requiretty/{ s/.*/# Defaults requiretty/ }' /etc/sudoers && sudo mount -t cifs //batchprodtest2.file.core.windows.net/data /mnt/foo -o vers=3.0,username=batchprodtest2,password=hoP+BHys7+8RDfc4Bzj8lEKhw86n4ppQFlMoRMgmsjN3lUU8WIrEyAThKu4bANbnRfg6uyI/BOo9PH46qaX5Hg==,dir_mode=0777,file_mode=0777