# README #

## Installation ##

1. Create a virtual environment and ensure Git works in it. 
2. Install DataObj by running the following command:

`pip install git+https://github.com/aarongerston/DataObj.git`

## Uninstallation

Run: `pip uninstall DataObj`
    
## Xtrodes DataObj class example ##

    from DataObj.DataObj import DataObj

    # To initialize the DataObj, provide DataObj either the parent directory and file name, as so:
    directory = r'C:\myDirectory'
    file_name = 'myFile.edf'
    obj = DataObj.DataObj(directory, file_name)

    # ...or the absolute path to the file, as so:
    full_file_path = r'C:\myDirectory\myFile.edf'
    obj = DataObj.DataObj(full_file_path)

    # Now you have everything you need!
    triggers = obj.annotations                      # list of event tuples: (time in sec (float), description (str))
    electrode_data = obj.data_exg                   # 2D numpy array (n_samples, n_channels)
    electrode_time = obj.ts_exg                     # 1D numpy array (n_samples,)
    electrode_sampling_rate = obj.fs_exg            # electrode sampling rate in Hz
    electrode_channel_names = obj.ch_names_exg      # list of electrode channel names defined by montage

    # The following data is only available with the latest firmware update:
    accelerometer_data = obj.data_imu               # 2D numpy array (n_samples, n_channels)
    accelerometer_time = obj.ts_imu                 # 1D numpy array (n_samples,)
    accelerometer_sampling_rate = obj.fs_imu        # IMU sampling rate in Hz
    accelerometer_channel_names = obj.ch_names_imu  # list of IMU channel names

    dau = obj.dau                                   # DAU version
    montage = obj.montage                           # montage SKU
    tablet_app_version = obj.app_ver                # tablet application version

    print('Done')
