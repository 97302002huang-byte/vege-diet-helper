import sqlite3
import json
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "vegetarian_diet.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 食材知識庫
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL CHECK (category IN ('葉菜類', '根莖類', '菇菌類', '豆製品', '蛋奶類', '五穀雜糧', '水果類', '調味品', '堅果種子類', '藻類', '甜品/點心類', '其他')),
                    five_color TEXT NOT NULL CHECK (five_color IN ('青', '赤', '黃', '白', '黑')),
                    nature TEXT NOT NULL CHECK (nature IN ('寒', '涼', '平', '溫', '熱')),
                    effects TEXT,
                    is_condiment BOOLEAN DEFAULT 0
                )
            """)
            
            # 食譜表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL CHECK (category IN ('主食', '主菜', '配菜', '湯品', '甜點/飲料', '醬料/醃料', '高湯/湯底')),
                    description TEXT
                )
            """)
            
            # 食譜-食材關聯表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipe_ingredients (
                    recipe_id INTEGER,
                    ingredient_id INTEGER,
                    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
                    FOREIGN KEY (ingredient_id) REFERENCES ingredients (id) ON DELETE CASCADE,
                    PRIMARY KEY (recipe_id, ingredient_id)
                )
            """)
            
            # 菜單工作區
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_workspace (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER,
                    custom_name TEXT,
                    ingredients_json TEXT,
                    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE SET NULL
                )
            """)
            
            # 套餐表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            """)
            
            # 套餐-食譜關聯表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu_set_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    menu_set_id INTEGER,
                    recipe_id INTEGER,
                    FOREIGN KEY (menu_set_id) REFERENCES menu_sets (id) ON DELETE CASCADE,
                    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
    
    # --- Ingredients CRUD ---
    def add_ingredient(self, name: str, category: str, five_color: str, 
                       nature: str, effects: str = "", is_condiment: bool = False) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ingredients (name, category, five_color, nature, effects, is_condiment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, category, five_color, nature, effects, is_condiment))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_ingredients(self) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingredients ORDER BY category, name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    # ★★★ 這是新增的功能 (修復 AttributeError 錯誤) ★★★
    def get_ingredient_by_name(self, name: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingredients WHERE name = ?", (name,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_ingredients_by_category(self, category: str) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingredients WHERE category = ? ORDER BY name", (category,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_ingredient(self, ingredient_id: int, name: str, category: str, 
                          five_color: str, nature: str, effects: str = "", 
                          is_condiment: bool = False) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ingredients 
                SET name = ?, category = ?, five_color = ?, nature = ?, effects = ?, is_condiment = ?
                WHERE id = ?
            """, (name, category, five_color, nature, effects, is_condiment, ingredient_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_ingredient(self, ingredient_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def search_ingredients(self, keyword: str) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ingredients 
                WHERE name LIKE ? OR effects LIKE ?
                ORDER BY category, name
            """, (f"%{keyword}%", f"%{keyword}%"))
            return [dict(row) for row in cursor.fetchall()]
    
    # --- Recipes CRUD ---
    def add_recipe(self, name: str, category: str, description: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO recipes (name, category, description) VALUES (?, ?, ?)", 
                           (name, category, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_recipes(self) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
    
    def get_recipe_with_ingredients(self, recipe_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 獲取食譜基本資訊
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            recipe = cursor.fetchone()
            if not recipe:
                return None
            
            recipe_dict = dict(recipe)
            
            # 獲取食譜的食材
            cursor.execute("""
                SELECT i.* FROM ingredients i
                JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
                WHERE ri.recipe_id = ?
                ORDER BY i.category, i.name
            """, (recipe_id,))
            recipe_dict['ingredients'] = [dict(row) for row in cursor.fetchall()]
            
            return recipe_dict
    
    def update_recipe(self, recipe_id: int, name: str, category: str, description: str = "") -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE recipes SET name = ?, category = ?, description = ? WHERE id = ?", 
                           (name, category, description, recipe_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_recipe(self, recipe_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- Recipe-Ingredients 關聯管理 ---
    def add_ingredient_to_recipe(self, recipe_id: int, ingredient_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id)
                    VALUES (?, ?)
                """, (recipe_id, ingredient_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def remove_ingredient_from_recipe(self, recipe_id: int, ingredient_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM recipe_ingredients 
                WHERE recipe_id = ? AND ingredient_id = ?
            """, (recipe_id, ingredient_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def set_recipe_ingredients(self, recipe_id: int, ingredient_ids: List[int]) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # 先刪除現有關聯
                cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", 
                             (recipe_id,))
                
                # 添加新關聯
                for ingredient_id in ingredient_ids:
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
                        VALUES (?, ?)
                    """, (recipe_id, ingredient_id))
                
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    # --- Menu Sets CRUD ---
    def add_menu_set(self, name: str, description: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO menu_sets (name, description) VALUES (?, ?)", 
                           (name, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_menu_sets(self) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_sets ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_menu_set_with_recipes(self, menu_set_id: int) -> Dict:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_sets WHERE id = ?", (menu_set_id,))
            menu_set = dict(cursor.fetchone())
            
            cursor.execute("""
                SELECT r.* FROM recipes r
                JOIN menu_set_items msi ON r.id = msi.recipe_id
                WHERE msi.menu_set_id = ?
                ORDER BY r.category, r.name
            """, (menu_set_id,))
            menu_set['recipes'] = [dict(row) for row in cursor.fetchall()]
            
            return menu_set
    
    def set_menu_set_recipes(self, menu_set_id: int, recipe_ids: List[int]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu_set_items WHERE menu_set_id = ?", (menu_set_id,))
            for recipe_id in recipe_ids:
                cursor.execute("INSERT INTO menu_set_items (menu_set_id, recipe_id) VALUES (?, ?)", 
                             (menu_set_id, recipe_id))
            conn.commit()
    
    def delete_menu_set(self, menu_set_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu_sets WHERE id = ?", (menu_set_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- Menu Workspace CRUD ---
    def add_menu_item(self, recipe_id: Optional[int] = None, 
                      custom_name: str = "", ingredients_json: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO menu_workspace (recipe_id, custom_name, ingredients_json)
                VALUES (?, ?, ?)
            """, (recipe_id, custom_name, ingredients_json))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_menu_items(self) -> List[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mw.*, r.name as recipe_name 
                FROM menu_workspace mw
                LEFT JOIN recipes r ON mw.recipe_id = r.id
                ORDER BY mw.id DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_menu_item_with_details(self, menu_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 獲取菜單項目基本資訊
            cursor.execute("""
                SELECT mw.*, r.name as recipe_name, r.description as recipe_description
                FROM menu_workspace mw
                LEFT JOIN recipes r ON mw.recipe_id = r.id
                WHERE mw.id = ?
            """, (menu_id,))
            menu_item = cursor.fetchone()
            if not menu_item:
                return None
            
            menu_dict = dict(menu_item)
            
            # 如果有自選食材，解析並獲取食材詳情
            if menu_dict['ingredients_json']:
                try:
                    ingredient_ids = json.loads(menu_dict['ingredients_json'])
                    if ingredient_ids:
                        placeholders = ','.join(['?' for _ in ingredient_ids])
                        cursor.execute(f"""
                            SELECT * FROM ingredients 
                            WHERE id IN ({placeholders})
                            ORDER BY category, name
                        """, ingredient_ids)
                        menu_dict['custom_ingredients'] = [dict(row) for row in cursor.fetchall()]
                    else:
                        menu_dict['custom_ingredients'] = []
                except json.JSONDecodeError:
                    menu_dict['custom_ingredients'] = []
            else:
                menu_dict['custom_ingredients'] = []
            
            # 如果基於食譜，獲取食譜食材
            if menu_dict['recipe_id']:
                cursor.execute("""
                    SELECT i.* FROM ingredients i
                    JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
                    WHERE ri.recipe_id = ?
                    ORDER BY i.category, i.name
                """, (menu_dict['recipe_id'],))
                menu_dict['recipe_ingredients'] = [dict(row) for row in cursor.fetchall()]
            else:
                menu_dict['recipe_ingredients'] = []
            
            return menu_dict
    
    def update_menu_item(self, menu_id: int, recipe_id: Optional[int] = None,
                         custom_name: str = "", ingredients_json: str = "") -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE menu_workspace 
                SET recipe_id = ?, custom_name = ?, ingredients_json = ?
                WHERE id = ?
            """, (recipe_id, custom_name, ingredients_json, menu_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_menu_item(self, menu_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM menu_workspace WHERE id = ?", (menu_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # --- Utility functions ---
    def get_categories(self) -> List[str]:
        return ['葉菜類', '根莖類', '菇菌類', '豆製品', '蛋奶類', '五穀雜糧', '水果類', '調味品', '堅果種子類', '藻類', '甜品/點心類', '其他']
    
    def get_recipe_categories(self) -> List[str]:
        return ['主食', '主菜', '配菜', '湯品', '甜點/飲料', '醬料/醃料', '高湯/湯底']
    
    def get_five_colors(self) -> List[str]:
        return ['青', '赤', '黃', '白', '黑']
    
    def get_natures(self) -> List[str]:
        return ['寒', '涼', '平', '溫', '熱']
    
    def close(self):
        # SQLite 不需要明確關閉連接
        pass

# 全域資料庫管理器實例
db = DatabaseManager()