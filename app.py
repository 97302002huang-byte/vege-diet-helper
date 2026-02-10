import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db_manager import db

# --- 1. 全域設定與 CSS ---
st.set_page_config(
    page_title="植感飲食",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="auto"
)

def inject_custom_css():
    st.markdown("""
    <style>
    /* 隱藏側邊欄 radio圓圈 */
    .stSidebar [data-testid="stRadio"] > div[role="radiogroup"] > div[data-testid="stVerticalBlock"] > div > label > div:first-child {
        display: none;
    }
    
    /* 側邊欄選中狀態樣式 (灰色區塊) */
    .stSidebar [data-testid="stRadio"] > div[role="radiogroup"] > div[data-testid="stVerticalBlock"] > div > label {
        background: transparent;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 2px 0;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .stSidebar [data-testid="stRadio"] > div[role="radiogroup"] > div[data-testid="stVerticalBlock"] > div > label[data-selected="true"] {
        background: #f0f0f0;
        border: 1px solid #e0e0e0;
        font-weight: 600;
        color: #333;
    }
    
    /* 減少按鈕 emoji 與樣式微調 */
    .stButton > button {
        font-weight: 500;
        border-radius: 8px;
    }
    
    /* 極簡標題樣式 */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-weight: 400;
        color: #2c3e50;
    }
    
    /* 隱藏 Plotly 模式列 */
    .js-plotly-plot .plotly .modebar {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 頁面功能函數 ---

def show_ingredients_page():
    # 標題一致性：食材
    st.title("食材")
    
    all_ingredients = db.get_all_ingredients()
    
    if not all_ingredients:
        st.info("資料庫中沒有食材資料，請先匯入 CSV 檔案")
        return
    
    # 篩選器區域
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            categories = db.get_categories()
            selected_categories = st.multiselect("分類", categories, default=[], key="filter_categories")
        
        with col2:
            five_colors = db.get_five_colors()
            selected_colors = st.multiselect("五色", five_colors, default=[], key="filter_colors")
        
        with col3:
            natures = db.get_natures()
            selected_natures = st.multiselect("食性", natures, default=[], key="filter_natures")
        
        with col4:
            search_keyword = st.text_input("搜尋", placeholder="食材名稱或功效...", key="search_keyword")
    
    # 套用篩選條件
    filtered_ingredients = []
    for ingredient in all_ingredients:
        if selected_categories and ingredient['category'] not in selected_categories: continue
        if selected_colors and ingredient['five_color'] not in selected_colors: continue
        if selected_natures and ingredient['nature'] not in selected_natures: continue
        if search_keyword:
            kw = search_keyword.lower()
            if kw not in ingredient['name'].lower() and (not ingredient['effects'] or kw not in ingredient['effects'].lower()):
                continue
        filtered_ingredients.append(ingredient)
    
    st.divider()
    st.caption(f"共 {len(filtered_ingredients)} 項食材")
    
    if not filtered_ingredients:
        st.info("沒有符合篩選條件的食材")
        return
    
    # 準備 DataFrame 資料
    df_data = []
    for ing in filtered_ingredients:
        df_data.append({
            '食材名稱': ing['name'],
            '分類': ing['category'],
            '五色': ing['five_color'],
            '食性': ing['nature'],
            '功效': ing['effects'] or '',
        })
    
    df = pd.DataFrame(df_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "食材名稱": st.column_config.TextColumn("食材", width="medium"),
            "食性": st.column_config.TextColumn("食性", width="small"),
        }
    )

def show_recipes_page():
    # 標題一致性：食譜
    st.title("食譜")
    
    # 新增食譜區塊
    with st.expander("建立新食譜", expanded=False):
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # 使用 key 綁定 session_state
            st.text_input("食譜名稱", key="new_recipe_name")
            st.selectbox("分類", db.get_recipe_categories(), key="new_recipe_category")
            st.text_area("描述", key="new_recipe_description", height=100)
        
        with c2:
            st.write("選擇食材")
            # 使用 Tabs 分類食材
            all_ingredients = db.get_all_ingredients()
            
            # 定義分頁邏輯
            tabs = st.tabs(["🥬 蔬菜/根莖", "🍄 菇/豆/蛋", "🌾 五穀/水果", "🧂 調味/其他"])
            
            # 輔助函數：生成選項
            def get_options(cats):
                return [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients if ing['category'] in cats]

            # Tab 1: 蔬菜類
            with tabs[0]:
                opts1 = get_options(['葉菜類', '根莖類', '花果類'])
                st.multiselect("選擇蔬菜", opts1, key="tab_veg")
            
            # Tab 2: 蛋白質/主食
            with tabs[1]:
                opts2 = get_options(['豆製品', '蛋奶類', '菇菌類'])
                st.multiselect("選擇蛋白質來源", opts2, key="tab_prot")
                
            # Tab 3: 五穀/水果
            with tabs[2]:
                opts3 = get_options(['五穀雜糧', '水果類', '堅果種子類'])
                st.multiselect("選擇主食/配料", opts3, key="tab_grain")
                
            # Tab 4: 其他
            with tabs[3]:
                covered = ['葉菜類', '根莖類', '花果類', '豆製品', '蛋奶類', '菇菌類', '五穀雜糧', '水果類', '堅果種子類']
                opts4 = [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients if ing['category'] not in covered]
                st.multiselect("選擇調味/其他", opts4, key="tab_other")

            # 定義 Callback 函數 (解決 StreamlitAPIException)
            def save_recipe_callback():
                # 從 session_state 獲取值
                r_name = st.session_state.new_recipe_name
                r_cat = st.session_state.new_recipe_category
                r_desc = st.session_state.new_recipe_description
                
                # 合併所有 Tabs 的選擇
                all_sels = (st.session_state.get("tab_veg", []) + 
                            st.session_state.get("tab_prot", []) + 
                            st.session_state.get("tab_grain", []) + 
                            st.session_state.get("tab_other", []))
                
                if r_name and all_sels:
                    try:
                        final_ids = []
                        for option in all_sels:
                            name = option.split("】")[1] if "】" in option else option
                            ing_db = db.get_ingredient_by_name(name)
                            if ing_db:
                                final_ids.append(ing_db['id'])
                        
                        rid = db.add_recipe(r_name, r_cat, r_desc)
                        db.set_recipe_ingredients(rid, final_ids)
                        st.toast('食譜已新增！')
                        
                        # 在 Callback 中清空欄位是安全的
                        st.session_state.new_recipe_name = ""
                        st.session_state.new_recipe_description = ""
                        st.session_state.tab_veg = []
                        st.session_state.tab_prot = []
                        st.session_state.tab_grain = []
                        st.session_state.tab_other = []
                        
                    except Exception as e:
                        st.toast(f"錯誤: {e}", icon="❌")
                else:
                    st.toast("請輸入名稱並選擇至少一種食材", icon="⚠️")

            st.write("") # Spacer
            st.button("儲存食譜", type="primary", use_container_width=True, on_click=save_recipe_callback)
    
    st.divider()
    
    # 顯示食譜列表
    recipes = db.get_all_recipes()
    if recipes:
        cats = db.get_recipe_categories()
        tabs = st.tabs(cats)
        
        for i, cat in enumerate(cats):
            with tabs[i]:
                cat_recipes = [r for r in recipes if r['category'] == cat]
                if cat_recipes:
                    for recipe in cat_recipes:
                        details = db.get_recipe_with_ingredients(recipe['id'])
                        ing_count = len(details.get('ingredients', []))
                        
                        with st.expander(f"{details['name']} ({ing_count}食材)"):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                if details['description']: st.caption(details['description'])
                                ings = [f"{ing['name']}" for ing in details.get('ingredients', [])]
                                st.write(" | ".join(ings))
                            with c2:
                                if st.button("刪除", key=f"del_{recipe['id']}"):
                                    db.delete_recipe(recipe['id'])
                                    st.rerun()
                else:
                    st.caption("無食譜")
    else:
        st.info("暫無食譜")

def show_menu_workspace_page():
    # 標題一致性：菜單
    st.title("菜單")
    
    # 初始化
    if 'menu_workspace' not in st.session_state: st.session_state.menu_workspace = []
    
    # 上方模式選擇
    modes = ["自由配", "🍱 快速樣板", "經典套餐"]
    mode = st.pills(None, options=modes, default=modes[0], selection_mode="single")
    
    if mode == "自由配":
        show_free_style_panel()
    elif mode == "🍱 快速樣板":
        show_quick_template_panel()
    elif mode == "經典套餐":
        show_set_menu_panel()
    
    st.divider()
    
    # 下方工作台 (常駐)
    st.subheader("今日菜單")
    show_workspace_dashboard()
    show_workspace_content()
    show_workspace_analysis()
    show_shopping_list_generator()

def show_free_style_panel():
    col1, col2 = st.columns(2)
    
    # 左欄：從食譜書挑選
    with col1:
        st.subheader("從食譜書挑選")
        
        r_cats = db.get_recipe_categories()
        if r_cats:
            sel_cat = st.selectbox("1. 篩選食譜分類", ["全部顯示"] + r_cats, key="fs_cat_filter")
            
            all_recipes = db.get_all_recipes()
            if sel_cat != "全部顯示":
                filtered_recipes = [r for r in all_recipes if r['category'] == sel_cat]
            else:
                filtered_recipes = all_recipes
                
            if filtered_recipes:
                opts = {f"{r['name']}": r['id'] for r in filtered_recipes}
                sel_recipe = st.selectbox("2. 選擇食譜", list(opts.keys()), key="fs_recipe_sel")
                
                if st.button("加入食譜", key="add_free", use_container_width=True):
                    r = db.get_recipe_by_id(opts[sel_recipe])
                    st.session_state.menu_workspace.append({'type':'recipe', **r})
                    st.rerun()
            else:
                st.info("此分類下暫無食譜")
        else:
            st.info("暫無食譜資料")
            
    # 右欄：自訂菜色 (DIY)
    with col2:
        st.subheader("自訂菜色 (DIY)")
        # 綁定 key 以便在 callback 中使用
        st.text_input("菜名", placeholder="例如: 燙青菜", key="fs_diy_name")
        
        # 獲取所有食材並格式化
        all_ingredients = db.get_all_ingredients()
        formatted_opts = [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients]
        
        # 分類篩選
        ing_cats = db.get_categories()
        filter_ing_cat = st.selectbox("1. 篩選食材分類", ["全部顯示"] + ing_cats, key="fs_diy_cat_filter")
        
        # 決定選項
        if filter_ing_cat == "全部顯示":
            current_cat_opts = formatted_opts
        else:
            current_cat_opts = [opt for opt in formatted_opts if f"【{filter_ing_cat}】" in opt]
            
        # Sticky Selection 邏輯
        current_selection = st.session_state.get("fs_diy_ing_sel", [])
        merged_options = sorted(list(set(current_cat_opts + current_selection)))
        
        st.multiselect("2. 選擇食材", options=merged_options, key="fs_diy_ing_sel")
        
        # 定義 Callback 函數 (解決 StreamlitAPIException)
        def add_diy_callback():
            c_name = st.session_state.fs_diy_name
            c_ings = st.session_state.fs_diy_ing_sel
            
            if c_name and c_ings:
                clean_ings = [opt.split("】")[1] if "】" in opt else opt for opt in c_ings]
                st.session_state.menu_workspace.append({
                    'type':'custom', 
                    'name':c_name, 
                    'ingredients':clean_ings, 
                    'category':'自訂'
                })
                # 清空選擇 (在 Callback 中是安全的)
                st.session_state.fs_diy_name = ""
                st.session_state.fs_diy_ing_sel = []
                st.toast('自訂菜色已加入！')
            elif not c_name:
                st.toast("請輸入菜名", icon="⚠️")

        st.button("加入自訂", key="add_cust_free", use_container_width=True, on_click=add_diy_callback)

def show_quick_template_panel():
    scenarios = ['1人獨享', '2人世界', '3-4人小家庭', '5-6人聚餐', '10人家族聚會', '20人中型派對', '30人大型宴會']
    sel_scn = st.selectbox("選擇用餐情境", scenarios)
    
    blueprints = {
        '1人獨享': {'主食': 1, '配菜': 1},
        '2人世界': {'主菜': 1, '配菜': 1, '主食': 1, '湯品': 1},
        '3-4人小家庭': {'主菜': 2, '配菜': 1, '主食': 1, '湯品': 1},
        '5-6人聚餐': {'主菜': 3, '配菜': 2, '主食': 1, '湯品': 1, '甜點/飲料': 1},
        '10人家族聚會': {'主菜': 4, '配菜': 2, '主食': 2, '湯品': 1, '甜點/飲料': 1},
        '20人中型派對': {'主菜': 5, '配菜': 3, '主食': 2, '湯品': 2, '甜點/飲料': 2},
        '30人大型宴會': {'主菜': 6, '配菜': 4, '主食': 3, '湯品': 2, '甜點/飲料': 3}
    }
    
    bp = blueprints.get(sel_scn, {})
    if 'temp_sels' not in st.session_state: st.session_state.temp_sels = {}
    
    cols = st.columns(4)
    idx = 0
    for cat, count in bp.items():
        for i in range(count):
            key = f"{cat}_{i}"
            with cols[idx % 4]:
                if key in st.session_state.temp_sels:
                    item = st.session_state.temp_sels[key]
                    st.success(f"{cat}: {item['name']}")
                    if st.button("移除", key=f"rm_{key}"):
                        del st.session_state.temp_sels[key]
                        st.rerun()
                else:
                    if st.button(f"＋ {cat}", key=f"add_{key}", type="primary", use_container_width=True):
                        show_slot_dialog(key, cat)
            idx += 1
            
    if st.session_state.temp_sels:
        if st.button("納入菜單", type="primary"):
            for v in st.session_state.temp_sels.values():
                st.session_state.menu_workspace.append(v)
            st.session_state.temp_sels = {}
            st.rerun()

@st.dialog("選擇菜色")
def show_slot_dialog(key, cat):
    t1, t2 = st.tabs(["從食譜書挑選", "DIY 自訂"])
    with t1:
        rs = [r for r in db.get_all_recipes() if r['category'] == cat]
        if rs:
            opts = {r['name']: r for r in rs}
            s = st.selectbox("選擇", list(opts.keys()), key=f"s_{key}")
            if st.button("確認", key=f"b_{key}"):
                r = opts[s]
                st.session_state.temp_sels[key] = {'type':'recipe', **r}
                st.rerun()
        else:
            st.info("無此類食譜")
    with t2:
        c_name = st.text_input("菜名", key=f"cn_{key}")
        
        # DIY 食材選擇優化 (Sticky Selection)
        all_ingredients = db.get_all_ingredients()
        formatted_opts = [f"【{ing['category']}】{ing['name']}" for ing in all_ingredients]
        
        ing_cats = db.get_categories()
        filter_cat = st.selectbox("篩選食材分類", ["全部顯示"] + ing_cats, key=f"diy_filter_{key}")
        
        if filter_cat == "全部顯示":
            current_cat_opts = formatted_opts
        else:
            current_cat_opts = [opt for opt in formatted_opts if f"【{filter_cat}】" in opt]
            
        # 確保已選項目不消失
        sel_key = f"ci_{key}"
        current_selection = st.session_state.get(sel_key, [])
        merged_options = sorted(list(set(current_cat_opts + current_selection)))
        
        c_ings = st.multiselect("包含食材", options=merged_options, key=sel_key)
        
        if st.button("確認自訂", key=f"bc_{key}"):
            if c_name:
                clean_ings = [opt.split("】")[1] if "】" in opt else opt for opt in c_ings]
                st.session_state.temp_sels[key] = {
                    'type':'custom', 
                    'name':c_name, 
                    'category': cat,
                    'ingredients': clean_ings
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
            
            # 簡化顯示
            for r in details['recipes']:
                desc = f" ({r['description']})" if r['description'] else ""
                st.write(f"• {r['name']}{desc}")
                
            if st.button("納入菜單", type="primary"):
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
    st.markdown(" | ".join(badges))

def show_workspace_content():
    if not st.session_state.menu_workspace: return
    
    for i, item in enumerate(st.session_state.menu_workspace):
        with st.container():
            c1, c2 = st.columns([5, 1])
            with c1:
                st.write(f"**{item['name']}**")
            with c2:
                if st.button("✕", key=f"rm_ws_{i}"):
                    st.session_state.menu_workspace.pop(i)
                    st.rerun()
    
    if st.button("清空", key="clr_ws"):
        st.session_state.menu_workspace = []
        st.rerun()

def show_workspace_analysis():
    if not st.session_state.menu_workspace: return
    
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("五色平衡")
        colors_list = []
        for item in st.session_state.menu_workspace:
            # 獲取食材顏色
            ings = []
            if item['type'] == 'recipe':
                ings = db.get_recipe_with_ingredients(item['id']).get('ingredients', [])
                for ing in ings: colors_list.append(ing['five_color'])
            elif item['type'] == 'custom' and item.get('ingredients'):
                # 查詢自訂食材的顏色
                for ing_name in item['ingredients']:
                    ing_db = db.get_ingredient_by_name(ing_name)
                    if ing_db: colors_list.append(ing_db['five_color'])

        if colors_list:
            counts = {c: colors_list.count(c) for c in set(colors_list) if c != '未知'}
            
            # 純色塊甜甜圈圖
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
        st.write("食性分析")
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
            
            res = "平和均衡 ⚖️"
            if score > 0.5: res = "偏溫補 🔥"
            elif score < -0.5: res = "偏清涼 ❄️"
            
            st.markdown(f"<h4 style='text-align:center;margin:0;'>{res}</h4>", unsafe_allow_html=True)
            
            # 漸層滑桿
            pct = (max(-1, min(1, score/1.5)) + 1) / 2 * 100
            st.markdown(f"""
            <div style="margin-top:15px; font-size:0.8em; color:#666; display:flex; justify-content:space-between;">
                <span>❄️寒</span><span>平</span><span>熱🔥</span>
            </div>
            <div style="height:8px; background:linear-gradient(90deg, #81D4FA, #A5D6A7, #EF9A9A); border-radius:4px; position:relative;">
                <div style="position:absolute; left:{pct}%; top:-4px; width:4px; height:16px; background:#333; transform:translateX(-50%); border-radius:2px;"></div>
            </div>
            """, unsafe_allow_html=True)

def show_shopping_list_generator():
    if not st.session_state.menu_workspace: return
    
    # 使用 session_state 控制顯示狀態 (修復消失 BUG)
    if 'show_shop_list' not in st.session_state: st.session_state.show_shop_list = False
    
    if st.button("產生採購清單", type="primary", use_container_width=True):
        st.session_state.show_shop_list = not st.session_state.show_shop_list
    
    if st.session_state.show_shop_list:
        st.divider()
        st.subheader("採購清單")
        
        core_ings = []
        condiments = []
        
        # 收集食材
        for item in st.session_state.menu_workspace:
            ings = []
            if item['type'] == 'recipe':
                ings = db.get_recipe_with_ingredients(item['id']).get('ingredients', [])
                for ing in ings:
                    if ing['is_condiment']: condiments.append(ing['name'])
                    else: core_ings.append(ing['name'])
            elif item['type'] == 'custom':
                # 自訂食材視為核心食材
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
            sel = st.multiselect("勾選缺少項目", condiments, key="ms_conds")
            st.session_state.miss_conds = sel
            
        final = core_ings + st.session_state.miss_conds
        if final:
            txt = "\n".join([f"- {i}" for i in final])
            st.code(txt, language="text")

def main():
    inject_custom_css()
    
    st.sidebar.title("植感飲食")
    pages = ["食材", "食譜", "菜單"]
    pg = st.sidebar.radio("導覽", pages, label_visibility="collapsed")
    
    st.sidebar.divider()
    st.sidebar.subheader("收藏")
    st.sidebar.caption(f"食材: {len(db.get_all_ingredients())}")
    st.sidebar.caption(f"食譜: {len(db.get_all_recipes())}")
    
    if pg == "食材": show_ingredients_page()
    elif pg == "食譜": show_recipes_page()
    elif pg == "菜單": show_menu_workspace_page()

if __name__ == "__main__":
    main()