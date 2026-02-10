import csv
import sqlite3
import os

# 設定資料庫路徑
DB_PATH = 'vegetarian_diet.db'
CSV_PATH = 'recipes.csv'

def get_ingredient_id(cursor, name):
    """根據食材名稱查找 ID"""
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name.strip(),))
    result = cursor.fetchone()
    return result[0] if result else None

def import_recipes():
    print("=== 食譜 CSV 匯入工具 ===")
    
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] 找不到檔案：{CSV_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. 讀取 CSV
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            recipes_count = 0
            
            print("正在匯入食譜...")

            for row in reader:
                recipe_name = row['name'].strip()
                category = row['category'].strip()
                description = row['description'].strip()
                ingredients_str = row['ingredients'] # 例如 "番茄|雞蛋|鹽"

                # 2. 新增食譜本體 (寫入 recipes 表)
                # 先檢查是否已存在，避免重複
                cursor.execute("SELECT id FROM recipes WHERE name = ?", (recipe_name,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"[SKIP] 食譜已存在：{recipe_name}")
                    recipe_id = existing[0]
                    # 選擇性：如果要更新描述，可以在這裡寫 UPDATE
                else:
                    cursor.execute(
                        "INSERT INTO recipes (name, category, description) VALUES (?, ?, ?)",
                        (recipe_name, category, description)
                    )
                    recipe_id = cursor.lastrowid
                    print(f"[NEW] 新增食譜：{recipe_name} ({category})")
                    recipes_count += 1

                # 3. 處理食材關聯 (寫入 recipe_ingredients 表)
                # 先清空該食譜的舊關聯 (如果是更新模式)
                cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))

                ingredient_list = ingredients_str.split('|')
                for ing_name in ingredient_list:
                    ing_name = ing_name.strip()
                    if not ing_name: continue

                    ing_id = get_ingredient_id(cursor, ing_name)
                    
                    if ing_id:
                        cursor.execute(
                            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)",
                            (recipe_id, ing_id)
                        )
                    else:
                        print(f"  ⚠️ 警告：在資料庫中找不到食材 '{ing_name}' (食譜：{recipe_name})")

        conn.commit()
        print(f"\n[SUCCESS] 匯入完成！共新增 {recipes_count} 道食譜。")

    except Exception as e:
        print(f"[ERROR] 發生錯誤：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_recipes()