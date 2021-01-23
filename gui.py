# Welcome to PyShine
# This is part 10 of the PyQt5 learning series
# Based on parameters, the GUI will plot live voice data using Matplotlib in PyQt5
# We will use Qthreads to run the audio stream data.

import sys
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import queue
import numpy as np
import sounddevice as sd

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio, QCameraInfo
import threading

input_audio_deviceInfos = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        fig.tight_layout()


class main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi("main.ui", self)
        self.resize(888, 600)
        icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap("PyShine.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.devices_list = []
        for device in input_audio_deviceInfos:
            self.devices_list.append(device.deviceName())

        self.comboBox.addItems(self.devices_list)
        self.comboBox.currentIndexChanged["QString"].connect(self.update_now)
        self.comboBox.setCurrentIndex(0)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.ui.gridLayout_4.addWidget(self.canvas, 2, 1, 1, 1)
        self.reference_plot = None
        self.q = queue.Queue(maxsize=20)

        self.device = 0
        self.window_length = 1000
        self.downsample = 1
        self.channels = [1]
        self.interval = 30

        device_info = sd.query_devices(self.device, "input")
        self.samplerate = device_info["default_samplerate"]
        length = int(self.window_length * self.samplerate / (1000 * self.downsample))
        sd.default.samplerate = self.samplerate

        self.plotdata = np.zeros((length, len(self.channels)))

        self.update_plot()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)  # msec
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.lineEdit.textChanged["QString"].connect(self.update_window_length)
        self.lineEdit_2.textChanged["QString"].connect(self.update_sample_rate)
        self.lineEdit_3.textChanged["QString"].connect(self.update_down_sample)
        self.lineEdit_4.textChanged["QString"].connect(self.update_interval)
        self.pushButton.clicked.connect(self.start_worker)
        self.pushButton_exit.clicked.connect(self.sys_exit)

    def getAudio(self):
        try:

            def audio_callback(indata, frames, time, status):
                self.q.put(indata[:: self.downsample, [0]])

            stream = sd.InputStream(
                device=self.device,
                channels=max(self.channels),
                samplerate=self.samplerate,
                callback=audio_callback,
            )
            with stream:
                input()
        except Exception as e:
            print("ERROR: ", e)

    def start_worker(self):
        # worker = Worker(
        #     self.start_stream,
        # )
        # self.threadpool.tryStart(worker)
        self.threadBackend = threading.Thread(target=self.start_stream, daemon=True)
        self.threadBackend.start()

    def sys_exit(self):
        self.timer.stop()

        sys.exit()

    def start_stream(self):
        self.lineEdit.setEnabled(False)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_3.setEnabled(False)
        self.lineEdit_4.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.getAudio()

    def update_now(self, value):
        self.device = self.devices_list.index(value)
        print("Device:", self.devices_list.index(value))

    def update_window_length(self, value):
        self.window_length = int(value)
        length = int(self.window_length * self.samplerate / (1000 * self.downsample))
        self.plotdata = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_sample_rate(self, value):
        self.samplerate = int(value)
        sd.default.samplerate = self.samplerate
        length = int(self.window_length * self.samplerate / (1000 * self.downsample))
        self.plotdata = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_down_sample(self, value):
        self.downsample = int(value)
        length = int(self.window_length * self.samplerate / (1000 * self.downsample))
        self.plotdata = np.zeros((length, len(self.channels)))
        self.update_plot()

    def update_interval(self, value):
        self.interval = int(value)
        self.timer.setInterval(self.interval)  # msec
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        try:
            data = [0]

            while True:
                try:
                    data = self.q.get_nowait()
                except queue.Empty:
                    break
                shift = len(data)
                self.plotdata = np.roll(self.plotdata, -shift, axis=0)
                self.plotdata[-shift:, :] = data
                self.ydata = self.plotdata[:]
                self.canvas.axes.set_facecolor((0, 0, 0))

                if self.reference_plot is None:
                    plot_refs = self.canvas.axes.plot(self.ydata, color=(0, 1, 0.29))
                    self.reference_plot = plot_refs[0]
                else:
                    self.reference_plot.set_ydata(self.ydata)

            self.canvas.axes.yaxis.grid(True, linestyle="--")
            start, end = self.canvas.axes.get_ylim()
            self.canvas.axes.yaxis.set_ticks(np.arange(start, end, 0.1))
            self.canvas.axes.yaxis.set_major_formatter(
                ticker.FormatStrFormatter("%0.1f")
            )
            self.canvas.axes.set_ylim(ymin=-0.5, ymax=0.5)
            self.canvas.draw()
        except:
            pass


app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = main()
    mainWindow.show()
    sys.exit(app.exec_())