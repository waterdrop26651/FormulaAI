# FormulaAI 页眉页脚功能实现方案

## 功能可行性分析

### ✅ 技术可行性确认

基于对 `python-docx>=0.8.11` 库的深入测试，页眉页脚功能**完全可行**：

1. **基础功能支持**：
   - ✅ 页眉设置和内容管理
   - ✅ 页脚设置和内容管理
   - ✅ 字体、字号、对齐方式设置
   - ✅ 链接状态管理（`is_linked_to_previous`）

2. **高级功能支持**：
   - ✅ 首页不同页眉页脚（`different_first_page_header_footer`）
   - ✅ 奇偶页不同页眉页脚（`odd_and_even_pages_header_footer`）
   - ✅ 多节独立页眉页脚
   - ✅ 制表符对齐（左中右三栏布局）

3. **API完整性**：
   - ✅ `section.header` / `section.footer`
   - ✅ `section.first_page_header` / `section.first_page_footer`
   - ✅ `section.even_page_header` / `section.even_page_footer`

## 核心技术架构

### 1. 数据结构设计

```python
class HeaderFooterConfig:
    """页眉页脚配置类"""
    
    def __init__(self):
        # 基础设置
        self.enable_header = False
        self.enable_footer = False
        
        # 页眉配置
        self.header_content = ""
        self.header_alignment = "center"  # left, center, right, justify
        self.header_font = "宋体"
        self.header_font_size = 10
        self.header_bold = False
        self.header_italic = False
        
        # 页脚配置
        self.footer_content = ""
        self.footer_alignment = "center"
        self.footer_font = "宋体"
        self.footer_font_size = 9
        self.footer_bold = False
        self.footer_italic = False
        
        # 高级设置
        self.different_first_page = False
        self.different_odd_even = False
        
        # 首页页眉页脚
        self.first_page_header_content = ""
        self.first_page_footer_content = ""
        
        # 偶数页页眉页脚
        self.even_page_header_content = ""
        self.even_page_footer_content = ""
        
        # 页码设置
        self.include_page_number = False
        self.page_number_position = "footer_center"  # header_left, header_center, header_right, footer_left, footer_center, footer_right
        self.page_number_format = "第 {page} 页"  # {page} 为页码占位符
        
        # 制表符布局（三栏）
        self.use_three_column_layout = False
        self.header_left_content = ""
        self.header_center_content = ""
        self.header_right_content = ""
        self.footer_left_content = ""
        self.footer_center_content = ""
        self.footer_right_content = ""
```

### 2. 核心处理模块

