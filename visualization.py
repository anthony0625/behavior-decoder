import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class Clean:
    def __init__(self, params_file, min_length):
        self.params_file = params_file
        self.min_length = min_length
        self.cleaned_params = None
        self.cleaned_params_1 = None
        self.cleaned_params_0 = None

    def clean_params(self):
        cleaned_params = []
        with open(self.params_file, 'r') as params_csv:
            for row in csv.reader(params_csv):
                if row[1] == "FTP" and row[4] == "clean":
                    if (int(row[7])-int(row[6]))>self.min_length:
                        cleaned_row = [1 if row[3] == "correct" else 0, int(row[6]), int(row[7])]
                        cleaned_params.append(cleaned_row)
        self.cleaned_params = np.array(cleaned_params, dtype=int)

    def separate_cleaned_params(self):
        if self.cleaned_params is None:
            self.clean_params()
        self.cleaned_params_1 = self.cleaned_params[self.cleaned_params[:, 0] == 1]
        self.cleaned_params_0 = self.cleaned_params[self.cleaned_params[:, 0] == 0]

    def get_cleaned_params(self):
        if self.cleaned_params is None:
            self.clean_params()
        return self.cleaned_params

    def get_cleaned_params_1(self):
        if self.cleaned_params_1 is None:
            self.separate_cleaned_params()
        return self.cleaned_params_1

    def get_cleaned_params_0(self):
        if self.cleaned_params_0 is None:
            self.separate_cleaned_params()
        return self.cleaned_params_0


class Transform:
    def __init__(self, session_file):
        self.session_file = session_file
        self.blocks_1 = None
        self.blocks_0 = None

    def get_blocks(self, cleaned_params, normalize=False):
        with open(self.session_file, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            data_array = [row for row in reader][1:]
        data = np.array(data_array, dtype=np.float32)[:, 1:]

        blocks = np.empty(0)
        for cleaned_row in cleaned_params:
            block = data[cleaned_row[1]:cleaned_row[2],:]
            block = np.fft.fft(block, axis=0)
            block = block.real[self.freqs, :]
            if blocks.ndim == 3:
                blocks = np.concatenate((blocks, block[:,:,np.newaxis]), axis=2)
            elif blocks.ndim == 2:
                blocks = np.dstack((blocks, block))
            else:
                blocks = block
        stacked_blocks = blocks
        if normalize:
            stacked_blocks -= stacked_blocks.min(axis=(0, 1), keepdims=True)
            stacked_blocks /= stacked_blocks.max(axis=(0, 1), keepdims=True)
        return stacked_blocks

    def generate_heatmaps(self, cleaned_params_1, cleaned_params_0, output_file, freqs, normalize=False):
        self.freqs = freqs
        blocks_1 = self.get_blocks(cleaned_params_1, normalize)
        blocks_0 = self.get_blocks(cleaned_params_0, normalize)

        with PdfPages(output_file) as pdf:
            num_blocks_1 = blocks_1.shape[2]
            num_blocks_0 = blocks_0.shape[2]
            num_blocks = max(num_blocks_1, num_blocks_0)
            for i in range(num_blocks):
                fig, axs = plt.subplots(1, 2, figsize=(10, 5))
                if i < num_blocks_1:
                    axs[0].imshow(blocks_1[:, :, i], cmap='hot', interpolation='nearest', aspect=10)
                    axs[0].set_title('Block {}'.format(i))
                if i < num_blocks_0:
                    axs[1].imshow(blocks_0[:, :, i], cmap='hot', interpolation='nearest', aspect=10)
                    axs[1].set_title('Block {}'.format(i))
                pdf.savefig(fig)
                plt.close()

clean = Clean('params.csv', 9)
transform = Transform('data.csv')
output_file = 'heatmaps.pdf'

cleaned_params_1 = clean.get_cleaned_params_1()
cleaned_params_0 = clean.get_cleaned_params_0()

#heatmap = Heatmaps("data.csv", "params.csv", freqs=[0,1,2,4,5,8,9], output_file=output_file)
#transform.generate_heatmaps(cleaned_params_1, cleaned_params_0, output_file, freqs=np.arange(1,10))
#transform.generate_heatmaps(cleaned_params_1, cleaned_params_0, "heatmaps2.pdf", freqs=[0,1,2,4,5,8,9])
transform.generate_heatmaps(cleaned_params_1, cleaned_params_0, "heatmaps2.pdf", freqs=[3])
