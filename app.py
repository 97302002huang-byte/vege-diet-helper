import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db_manager import db

# --- 1. 全域設定與 CSS ---
st.set_page_config(
    page_title="植感飲食",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
    <style>
    /* 1. 極簡標題樣式 */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-weight: 400;
        color: #2c3e50;
        text-align: center;
    }
    
    /* 2. 導航頁籤 (Segmented Control) 滿版均分優化 */
    /* 強制讓 Segmented Control 的外層容器填滿 */
    div[data-testid="stSegmentedControl"] {
        width: 100% !important;
    }
    div[data-testid="stSegmentedControl"] > div {
        width: 100% !important;
        display: flex !important;
    }
    /* 關鍵：讓每個選項按鈕平分寬度 (Flex Grow) */
    div[data-testid="stSegmentedControl"] button {
        flex: 1 !important;
        min-width: 0px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        justify-content: center !important;
    }
    
    /* 3. 今日菜單 Data Editor 優化 */
    /* 隱藏 Data Editor 的索引列 (如果有的話) */
    div[data-testid="stDataFrame"] table thead th:first-child {
        display: none;
    }
    div[data-testid="stDataFrame"] table tbody td:first-child {
        display: none;
    }

    /* 隱藏 Plotly 模式列 */
    .js-plotly-plot .plotly .modebar {
        display: none !important;
    }
    
    /* 一般按鈕樣式 */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 頁面功能函數 ---

def show_ingredients_page():
    # 簡易篩選器
    categories = ["全部"] + db.get_categories()
    selected_cat = st.pills("分類篩選", categories, default="全部", selection_mode="single", label_visibility="collapsed")
    
    # 搜尋欄位
    search_keyword = st.text_input("搜尋", placeholder="輸入名稱或功效...", key="search_keyword", label_visibility="collapsed")
    st.write("") # Spacer
    
    # 資料處理
    all_ingredients = db.get_all_ingredients()
    filtered_ingredients = []
    
    for ingredient in all_ingredients:
        if selected_cat != "全部" and ingredient['category'] != selected_cat:
            continue
        if search_keyword:
            kw = search_keyword.lower()
            if kw not in ingredient['name'].lower() and (not ingredient['effects'] or kw not in ingredient['effects'].lower()):
                continue
        filtered_ingredients.append(ingredient)
    
    st.caption(f"共 {len(filtered_ingredients)} 項食材")
    
    if not filtered_ingredients:
        st.info("沒有符合條件的食材")
        return
    
    df_data = []
    for ing in filtered_ingredients:
        df_data.append({
            '食材名稱': ing['name'],
            '食性': ing['nature'],
            '五色': ing['five_color'],
            '功效': ing['effects'] or '',
        })
    
    df = pd.DataFrame(df_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "食材名稱": st.column_config.TextColumn("食材", width="small", pinned=True),
            "食性": st.column_config.TextColumn("食性", width="small"),
            "五色": st.column_config.TextColumn("五色", width="small"),
            "功效": st.column_config.TextColumn("功效", width="large"),
        }
    )