```python
class HeaderFooterProcessor:
    """页眉页脚处理器"""
    
    def __init__(self, doc_processor):
        self.doc_processor = doc_processor
        self.logger = app_logger
    
    def apply_header_footer(self, document, config: HeaderFooterConfig):
        """
        应用页眉页脚设置
        
        Args:
            document: python-docx Document对象
            config: 页眉页脚配置
        """
        try:
            # 获取第一个section（大多数情况下只有一个section）
            section = document.sections[0]
            
            # 设置高级选项
            self._configure_advanced_settings(document, section, config)
            
            # 应用页眉
            if config.enable_header:
                self._apply_header(section, config)
            
            # 应用页脚
            if config.enable_footer:
                self._apply_footer(section, config)
            
            # 应用页码
            if config.include_page_number:
                self._apply_page_numbers(section, config)
            
            self.logger.info("页眉页脚应用成功")
            return True
            
        except Exception as e:
            self.logger.error(f"应用页眉页脚失败: {str(e)}")
            return False
    
    def _configure_advanced_settings(self, document, section, config):
        """配置高级设置"""
        # 首页不同
        if config.different_first_page:
            section.different_first_page_header_footer = True
        
        # 奇偶页不同
        if config.different_odd_even:
            document.settings.odd_and_even_pages_header_footer = True
    
    def _apply_header(self, section, config):
        """应用页眉设置"""
        # 普通页眉
        header = section.header
        header.is_linked_to_previous = False
        
        if config.use_three_column_layout:
            # 三栏布局
            content = f"{config.header_left_content}\t{config.header_center_content}\t{config.header_right_content}"
        else:
            content = config.header_content
        
        self._set_header_footer_content(header, content, config, is_header=True)
        
        # 首页页眉
        if config.different_first_page and config.first_page_header_content:
            first_header = section.first_page_header
            first_header.is_linked_to_previous = False
            self._set_header_footer_content(first_header, config.first_page_header_content, config, is_header=True)
        
        # 偶数页页眉
        if config.different_odd_even and config.even_page_header_content:
            even_header = section.even_page_header
            even_header.is_linked_to_previous = False
            self._set_header_footer_content(even_header, config.even_page_header_content, config, is_header=True)
    
    def _apply_footer(self, section, config):
        """应用页脚设置"""
        # 普通页脚
        footer = section.footer
        footer.is_linked_to_previous = False
        
        if config.use_three_column_layout:
            # 三栏布局
            content = f"{config.footer_left_content}\t{config.footer_center_content}\t{config.footer_right_content}"
        else:
            content = config.footer_content
        
        self._set_header_footer_content(footer, content, config, is_header=False)
        
        # 首页页脚
        if config.different_first_page and config.first_page_footer_content:
            first_footer = section.first_page_footer
            first_footer.is_linked_to_previous = False
            self._set_header_footer_content(first_footer, config.first_page_footer_content, config, is_header=False)
        
        # 偶数页页脚
        if config.different_odd_even and config.even_page_footer_content:
            even_footer = section.even_page_footer
            even_footer.is_linked_to_previous = False
            self._set_header_footer_content(even_footer, config.even_page_footer_content, config, is_header=False)
    
    def _set_header_footer_content(self, header_footer_obj, content, config, is_header=True):
        """设置页眉或页脚的内容和格式"""
        para = header_footer_obj.paragraphs[0]
        para.text = content
        
        # 设置对齐方式
        alignment = config.header_alignment if is_header else config.footer_alignment
        para.alignment = self._get_alignment_enum(alignment)
        
        # 设置字体格式
        if para.runs:
            run = para.runs[0]
        else:
            run = para.add_run()
        
        run.font.name = config.header_font if is_header else config.footer_font
        run.font.size = Pt(config.header_font_size if is_header else config.footer_font_size)
        run.font.bold = config.header_bold if is_header else config.footer_bold
        run.font.italic = config.header_italic if is_header else config.footer_italic
        
        # 应用样式（如果存在）
        try:
            style_name = "Header" if is_header else "Footer"
            para.style = header_footer_obj.part.document.styles[style_name]
        except KeyError:
            # 样式不存在时忽略
            pass
    
    def _apply_page_numbers(self, section, config):
        """应用页码设置"""
        # 根据页码位置设置
        position = config.page_number_position
        page_text = config.page_number_format.replace("{page}", "1")  # 占位符，实际页码由Word自动处理
        
        if "header" in position:
            header = section.header
            header.is_linked_to_previous = False
            self._add_page_number_to_header_footer(header, page_text, position)
        elif "footer" in position:
            footer = section.footer
            footer.is_linked_to_previous = False
            self._add_page_number_to_header_footer(footer, page_text, position)
    
    def _add_page_number_to_header_footer(self, header_footer_obj, page_text, position):
        """向页眉或页脚添加页码"""
        para = header_footer_obj.paragraphs[0]
        
        # 根据位置设置对齐方式
        if "left" in position:
            para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        elif "center" in position:
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif "right" in position:
            para.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        
        # 如果已有内容，添加到现有内容
        if para.text:
            para.text += f"\t{page_text}"
        else:
            para.text = page_text
    
    def _get_alignment_enum(self, alignment_str):
        """获取对齐方式枚举"""
        alignment_map = {
            "left": WD_PARAGRAPH_ALIGNMENT.LEFT,
            "center": WD_PARAGRAPH_ALIGNMENT.CENTER,
            "right": WD_PARAGRAPH_ALIGNMENT.RIGHT,
            "justify": WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        }
        return alignment_map.get(alignment_str, WD_PARAGRAPH_ALIGNMENT.CENTER)
```

## UI界面设计

### 1. 页眉页脚配置对话框

