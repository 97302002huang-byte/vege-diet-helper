# 🥗 植感飲食 (Vegetarian Diet Helper)

這是一個專為蛋奶素食者設計的飲食管理工具，提供食材查詢、食譜管理以及智慧菜單規劃功能。

## ✨ 功能特色
- **食材庫**：包含五色與食性分析的完整素食資料庫。
- **食譜書**：可自訂建立食譜，並自動計算整道菜的營養屬性。
- **菜單工作台**：
  - 🍱 **快速樣板**：一鍵生成 1~30 人的用餐配置。
  - 🛒 **智慧採購**：自動產生採購清單，並可勾選調味品。
  - 📊 **能量分析**：視覺化呈現當日菜單的寒熱食性與五色平衡。

## 🚀 如何執行
1. 安裝套件：`pip install -r requirements.txt`
2. 初始化資料庫：
   ```bash
   python import_csv.py
   python import_recipes.py
   python import_set_menus.py
   ```
3. 啟動網頁：`streamlit run app.py`