def show_recipes_page():
    with st.expander("➕ 建立新食譜", expanded=False):
        st.text_input("食譜名稱", key="new_recipe_name")
        st.selectbox("分類", db.get_recipe_categories(), key="new_recipe_category")
        st.text_area("描述", key="new_recipe_description", height=80)
        
        st.write("---")
        st.write("**選擇食材**")
        
        all_ingredients = db.get_all_ingredients()
        tabs = st.tabs(["🥬 蔬果", "🍄 蛋豆菇", "🌾 主食", "🧂 其他"])
        
        def get_options(cats):
            return [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients if ing['category'] in cats]

        with tabs[0]:
            opts1 = get_options(['葉菜類', '根莖類', '花果類', '水果類'])
            st.multiselect("選擇蔬果", opts1, key="tab_veg")
        
        with tabs[1]:
            opts2 = get_options(['豆製品', '蛋奶類', '菇菌類'])
            st.multiselect("選擇蛋白質", opts2, key="tab_prot")
            
        with tabs[2]:
            opts3 = get_options(['五穀雜糧', '堅果種子類'])
            st.multiselect("選擇主食", opts3, key="tab_grain")
            
        with tabs[3]:
            covered = ['葉菜類', '根莖類', '花果類', '水果類', '豆製品', '蛋奶類', '菇菌類', '五穀雜糧', '堅果種子類']
            opts4 = [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients if ing['category'] not in covered]
            st.multiselect("選擇調味/其他", opts4, key="tab_other")

        def save_recipe_callback():
            r_name = st.session_state.new_recipe_name
            r_cat = st.session_state.new_recipe_category
            r_desc = st.session_state.new_recipe_description
            all_sels = (st.session_state.get("tab_veg", []) + st.session_state.get("tab_prot", []) + 
                        st.session_state.get("tab_grain", []) + st.session_state.get("tab_other", []))
            
            if r_name and all_sels:
                try:
                    final_ids = []
                    for option in all_sels:
                        name = option.split("】")[1] if "】" in option else option
                        ing_db = db.get_ingredient_by_name(name)
                        if ing_db: final_ids.append(ing_db['id'])
                    
                    rid = db.add_recipe(r_name, r_cat, r_desc)
                    db.set_recipe_ingredients(rid, final_ids)
                    st.toast('✅ 食譜已新增！')
                    st.session_state.new_recipe_name = ""
                    st.session_state.new_recipe_description = ""
                    st.session_state.tab_veg = []
                    st.session_state.tab_prot = []
                    st.session_state.tab_grain = []
                    st.session_state.tab_other = []
                except Exception as e:
                    st.toast(f"錯誤: {e}", icon="❌")
            else:
                st.toast("請輸入名稱並選擇食材", icon="⚠️")

        st.button("儲存食譜", type="primary", use_container_width=True, on_click=save_recipe_callback)
    
    st.divider()
    
    recipes = db.get_all_recipes()
    if recipes:
        cats = db.get_recipe_categories()
        view_cat = st.selectbox("瀏覽分類", ["全部"] + cats)
        
        display_recipes = recipes if view_cat == "全部" else [r for r in recipes if r['category'] == view_cat]
        
        if display_recipes:
            for recipe in display_recipes:
                details = db.get_recipe_with_ingredients(recipe['id'])
                ing_count = len(details.get('ingredients', []))
                
                with st.expander(f"{details['name']} ({ing_count}食材)"):
                    if details['description']: st.caption(details['description'])
                    ings = [f"{ing['name']}" for ing in details.get('ingredients', [])]
                    st.write("、".join(ings))
        else:
            st.info("此分類暫無食譜")
    else:
        st.info("暫無食譜")

def show_menu_workspace_page():
    if 'menu_workspace' not in st.session_state: st.session_state.menu_workspace = []
    
    modes = ["自由配", "快速樣板", "經典套餐"]
    mode = st.segmented_control(None, options=modes, default=modes[0], selection_mode="single", key="menu_mode_selector")
    
    if mode == "自由配":
        show_free_style_panel()
    elif mode == "快速樣板":
        show_quick_template_panel()
    elif mode == "經典套餐":
        show_set_menu_panel()
    
    st.divider()
    
    st.subheader("今日菜單")
    show_workspace_dashboard()
    show_workspace_content_table() # 改用新的表格呈現方式
    show_workspace_analysis()
    show_shopping_list_generator()

