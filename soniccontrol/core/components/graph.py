# import ttkbootstrap as ttk
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.animation import FuncAnimation

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use("fivethirtyeight")

def init() -> None:
    

def animate() -> None:
    data = pd.read

# class SonicGraph(FigureCanvasTkAgg):
#     def __init__(self, figure: Figure, plot_frame: ttk.Frame, *args, **kwargs) -> None:
#         super().__init__(figure, plot_frame, *args, **kwargs)
#         self.figure: Figure = figure
#         self.plot_frame: ttk.Frame = plot_frame

#     def update(self) -> None:
#         pass

#     def start(self) -> None:
#         self.figure.clear()
#         self.figure.clear()
#         self.ax1_frequency = self.figure.add_subplot(1, 1, 1)  # Main axis for frequency
#         self.ax2_urms = self.ax1_frequency.twinx()  # Secondary axis for urms
#         self.ax3_irms = self.ax1_frequency.twinx()  # Tertiary axis for irms
#         self.ax3_irms.spines["right"].set_position(
#             ("outward", 60)
#         )  # Move tertiary axis to the right
#         self.ax4_phase = self.ax1_frequency.twinx()

#         (self.line_frequency,) = self.ax1_frequency.plot(
#             [], [], lw=2, label="Frequency", color="black"
#         )
#         (self.line_urms,) = self.ax2_urms.plot(
#             [], [], lw=2, label="Urms", color="blue", linestyle="--"
#         )
#         (self.line_irms,) = self.ax3_irms.plot(
#             [], [], lw=2, label="Irms", color="red", linestyle=":"
#         )
#         (self.line_phase,) = self.ax4_phase.plot(
#             [], [], lw=2, label="Irms", color="green", linestyle=":"
#         )

#         self.time_data = []
#         self.frequency_data = []
#         self.phase_data = []
#         self.urms_data = []
#         self.irms_data = []

#         self.figure.canvas.mpl_connect("draw_event", self.sync_axes)

#         self.ax1_frequency.legend(loc="upper left")
#         self.ax2_urms.legend(loc="upper left")
#         self.ax3_irms.legend(loc="upper left")
#         self.ax4_phase.legend(loc="upper left")

#     def
