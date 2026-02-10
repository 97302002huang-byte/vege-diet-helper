import csv
import sqlite3
import os

# 設定資料庫路徑
DB_PATH = 'vegetarian_diet.db'
CSV_PATH = 'set_menus.csv'

def get_recipe_id(cursor, recipe_name):
    """根據食譜名稱查找 ID"""
    cursor.execute("SELECT id FROM recipes WHERE name = ?", (recipe_name.strip(),))
    result = cursor.fetchone()
    return result[0] if result else None

def import_set_menus():
    print("=== 套餐 CSV 匯入工具 ===")
    
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] 找不到檔案：{CSV_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. 讀取 CSV
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sets_count = 0
            
            print("正在匯入套餐...")

            for row in reader:
                set_name = row['name'].strip()
                description = row['description'].strip()
                recipes_str = row['recipes'] # 例如 "紅燒獅子頭|三杯菇"

                # 2. 新增套餐本體 (寫入 menu_sets)
                # 檢查是否已存在
                cursor.execute("SELECT id FROM menu_sets WHERE name = ?", (set_name,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"[SKIP] 套餐已存在：{set_name}")
                    menu_set_id = existing[0]
                    # 更新描述
                    cursor.execute("UPDATE menu_sets SET description = ? WHERE id = ?", (description, menu_set_id))
                else:
                    cursor.execute(
                        "INSERT INTO menu_sets (name, description) VALUES (?, ?)",
                        (set_name, description)
                    )
                    menu_set_id = cursor.lastrowid
                    print(f"[NEW] 新增套餐：{set_name}")
                    sets_count += 1

                # 3. 處理食譜關聯 (寫入 menu_set_items)
                # 先清空該套餐的舊關聯 (重置內容)
                cursor.execute("DELETE FROM menu_set_items WHERE menu_set_id = ?", (menu_set_id,))

                recipe_list = recipes_str.split('|')
                for rec_name in recipe_list:
                    rec_name = rec_name.strip()
                    if not rec_name: continue

                    rec_id = get_recipe_id(cursor, rec_name)
                    
                    if rec_id:
                        cursor.execute(
                            "INSERT INTO menu_set_items (menu_set_id, recipe_id) VALUES (?, ?)",
                            (menu_set_id, rec_id)
                        )
                    else:
                        print(f"  ⚠️ 警告：找不到食譜 '{rec_name}' (屬於套餐：{set_name}) - 請確認 recipes.csv 有這道菜")

        conn.commit()
        print(f"\n[SUCCESS] 匯入完成！共處理 {sets_count} 組套餐。")

    except Exception as e:
        print(f"[ERROR] 發生錯誤：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_set_menus()