def show_free_style_panel():
    st.caption("方式 A：從食譜挑選")
    
    r_cats = db.get_recipe_categories()
    if r_cats:
        c1, c2 = st.columns([1, 2])
        with c1:
            sel_cat = st.selectbox("食譜分類", ["全部"] + r_cats, key="fs_cat_filter", label_visibility="collapsed")
        with c2:
            all_recipes = db.get_all_recipes()
            if sel_cat != "全部":
                filtered_recipes = [r for r in all_recipes if r['category'] == sel_cat]
            else:
                filtered_recipes = all_recipes
                
            if filtered_recipes:
                opts = {f"{r['name']}": r['id'] for r in filtered_recipes}
                sel_recipe = st.selectbox("選擇食譜", list(opts.keys()), key="fs_recipe_sel", label_visibility="collapsed")
                
                if st.button("＋ 加入", key="add_free", use_container_width=True):
                    r = db.get_recipe_by_id(opts[sel_recipe])
                    st.session_state.menu_workspace.append({'type':'recipe', **r})
                    st.toast(f"已加入：{r['name']}")
            else:
                st.info("無食譜")
    
    st.write("")
    st.caption("方式 B：自訂菜色 (DIY)")
    
    c_name = st.text_input("菜名", placeholder="例如: 燙青菜", key="fs_diy_name")
    
    all_ingredients = db.get_all_ingredients()
    formatted_opts = [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients]
    
    filter_ing_cat = st.selectbox("篩選食材分類", ["全部"] + db.get_categories(), key="fs_diy_cat_filter")
    
    if filter_ing_cat == "全部":
        current_cat_opts = formatted_opts
    else:
        current_cat_opts = [opt for opt in formatted_opts if f"【{filter_ing_cat}】" in opt]
        
    current_selection = st.session_state.get("fs_diy_ing_sel", [])
    merged_options = sorted(list(set(current_cat_opts + current_selection)))
    
    st.multiselect("包含食材", options=merged_options, key="fs_diy_ing_sel")
    
    def add_diy_callback():
        c_name = st.session_state.fs_diy_name
        c_ings = st.session_state.fs_diy_ing_sel
        if c_name and c_ings:
            clean_ings = [opt.split("】")[1] if "】" in opt else opt for opt in c_ings]
            st.session_state.menu_workspace.append({
                'type':'custom', 'name':c_name, 'ingredients':clean_ings, 'category':'自訂'
            })
            st.session_state.fs_diy_name = ""
            st.session_state.fs_diy_ing_sel = []
            st.toast('✅ 自訂菜色已加入！')
        elif not c_name:
            st.toast("請輸入菜名", icon="⚠️")

    st.button("＋ 加入", key="add_cust_free", use_container_width=True, on_click=add_diy_callback)

def show_quick_template_panel():
    scenarios = ['1人獨享', '2人世界', '3-4人小家庭', '5-6人聚餐', '10人家族聚會', '20人中型派對']
    sel_scn = st.selectbox("選擇用餐情境", scenarios)
    
    blueprints = {
        '1人獨享': {'主食': 1, '配菜': 1},
        '2人世界': {'主菜': 1, '配菜': 1, '主食': 1, '湯品': 1},
        '3-4人小家庭': {'主菜': 2, '配菜': 1, '主食': 1, '湯品': 1},
        '5-6人聚餐': {'主菜': 3, '配菜': 2, '主食': 1, '湯品': 1, '甜點/飲料': 1},
        '10人家族聚會': {'主菜': 4, '配菜': 2, '主食': 2, '湯品': 1, '甜點/飲料': 1},
        '20人中型派對': {'主菜': 5, '配菜': 3, '主食': 2, '湯品': 2, '甜點/飲料': 2}
    }
    
    bp = blueprints.get(sel_scn, {})
    if 'temp_sels' not in st.session_state: st.session_state.temp_sels = {}
    
    for cat, count in bp.items():
        for i in range(count):
            key = f"{cat}_{i}"
            if key in st.session_state.temp_sels:
                item = st.session_state.temp_sels[key]
                c1, c2 = st.columns([0.85, 0.15], vertical_alignment="center")
                with c1: st.success(f"{cat}: {item['name']}")
                with c2: 
                    if st.button("✕", key=f"rm_{key}"):
                        del st.session_state.temp_sels[key]
                        st.rerun()
            else:
                if st.button(f"＋ 選擇 {cat}", key=f"add_{key}", type="secondary", use_container_width=True):
                    show_slot_dialog(key, cat)
            
    if st.session_state.temp_sels:
        st.write("")
        if st.button("🚀 全部納入菜單", type="primary", use_container_width=True):
            for v in st.session_state.temp_sels.values():
                st.session_state.menu_workspace.append(v)
            st.session_state.temp_sels = {}
            st.toast("已加入工作台！")
            st.rerun()

