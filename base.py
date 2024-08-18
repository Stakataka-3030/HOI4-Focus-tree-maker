import pygame 
import os 
import json  # 用于保存和加载国策树
import tkinter as tk
from tkinter import filedialog  # 用于文件选择
pygame.init() 
pygame.mixer.init() 
os.environ['SDL_IME_SHOW_UI'] = "1"
small_font = pygame.font.SysFont("simhei", 20)  # 较小的字体

# 说明文本内容
instruction_text = "作者：stakataka_3030,开源代码地址：\n适配1.14.7 stella polaris，以下是使用说明：\n名称（可中文），id（英文、数字、下划线），gfx（可不填，会自动生成为GFX_id）\n位置（x，y，相对于第一个国策），时间（日，导出时会自动转化为p时间）\n前置国策（可不填，多个请用英文,分隔，暂时只能做必选，二选一请自行在导出的文件里调整）\n互斥国策（可不填，请用英文,分隔）\n，互斥国策两个都需要填对方的id，互斥显示暂时有问题，请谅解。"
# 设置初始窗口大小 
width = 800   
height = 600   
selected_info_index = -1  # 用于记录选中的国策索引 
selected_info_index_2 = -1 
# 颜色定义 
BLACK = (0, 0, 0) 
WHITE = (255, 255, 255) 
GRAY = (180, 180, 180)  # 灰色背景调浅 
DARK_GRAY = (100, 100, 100)   
BUTTON_COLOR = DARK_GRAY   
SELECTED_COLOR = (0, 255, 0)   
# 初始化计数器 
i = 0 
scroll_offset = 0
# 创建可调整大小的窗口 
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE) 
pygame.display.set_caption("HOI4 Focustree creator Powered by Stakataka_3030") 
# 创建时钟 
clock = pygame.time.Clock() 
running = True 
# 定义按钮 
button_rect = pygame.Rect(width // 2 - 50, height - 70, 100, 50)   
save_button_rect = pygame.Rect(width // 2 - 150, height - 70, 100, 50)
load_button_rect = pygame.Rect(width // 2 + 50, height - 70, 100, 50)
export_button_rect = pygame.Rect(width // 2 + 150, height - 70, 100, 50)  # 新增导出按钮

# 加载字体 
myfont = pygame.font.SysFont("simhei", 30)   
input_boxes = [] 
input_y_positions = []   
box_width = 100 
box_height = 50 
input_instructions = [ 
    "国策名称",  
    "国策id",  
    "国策gfx",  
    "相对x坐标",  
    "相对y坐标", 
    "国策时间",        # 新增的输入框 
    "前置国策id",      # 新增的输入框 
    "互斥国策id"       # 新增的输入框 
] 
# 新的输入框位置 
input_y_positions = [ 
    height // 2 + 10,  
    height // 2 + 60,  
    height // 2 + 110,  
    height // 2 + 160,  
    height // 2 + 210, 
    height // 2 + 260,  # 国策时间 
    height // 2 + 310,  # 前置国策id 
    height // 2 + 360   # 互斥国策id 
] 
# 创建输入框 
for i, y_pos in enumerate(input_y_positions): 
    input_boxes.append(pygame.Rect(10, y_pos, 500, 40))   
input_texts = ["", "", "", "", "", "", "", ""]  # 初始化所有输入框的文本内容 
focus_num = 0 
selected_index = -1   
saved_select_info_index = -1
# 记录退格键是否处于按下状态 
backspace_pressed = False 
# 记录退格键开始按下的时间 
backspace_press_start_time = 0 
shown_infos = []  # 用于存储所有显示的国策信息 
def validate_input(text): 
    try: 
        int(text) 
        return True 
    except ValueError: 
        text = text.strip() 
        if text == '-':   
            return True 
        if text.startswith('-'): 
            if text[1:].isdigit(): 
                return True 
        return False 
def is_input_complete():
    # 检查国策名称、id、x 坐标和 y 坐标是否都有输入
    if not input_texts[0] or not input_texts[1] or not validate_input(input_texts[3]) or not validate_input(input_texts[4])or not validate_input(input_texts[5]):
        return False
    return True
def show_input_instructions(screen, box, font, instruction):  
    if not box.collidepoint(pygame.mouse.get_pos()) and len(input_texts[input_boxes.index(box)]) == 0:  
        instruction_surface = font.render(instruction, True, BLACK)  # 提示文字颜色改为黑色  
        screen.blit(instruction_surface, (box.x + 5, box.y + 5))  
def show_info_boxes(screen, font, scroll_offset):
    global selected_info_index, focus_num, saved_select_info_index
    box_width = 100
    box_height = 50
    if shown_infos:
        center_x = screen.get_width() // 2
        first_x = center_x - box_width // 2
        first_y = 0 + scroll_offset  # 应用滚动偏移量
        for index, shown_info in enumerate(shown_infos):
            if index == 0:
                x = first_x
                y = first_y
            else:
                x = first_x + (int(shown_info[3])) * 100
                y = first_y + (int(shown_info[4])) * 75
            
            info_box_rect = pygame.Rect(x, y, box_width, box_height)
            extended_rect = pygame.Rect(x, y, box_width + 50, box_height + 50)

            # 处理鼠标悬停和点击事件（保持不变）
            if extended_rect.collidepoint(pygame.mouse.get_pos()):
                selected_info_index = index
                modify_button_rect = pygame.Rect(x + box_width, y, 50, 25)
                delete_button_rect = pygame.Rect(x + box_width, y + 25, 50, 25)
                pygame.draw.rect(screen, BUTTON_COLOR, modify_button_rect)
                modify_text = font.render("修改", True, WHITE)
                modify_text_rect = modify_text.get_rect(center=modify_button_rect.center)
                screen.blit(modify_text, modify_text_rect)
                pygame.draw.rect(screen, BUTTON_COLOR, delete_button_rect)
                delete_text = font.render("删除", True, WHITE)
                delete_text_rect = delete_text.get_rect(center=delete_button_rect.center)
                screen.blit(delete_text, delete_button_rect)

                # 处理修改和删除按钮的点击事件（保持不变）
                if modify_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    for i in range(len(input_texts)):
                        input_texts[i] = str(shown_infos[selected_info_index][i])
                    selected_index = 0
                    saved_select_info_index = selected_info_index
                    selected_info_index = -1
                if delete_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    del shown_infos[selected_info_index]
                    selected_info_index = -1
                    focus_num -= 1

            # 绘制国策框
            pygame.draw.rect(screen, BLACK, info_box_rect, 2)
            content_surface = font.render(str(shown_info[0]), True, BLACK)
            content_rect = content_surface.get_rect(center=(info_box_rect.x + info_box_rect.width // 2, info_box_rect.y + 25))
            screen.blit(content_surface, content_rect)

            # 绘制前置国策的折线
            pre_focus_ids = [id.strip() for id in shown_info[6].replace(';', ',').split(',')]
            pre_focus_positions = []
            for pre_focus_id in pre_focus_ids:
                for pre_info in shown_infos:
                    if pre_info[1] == pre_focus_id:
                        pre_x = int(pre_info[3]) * 100 + box_width // 2 + first_x
                        pre_y = int(pre_info[4]) * 75 + box_height + scroll_offset  # 应用滚动偏移量
                        pre_focus_positions.append((pre_x, pre_y))
                        break
            
            # 绘制前置国策的线条
            if pre_focus_positions:
                for pre_x, pre_y in pre_focus_positions:
                    if pre_y < y + scroll_offset:  # 确保前置国策在新国策上方
                        mid_x = (pre_x + x + box_width // 2) // 2
                        mid_y = pre_y + (y - pre_y) // 2
                        pygame.draw.line(screen, BLACK, (pre_x, pre_y), (pre_x, mid_y), 2)
                        pygame.draw.line(screen, BLACK, (pre_x, mid_y), (x + box_width // 2, mid_y), 2)
                        pygame.draw.line(screen, BLACK, (x + box_width // 2, mid_y), (x + box_width // 2, y), 2)

            # 绘制互斥国策的线条
            mutex_ids = [id.strip() for id in shown_info[7].replace(';', ',').split(',')]
            mutex_positions = []
            for mutex_id in mutex_ids:
                for mutex_info in shown_infos:
                    if mutex_info[1] == mutex_id:
                        mutex_x = int(mutex_info[3]) * 100 + box_width // 2 + first_x
                        mutex_y = int(mutex_info[4]) * 75 + box_height + scroll_offset
                        mutex_positions.append((mutex_x, mutex_y))
                        break
            
            # 只在互斥国策在当前国策同一行时绘制直线
            if len(mutex_positions) > 1:
                for i in range(len(mutex_positions) - 1):
                    if mutex_positions[i][1] == mutex_positions[i + 1][1]:  # 确保在同一行
                        pygame.draw.line(screen, BLACK, mutex_positions[i], mutex_positions[i + 1], 2)
            # 绘制互斥国策的箭头和感叹号（保持不变）
            if len(mutex_positions) == 2:
                mid_x = (mutex_positions[0][0] + mutex_positions[1][0]) // 2
                mid_y = mutex_positions[0][1]
                pygame.draw.line(screen, BLACK, mutex_positions[0], mutex_positions[1], 2)
                arrow_length = 10
                pygame.draw.polygon(screen, BLACK, [(mutex_positions[0][0], mutex_positions[0][1]),
                                                     (mutex_positions[0][0] - arrow_length, mutex_positions[0][1] - arrow_length),
                                                     (mutex_positions[0][0] - arrow_length, mutex_positions[0][1] + arrow_length)])
                pygame.draw.polygon(screen, BLACK, [(mutex_positions[1][0], mutex_positions[1][1]),
                                                     (mutex_positions[1][0] + arrow_length, mutex_positions[1][1] - arrow_length),
                                                     (mutex_positions[1][0] + arrow_length, mutex_positions[1][1] + arrow_length)])
                exclamation_surface = font.render("!", True, BLACK)
                exclamation_rect = exclamation_surface.get_rect(center=(mid_x, mid_y))
                screen.blit(exclamation_surface, exclamation_rect)
def save_focus_tree(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(shown_infos, f, ensure_ascii=False)

def load_focus_tree(filename):
    global shown_infos, focus_num
    with open(filename, 'r', encoding='utf-8') as f:
        shown_infos = json.load(f)
        focus_num = len(shown_infos)

def select_save_file():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    return file_path

def select_load_file():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    return file_path
def select_export_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    return file_path

def export_focus_tree(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        id = shown_infos[0][1]+"_tree"
        f.write(f"focus_tree = {{\n")
        f.write(f"\tid = {id}\n")
        f.write(f"\tdefault = no\n")
        f.write(f"\tshared_focus = {id}\n")
        f.write(f"}}\n\n")
        for index, info in enumerate(shown_infos):
            id = info[1]
            icon = info[2] if info[2] else f"GFX_{id}"  # 如果没有gfx，自动设置为GFX_(国策id)
            cost = round(float(info[5]) / 7, 3)
            x = 6 if index == 0 else info[3]
            y = 0 if index == 0 else info[4]
            relative_position_id = shown_infos[0][1]  # 第一个国策的id
            prerequisite_ids = [id.strip() for id in info[6].replace(';', ',').split(',') if id.strip()]
            mutually_exclusive_ids = [id.strip() for id in info[7].replace(';', ',').split(',') if id.strip()]

            f.write(f"shared_focus = {{\n")
            f.write(f"\tid = {id}\n")
            f.write(f"\ticon = {icon}\n")
            f.write(f"\tcost = {cost}\n")
            f.write(f"\tx = {x}\n")
            f.write(f"\ty = {y}\n")
            f.write(f"\trelative_position_id = {relative_position_id}\n")

            # 处理前置国策
            if prerequisite_ids:
                if len(prerequisite_ids) > 1:
                    f.write("\tprerequisite = {\n")
                    for pre_id in prerequisite_ids:
                        f.write(f"\t\tfocus = {pre_id}\n")
                    f.write("\t}\n")
                else:
                    f.write(f"\tprerequisite = {{ focus = {prerequisite_ids[0]} }}\n")

            # 处理互斥国策
            if mutually_exclusive_ids:
                if len(mutually_exclusive_ids) > 1:
                    f.write("\tmutually_exclusive = {\n")
                    for mutex_id in mutually_exclusive_ids:
                        f.write(f"\t\tfocus = {mutex_id}\n")
                    f.write("\t}\n")
                else:
                    f.write(f"\tmutually_exclusive = {{ focus = {mutually_exclusive_ids[0]} }}\n")

            f.write(f"\tcompletion_reward = {{\n")
            f.write(f"\t\tlog = \"[GetDateText]: [Root.GetName]: Focus {id}\"\n")
            f.write(f"\t}}\n")
            f.write(f"}}\n\n")

while running: 
    # 更新主窗口 
    screen.fill(WHITE) 
    # 获取当前窗口大小 
    current_width, current_height = screen.get_size() 
    # 绘制灰色区域，跟随窗口大小改变 
    gray_area = pygame.Rect(0, current_height // 2, current_width, current_height // 2) 
    pygame.draw.rect(screen, GRAY, gray_area) 
    # 绘制计数器文本 
    textImage = small_font.render("当前国策数量：" + str(focus_num), True, BLACK) 
    screen.blit(textImage, (10, 10)) 
    # 绘制说明文字框
    instruction_surface = small_font.render(instruction_text, True, BLACK)
    screen.blit(instruction_surface, (current_width //2 +150, 10))  # 右上角位置

    # 其他绘制代码...
    # 绘制计数器文本 
    textImage = small_font.render("当前国策数量：" + str(focus_num), True, BLACK) 
    screen.blit(textImage, (10, 10)) 
    # 绘制按钮 
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect) 
    button_text = small_font.render("创建国策", True, WHITE)  # 按钮文本改成“创建国策” 
    text_rect = button_text.get_rect(center=button_rect.center) 
    screen.blit(button_text, text_rect) 

    # 绘制保存按钮
    pygame.draw.rect(screen, BUTTON_COLOR, save_button_rect)
    save_text = small_font.render("保存国策树文件.json", True, WHITE)
    save_text_rect = save_text.get_rect(center=save_button_rect.center)
    screen.blit(save_text, save_text_rect)

    # 绘制载入按钮
    pygame.draw.rect(screen, BUTTON_COLOR, load_button_rect)
    load_text = small_font.render("载入国策树文件.json", True, WHITE)
    load_text_rect = load_text.get_rect(center=load_button_rect.center)
    screen.blit(load_text, load_text_rect)
    pygame.draw.rect(screen, BUTTON_COLOR, export_button_rect)  # 绘制导出按钮
    export_text = small_font.render("导出国策树为paradox语言", True, WHITE)
    export_text_rect = export_text.get_rect(center=export_button_rect.center)
    screen.blit(export_text, export_text_rect)
    for idx, (instruction, box) in enumerate(zip(input_instructions, input_boxes)):  
        pygame.draw.rect(screen, BLACK, box, 2)    
        input_surface = myfont.render(input_texts[idx], True, BLACK)  # 框内字体调黑  
        screen.blit(input_surface, (box.x + 5, box.y + 5))  
        show_input_instructions(screen, box, myfont, instruction)  # 显示输入说明  
    # 处理事件 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False 
        elif event.type == pygame.VIDEORESIZE: 
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE) 
            current_width, current_height = screen.get_size() 
            button_rect.topleft = (current_width // 2 - 50, current_height - 70)
            save_button_rect.topleft = (current_width // 2 - 250, current_height - 70)
            load_button_rect.topleft = (current_width // 2 + 150, current_height - 70)
            export_button_rect.topleft = (current_width // 2 + 350, current_height - 70)  # 更新导出按钮位置
            # select_button_rect.topleft = (10, event.h - 70)  # 调整选择按钮位置 
            # 重新计算输入框位置 
            input_y_positions = [ 
                current_height // 2 + 10,  
                current_height // 2 + 60,  
                current_height // 2 + 110,  
                current_height // 2 + 160,  
                current_height // 2 + 210, 
                current_height // 2 + 260,  # 国策时间 
                current_height // 2 + 310,  # 前置国策id 
                current_height // 2 + 360   # 互斥国策id 
            ] 
            for i, y_pos in enumerate(input_y_positions): 
                input_boxes[i].topleft = (10, y_pos) 
        elif event.type == pygame.MOUSEBUTTONDOWN: 
            if event.button == 4:  # 滚轮向上
                scroll_offset += 10  # 向上滚动
            elif event.button == 5:  # 滚轮向下
                scroll_offset -= 10  # 向下滚动
            elif event.button == 1:   
                if save_button_rect.collidepoint(event.pos):
                    file_path = select_save_file()
                    if file_path:
                        save_focus_tree(file_path)
                elif export_button_rect.collidepoint(event.pos):  # 导出国策树
                    file_path = select_export_file()
                    if file_path:
                        export_focus_tree(file_path)
                # 载入国策
                elif load_button_rect.collidepoint(event.pos):
                    file_path = select_load_file()
                    if file_path:
                        load_focus_tree(file_path)
                    
                elif button_rect.collidepoint(event.pos):   
                    # 检查输入是否完整，如果不完整则不执行创建国策的操作 
                    if is_input_complete():
                        if saved_select_info_index != -1 :
                            del shown_infos[saved_select_info_index] 
                            saved_select_info_index = -1  # 重置选中的国策索引 
                            focus_num = focus_num - 1 
                        focus_num += 1
                        shown_info = tuple(input_texts)
                        # 更新互斥国策
                        mutex_ids = [id.strip() for id in input_texts[7].replace(';', ',').split(',')]
                        existing_mutex_ids = []
                        for mutex_id in mutex_ids:
                            if mutex_id not in existing_mutex_ids:
                                existing_mutex_ids.append(mutex_id)

                        # 确保互斥国策的格式正确
                        if existing_mutex_ids:
                            shown_info = list(shown_info[:7]) + [', '.join(existing_mutex_ids)]

                        if focus_num == 1:
                            shown_info = (shown_info[0], shown_info[1], shown_info[2], 0, 0, shown_info[5], shown_info[6], shown_info[7])
                        shown_infos.append(shown_info)

                        # 清空输入框
                        for i in range(len(input_texts)):
                            input_texts[i] = ""
                for idx, box in enumerate(input_boxes): 
                    if box.collidepoint(event.pos):   
                        selected_index = idx   
                        break 
                else: 
                    selected_index = -1   
                for index, shown_info in enumerate(shown_infos): 
                    x = int(shown_info[3]) * 100 
                    y = int(shown_info[4]) * 75 
                    info_box_rect = pygame.Rect(x, y, box_width, box_height) 
                    if info_box_rect.collidepoint(event.pos): 
                        if selected_info_index == -1: 
                            selected_info_index = index 
                        break 
                    modify_button_rect = pygame.Rect(x + box_width, y, 50, 25) 
                    if modify_button_rect.collidepoint(event.pos): 
                        # 处理修改操作 
                        for i in range(len(input_texts)): 
                            input_texts[i] = str(shown_infos[selected_info_index][i]) 
                        selected_index = 0 
                        break 
                    delete_button_rect = pygame.Rect(x + box_width, y + 25, 50, 25) 
                    if delete_button_rect.collidepoint(event.pos): 
                        # 处理删除操作 
                        del shown_infos[selected_info_index] 
                        selected_info_index = -1  # 重置选中的国策索引 
                        break 
            
        elif event.type == pygame.KEYDOWN: 
            if selected_index!= -1:   
                if event.key == pygame.K_BACKSPACE: 
                    backspace_pressed = True 
                    backspace_press_start_time = pygame.time.get_ticks()  # 记录退格键按下的起始时间 
                elif event.key == pygame.K_DELETE:
                    input_texts[selected_index] = ""  # 清空输入框
                elif selected_index != 0: 
                    input_texts[selected_index] += event.unicode 
                else:
                    pass
        elif event.type == pygame.TEXTINPUT:
            if selected_index == 0:
                input_texts[selected_index] += event.text
        elif event.type == pygame.KEYUP: 
            if event.key == pygame.K_BACKSPACE: 
                backspace_pressed = False 
                if pygame.time.get_ticks() - backspace_press_start_time > 500:  # 判断是否长按（这里设置 500 毫秒为长按阈值，您可以按需调整） 
                    input_texts[selected_index] = ""  # 直接清空输入框内容 
                else: 
                    input_texts[selected_index] = input_texts[selected_index][:-1]  # 短按则删除一个字符 
            if selected_index in [3, 4] and not validate_input(input_texts[selected_index]):  # 验证 x 和 y 输入是否为整数 
                input_texts[selected_index] = ""  # 如果不是整数，清空输入 
    show_info_boxes(screen, myfont, scroll_offset) 
    # 刷新窗口 
    pygame.display.flip() 
    # 控制帧率 
    clock.tick(60) 
pygame.quit()    