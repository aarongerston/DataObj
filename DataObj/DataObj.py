import os
import mne


class DataObj:

    def __init__(self, filepath: str, filename: str = None):
        """
        Initialize a DataObject from an EDF file.

        :param filepath: absolute file path or parent directory if <filename> is also given.
        :param filename: (OPTIONAL) file name (with extension), necessary only if <filepath> is the directory containing
                         the EDF file <filename>.
        """

        # If <filepath> is the absolute file path, deduce <filename> from it:
        if filename is None:
            self.filename = os.path.basename(filepath)
            self.filepath = filepath

        # If both <filepath> and <filename> are given, concatenate file directory and file name and store as <filepath>:
        else:
            self.filename = filename
            if filename == os.path.basename(filepath):
                self.filepath = filepath
            elif os.path.isdir(filepath):
                self.filepath = os.path.join(filepath, filename)
            else:
                raise Exception('filepath must be parent directory (if filename is also given) or absolute path to file.')

        # Initialize all other properties as None, until DataObj.readEDF() is called:
        self.data_exg = None
        self.data_imu = None
        self.ts_exg = None
        self.ts_imu = None
        self.fs_exg = None
        self.fs_imu = None
        self.ch_names_exg = None
        self.ch_names_imu = None
        self.annotations = None
        self.filters_exg = None
        self.filters_imu = None
        self.montage = None
        self.dau = None
        self.app_ver = None

        # Initialize from EDF
        self.readEDF()

    def readEDF(self):
        """
        Read EDF file using mne package:
        Input: filepath - EDF's file directory OR full absolute path to file.
               filename (OPTIONAL) - EDF's file name.
        Output: self, with properties:
                raw_exg - 2D Numpy ndarray of the raw electrode data.
                raw_imu - 2D Numpy ndarray of the raw IMU (accelerometer) data.
                ts_exg - 1D Numpy ndarray of the timestamp vector corresponding to electrode sampling.
                ts_imu - 1D Numpy ndarray of the timestamp vector corresponding to IMU (accelerometer) sampling.
                fs_exg - sampling rate of electrodes
                fs_imu - sampling rate of IMU (accelerometer)
                ch_names_exg - list of electrode channel headers.
                ch_names_imu - list of accelerometer channel headers.
                annotations - Data's annotations: a 1D list of 2-item tuples, where item[0] is the event time in seconds
                              since recording start and item[1] is the event description.
                montage - electrode array version
                dau - DAU version
        """

        # """ USE PyEDFreader TO PARSE THE DATA: """
        # print(f'Extracting data from {self.filepath}...')
        # raw, channel_info, header = highlevel.read_edf(self.filepath)
        #
        # # Recording info
        # self.montage = header['annotations'][12][2][len('montageSku: '):]
        # self.dau = header['annotations'][7][2][len('DAU No.: '):]
        # self.app_ver = header['annotations'][6][2][len('App version: '):]
        # self.annotations = [(event[0], event[2]) for event in header['annotations']
        #                     if (event[0] > 0) and ('File started' not in event[2])]
        #
        # # Channels info
        # self.channel_names = [ch['label'] for ch in channel_info]
        # imu_channels = self.get_channels('imu')
        # exg_channels = self.get_channels('exg')
        #
        # # Raw electrode data matrices
        # raw_exg = None if exg_channels is None else np.transpose(np.stack([raw[col] for col in exg_channels]))
        # raw_imu = None if imu_channels is None else np.transpose(np.stack([raw[col] for col in imu_channels]))
        #
        # # Sampling rate
        # # (EXG)
        # fss_exg = [ch['sample_rate'] for n, ch in enumerate(channel_info) if n in exg_channels]
        # if all(fs == fss_exg[0] for fs in fss_exg):
        #     fs_exg = fss_exg[0]
        # else:
        #     raise Exception('Electrode sampling rates are unequal. Parser not yet equipped to handle this.')
        # # (IMU)
        # fss_imu = [ch['sample_rate'] for n, ch in enumerate(channel_info) if n in imu_channels]
        # if all(fs == fss_imu[0] for fs in fss_imu):
        #     fs_imu = fss_imu[0]
        # else:
        #     raise Exception('IMU sampling rates are unequal. Parser not yet equipped to handle this.')
        #
        # # Timestamp vectors
        # n_samples_exg = None if exg_channels is None else raw_exg.shape[0]
        # n_samples_imu = None if imu_channels is None else raw_imu.shape[0]
        # ts_exg = None if exg_channels is None else np.linspace(0, (n_samples_exg - 1) / fs_exg, n_samples_exg)
        # ts_imu = None if imu_channels is None else np.linspace(0, (n_samples_imu - 1) / fs_imu, n_samples_imu)
        #
        # # Decimate data as desired
        # self.raw_exg, self.ts_exg, self.fs_exg = DataObj.decimate(raw_exg, ts_exg, fs_exg, decimation_exg)
        # self.raw_imu, self.ts_imu, self.fs_imu = DataObj.decimate(raw_imu, ts_imu, fs_imu, decimation_imu)

        """ USE MNE TO PARSE THE DATA """
        try:
            edfData = mne.io.read_raw_edf(self.filepath, exclude={'N.A'})
        except Exception as e:
            print('Failed to parse EDF file: ' + str(e))
            return

        # Triggers
        self.annotations = [(time, desc) for time, desc in
                            zip(edfData.annotations.onset, edfData.annotations.description) if
                            ('File started' not in desc) and ('Change mode' not in desc) and (time > 0)]

        try:  # If new EDF format (after AWS lambda update on 20 Oct. 2021)

            # Get recording info that exists only in the new EDF format
            self.montage = [txt for txt in edfData.annotations.description if 'montageSku: ' in txt][0][len('montageSku: '):]
            self.dau = [txt for txt in edfData.annotations.description if 'DAU No.: ' in txt][0][len('DAU No.: '):]
            self.app_ver = [txt for txt in edfData.annotations.description if 'App version: ' in txt][0][len('App version: '):]

            edf_format = 'new'
        except IndexError:  # If old EDF format (before AWS lambda update on 20 Oct. 2021)
            edf_format = 'old'

        if edf_format == 'new':

            # Separately parse EXG and IMU channels. Otherwise MNE automatically resamples to equal sampling rates.
            imu_channels = [n for n, ch in enumerate(edfData.ch_names) if 'Accelerometer' in ch]
            exg_channels = [n for n, ch in enumerate(edfData.ch_names) if 'Accelerometer' not in ch]
            edf_exg = mne.io.read_raw_edf(self.filepath, exclude=[edfData.ch_names[ch] for ch in imu_channels])
            edf_imu = mne.io.read_raw_edf(self.filepath, exclude=[edfData.ch_names[ch] for ch in exg_channels])

            # Raw electrode data matrices
            self.data_imu = edf_imu[:, :][0].T*1e6
            self.ts_imu = edf_imu.times
            self.fs_imu = edf_imu.info['sfreq']
            self.ch_names_imu = edf_imu.ch_names

        else:
            # Ignore IMU part
            self.data_imu = None
            self.ts_imu = None
            self.fs_imu = None

            edf_exg = edfData

        # Parse EXG part of EDF
        self.data_exg = edf_exg[:, :][0].T*1e6
        self.ts_exg = edf_exg.times
        self.fs_exg = edf_exg.info['sfreq']
        self.ch_names_exg = edf_exg.ch_names

        # # Decimate data (and correspondingly adjust the timestamp vector and sampling rate) if desired
        # self.data_exg, self.ts_exg, self.fs_exg = DataObj.decimate(raw_exg, ts_exg, fs_exg, decimation_exg)
        # self.data_imu, self.ts_imu, self.fs_imu = DataObj.decimate(raw_imu, ts_imu, fs_imu, decimation_imu)

    def get_channels(self, subset: str) -> list:
        """
        Returns list of column numbers of the corresponding data set (self.data_exg) pertaining to modality <subset>
        according to stored channel names (self.ch_names_exg).

        :param subset: (str) Must be one of: ('EMG', 'EEG', 'EOG', 'EKG', 'ECG')
        :return: (list) column numbers of the corresponding data set pertaining to the requested modality
        """

        valid_subsets = ('IMU', 'ACCELEROMETER', 'EMG', 'EEG', 'EOG', 'EKG', 'ECG', 'EXG')

        subset = subset.upper()
        if subset == 'EMG':
            channels = [n for n, ch in enumerate(self.ch_names_exg) if 'EMG' in ch]
        elif subset == 'EEG':
            channels = [n for n, ch in enumerate(self.ch_names_exg) if 'EEG' in ch]
        elif subset == 'EOG':
            channels = [n for n, ch in enumerate(self.ch_names_exg) if 'EOG' in ch]
        elif subset in ('EKG', 'ECG'):
            channels = [n for n, ch in enumerate(self.ch_names_exg) if ('EKG' in ch) or ('ECG' in ch)]
        # elif subset == 'EXG':
        #     channels = [n for n, ch in enumerate(self.ch_names_exg) if
        #                 any(mod in ch for mod in ('EMG', 'EEG', 'EOG', 'EKG', 'ECG'))]
        # elif subset in ('ACCELEROMETER', 'IMU'):
        #     channels = [n for n, ch in enumerate(self.ch_names_imu) if 'Accelerometer' in ch]
        else:
            raise Exception(f'Subset {subset} not valid. Must be in {valid_subsets}.')

        return channels

    # @staticmethod
    # def decimate(data: np.ndarray, ts: np.ndarray, fs: float, decimation_factor: int = 1):
    #     """
    #     Decimates 2D <data> matrix column-wise by a factor of <decimation_factor>.
    #
    #     :param data: 2D data matrix. Rows are samples, columns are channels.
    #     :param ts: 1D timestamp vector equal in samples to number of rows of <data>.
    #     :param fs: sampling rate.
    #     :param decimation_factor: returned data is decimated by a factor of <decimation_factor>
    #     :return: Decimated data matrix, <decimation_factor>-times smaller than the input <data>.
    #     """
    #
    #     if (decimation_factor == 1) or any(arg for arg in (data, ts, fs, decimation_factor) is None):
    #         return data, ts, fs
    #
    #     # Performs the same computation as
    #     # ``data = sig.decimate(data, q=decimation_factor, axis=0, n=2)``
    #     # except that the computation is done column-by-column instead of all at once to prevent crashing
    #     system = sig.dlti(*sig.cheby1(N=2, rp=0.05, Wn=0.8 / decimation_factor))
    #     b, a = system.num, system.den
    #     for col in range(data.shape[1]):
    #         data[:, col] = sig.filtfilt(b, a, data[:, col], axis=0)
    #     data = data[::decimation_factor, :]
    #
    #     # Downsample timestamp vector without filtering
    #     ts = ts[::decimation_factor]
    #
    #     # Update effective sampling rate
    #     fs = fs / decimation_factor
    #
    #     return data, ts, fs