@st.dialog("選擇菜色")
def show_slot_dialog(key, cat):
    t1, t2 = st.tabs(["從食譜挑選", "DIY"])
    with t1:
        rs = [r for r in db.get_all_recipes() if r['category'] == cat]
        if rs:
            opts = {r['name']: r for r in rs}
            s = st.selectbox("選擇", list(opts.keys()), key=f"s_{key}")
            if st.button("確認", key=f"b_{key}", type="primary", use_container_width=True):
                r = opts[s]
                st.session_state.temp_sels[key] = {'type':'recipe', **r}
                st.rerun()
        else:
            st.info("無此類食譜")
    with t2:
        c_name = st.text_input("菜名", key=f"cn_{key}")
        all_ings = [i['name'] for i in db.get_all_ingredients()]
        c_ings = st.multiselect("食材", options=all_ings, key=f"ci_{key}")
        
        if st.button("確認", key=f"bc_{key}", type="primary", use_container_width=True):
            if c_name:
                st.session_state.temp_sels[key] = {
                    'type':'custom', 'name':c_name, 'category': cat, 'ingredients': c_ings
                }
                st.rerun()

def show_set_menu_panel():
    sets = db.get_all_menu_sets()
    if sets:
        opts = {s['name']: s['id'] for s in sets}
        s_name = st.selectbox("選擇套餐", list(opts.keys()))
        if s_name:
            sid = opts[s_name]
            details = db.get_menu_set_with_recipes(sid)
            if details['description']: st.caption(details['description'])
            
            for r in details['recipes']:
                desc = f" ({r['description']})" if r['description'] else ""
                st.write(f"• {r['name']}{desc}")
                
            if st.button("納入菜單", type="primary", use_container_width=True):
                for r in details['recipes']:
                    st.session_state.menu_workspace.append({'type':'recipe', **r})
                st.toast("已載入套餐！")
                st.rerun()
    else:
        st.info("暫無套餐")

def show_workspace_dashboard():
    if not st.session_state.menu_workspace:
        st.caption("尚未加入菜色")
        return
        
    counts = {}
    for item in st.session_state.menu_workspace:
        cat = item.get('category', '自訂')
        counts[cat] = counts.get(cat, 0) + 1
    
    badges = [f"{k}: {v}" for k,v in counts.items()]
    st.info(" | ".join(badges), icon="🍽️")

# ★★★ 新版：使用 Data Editor 取代按鈕清單 ★★★
def show_workspace_content_table():
    if not st.session_state.menu_workspace: return
    
    # 1. 準備資料給 Data Editor
    # 我們需要一個 DataFrame，包含 '菜名' 和 '刪除' (checkbox)
    data = []
    for item in st.session_state.menu_workspace:
        data.append({
            "菜名": item['name'],
            "刪除": False # 預設不刪除
        })
    
    df = pd.DataFrame(data)
    
    # 2. 顯示 Data Editor
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "菜名": st.column_config.TextColumn("菜名", disabled=True), # 禁止編輯菜名
            "刪除": st.column_config.CheckboxColumn("移除", width="small") # Checkbox
        },
        key="workspace_editor"
    )
    
    # 3. 檢查是否有被勾選刪除的項目
    # 如果使用者勾選了，edited_df 裡的 '刪除' 欄位會變成 True
    if edited_df['刪除'].any():
        # 保留那些 '刪除' 為 False 的項目 (即未被勾選的)
        indices_to_keep = edited_df[~edited_df['刪除']].index.tolist()
        
        # 根據 index 更新 session_state
        new_workspace = [st.session_state.menu_workspace[i] for i in indices_to_keep]
        st.session_state.menu_workspace = new_workspace
        
        # 重新整理頁面
        st.rerun()

    if st.button("清空工作台", key="clr_ws", use_container_width=True):
        st.session_state.menu_workspace = []
        st.rerun()

