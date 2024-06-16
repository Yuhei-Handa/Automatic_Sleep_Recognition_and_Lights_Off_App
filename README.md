# Automatic_Sleep_Recognition_and_Lights_Off_App

yolov8とSwitchbotを使用した起床、睡眠検知の可視化と自動消灯アプリ。

睡眠状態検知に関しては、以下のリポジトリから参照してください。  

[https://github.com/Yuhei-Handa/sleep_recognition_app](https://github.com/Yuhei-Handa/sleep_recognition_app)

使用する際は以下の手順に従ってください。

```
git clone https://github.com/Yuhei-Handa/Automatic_Sleep_Recognition_and_Lights_Off_App
cd Automatic_Sleep_Recognition_and_Lights_Off_App
python app.py
```

### パラメータ
・Window Time：起床・睡眠フラグを現在からどの程度の参照するかを示す期間 [s]  
・Warn Threshold：睡眠状態を警告する起床・睡眠フラグの割合に対する閾値 (0,1]  
・Sleep Threshold：睡眠状態を判定する起床・睡眠フラグの割合に対する閾値 (0,1]  
・Sleep Time：睡眠状態検知に用いる秒数 [s]

### ボタン
・Update：上記のパラメータを反映  
・Close：終了  

https://github.com/Yuhei-Handa/Automatic_Sleep_Recognition_and_Lights_Off_App/assets/135846516/f540ccb1-cc34-4144-b4cf-a66fee58437f