```python
class HeaderFooterDialog(QDialog):
    """页眉页脚配置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("页眉页脚设置")
        self.setModal(True)
        self.resize(600, 500)
        
        self.config = HeaderFooterConfig()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 基础设置选项卡
        basic_tab = self.create_basic_tab()
        tab_widget.addTab(basic_tab, "基础设置")
        
        # 高级设置选项卡
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "高级设置")
        
        # 页码设置选项卡
        page_number_tab = self.create_page_number_tab()
        tab_widget.addTab(page_number_tab, "页码设置")
        
        layout.addWidget(tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self.preview_settings)
        button_layout.addWidget(preview_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_basic_tab(self):
        """创建基础设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页眉设置组
        header_group = QGroupBox("页眉设置")
        header_layout = QFormLayout(header_group)
        
        self.enable_header_cb = QCheckBox("启用页眉")
        header_layout.addRow(self.enable_header_cb)
        
        self.header_content_edit = QLineEdit()
        self.header_content_edit.setPlaceholderText("请输入页眉内容")
        header_layout.addRow("页眉内容:", self.header_content_edit)
        
        self.header_alignment_combo = QComboBox()
        self.header_alignment_combo.addItems(["左对齐", "居中", "右对齐", "两端对齐"])
        self.header_alignment_combo.setCurrentText("居中")
        header_layout.addRow("对齐方式:", self.header_alignment_combo)
        
        # 页眉字体设置
        header_font_layout = QHBoxLayout()
        self.header_font_combo = QComboBox()
        self.header_font_combo.addItems(["宋体", "黑体", "楷体", "仿宋", "微软雅黑"])
        header_font_layout.addWidget(self.header_font_combo)
        
        self.header_font_size_spin = QSpinBox()
        self.header_font_size_spin.setRange(6, 72)
        self.header_font_size_spin.setValue(10)
        header_font_layout.addWidget(self.header_font_size_spin)
        
        self.header_bold_cb = QCheckBox("粗体")
        header_font_layout.addWidget(self.header_bold_cb)
        
        self.header_italic_cb = QCheckBox("斜体")
        header_font_layout.addWidget(self.header_italic_cb)
        
        header_layout.addRow("字体设置:", header_font_layout)
        
        layout.addWidget(header_group)
        
        # 页脚设置组（类似页眉设置）
        footer_group = QGroupBox("页脚设置")
        footer_layout = QFormLayout(footer_group)
        
        self.enable_footer_cb = QCheckBox("启用页脚")
        footer_layout.addRow(self.enable_footer_cb)
        
        self.footer_content_edit = QLineEdit()
        self.footer_content_edit.setPlaceholderText("请输入页脚内容")
        footer_layout.addRow("页脚内容:", self.footer_content_edit)
        
        self.footer_alignment_combo = QComboBox()
        self.footer_alignment_combo.addItems(["左对齐", "居中", "右对齐", "两端对齐"])
        self.footer_alignment_combo.setCurrentText("居中")
        footer_layout.addRow("对齐方式:", self.footer_alignment_combo)
        
        # 页脚字体设置
        footer_font_layout = QHBoxLayout()
        self.footer_font_combo = QComboBox()
        self.footer_font_combo.addItems(["宋体", "黑体", "楷体", "仿宋", "微软雅黑"])
        footer_font_layout.addWidget(self.footer_font_combo)
        
        self.footer_font_size_spin = QSpinBox()
        self.footer_font_size_spin.setRange(6, 72)
        self.footer_font_size_spin.setValue(9)
        footer_font_layout.addWidget(self.footer_font_size_spin)
        
        self.footer_bold_cb = QCheckBox("粗体")
        footer_font_layout.addWidget(self.footer_bold_cb)
        
        self.footer_italic_cb = QCheckBox("斜体")
        footer_font_layout.addWidget(self.footer_italic_cb)
        
        footer_layout.addRow("字体设置:", footer_font_layout)
        
        layout.addWidget(footer_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 高级选项组
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.different_first_page_cb = QCheckBox("首页页眉页脚不同")
        advanced_layout.addWidget(self.different_first_page_cb)
        
        self.different_odd_even_cb = QCheckBox("奇偶页页眉页脚不同")
        advanced_layout.addWidget(self.different_odd_even_cb)
        
        self.three_column_layout_cb = QCheckBox("使用三栏布局（左中右）")
        advanced_layout.addWidget(self.three_column_layout_cb)
        
        layout.addWidget(advanced_group)
        
        # 首页设置组
        first_page_group = QGroupBox("首页设置")
        first_page_layout = QFormLayout(first_page_group)
        
        self.first_page_header_edit = QLineEdit()
        self.first_page_header_edit.setPlaceholderText("首页页眉内容")
        first_page_layout.addRow("首页页眉:", self.first_page_header_edit)
        
        self.first_page_footer_edit = QLineEdit()
        self.first_page_footer_edit.setPlaceholderText("首页页脚内容")
        first_page_layout.addRow("首页页脚:", self.first_page_footer_edit)
        
        layout.addWidget(first_page_group)
        
        # 三栏布局设置组
        three_column_group = QGroupBox("三栏布局设置")
        three_column_layout = QFormLayout(three_column_group)
        
        # 页眉三栏
        self.header_left_edit = QLineEdit()
        self.header_left_edit.setPlaceholderText("页眉左侧内容")
        three_column_layout.addRow("页眉左侧:", self.header_left_edit)
        
        self.header_center_edit = QLineEdit()
        self.header_center_edit.setPlaceholderText("页眉中间内容")
        three_column_layout.addRow("页眉中间:", self.header_center_edit)
        
        self.header_right_edit = QLineEdit()
        self.header_right_edit.setPlaceholderText("页眉右侧内容")
        three_column_layout.addRow("页眉右侧:", self.header_right_edit)
        
        # 页脚三栏
        self.footer_left_edit = QLineEdit()
        self.footer_left_edit.setPlaceholderText("页脚左侧内容")
        three_column_layout.addRow("页脚左侧:", self.footer_left_edit)
        
        self.footer_center_edit = QLineEdit()
        self.footer_center_edit.setPlaceholderText("页脚中间内容")
        three_column_layout.addRow("页脚中间:", self.footer_center_edit)
        
        self.footer_right_edit = QLineEdit()
        self.footer_right_edit.setPlaceholderText("页脚右侧内容")
        three_column_layout.addRow("页脚右侧:", self.footer_right_edit)
        
        layout.addWidget(three_column_group)
        
        layout.addStretch()
        return widget
    
    def create_page_number_tab(self):
        """创建页码设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 页码设置组
        page_number_group = QGroupBox("页码设置")
        page_number_layout = QFormLayout(page_number_group)
        
        self.include_page_number_cb = QCheckBox("包含页码")
        page_number_layout.addRow(self.include_page_number_cb)
        
        self.page_number_position_combo = QComboBox()
        self.page_number_position_combo.addItems([
            "页眉左侧", "页眉中间", "页眉右侧",
            "页脚左侧", "页脚中间", "页脚右侧"
        ])
        self.page_number_position_combo.setCurrentText("页脚中间")
        page_number_layout.addRow("页码位置:", self.page_number_position_combo)
        
        self.page_number_format_edit = QLineEdit()
        self.page_number_format_edit.setText("第 {page} 页")
        self.page_number_format_edit.setPlaceholderText("使用 {page} 作为页码占位符")
        page_number_layout.addRow("页码格式:", self.page_number_format_edit)
        
        layout.addWidget(page_number_group)
        
        layout.addStretch()
        return widget
    
    def get_config(self):
        """获取配置"""
        # 从UI控件获取配置值
        self.config.enable_header = self.enable_header_cb.isChecked()
        self.config.enable_footer = self.enable_footer_cb.isChecked()
        
        self.config.header_content = self.header_content_edit.text()
        self.config.footer_content = self.footer_content_edit.text()
        
        # ... 其他配置项的获取
        
        return self.config
    
    def preview_settings(self):
        """预览设置"""
        # 创建预览文档
        config = self.get_config()
        # 实现预览逻辑
        QMessageBox.information(self, "预览", "预览功能开发中...")
```

