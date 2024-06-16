import tkinter as tk
from tkinter import font
import numpy as np
import matplotlib.pyplot as plt
import cv2
from ultralytics import YOLO
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import time
import ctypes
from switchbot_api.switchbot_api import Bot

class SleepRecognition:
    def __init__(self, warn_threshold=0.5, sleep_threshold=0.9, sleep_time=10):
        self.is_sleep = False
        self.warn_threshold = warn_threshold
        self.sleep_threshold = sleep_threshold
        self.sleep_time = sleep_time
        self.start_time = 0
    
    def check_sleep(self, mean_rate):
        if mean_rate > self.sleep_threshold:
            if not self.is_sleep:
                self.start_time = time.time()
                self.is_sleep = True
            else:
                if time.time() - self.start_time > self.sleep_time:
                    return True
                else:
                    print("sleeping")
        else:
            self.is_sleep = False
        return False

# Define the function
def monitor_off():
    # -1 to turn off the monitor
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, 2)

def get_class_name(all_classes, all_confidences):
    if len(all_classes) == 0:
        return 0  # 検出されない場合もawakeとする
    else:
        awake_index = np.array(np.where(all_classes == 0))
        sleep_index = np.array(np.where(all_classes == 1))

        if awake_index.shape[1] == 0 and sleep_index.shape[1] != 0:
            return 1
        elif awake_index.shape[1] != 0 and sleep_index.shape[1] == 0:
            return 0
        else:
            awake_probs = np.max(all_confidences[awake_index])
            sleep_probs = np.max(all_confidences[sleep_index])

            if awake_probs > sleep_probs:
                return 0
            else:
                return 1

