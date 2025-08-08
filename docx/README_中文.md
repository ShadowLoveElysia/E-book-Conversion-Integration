# 批量电子书转换器

**其他语言 / Other Languages / 他の言語:**
- [English Version](../README.md)
- [日本語版 (Japanese)](README_日本語.md)

---

一个功能强大的Python工具，用于批量将各种文档格式转换为不同的电子书格式。支持漫画模式（图片优先）和小说模式（文本优先）处理。

## 功能特性

- **多格式支持**：在PDF、EPUB、CBZ、MOBI、AZW3等多种格式之间转换
- **双处理模式**：
  - 漫画模式：针对扫描文档和图片密集型内容优化
  - 小说模式：针对基于文本的电子书优化
- **批量处理**：一次性处理整个文件夹的文档
- **并行处理**：多线程转换，提高处理速度
- **交互式和命令行**：支持类似GUI的交互模式和命令行界面
- **多语言支持**：中文、英文和日文界面
- **自动Calibre集成**：自动下载和设置Calibre工具
- **质量控制**：可调节的图片质量设置

## 安装

### 前置要求

安装所需的Python包：

```bash
pip install PyMuPDF Pillow EbookLib requests tqdm natsort
```

### Calibre集成

工具处理Calibre安装：
- **Windows**：自动下载和设置便携版Calibre（仅Windows支持自动安装）
- **Linux/macOS**：需要手动安装 - 您需要手动配置Calibre路径
- **原生格式**：CBZ和PDF整合成EPUB（仅漫画模式）无需Calibre

**注意**：对于Linux和macOS用户，您需要手动安装Calibre并确保`ebook-convert`工具在系统PATH中。原生CBZ和PDF到EPUB的转换（仅漫画模式）不需要Calibre。

## 使用方法

### 交互模式

不带参数运行进入交互模式：

```bash
python 批量电子书整合.py
```

### 命令行模式

```bash
python 批量电子书整合.py -p "源文件路径" -f epub -m comic
```

#### 参数说明

**必需参数：**
- `-p, --path`：包含要转换文件的源文件夹路径
- `-f, --format`：目标输出格式（epub、pdf、cbz、mobi等）
- `-m, --mode`：处理模式（`comic`或`novel`）

**可选参数：**
- `-o, --output`：输出文件基础名称（默认：文件夹名称）
- `-q, --quality`：图片质量1-100（默认：85）
- `-t, --title`：电子书元数据中的标题
- `-l, --lang`：界面语言（zh/en/ja，默认：zh）
- `-w, --workers`：并行线程数（默认：CPU核心数）

### 格式选项

**常用格式：**
- `epub` - 通用电子书格式
- `pdf` - 通用文档格式
- `cbz` - 漫画书存档格式

**Kindle格式：（需要Calibre）**
- `mobi` - 旧版Kindle格式
- `azw3` - 新版Kindle格式

**其他格式（需要Calibre）：**
- `docx`、`txt`、`kepub`、`fb2`、`lit`、`lrf`、`pdb`、`pmlz`、`rb`、`rtf`、`tcr`、`txtz`、`htmlz`

**特殊选项：**
- `all_native` - 同时生成EPUB + PDF + CBZ

## 使用示例

### 漫画模式示例

```bash
# 将PDF扫描件转换为EPUB
python 批量电子书整合.py -p "C:\我的扫描" -f epub --mode comic

# 将CBZ漫画转换为PDF
python 批量电子书整合.py -p "D:\漫画" -f pdf --mode comic

# 转换为多种格式
python 批量电子书整合.py -p "C:\漫画" -f all_native --mode comic
```

### 小说模式示例

```bash
# 将EPUB小说转换为MOBI格式用于Kindle
python 批量电子书整合.py -p "D:\小说" -f mobi --mode novel

# 将混合格式转换为EPUB
python 批量电子书整合.py -p "E:\书籍" -f epub --mode novel

# 高质量转换
python 批量电子书整合.py -p "F:\图书馆" -f azw3 --mode novel -q 95
```

## 处理模式

### 漫画模式
- **最适合**：扫描文档、漫画、图片密集型内容
- **处理流程**：文件 → 图片 → EPUB → 最终格式
- **优化重点**：图片质量和布局保持

### 小说模式
- **最适合**：基于文本的电子书、小说、文档
- **处理流程**：文件 → PDF → 合并PDF → EPUB → 最终格式
- **优化重点**：文本流和阅读体验

## 支持的输入格式

- **PDF**：扫描文档、数字PDF
- **CBZ/CBR**：漫画书存档
- **EPUB**：数字电子书
- **MOBI/AZW3**：Kindle格式
- **其他**：Calibre支持的任何格式

## 输出质量

- **图片质量**：可调节1-100（默认：85）
- **并行处理**：多线程提高速度
- **格式保持**：保持原始布局和格式
- **元数据**：保持书籍标题和作者信息

## 故障排除

### 常见问题

1. **缺少依赖项**：使用pip安装所需包
2. **找不到Calibre**：使用交互模式进行自动下载
3. **权限错误**：以管理员身份运行或检查文件夹权限
4. **DRM保护文件**：无法处理DRM保护的内容

### 性能优化建议

- 使用SSD存储以提高处理速度
- 根据CPU核心数调整工作线程数
- 降低图片质量以加快处理速度
- 大型转换期间关闭其他应用程序

## 致谢

本项目依赖于多个优秀的开源库和工具：

### 核心依赖
- **[Calibre](https://calibre-ebook.com/)**：强大的电子书管理和转换套件，支持格式转换
- **[PyMuPDF](https://pymupdf.readthedocs.io/)**：高性能PDF和图像处理
- **[Pillow](https://python-pillow.org/)**：Python图像处理库
- **[EbookLib](https://github.com/aerkalov/ebooklib)**：电子书创建和操作库

### 附加库
- **requests**：HTTP请求库
- **tqdm**：进度条库，提升用户体验
- **natsort**：自然排序，用于文件组织
- **argparse**：命令行参数解析

### 特别感谢
- **Calibre团队**：提供最全面的电子书转换工具