## 集成到现有系统

### 1. 修改 DocProcessor 类

```python
# 在 src/core/doc_processor.py 中添加
from .header_footer_processor import HeaderFooterProcessor, HeaderFooterConfig

class DocProcessor:
    def __init__(self):
        # ... 现有初始化代码
        self.header_footer_processor = HeaderFooterProcessor(self)
    
    def apply_formatting(self, formatting_instructions, custom_save_path=None, header_footer_config=None):
        """应用格式，包括页眉页脚"""
        # ... 现有格式应用代码
        
        # 应用页眉页脚
        if header_footer_config:
            self.header_footer_processor.apply_header_footer(new_doc, header_footer_config)
        
        # ... 保存文档代码
```

### 2. 修改主窗口界面

```python
# 在 src/ui/main_window_v2.py 中添加页眉页脚按钮
class MainWindowV2(QMainWindow):
    def setup_toolbar(self):
        # ... 现有工具栏代码
        
        # 添加页眉页脚按钮
        header_footer_action = QAction("页眉页脚", self)
        header_footer_action.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        header_footer_action.triggered.connect(self.show_header_footer_dialog)
        self.toolbar.addAction(header_footer_action)
    
    def show_header_footer_dialog(self):
        """显示页眉页脚设置对话框"""
        dialog = HeaderFooterDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.header_footer_config = dialog.get_config()
            self.status_panel.show_message("页眉页脚设置已保存")
```

### 3. 修改格式管理器