class Application(tk.Frame):
    def __init__(self, master, video_source=0, model_weight=None):
        super().__init__(master)

        self.master.geometry("1500x750")
        self.master.title("Tkinter with Video Streaming and Capture")
        self.model = YOLO(model_weight)

        # ---------------------------------------------------------
        # ポイント設定
        # ---------------------------------------------------------
        self.camera_x = 10
        self.camera_y = 10
        self.camera_w = 640
        self.camera_h = 480
        self.camera_padx = 10
        self.camera_pady = 10

        self.graph_x = self.camera_x + self.camera_w + self.camera_padx
        self.graph_y = self.camera_y
        self.graph_w = 640
        self.graph_h = 480
        self.graph_padx = 10
        self.graph_pady = 10
        # ---------------------------------------------------------
        # グラフの設定
        # ---------------------------------------------------------
        self.class_array = np.array([])
        self.mean_rate_array = np.array([])
        self.window_time = 100
        self.next_time = 3
        self.processing_time = 40
        self.delay = self.next_time + self.processing_time  # [mili seconds]
        self.reset_threshold = int(self.window_time / (self.delay / 1000))
        self.xrange = np.arange(0, self.window_time, self.delay / 1000)
        self.warn_threshold = 0.5
        self.sleep_threshold = 0.9
        self.wait_time = 10

        # ---------------------------------------------------------
        # フォント設定
        # ---------------------------------------------------------
        self.font_frame = font.Font(family="Meiryo UI", size=15, weight="normal")
        self.font_btn_big = font.Font(family="Meiryo UI", size=20, weight="bold")
        self.font_btn_small = font.Font(family="Meiryo UI", size=15, weight="bold")

        self.font_lbl_bigger = font.Font(family="Meiryo UI", size=45, weight="bold")
        self.font_lbl_big = font.Font(family="Meiryo UI", size=30, weight="bold")
        self.font_lbl_middle = font.Font(family="Meiryo UI", size=15, weight="bold")
        self.font_lbl_small = font.Font(family="Meiryo UI", size=12, weight="normal")

        # ---------------------------------------------------------
        # ビデオソースのオープン
        # ---------------------------------------------------------

        self.vcap = cv2.VideoCapture(video_source)
        self.width = self.vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # ---------------------------------------------------------
        # 状態の更新フラグ
        # ---------------------------------------------------------
        self.is_updated = False

        # ---------------------------------------------------------
        # スリープ判定
        # ---------------------------------------------------------
        #睡眠を判定する時間間隔
        self.sleep_time = 10
        self.sleep_recognition = SleepRecognition(warn_threshold=self.warn_threshold, sleep_threshold=self.sleep_threshold, sleep_time=self.sleep_time)

        # ---------------------------------------------------------
        # SwitchBot API
        # ---------------------------------------------------------
        self.switchbot = Bot()
    
        # ---------------------------------------------------------
        # ウィジェットの作成
        # ---------------------------------------------------------

        self.create_widgets()

        self.update()

    def create_widgets(self):
        # Frame_Camera
        self.frame_cam = tk.LabelFrame(self.master, text='Camera', font=self.font_frame)
        self.frame_cam.place(x=self.camera_x, y=self.camera_y, width=self.camera_w, height=self.camera_h)
        self.frame_cam.grid_propagate(0)

        # 画像用Canvas
        self.canvas1 = tk.Canvas(self.frame_cam, width=self.camera_w, height=self.camera_h)
        self.canvas1.grid(column=0, row=0, padx=10, pady=10)

        # Graph
        self.frame_graph = tk.LabelFrame(self.master, text='Graph', font=self.font_frame)
        self.frame_graph.place(x=self.graph_x, y=self.graph_y, width=self.graph_w, height=self.graph_h)
        self.frame_graph.grid_propagate(0)

        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.axhline(y=self.warn_threshold, color='orange', linestyle='--')
        self.ax.axhline(y=self.sleep_threshold, color='red', linestyle='--')
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Sleep Rate')
        self.ax.text(0, self.warn_threshold, 'warn', color='orange')
        self.ax.text(0, self.sleep_threshold, 'sleep', color='red')
        self.ax.set_xlim(0, self.window_time)
        self.ax.set_ylim(0, 1)

        self.canvas2 = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control
        self.control = tk.LabelFrame(self.master, text='Control', font=self.font_frame)
        self.control.place(x=10, y=550, width=self.camera_w + self.graph_padx + self.graph_w + self.graph_padx + 150, height=200)
        self.control.grid_propagate(0)

        # Window Time
        self.lbl_window_time = tk.Label(self.control, text="Window Time", font=self.font_lbl_small)
        self.lbl_window_time.grid(column=0, row=0, padx=10, pady=10)
        self.entry_window_time = tk.Entry(self.control, font=self.font_lbl_small)
        self.entry_window_time.grid(column=1, row=0, padx=10, pady=10)

        # Warn Threshold
        self.lbl_warn_threshold = tk.Label(self.control, text="Warn Threshold", font=self.font_lbl_small)
        self.lbl_warn_threshold.grid(column=2, row=0, padx=10, pady=10)
        self.entry_warn_threshold = tk.Entry(self.control, font=self.font_lbl_small)
        self.entry_warn_threshold.grid(column=3, row=0, padx=10, pady=10)

        # Sleep Threshold
        self.lbl_sleep_threshold = tk.Label(self.control, text="Sleep Threshold", font=self.font_lbl_small)
        self.lbl_sleep_threshold.grid(column=4, row=0, padx=10, pady=10)
        self.entry_sleep_threshold = tk.Entry(self.control, font=self.font_lbl_small)
        self.entry_sleep_threshold.grid(column=5, row=0, padx=10, pady=10)

        # Update Button
        self.btn_update = tk.Button(self.control, text='Update', font=self.font_btn_big, command=self.update_settings)
        self.btn_update.grid(column=6, row=0, padx=20, pady=10)

        # Close Button
        self.btn_close = tk.Button(self.control, text='Close', font=self.font_btn_big, command=self.press_close_button)
        self.btn_close.grid(column=7, row=0, padx=20, pady=10)

        # ---------------------------------------------------------
        # Check sleep
        #ラベルの作成
        self.lbl_sleep = tk.Label(self.control, text="Sleep Time", font=self.font_lbl_small)
        self.lbl_sleep.grid(column=0, row=1, padx=10, pady=10)

        #睡眠時間の入力欄
        self.entry_sleep = tk.Entry(self.control, font=self.font_lbl_small)
        self.entry_sleep.grid(column=1, row=1, padx=10, pady=10)
        # ---------------------------------------------------------
        #ステータスの描画
        # ---------------------------------------------------------
        self.lbl_status = tk.Label(self.master, text=f"Status: Window Time: {self.window_time} [s] Warn Threshold: {self.warn_threshold} Sleep Threshold: {self.sleep_threshold} Sleep Time: {self.sleep_time} [s]", font=self.font_lbl_small)
        self.lbl_status.place(x=20, y=720)



    def update_settings(self):
        try:
            self.window_time = int(self.entry_window_time.get())
            self.warn_threshold = float(self.entry_warn_threshold.get())
            self.sleep_threshold = float(self.entry_sleep_threshold.get())
            self.sleep_time = int(self.entry_sleep.get())
            self.reset_threshold = int(self.window_time / (self.delay / 1000))

            self.sleep_recognition = SleepRecognition(warn_threshold=self.warn_threshold, sleep_threshold=self.sleep_threshold, sleep_time=self.sleep_time)

            self.xrange = np.arange(0, self.window_time, self.delay / 1000)

            self.mean_rate_array = np.array([])
            self.class_array = np.array([])
            self.xrange = np.arange(0, self.window_time, self.delay / 1000)

            self.x = self.xrange[:len(self.mean_rate_array)]
            self.y = self.mean_rate_array

            self.ax.clear()
            self.ax.axhline(y=self.warn_threshold, color='orange', linestyle='--')
            self.ax.axhline(y=self.sleep_threshold, color='red', linestyle='--')

            self.ax.set_xlabel('Time [s]')
            self.ax.set_ylabel('Sleep Rate')

            self.ax.text(0, self.warn_threshold, 'warn', color='orange')
            self.ax.text(0, self.sleep_threshold, 'sleep', color='red')

            self.ax.set_xlim(0, self.window_time)
            self.ax.set_ylim(0, 1)

            self.lbl_status = tk.Label(self.master, text=f"Status: Window Time: {self.window_time} [s] Warn Threshold: {self.warn_threshold} Sleep Threshold: {self.sleep_threshold} Sleep Time: {self.sleep_time} [s]", font=self.font_lbl_small)
            self.lbl_status.place(x=20, y=720)
            self.canvas2.draw()
        except ValueError:
            print("Invalid input for one of the settings")

    def update(self):
        # ビデオソースからフレームを取得
        _, frame = self.vcap.read()

        results = self.model(frame, show=False, conf=0.65, iou=0.5, device='cuda:0')

        all_classes = results[0].boxes.cls.cpu().numpy()
        all_confidences = results[0].boxes.conf.cpu().numpy()

        detected_class = get_class_name(all_classes, all_confidences)  # 0:awake, 1:sleep


        self.class_array  = np.append(self.class_array, detected_class)

        self.reset_threshold = int(self.window_time / (self.delay / 1000))

        if len(self.class_array) > self.reset_threshold:
            self.class_array = self.class_array[1:]

        self.wait_threshold = int(self.wait_time / (self.delay / 1000))
        if len(self.class_array) > self.wait_threshold:
            mean_rate = np.sum(self.class_array[self.class_array != None]) / len(self.class_array)
        else:
            mean_rate = 0  # 初期のの推論結果は変動幅が大きいため0とする

        self.mean_rate_array = np.append(self.mean_rate_array, mean_rate)

        if len(self.mean_rate_array) > self.reset_threshold:
            self.mean_rate_array = self.mean_rate_array[1:]

        self.x = self.xrange[:len(self.mean_rate_array)]
        self.y = self.mean_rate_array

        # グラフの更新
        self.ax.clear()

        # グラフに閾値を表示
        self.ax.axhline(y=self.warn_threshold, color='orange', linestyle='--')
        self.ax.axhline(y=self.sleep_threshold, color='red', linestyle='--')

        # ラベルの設定
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Sleep Rate')

        self.ax.text(0, self.warn_threshold, 'warn', color='orange')
        self.ax.text(0, self.sleep_threshold, 'sleep', color='red')

        # 閾値を超えたら色を変える
        if self.y[-1] > self.sleep_threshold:
            self.ax.plot(self.x, self.y, color='red')
        elif self.y[-1] > self.warn_threshold:
            self.ax.plot(self.x, self.y, color='orange')
        else:
            self.ax.plot(self.x, self.y, color='blue')
        self.canvas2.draw()
        
        # 画像の更新
        annotated_img = results[0].plot()
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(annotated_img))

        # self.photo -> Canvas
        self.canvas1.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.master.after(self.next_time, self.update)

        #睡眠判定
        is_sleep = self.sleep_recognition.check_sleep(mean_rate)
        if is_sleep:
            print("sleep")
            self.switchbot.press()
            monitor_off()
            time.sleep(10)
            self.master.destroy()
        else:
            #print("awake")
            pass

    def press_close_button(self):
        self.master.destroy()

def main():
    pretrained_weight_path = "yolov8_sleep_recognition/runs/detect/train10/weights/best.pt"

    root = tk.Tk()
    app = Application(master=root, video_source=0, model_weight=pretrained_weight_path)
    app.mainloop()

if __name__ == "__main__":
    main()