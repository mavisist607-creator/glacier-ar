冰河地景 AR｜連續地形示意版 V3
=============================

定位：高一地理教學活動原型。
此版本從高山冰蝕區（左）延伸至冰磧、冰水沉積區與下風處風積區（右）。

學科提醒：
1. 「沿上游往下游」只是教學上的連續地景比喻，不代表所有冰川均依此順序出現。
2. 蛇丘常形成於冰河內或冰河底部融冰水通道，並非單純的冰河末端下游河道堆積。
3. 風積區是下風處；風積沙丘並非一定要出現在河川最下游。
4. 羊背石是冰蝕基岩地形；鼓丘多由冰磧物質或冰底物質塑形。等高線只能顯示形態，不能單獨判明成因。
5. 本圖的高程為「合成的教學地形」，不是實測地形；等高距 40 m 只對此合成模型有效；3D 有垂直誇張。

檔案：
index.html            iPad Safari AR 網頁
print.html            A4 橫式列印頁
sheet-student.png     學生等高線圖（直接列印）
sheet-teacher.png     教師參考，附數字標記（勿拿此圖編譯 AR）
tracking-target.png   上傳 MindAR 編譯器的辨識底圖（學生版縮圖）
terrain.glb           由同一份高程網格製作的立體地形模型
features.json         3D 上地形標記的座標與名稱
teacher-key.txt       地形名稱對照
build.py              產製高程、地圖、模型及解答的原始程式

部署方法：
1. 把 index.html、print.html、sheet-student.png、sheet-teacher.png、terrain.glb、features.json
   上傳到 GitHub Pages 儲存庫根目錄（與原本 V2 的 index.html 同一層）。
2. 在電腦瀏覽器打開官方 MindAR 編譯器：
   https://hiukim.github.io/mind-ar-js-doc/tools/compile/
3. 將「tracking-target.png」拖進編譯器，按 Start，完成後下載 targets.mind。
4. 將剛下載的 targets.mind 上傳到 GitHub 儲存庫根目錄（名稱請完全一致）。
5. 使用 iPad Safari 開啟自己 GitHub Pages 網址，允許相機權限。
6. 使用 print.html 列印「學生版」A4 橫式紙張，讓鏡頭對準整張圖。
7. 完成對位後，試用顯示／隱藏地形、四角校準點以及教師標記功能。

編譯底圖與列印底圖：
- 請使用本包內相同版本；更改圖面文字、形狀、版面後，要重新編譯 targets.mind。
- 建議先在學生沒有彩色標註的全新紙本上測試，再測試塗畫後追蹤效果。
- 必須實際在學校 iPad 測試；整張 A4 作為追蹤目標不保證比小圖卡更穩。
- 四角 X1~X4 是可供目視校準的紙面記號，實際追蹤是依賴整張 A4 的影像特徵。
- 背景相機由 MindAR 提供，沒有額外要求第二組攝影機權限。

備註：MindAR、A-Frame 由 CDN 載入，首次開啟須有網路。GitHub Pages 免費公開網站可用。
這是第一份可測試的連續地形原型，不宜在未檢查辨識準確度與課堂內容前直接定稿。
