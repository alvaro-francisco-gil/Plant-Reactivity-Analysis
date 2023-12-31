from torch.utils.data import Dataset
import numpy as np

class SignalDataset(Dataset):
    def __init__(self, signals, labels, sample_rate: int= 10000):
        """
        Initialize the SignalDataset instance.

        :param signals: A list or array of signal data.
        :param labels: A list or array of labels corresponding to the signals.
        :param sample_rate: The sample rate of the signals.
        """
        assert len(signals) == len(labels), "The length of signals and labels must be the same."
        self.signals = signals
        self.labels = labels
        self.sample_rate = sample_rate
        self.standardization = 'None'

    def __len__(self):
        """
        Return the number of samples in the dataset.
        """
        return len(self.signals)

    def __getitem__(self, idx):
        """
        Fetch the signal and its corresponding label at the specified index.
        """
        return self.signals[idx], self.labels[idx]

    def trim_signals(self, time_intervals):
        """
        Trims the signals in the dataset based on the provided time intervals.

        :param time_intervals: A list of tuples, each containing start and end times in seconds.
        """
        assert len(time_intervals) == len(self.signals), "Time intervals must match the number of signals."

        trimmed_signals = []
        for signal, (start_time, end_time) in zip(self.signals, time_intervals):
            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)
            trimmed_signal = signal[start_sample:end_sample]
            trimmed_signals.append(trimmed_signal)

        self.signals = trimmed_signals
        self.transformed = True
    
    
    # Standardization Methods
        
    @staticmethod
    def standardize_wave_peak(waveform):
        """
        Standardizes an audio waveform by removing the DC offset and normalizing its peak.

        :param waveform: An array representing the audio waveform.
        :return: The standardized waveform.
        """

        dc_offset = np.mean(waveform)
        waveform_without_dc = waveform - dc_offset

        normalized_waveform = waveform_without_dc / np.max(np.abs(waveform_without_dc))

        return normalized_waveform
    
    @staticmethod
    def standardize_wave_zscore(waveform):
        """
        Standardizes a waveform using z-score transformation.

        Parameters:
        - waveform (np.ndarray): The input waveform to be standardized.

        Returns:
        - standardized_waveform (np.ndarray): The standardized waveform using z-scores.
        """
        
        mean = np.mean(waveform)
        std_dev = np.std(waveform)

        if std_dev!=0:
            waveform = (waveform - mean) / std_dev

        return waveform

    @staticmethod
    def standardize_wave_min_max(waveform):
        """
        Standardizes a waveform using Min-Max scaling.

        Parameters:
        - waveform (np.ndarray): The input waveform to be standardized.

        Returns:
        - standardized_waveform (np.ndarray): The standardized waveform using Min-Max scaling.
        """
        
        min_val = np.min(waveform)
        max_val = np.max(waveform)

        standardized_waveform = (waveform - min_val) / (max_val - min_val)

        return standardized_waveform
    
    def standardize_signals(self, method):
        """
        Applies the specified standardization technique to all signals in the dataset.

        :param method: The standardization method to use ('peak', 'zscore', 'min_max').
        """
        standardize_func = None
        if method == 'peak':
            standardize_func = self.standardize_wave_peak
        elif method == 'zscore':
            standardize_func = self.standardize_wave_zscore
        elif method == 'min_max':
            standardize_func = self.standardize_wave_min_max
        else:
            raise ValueError("Invalid standardization method. Choose 'peak', 'zscore', or 'min_max'.")

        # Apply the chosen standardization function to each signal
        self.signals = [standardize_func(signal) for signal in self.signals]

        # Update the standardization attribute
        self.standardization = method

    def get_labels(self):
        """
        Returns the labels of the dataset.
        """
        return self.labels

    def get_signals(self):
        """
        Returns the signals of the dataset.
        """
        return self.signals

    def get_data(self):
        """
        Returns all the signal-label pairs in the dataset.
        """
        return self.signals, self.labels

    def get_datapoint_by_key(self, key):
        """
        Returns the signal-label pair corresponding to the given key.
        
        Note: This method assumes that 'key' is an identifier within the labels list.
        """
        try:
            idx = self.labels.index(key)
            return self.signals[idx], self.labels[idx]
        except ValueError:
            return None

    def get_datapoint_by_index(self, idx):
        """
        Returns the signal-label pair at the specified index.
        """
        if idx < len(self.signals):
            return self.signals[idx], self.labels[idx]
        else:
            return None
