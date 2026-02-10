import sqlite3
import pandas as pd
from db_manager import db

def import_ingredients_from_csv(csv_file_path="ingredients.csv"):
    """
    從 CSV 檔案匯入食材資料到 SQLite 資料庫
    
    Args:
        csv_file_path (str): CSV 檔案路徑，預設為 "ingredients.csv"
    """
    try:
        # 連線到資料庫
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # 清空舊資料
        print("正在清空舊的食材資料...")
        cursor.execute("DELETE FROM ingredients")
        conn.commit()
        print("[OK] 已清空舊資料")
        
        # 讀取 CSV 檔案 (utf-8 編碼)
        print(f"正在讀取 CSV 檔案: {csv_file_path}")
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        print(f"[OK] 成功讀取 {len(df)} 筆資料")
        
        # 檢查必要的欄位
        required_columns = ['name', 'category', 'five_color', 'nature', 'effects', 'is_condiment']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"[ERROR] CSV 檔案缺少必要欄位: {missing_columns}")
            return False
        
        # 轉換 is_condiment 欄位為布林值
        df['is_condiment'] = df['is_condiment'].astype(bool)
        
        # 逐筆插入資料
        success_count = 0
        error_count = 0
        
        print("正在匯入資料...")
        for index, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO ingredients (name, category, five_color, nature, effects, is_condiment)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row['name'],
                    row['category'],
                    row['five_color'],
                    row['nature'],
                    row['effects'],
                    row['is_condiment']
                ))
                success_count += 1
            except Exception as e:
                print(f"[ERROR] 第 {index + 1} 行匯入失敗: {e}")
                error_count += 1
        
        # 提交交易
        conn.commit()
        
        # 關閉連線
        conn.close()
        
        # 印出結果
        print(f"\n匯入完成！")
        print(f"[OK] 成功匯入: {success_count} 筆")
        if error_count > 0:
            print(f"[ERROR] 失敗: {error_count} 筆")
        
        return success_count > 0
        
    except FileNotFoundError:
        print(f"[ERROR] 找不到檔案: {csv_file_path}")
        return False
    except Exception as e:
        print(f"[ERROR] 匯入過程發生錯誤: {e}")
        return False

def create_sample_csv():
    """
    創建範例 CSV 檔案
    """
    sample_data = {
        'name': ['菠菜', '紅蘿蔔', '香菇', '豆腐', '雞蛋', '鹽', '糖'],
        'category': ['葉菜類', '根莖類', '菇菌類', '豆製品', '蛋奶類', '調味品', '調味品'],
        'five_color': ['青', '赤', '黑', '白', '黃', '白', '黃'],
        'nature': ['涼', '平', '平', '涼', '平', '寒', '平'],
        'effects': ['補血、助消化', '補肝明目', '益氣補虛', '清熱潤燥', '滋陰潤燥', '清火解毒', '潤肺生津'],
        'is_condiment': [False, False, False, False, False, True, True]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('ingredients.csv', index=False, encoding='utf-8')
    print("[OK] 已創建範例 ingredients.csv 檔案")

if __name__ == "__main__":
    print("=== 食材 CSV 匯入工具 ===")
    print()
    
    # 檢查是否存在 CSV 檔案
    import os
    if not os.path.exists("ingredients.csv"):
        print("未找到 ingredients.csv 檔案")
        choice = input("是否創建範例檔案? (y/n): ").lower().strip()
        if choice == 'y':
            create_sample_csv()
        else:
            print("請準備 ingredients.csv 檔案後再執行")
            exit()
    
    # 執行匯入
    success = import_ingredients_from_csv()
    
    if success:
        print("\n[SUCCESS] 匯入成功！")
    else:
        print("\n[FAILED] 匯入失敗！")