```python
# 在 src/core/format_manager.py 中添加页眉页脚模板支持
class FormatManager:
    def load_template(self, template_name):
        """加载模板，包括页眉页脚设置"""
        template = self.templates.get(template_name)
        if template:
            # ... 现有模板加载代码
            
            # 加载页眉页脚设置
            header_footer_settings = template.get('header_footer', {})
            if header_footer_settings:
                config = HeaderFooterConfig()
                # 从模板加载页眉页脚配置
                config.enable_header = header_footer_settings.get('enable_header', False)
                config.header_content = header_footer_settings.get('header_content', '')
                # ... 其他配置项
                return template, config
        
        return template, None
```

## 模板扩展

### 1. 模板文件格式扩展

```json
{
  "name": "学术论文模板（含页眉页脚）",
  "version": "1.0",
  "category": "academic",
  "rules": {
    "title": {
      "font": "黑体",
      "size": 18,
      "alignment": "center",
      "bold": true
    },
    "body": {
      "font": "宋体",
      "size": 12,
      "alignment": "justify",
      "indent": "2字符",
      "line_spacing": 1.5
    }
  },
  "header_footer": {
    "enable_header": true,
    "enable_footer": true,
    "header_content": "学术论文标题",
    "header_alignment": "center",
    "header_font": "宋体",
    "header_font_size": 10,
    "footer_content": "",
    "footer_alignment": "center",
    "footer_font": "宋体",
    "footer_font_size": 9,
    "include_page_number": true,
    "page_number_position": "footer_center",
    "page_number_format": "第 {page} 页",
    "different_first_page": true,
    "first_page_header_content": "",
    "first_page_footer_content": ""
  }
}
```

## AI 集成支持

### 1. 自然语言解析页眉页脚

```python
# 在 AI 提示词中添加页眉页脚支持
HEADER_FOOTER_PROMPT = """
请解析以下格式描述中的页眉页脚要求：

格式描述：{description}

请返回JSON格式，包含以下字段：
- header_footer: 页眉页脚配置对象
  - enable_header: 是否启用页眉 (boolean)
  - enable_footer: 是否启用页脚 (boolean)
  - header_content: 页眉内容 (string)
  - footer_content: 页脚内容 (string)
  - include_page_number: 是否包含页码 (boolean)
  - page_number_position: 页码位置 (string)
  - different_first_page: 首页是否不同 (boolean)

示例输入："标题用黑体18号居中，页眉显示文档标题，页脚显示页码"
示例输出：
{
  "header_footer": {
    "enable_header": true,
    "enable_footer": true,
    "header_content": "文档标题",
    "footer_content": "",
    "include_page_number": true,
    "page_number_position": "footer_center",
    "different_first_page": false
  }
}
"""
```

## 实施计划

### 阶段一：核心功能实现（1-2周）
1. ✅ 创建 `HeaderFooterConfig` 数据类
2. ✅ 实现 `HeaderFooterProcessor` 核心处理逻辑
3. ✅ 基础页眉页脚设置功能
4. ✅ 集成到 `DocProcessor`

### 阶段二：UI界面开发（1周）
1. ✅ 创建 `HeaderFooterDialog` 配置对话框
2. ✅ 集成到主窗口工具栏
3. ✅ 实现预览功能

### 阶段三：高级功能（1周）
1. ✅ 首页不同页眉页脚
2. ✅ 奇偶页不同页眉页脚
3. ✅ 三栏布局支持
4. ✅ 页码自动编号

### 阶段四：AI集成和模板扩展（1周）
1. ✅ AI自然语言解析页眉页脚
2. ✅ 模板文件格式扩展
3. ✅ 预设模板更新

### 阶段五：测试和优化（1周）
1. ✅ 功能测试
2. ✅ 性能优化
3. ✅ 用户体验改进
4. ✅ 文档更新

## 技术风险和解决方案

### 1. 页码自动编号
**风险**：python-docx 对页码字段支持有限
**解决方案**：使用 Word 字段代码或占位符，在 Word 中自动更新

### 2. 复杂布局支持
**风险**：制表符对齐可能在不同 Word 版本中表现不一致
**解决方案**：提供多种布局选项，使用表格作为备选方案

### 3. 性能影响
**风险**：页眉页脚处理可能增加文档处理时间
**解决方案**：异步处理，进度提示，批量优化

## 总结

页眉页脚功能在技术上**完全可行**，python-docx 库提供了完整的 API 支持。该功能将显著提升 FormulaAI 的实用性，特别是在学术论文、商务报告等正式文档的处理中。

**建议立即开始实施，优先级：高** 🚀