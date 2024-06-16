# sleep_recognition_app

yolov8を使用した起床、睡眠検知の可視化アプリ。

学習済みモデルは以下のリポジトリを参照。

使用したい場合は、以下の手順に従う。

```
#任意のディレクトリ
git clone https://github.com/Yuhei-Handa/sleep_recognition_app
cd sleep_recognition_app
git clone https://github.com/Yuhei-Handa/video_sleep_recognition
```

### パラメータ
・Window Time：起床・睡眠フラグを現在からどの程度の参照するかを示す期間 [s]  
・Warn Threshold：睡眠状態を警告する起床・睡眠フラグの割合に対する閾値 (0,1]  
・Sleep Threshold：眠状態を判定する起床・睡眠フラグの割合に対する閾値 (0,1]  

### ボタン
・Update：上記のパラメータを反映  
・Close：終了  

https://github.com/Yuhei-Handa/sleep_recognition_app/assets/135846516/e223299d-4bd5-42ce-be43-c502aed28725