def show_workspace_analysis():
    if not st.session_state.menu_workspace: return
    
    st.write("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("**五色平衡**")
        colors_list = []
        for item in st.session_state.menu_workspace:
            ings = []
            if item['type'] == 'recipe':
                ings = db.get_recipe_with_ingredients(item['id']).get('ingredients', [])
                for ing in ings: colors_list.append(ing['five_color'])
            elif item['type'] == 'custom' and item.get('ingredients'):
                for ing_name in item['ingredients']:
                    ing_db = db.get_ingredient_by_name(ing_name)
                    if ing_db: colors_list.append(ing_db['five_color'])

        if colors_list:
            counts = {c: colors_list.count(c) for c in set(colors_list) if c != '未知'}
            color_map = {'青':'#4CAF50', '赤':'#F44336', '黃':'#FFC107', '白':'#E0E0E0', '黑':'#424242'}
            labels = list(counts.keys())
            values = list(counts.values())
            cols = [color_map.get(l, '#999') for l in labels]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values, hole=0.6,
                marker_colors=cols, textinfo='none', hoverinfo='skip', showlegend=False
            )])
            fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), height=150, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
            
    with c2:
        st.write("**食性分析**")
        natures = []
        for item in st.session_state.menu_workspace:
            if item['type'] == 'recipe':
                ings = db.get_recipe_with_ingredients(item['id']).get('ingredients', [])
                for ing in ings: natures.append(ing['nature'])
            elif item['type'] == 'custom' and item.get('ingredients'):
                for ing_name in item['ingredients']:
                    ing_db = db.get_ingredient_by_name(ing_name)
                    if ing_db: natures.append(ing_db['nature'])
        
        if natures:
            scores = {'熱':2, '溫':1, '平':0, '涼':-1, '寒':-2}
            score = sum(scores.get(n,0) for n in natures) / len(natures)
            
            pct = (max(-1, min(1, score/1.5)) + 1) / 2 * 100
            
            st.markdown(f"""
            <div style="margin-top:20px; font-size:0.8em; color:#666; display:flex; justify-content:space-between;">
                <span>❄️寒</span><span>平</span><span>熱🔥</span>
            </div>
            <div style="height:8px; background:linear-gradient(90deg, #81D4FA, #A5D6A7, #EF9A9A); border-radius:4px; position:relative; margin-bottom: 30px;">
                <div style="position:absolute; left:{pct}%; top:-4px; width:4px; height:16px; background:#333; transform:translateX(-50%); border-radius:2px;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") 

def show_shopping_list_generator():
    if not st.session_state.menu_workspace: return
    
    if 'show_shop_list' not in st.session_state: st.session_state.show_shop_list = False
    
    if st.button("產生採購清單", type="primary", use_container_width=True):
        st.session_state.show_shop_list = not st.session_state.show_shop_list
    
    if st.session_state.show_shop_list:
        st.divider()
        st.subheader("採購清單")
        
        core_ings = []
        condiments = []
        
        for item in st.session_state.menu_workspace:
            ings = []
            if item['type'] == 'recipe':
                ings = db.get_recipe_with_ingredients(item['id']).get('ingredients', [])
                for ing in ings:
                    if ing['is_condiment']: condiments.append(ing['name'])
                    else: core_ings.append(ing['name'])
            elif item['type'] == 'custom':
                for ing in item.get('ingredients', []):
                    core_ings.append(ing)
        
        core_ings = sorted(list(set(core_ings)))
        condiments = sorted(list(set(condiments)))
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**核心食材**")
            for i in core_ings: st.write(f"• {i}")
        
        with c2:
            st.write("**調味品檢查**")
            if 'miss_conds' not in st.session_state: st.session_state.miss_conds = []
            
            if len(condiments) < 10:
                sel = st.pills("勾選缺少項目", condiments, selection_mode="multi", key="ms_conds")
            else:
                sel = st.multiselect("勾選缺少項目", condiments, key="ms_conds_multi")
            st.session_state.miss_conds = sel
            
        final = core_ings + st.session_state.miss_conds
        if final:
            txt = "\n".join([f"- {i}" for i in final])
            st.code(txt, language="text")

def main():
    inject_custom_css()
    
    st.markdown("<h1>植感飲食</h1>", unsafe_allow_html=True)
    
    pages = ["食材", "食譜", "菜單"]
    pg = st.segmented_control(None, options=pages, default=pages[0], selection_mode="single", key="main_nav")
    
    if not pg: pg = "食材"

    if pg == "食材": show_ingredients_page()
    elif pg == "食譜": show_recipes_page()
    elif pg == "菜單": show_menu_workspace_page()

if __name__ == "__main__":
    main()
