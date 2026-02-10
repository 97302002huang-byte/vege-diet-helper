from db_manager import db

def init_sample_data():
    # 添加範例食材
    ingredients_data = [
        # 葉菜類
        ("菠菜", "葉菜類", "青", "涼", "補血、助消化、潤腸", False),
        ("白菜", "葉菜類", "白", "平", "清熱解毒、潤腸通便", False),
        ("空心菜", "葉菜類", "青", "寒", "清熱解毒、利尿", False),
        ("芥藍", "葉菜類", "青", "涼", "清熱解毒、化痰止咳", False),
        
        # 根莖類
        ("紅蘿蔔", "根莖類", "赤", "平", "補肝明目、健脾消食", False),
        ("白蘿蔔", "根莖類", "白", "涼", "消食化積、化痰止咳", False),
        ("馬鈴薯", "根莖類", "黃", "平", "健脾益氣、解毒", False),
        ("地瓜", "根莖類", "黃", "平", "補中益氣、健脾養胃", False),
        ("蓮藕", "根莖類", "白", "涼", "清熱涼血、健脾開胃", False),
        
        # 菇菌類
        ("香菇", "菇菌類", "黑", "平", "益氣補虛、健脾胃", False),
        ("杏鮑菇", "菇菌類", "白", "平", "潤腸、美容、降血壓", False),
        ("木耳", "菇菌類", "黑", "平", "補氣血、潤肺、止血", False),
        ("金針菇", "菇菌類", "黃", "涼", "補肝、益腸胃、益智", False),
        
        # 豆製品
        ("豆腐", "豆製品", "白", "涼", "清熱潤燥、生津解毒、補中益氣", False),
        ("豆漿", "豆製品", "白", "平", "補虛潤燥、清肺化痰", False),
        ("豆干", "豆製品", "黃", "平", "健脾益氣、補虛損", False),
        ("毛豆", "豆製品", "青", "平", "健脾寬中、潤燥消水", False),
        
        # 蛋奶類
        ("雞蛋", "蛋奶類", "黃", "平", "滋陰潤燥、養血安胎", False),
        ("牛奶", "蛋奶類", "白", "平", "補虛損、益肺胃、生津潤腸", False),
        ("起司", "蛋奶類", "黃", "溫", "補肺、潤腸、養陰", False),
        ("優格", "蛋奶類", "白", "涼", "補虛、潤腸、解毒", False),
        
        # 五穀雜糧
        ("糙米", "五穀雜糧", "黃", "溫", "健脾益氣、和胃除煩", False),
        ("燕麥", "五穀雜糧", "黃", "溫", "益脾和胃、潤腸", False),
        ("小米", "五穀雜糧", "黃", "涼", "健脾和胃、補益虛損", False),
        ("薏仁", "五穀雜糧", "白", "涼", "健脾滲濕、除痺止瀉", False),
        
        # 水果類
        ("蘋果", "水果類", "赤", "平", "生津止渴、潤肺除煩、健脾益胃", False),
        ("香蕉", "水果類", "黃", "寒", "清熱潤潤腸、潤肺止咳", False),
        ("葡萄", "水果類", "赤", "平", "補氣血、強筋骨、利小便", False),
        ("柳橙", "水果類", "黃", "涼", "生津止渴、開胃下氣", False),
        
        # 調味品
        ("醬油", "調味品", "黑", "溫", "清熱解毒、開胃", True),
        ("鹽", "調味品", "白", "寒", "清火、涼血、解毒", True),
        ("糖", "調味品", "黃", "平", "潤肺生津、補中緩急", True),
        ("醋", "調味品", "赤", "溫", "散瘀、止血、解毒", True),
        ("薑", "調味品", "黃", "溫", "發汗解表、溫中止嘔", True),
        ("蒜", "調味品", "白", "溫", "溫中行滯、解毒殺蟲", True),
    ]
    
    print("正在添加範例食材...")
    for name, category, five_color, nature, effects, is_condiment in ingredients_data:
        try:
            db.add_ingredient(name, category, five_color, nature, effects, is_condiment)
            print(f"[OK] 已添加食材: {name}")
        except Exception as e:
            print(f"[ERROR] 添加食材失敗 {name}: {e}")
    
    # 添加範例食譜
    recipes_data = [
        ("菠菜炒蛋", "適合一般營養補充，富含蛋白質和鐵質"),
        ("香菇豆腐湯", "清淡養生，適合消化不良時食用"),
        ("蔬菜燴飯", "營養均衡，適合一餐主食"),
        ("涼拌木耳", "清熱涼血，適合夏季食用"),
        ("紅蘿蔔炒豆干", "補肝明目，適合經常用眼者"),
    ]
    
    print("\n正在添加範例食譜...")
    for name, description in recipes_data:
        try:
            recipe_id = db.add_recipe(name, description)
            print(f"[OK] 已添加食譜: {name} (ID: {recipe_id})")
            
            # 為每個食譜添加一些食材
            if name == "菠菜炒蛋":
                db.add_ingredient_to_recipe(recipe_id, 1)  # 菠菜
                db.add_ingredient_to_recipe(recipe_id, 19) # 雞蛋
                db.add_ingredient_to_recipe(recipe_id, 33) # 鹽
                db.add_ingredient_to_recipe(recipe_id, 35) # 薑
            elif name == "香菇豆腐湯":
                db.add_ingredient_to_recipe(recipe_id, 10) # 香菇
                db.add_ingredient_to_recipe(recipe_id, 13) # 豆腐
                db.add_ingredient_to_recipe(recipe_id, 33) # 鹽
            elif name == "蔬菜燴飯":
                db.add_ingredient_to_recipe(recipe_id, 2)  # 白菜
                db.add_ingredient_to_recipe(recipe_id, 5)  # 紅蘿蔔
                db.add_ingredient_to_recipe(recipe_id, 24) # 糙米
                db.add_ingredient_to_recipe(recipe_id, 33) # 鹽
            elif name == "涼拌木耳":
                db.add_ingredient_to_recipe(recipe_id, 12) # 木耳
                db.add_ingredient_to_recipe(recipe_id, 34) # 醋
                db.add_ingredient_to_recipe(recipe_id, 36) # 蒜
            elif name == "紅蘿蔔炒豆干":
                db.add_ingredient_to_recipe(recipe_id, 5)  # 紅蘿蔔
                db.add_ingredient_to_recipe(recipe_id, 15) # 豆干
                db.add_ingredient_to_recipe(recipe_id, 33) # 鹽
                
        except Exception as e:
            print(f"[ERROR] 添加食譜失敗 {name}: {e}")
    
    # 添加範例菜單項目
    print("\n正在添加範例菜單項目...")
    try:
        # 基於食譜的菜單項目
        menu_id1 = db.add_menu_item(recipe_id=1, custom_name="今日早餐：菠菜炒蛋")
        print(f"[OK] 已添加菜單項目: 今日早餐：菠菜炒蛋 (ID: {menu_id1})")
        
        # 自定義菜單項目
        custom_ingredients = [1, 19, 13, 33]  # 菠菜、雞蛋、豆腐、鹽
        menu_id2 = db.add_menu_item(
            custom_name="自創營養餐", 
            ingredients_json=str(custom_ingredients)
        )
        print(f"[OK] 已添加菜單項目: 自創營養餐 (ID: {menu_id2})")
        
    except Exception as e:
        print(f"[ERROR] 添加菜單項目失敗: {e}")
    
    print("\n範例資料初始化完成！")

if __name__ == "__main__":
    init_sample_data()
