import os
import re
import sys
import io
import argparse
import platform
import shutil
import webbrowser
import xml.etree.ElementTree as ET
import subprocess
import time
import zipfile
import importlib

elysiaFitz = None
edenImage = None
griseoEpub = None
kevinConcurrent = None
aponiaRequests = None
villVTqdm = None
kalpasNatsort = None

kiana_custom_calibre_path = None # USER-CONFIGURED: DO NOT CHANGE MANUALLY

FORMAT_CHOICE_MAP = {
    '1': 'epub', '2': 'pdf', '3': 'cbz', '4': 'mobi', '5': 'azw3', '6': 'docx',
    '7': 'txt', '8': 'kepub', '9': 'fb2', '10': 'lit', '11': 'lrf',
    '12': 'pdb', '13': 'pmlz', '14': 'rb', '15': 'rtf', '16': 'tcr',
    '17': 'txtz', '18': 'htmlz',
    '19': 'all_native'
}
ALL_FORMAT_VALUES = list(FORMAT_CHOICE_MAP.values())

STRINGS = {
    'error_dir_not_exist': {'zh': "错误: 目录 '{}' 不存在。", 'en': "Error: Directory '{}' does not exist.", 'ja': "エラー: ディレクトリ「{}」が見つかりません。"},
    'error_no_files': {'zh': "错误：在目录 '{}' 中未找到任何 '{}' 文件。", 'en': "Error: No '{}' files found in the directory '{}'.", 'ja': "エラー：ディレクトリ「{}」に「{}」ファイルが見つかりませんでした。"},
    'prompt_main_menu': {'zh': "\n欢迎使用！请选择操作模式:\n  1) 控制台交互模式\n  2) 查看所有参数说明\n  3) 退出\n请输入选项 (1, 2 或 3):", 'en': "\nWelcome! Please select an operation mode:\n  1) Interactive Console Mode\n  2) View All Parameter Help\n  3) Exit\nEnter your choice (1, 2 or 3):", 'ja': "\nようこそ！操作モードを選択してください:\n  1) 対話型コンソールモード\n  2) すべてのパラメータヘルプを表示\n  3) 終了\n選択肢（1、2、または3）を入力してください:"},
    'prompt_language_select': {'zh': "请选择后续提示的语言 (zh, en, ja):", 'en': "Please select a language for subsequent prompts (zh, en, ja):", 'ja': "後続のプロンプトの言語を選択してください (zh, en, ja):"},
    'prompt_input_path': {'zh': "请输入包含源文件（PDF, CBZ, EPUB等）的文件夹路径:", 'en': "Please enter the path to the folder containing source files (PDFs, CBZs, EPUBs, etc.):", 'ja': "ソースファイル（PDF、CBZ、EPUBなど）が含まれるフォルダのパスを入力してください:"},
    'multi_folder_tip': {'zh': "提示：若要一次性处理多个文件夹，请使用命令行参数模式 (例如: python your_script.py -p C:\\A C:\\B ...)。", 'en': "Tip: To process multiple folders at once, please use the command-line argument mode (e.g., python your_script.py -p C:\\A C:\\B ...).", 'ja': "ヒント：一度に複数のフォルダを処理するには、コマンドライン引数モードを使用してください (例: python your_script.py -p C:\\A C:\\B ...)。"},
    'warn_multi_folder_output_ignored': {'zh': "警告：在多文件夹模式下，-o/--output 参数 '{}' 将被忽略，以防止文件覆盖。将使用文件夹名称作为输出文件名。", 'en': "Warning: In multi-folder mode, the -o/--output argument '{}' is ignored to prevent file overwrites. Folder names will be used for output files.", 'ja': "警告：複数フォルダモードでは、-o/--output引数「{}」はファイルの上書きを防ぐために無視されます。フォルダ名が出力ファイル名として使用されます。"},
    'warn_multi_folder_title_ignored': {'zh': "警告：在多文件夹模式下，-t/--title 参数 '{}' 将被忽略。将使用文件夹名称作为标题。", 'en': "Warning: In multi-folder mode, the -t/--title argument '{}' is ignored. Folder names will be used for titles.", 'ja': "警告：複数フォルダモードでは、-t/--title引数「{}」は無視されます。フォルダ名がタイトルとして使用されます。"},
    'detected_folder_type': {'zh': "检测到文件夹主要包含 '{}' 文件。将首先将它们批量整合成一个临时的EPUB文件。", 'en': "Detected folder primarily contains '{}' files. They will be consolidated into a single temporary EPUB file first.", 'ja': "フォルダに主に「{}」ファイルが含まれていることが検出されました。最初にこれらを単一の一時的なEPUBに統合します。"},
    'consolidating': {'zh': "第一步：整合 {} 个 '{}' 文件...", 'en': "Step 1: Consolidating {} '{}' files...", 'ja': "ステップ1：{}個の「{}」ファイルを統合しています..."},
    'consolidation_complete': {'zh': "整合完成，临时EPUB文件已生成。", 'en': "Consolidation complete, temporary EPUB file generated.", 'ja': "統合が完了し、一時的なEPUBファイルが生成されました。"},
    'distributing': {'zh': "分发步骤：从临时文件分发到最终格式...", 'en': "Distribution Step: Distributing from temporary file to final formats...", 'ja': "配布ステップ：一時ファイルから最終フォーマットに配布しています..."},
    'calibre_needed': {'zh': "此操作需要Calibre命令行工具。", 'en': "This operation requires the Calibre command-line tools.", 'ja': "この操作にはCalibreコマンドラインツールが必要です。"},
    'calibre_needed_param_mode': {'zh': "错误：此操作需要Calibre，但在系统中未找到。请手动安装Calibre并确保其在系统PATH中，或使用控制台模式进行自动下载。", 'en': "Error: This operation requires Calibre, which was not found. Please install Calibre manually and ensure it's in the system PATH, or use the interactive console mode for automatic download.", 'ja': "エラー：この操作にはCalibreが必要ですが、システムに見つかりませんでした。手動でCalibreをインストールしてPATHに追加するか、コンソールモードを使用して自動ダウンロードを行ってください。"},
    'prompt_calibre_download': {'zh': "  1) 自动下载并安装到脚本目录 (推荐, 仅限Windows)\n  2) 打开官网手动下载\n请选择 (1或2):", 'en': "  1) Automatically download and set up locally (Recommended, Windows Only)\n  2) Open official website to download manually\nPlease choose (1 or 2):", 'ja': "  1) 自動的にダウンロードしてローカルに設定 (推奨, Windowsのみ)\n  2) 公式サイトを開いて手動でダウンロード\n選択してください (1または2):"},
    'calibre_downloading': {'zh': "正在从官网下载Calibre便携版...", 'en': "Downloading Calibre Portable from the official website...", 'ja': "公式サイトからCalibreポータブル版をダウンロードしています..."},
    'calibre_extracting': {'zh': "下载完成。正在安装到 '{}'...", 'en': "Download complete. Installing to '{}'...", 'ja': "ダウンロードが完了しました。「{}」にインストールしています..."},
    'calibre_ready': {'zh': "Calibre已准备就绪。", 'en': "Calibre is ready.", 'ja': "Calibreの準備ができました。"},
    'calibre_manual_prompt': {'zh': "请访问 https://calibre-ebook.com/download 进行下载和安装，然后重新运行脚本。", 'en': "Please visit https://calibre-ebook.com/download to download and install, then restart the script.", 'ja': "https://calibre-ebook.com/download にアクセスしてダウンロードとインストールを行い、スクリプトを再起動してください。"},
    'calibre_download_failed': {'zh': "自动下载失败。请检查您的网络连接。", 'en': "Automatic download failed. Please check your network connection.", 'ja': "自動ダウンロードに失敗しました。网络接続を確認してください。"},
    'calibre_install_failed': {'zh': "Calibre 安装失败。请尝试手动安装或检查权限。", 'en': "Calibre installation failed. Please try manual installation or check permissions.", 'ja': "Calibreのインストールに失敗しました。手動でインストールを試すか、権限を確認してください。"},
    'prompt_final_format': {
        'zh': """请选择最终输出格式 (输入数字):
--- 常用格式 ---
  1) EPUB (通用电子书)
  2) PDF (通用文档)
  3) CBZ (漫画格式)
--- Kindle 专用 ---
  4) MOBI (旧Kindle)
  5) AZW3 (新Kindle)
--- 其他格式 (需要Calibre) ---
  6) DOCX   7) TXT    8) KEPUB  9) FB2
  10) LIT   11) LRF   12) PDB   13) PMLZ
  14) RB    15) RTF   16) TCR   17) TXTZ
  18) HTMLZ
--- 特殊选项 ---
  19) 全部原生格式 (EPUB+PDF+CBZ)
您的选择:""",
        'en': """Please select the final output format (enter number):
--- Common Formats ---
  1) EPUB (Universal E-book)
  2) PDF (Universal Document)
  3) CBZ (Comic Book Archive)
--- Kindle Formats ---
  4) MOBI (Old Kindle)
  5) AZW3 (New Kindle)
--- Other Formats (Calibre Required) ---
  6) DOCX   7) TXT    8) KEPUB  9) FB2
  10) LIT   11) LRF   12) PDB   13) PMLZ
  14) RB    15) RTF   16) TCR   17) TXTZ
  18) HTMLZ
--- Special Options ---
  19) All Native Formats (EPUB+PDF+CBZ)
Your choice:""",
        'ja': """最終的な出力形式を選択してください（番号を入力）:
--- 一般的な形式 ---
  1) EPUB (汎用電子書籍)
  2) PDF (汎用ドキュメント)
  3) CBZ (コミックブックアーカイブ)
--- Kindle形式 ---
  4) MOBI (旧Kindle)
  5) AZW3 (新Kindle)
--- その他の形式 (Calibreが必要) ---
  6) DOCX   7) TXT    8) KEPUB  9) FB2
  10) LIT   11) LRF   12) PDB   13) PMLZ
  14) RB    15) RTF   16) TCR   17) TXTZ
  18) HTMLZ
--- 特別なオプション ---
  19) すべてのネイティブ形式 (EPUB+PDF+CBZ)
選択:"""
    },
    'creating_epub': {'zh': "创建EPUB...", 'en': "Creating EPUB...", 'ja': "EPUBを作成..."},
    'creating_pdf': {'zh': "创建PDF...", 'en': "Creating PDF...", 'ja': "PDFを作成..."},
    'creating_cbz': {'zh': "创建CBZ...", 'en': "Creating CBZ...", 'ja': "CBZを作成..."},
    'preparing_pages': {'zh': "正在准备页面列表... 发现 {} 个总页面/图片。", 'en': "Preparing page list... Found {} total pages/images.", 'ja': "ページリストを準備中... 合計{}ページ/画像が見つかりました。"},
    'processing_and_writing': {'zh': "正在使用 {} 个线程并行处理并写入: {}/{}", 'en': "Processing and writing in parallel with {} workers: {}/{}", 'ja': "{}個のワーカーで並列処理および書き込み中: {}/{}"},
    'finalizing_file': {'zh': "\n所有内容处理完毕。正在最终化文件...", 'en': "\nAll content processed. Finalizing file...", 'ja': "\nすべてのコンテンツが処理されました。最終ファイルを生成しています..."},
    'task_complete': {'zh': "任务完成！文件已保存为 '{}'", 'en': "Task complete! File saved as '{}'", 'ja': "タスク完了！ファイルは「{}」として保存されました。"},
    'exiting': {'zh': "正在退出...", 'en': "Exiting...", 'ja': "終了しています..."},
    'error_invalid_choice': {'zh': "输入无效。", 'en': "Invalid input.", 'ja': "無効な入力です。"},
    'epub_merge_notice_calibre': {'zh': "警告：EPUB合并功能将使用Calibre的 ebook-convert 工具。此方法会保留文本和排版，但对于不同来源的EPUB，仍可能出现小的格式调整。", 'en': "Warning: EPUB merge will use Calibre's ebook-convert tool. This method preserves text and layout but might have minor formatting adjustments for EPUBs from different sources.", 'ja': "警告：EPUB結合機能はCalibreのebook-convertツールを使用します。この方法はテキストとレイアウトを保持しますが、異なるソースのEPUBでは、小さなフォーマット調整が発生する可能性があります。"},
    'epub_merge_fail_calibre': {'zh': "EPUB合并失败。", 'en': "EPUB merge failed.", 'ja': "EPUB結合に失敗しました。"},
    'dep_missing_tip': {'zh': "缺少 Python 库：'{}'。请运行以下命令安装：\n  pip install {}", 'en': "Missing Python library: '{}'. Please install it using:\n  pip install {}", 'ja': "Pythonライブラリ「{}」が見つかりません。以下のコマンドでインストールしてください:\n  pip install {}"},
    'dep_reboot_tip': {'zh': "请安装上述缺失的库后，重新运行脚本。", 'en': "Please install the missing libraries above, then restart the script.", 'ja': "上記の見つからないライブラリをインストールしてから、スクリプトを再起動してください。"},
    'get_version_fail': {'zh': "无法获取Calibre最新版本信息。请检查网络或稍后重试。", 'en': "Could not fetch latest Calibre version. Check network or try again later.", 'ja': "Calibreの最新バージョン情報を取得できませんでした。ネットワークを確認するか、後で再試行してください。"},
    'download_url_fail': {'zh': "未能找到Calibre便携版下载链接。", 'en': "Could not find Calibre Portable download link.", 'ja': "Calibreポータブル版のダウンロードリンクが見つかりませんでした。"},
    'calibre_tool_missing_specific': {'zh': "错误：Calibre 工具 '{}' 在您的 Calibre 安装中未找到。\n此操作需要此工具。请尝试使用本脚本的自动下载功能，或手动安装完整的 Calibre 桌面版。", 'en': "Error: Calibre tool '{}' not found in your Calibre installation.\nThis operation requires this tool. Try using the script's automatic download, or manually install the full Calibre desktop version.", 'ja': "エラー：Calibreツール「{}」がCalibreのインストールに見つかりませんでした。\nこの操作にはこのツールが必要です。このスクリプトの自動ダウンロードを試すか、Calibreの完全デスクトップ版を手動でインストールしてください。"},
    'prompt_mode_select': {'zh': "请选择处理模式:\n  1) 漫画模式 (图片优先，适合扫描PDF/CBZ)\n  2) 小说模式 (文本优先，适合标准电子书)\n您的选择:", 'en': "Select mode:\n  1) Comic Mode (Image-first)\n  2) Novel Mode (Text-first)\nChoice:", 'ja': "モード選択:\n  1) コミック\n  2) 小説\n選択:"},
    'novel_mode_intro': {'zh': "已选择小说模式。流程: [文件] -> 统一为PDF -> 合并为一个PDF -> 转换为EPUB -> 最终格式。", 'en': 'Novel mode selected.', 'ja': '小説モードが選択されました。'},
    'novel_step1_convert_to_pdf': {'zh': "小说模式第一步：使用Calibre将所有源文件转换为PDF格式...", 'en': 'Novel Mode Step 1: Converting all source files to PDF using Calibre...', 'ja': '小説モードステップ1：CalibreでPDFに変換...'},
    'novel_step1_skip_convert': {'zh': "小说模式第一步：检测到源文件已是PDF，跳过转换步骤。", 'en': 'Novel Mode Step 1: Source files are already PDF, skipping conversion.', 'ja': '小説モードステップ1：PDFのため、変換をスキップ。'},
    'novel_step2_merge_pdf': {'zh': "小说模式第二步：合并所有PDF文件为一个临时文件...", 'en': 'Novel Mode Step 2: Merging all PDF files into a single temporary file...', 'ja': '小説モードステップ2：PDFを一つに統合...'},
    'novel_step3_convert_to_epub': {'zh': "小说模式第三步：使用Calibre将合并后的PDF转换为临时EPUB...", 'en': 'Novel Mode Step 3: Converting merged PDF to temporary EPUB using Calibre...', 'ja': '小説モードステップ3：統合PDFをEPUBに変換...'},
    'calibre_conversion_failed_drm': {'zh': "错误：文件 '{}' 转换失败。\n该文件可能有DRM保护，我们无法处理这个步骤，请获取到无DRM保护的版本！", 'en': "Error: Conversion failed for '{}'. The file may be DRM-protected.", 'ja': "エラー：'{}'の変換に失敗しました。DRM保護されている可能性があります。"},
    'pdf_merge_success': {'zh': "PDF合并完成，已生成 '{}'", 'en': "PDF merge complete: '{}'", 'ja': "PDF統合完了: '{}'"},
    'pdf_merge_fail': {'zh': "PDF合并失败: {}", 'en': "PDF merge failed: {}", 'ja': "PDF統合失敗: {}"},
    'prompt_confirm_path': {'zh': "您输入的路径是：'{}'\n确认无误吗？(y/n): ", 'en': "You entered path: '{}'\nIs this correct? (y/n): ", 'ja': "入力されたパスは「{}」です。\nよろしいですか？(y/n): "},
    'prompt_confirm_mode': {'zh': "您选择的处理模式是：{}模式。\n确认吗？(y/n): ", 'en': "You selected {} Mode.\nConfirm? (y/n): ", 'ja': "選択された処理モードは「{}」です。\nよろしいですか？(y/n): "},
    'prompt_confirm_format': {'zh': "您选择的最终输出格式是：{}。\n确认吗？(y/n): ", 'en': "You selected output format: {}.\nConfirm? (y/n): ", 'ja': "選択された出力形式は「{}」です。\nよろしいですか？(y/n): "},
    'prompt_confirm_output_name': {'zh': "输出文件的基础名称将是：'{}'\n确认吗？(y/n): ", 'en': "Output base name: '{}'\nConfirm? (y/n): ", 'ja': "出力ファイル名は「{}」です。\nよろしいですか？(y/n): "},
    'prompt_confirm_quality': {'zh': "图片质量设置为：{}。\n确认吗？(y/n): ", 'en': "Image quality: {}.\nConfirm? (y/n): ", 'ja': "画像品質は{}です。\nよろしいですか？(y/n): "},
    'prompt_confirm_title': {'zh': "电子书标题将是：'{}'\n确认吗？(y/n): ", 'en': "Book title: '{}'\nConfirm? (y/n): ", 'ja': "本のタイトルは「{}」です。\nよろしいですか？(y/n): "},
    'prompt_confirm_workers': {'zh': "并行线程数设置为：{}。\n确认吗？(y/n): ", 'en': "Number of workers: {}.\nConfirm? (y/n): ", 'ja': "並列スレッド数は{}です。\nよろしいですか？(y/n): "},
    'starting_task': {'zh': "所有配置已确认。开始处理任务...", 'en': "All configurations confirmed. Starting task...", 'ja': "すべての設定が確認されました。タスクを開始します..."},
    'invalid_confirmation': {'zh': "无效确认，请重新输入。", 'en': "Invalid confirmation, please re-enter.", 'ja': "無効な入力です。もう一度入力してください。"},
    'comic_mode_name': {'zh': "漫画", 'en': "Comic", 'ja': "コミック"},
    'novel_mode_name': {'zh': "小说", 'en': "Novel", 'ja': "小説"},
    'calibre_conversion_timed': {'zh': "完成, 耗时 {:.1f} 秒。", 'en': "Done, took {:.1f}s.", 'ja': "完了、{:.1f}秒かかりました。"},
    'congratulations_complete': {'zh': "恭喜您完成了转换 '{}' 的流程，本次处理花费了 {:.1f} 秒，其中Calibre转换花费了 {:.1f} 秒。", 'en': "Congratulations! Processing for '{}' is complete. Total time: {:.1f}s, Calibre conversion time: {:.1f}s.", 'ja': "「{}」の変換が完了しました。総処理時間：{:.1f}秒、Calibre変換時間：{:.1f}秒。"},
    'prompt_file_summary': {
        'zh': "文件分析摘要:\n  - 共发现 {total_count} 个受支持的文件。\n  - 文件按数字顺序排列范围: {min_num}-{max_num}。\n  - 格式分布:\n{breakdown}\n  - 发现 {decimal_count} 个文件名中包含小数 (例如 '1.5.pdf')。",
        'en': "File Analysis Summary:\n  - Found {total_count} supported files in total.\n  - Files are numerically sorted from {min_num} to {max_num}.\n  - Format Distribution:\n{breakdown}\n  - Found {decimal_count} files with decimal numbers in their names (e.g., '1.5.pdf').",
        'ja': "ファイル分析概要:\n  - 合計{total_count}個のサポートされているファイルが見つかりました。\n  - ファイルは{min_num}から{max_num}まで数値順にソートされています。\n  - 形式の分布:\n{breakdown}\n  - 名前に小数を含むファイルが{decimal_count}個見つかりました（例: '1.5.pdf'）。"
    },
    'prompt_confirm_decimal_ignore': {
        'zh': "是否处理所有文件？ (y = 全部处理, n = 忽略带小数的文件): ",
        'en': "Process all files? (y = process all, n = ignore files with decimals): ",
        'ja': "すべてのファイルを処理しますか？ (y = すべて処理, n = 小数を含むファイルを無視): "
    },
    'calibre_conversion_error': {
        'zh': "错误：Calibre 转换失败。",
        'en': "Error: Calibre conversion failed.",
        'ja': "エラー：Calibre変換に失敗しました。"
    },
    'prompt_skip_failed_file': {
        'zh': "文件 '{}' 转换失败。请选择操作 (r = 重试, s = 跳过, a = 中止): ",
        'en': "Conversion failed for file '{}'. Choose an action (r = retry, s = skip, a = abort): ",
        'ja': "ファイル「{}」の変換に失敗しました。アクションを選択してください (r = 再試行, s = スキップ, a = 中止): "
    },
    'prompt_specify_calibre_path': {'zh': "在您的系统中找不到Calibre。是否要指定一个自定义的Calibre安装路径? (y/n):", 'en': "Calibre not found on your system. Would you like to specify a custom path to your Calibre installation? (y/n):", 'ja': "システムにCalibreが見つかりません。カスタムのCalibreインストールパスを指定しますか？ (y/n):"},
    'prompt_enter_calibre_path': {'zh': "请输入您的Calibre安装文件夹的完整路径 (例如: C:\Program Files\Calibre2):", 'en': "Please enter the full path to your Calibre installation folder (e.g., C:\Program Files\Calibre2):", 'ja': "Calibreインストールフォルダへのフルパスを入力してください（例：C:\Program Files\Calibre2）："},
    'warn_custom_path_set': {'zh': "警告：指定自定义路径后，脚本将始终使用此路径，自动搜索功能将失效。如果与他人分享此脚本，他们可能需要修改此路径。\n路径已成功验证并保存。请重新启动脚本以使更改生效。", 'en': "Warning: After setting a custom path, the script will always use it, and the auto-search feature will be disabled. If you share this script, others may need to change this path.\nThe path has been successfully validated and saved. Please restart the script for the changes to take effect.", 'ja': "警告：カスタムパスを設定すると、スクリプトは常にこのパスを使用し、自動検索機能は無効になります。このスクリプトを他の人と共有する場合、彼らはこのパスを変更する必要があるかもしれません。\nパスは正常に検証され、保存されました。変更を有効にするためにスクリプトを再起動してください。"},
    'error_invalid_calibre_path': {'zh': "错误：提供的路径无效或在该路径下找不到Calibre工具 '{}'。请重试。", 'en': "Error: The provided path is invalid or the Calibre tool '{}' was not found in that path. Please try again.", 'ja': "エラー：指定されたパスが無効か、そのパスにCalibreツール「{}」が見つかりませんでした。再試行してください。"}
}

def checkDependencies():
    global elysiaFitz, edenImage, griseoEpub, kevinConcurrent, aponiaRequests, villVTqdm, kalpasNatsort
    missingPardofelisDeps = []
    
    huaDependencies = [
        ('PyMuPDF', 'PyMuPDF', 'import fitz'),
        ('Pillow', 'Pillow', 'from PIL import Image'),
        ('EbookLib', 'EbookLib', 'from ebooklib import epub'),
        ('requests', 'requests', 'import requests'),
        ('tqdm', 'tqdm', 'from tqdm import tqdm'),
        ('natsort', 'natsort', 'import natsort')
    ]

    for displayName, installName, importCommand in huaDependencies:
        try:
            exec(importCommand, globals())
        except ImportError:
            missingPardofelisDeps.append((displayName, installName))

    if missingPardofelisDeps:
        print("\n--- 依赖库检查 (Dependency Check) ---")
        for displayName, installName in missingPardofelisDeps:
            print(STRINGS['dep_missing_tip']['en'].format(displayName, installName))
            print(STRINGS['dep_missing_tip']['zh'].format(displayName, installName))
            print(STRINGS['dep_missing_tip']['ja'].format(displayName, installName))
            print("-" * 20)
        print(STRINGS['dep_reboot_tip']['en'])
        print(STRINGS['dep_reboot_tip']['zh'])
        print(STRINGS['dep_reboot_tip']['ja'])
        sys.exit(1)
    
    import concurrent.futures
    
    elysiaFitz = globals().get('fitz')
    edenImage = globals().get('Image')
    griseoEpub = globals().get('epub')
    kevinConcurrent = concurrent.futures
    aponiaRequests = globals().get('requests')
    villVTqdm = globals().get('tqdm')
    kalpasNatsort = globals().get('natsort')

def getLatestCalibrePortableUrl(languageCode):
    # This URL is now locked as per user request.
    # The previous implementation was fetching this URL and then trying to parse it, which was incorrect.
    return "https://download.calibre-ebook.com/8.9.0/calibre-portable-installer-8.9.0.exe"


def getCalibreToolPath(toolName):
    if kiana_custom_calibre_path and os.path.isdir(kiana_custom_calibre_path):
        custom_tool_path = os.path.join(kiana_custom_calibre_path, toolName)
        if os.path.exists(custom_tool_path):
            return custom_tool_path

    try:
        sakuraScriptDirectory = os.path.dirname(__file__)
    except NameError: 
        sakuraScriptDirectory = os.getcwd()

    if platform.system() == "Windows":
        portableBaseLibraryPath = os.path.join(sakuraScriptDirectory, 'lib', 'Calibre Portable')
        
        possiblePaths = [
            os.path.join(portableBaseLibraryPath, 'Calibre Portable', 'app', toolName),
            os.path.join(portableBaseLibraryPath, 'app', toolName),
            os.path.join(portableBaseLibraryPath, 'Calibre Portable', toolName),
            os.path.join(portableBaseLibraryPath, toolName)
        ]
        for path in possiblePaths:
            if os.path.exists(path):
                return path

        systemPaths = [
            os.path.join("C:\\Program Files\\Calibre2", toolName),
            os.path.join("C:\\Program Files\\Calibre", toolName)
        ]
        for path in systemPaths:
            if os.path.exists(path):
                return path
    else:
        whichCommand = shutil.which
        if whichCommand(toolName):
            return whichCommand(toolName)
    return None

def downloadCalibre(languageCode):
    mobiusDownloadUrl = getLatestCalibrePortableUrl(languageCode)
    if not mobiusDownloadUrl:
        return None
    
    try:
        script_dir = os.path.dirname(__file__)
    except NameError: 
        script_dir = os.getcwd()
    installerPath = os.path.join(script_dir, "calibre_portable_installer.exe")
        
    try:
        print(STRINGS['calibre_downloading'][languageCode])
        aponiaResponse = aponiaRequests.get(mobiusDownloadUrl, stream=True)
        aponiaResponse.raise_for_status()
        totalSize = int(aponiaResponse.headers.get('content-length', 0))
        with open(installerPath, 'wb') as localFile, villVTqdm(total=totalSize, unit='iB', unit_scale=True, unit_divisor=1024) as progressBar:
            for dataChunk in aponiaResponse.iter_content(chunk_size=1024):
                progressBar.update(localFile.write(dataChunk))
        return installerPath
    except aponiaRequests.exceptions.RequestException as requestError:
        print(f"\n{STRINGS['calibre_download_failed'][languageCode]}: {requestError}")
        return None

def setupCalibreLocally(languageCode):
    installerPath = downloadCalibre(languageCode)
    if not installerPath:
        return False
    
    try:
        script_dir = os.path.dirname(__file__)
    except NameError: 
        script_dir = os.getcwd()
    installDirectory = os.path.join(script_dir, 'lib', 'Calibre Portable')

    os.makedirs(installDirectory, exist_ok=True)
    
    print(STRINGS['calibre_extracting'][languageCode].format(installDirectory))
    
    command = [installerPath, '/S', f'/D={installDirectory}']
    
    try:
        processResult = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        
        if getCalibreToolPath('ebook-convert.exe'):
            print(STRINGS['calibre_ready'][languageCode])
            return True
        else:
            print(STRINGS['calibre_install_failed'][languageCode])
            return False
    except subprocess.CalledProcessError as processError:
        print(f"{STRINGS['calibre_install_failed'][languageCode]}: {processError.stderr if hasattr(processError, 'stderr') else processError}")
        return False
    except Exception as error:
        print(f"An unexpected error occurred during Calibre installation: {error}")
        return False
    finally:
        if os.path.exists(installerPath):
            os.remove(installerPath)

def ensureCalibreTool(toolName, languageCode, isInteractive=True):
    toolPath = getCalibreToolPath(toolName)
    if toolPath:
        if isInteractive:
            print(STRINGS['calibre_ready'][languageCode])
        return toolPath
    
    if isInteractive:
        print(STRINGS['calibre_needed'][languageCode])

        while True:
            userChoice = input(STRINGS['prompt_specify_calibre_path'][languageCode]).strip().lower()
            if userChoice in ['y', 'yes']:
                customPath = input(STRINGS['prompt_enter_calibre_path'][languageCode]).strip().replace('"', '')
                
                if os.path.isdir(customPath) and os.path.exists(os.path.join(customPath, toolName)):
                    try:
                        try:
                            script_path = os.path.abspath(__file__)
                        except NameError:
                            script_path = os.path.abspath(sys.argv[0])
                        
                        with open(script_path, 'r', encoding='utf-8') as f:
                            script_content = f.read()
                        
                        escaped_path = repr(customPath)
                        
                        new_content = re.sub(
                            r"kiana_custom_calibre_path = None",
                            f"kiana_custom_calibre_path = {escaped_path}",
                            script_content,
                            count=1
                        )
                        
                        if new_content != script_content:
                            with open(script_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(STRINGS['warn_custom_path_set'][languageCode])
                            sys.exit(0)
                        else:
                            print("Error: Could not find the placeholder to update the path in the script.")
                            return None
                    except Exception as e:
                        print(f"An error occurred while saving the path: {e}")
                        return None
                else:
                    print(STRINGS['error_invalid_calibre_path'][languageCode].format(toolName))
            
            elif userChoice in ['n', 'no']:
                break
            else:
                print(STRINGS['error_invalid_choice'][languageCode])

        print(STRINGS['calibre_tool_missing_specific'][languageCode].format(toolName))
        while True:
            print(STRINGS['prompt_calibre_download'][languageCode])
            userChoice = input("> ").strip()
            if userChoice == '2':
                print(STRINGS['calibre_manual_prompt'][languageCode])
                webbrowser.open("https://calibre-ebook.com/download")
                return None
            elif userChoice == '1':
                if platform.system() != "Windows":
                    print("Automatic download is currently only supported for Windows.")
                    return None
                setupSuccess = setupCalibreLocally(languageCode)
                if setupSuccess:
                    return getCalibreToolPath(toolName)
                else:
                    return None
            else:
                print(STRINGS['error_invalid_choice'][languageCode])
    else: 
        print(STRINGS['calibre_needed_param_mode'][languageCode])
        return None

def processPageWorker(workerArguments):
    pageIndex, filePath, pageNumber, imageQuality = workerArguments
    try:
        with elysiaFitz.open(filePath) as pdfDocument:
            pageObject = pdfDocument.load_page(pageNumber)
            imageList = pageObject.get_images(full=True)
            if not imageList:
                return {'index': pageIndex, 'data': None}
            
            imageInfo = pdfDocument.extract_image(imageList[0][0])
            imageData = imageInfo["image"]
            
            pillowImage = edenImage.open(io.BytesIO(imageData))
            if pillowImage.mode in ("RGBA", "P"):
                pillowImage = pillowImage.convert("RGB")
            
            byteBuffer = io.BytesIO()
            pillowImage.save(byteBuffer, format="JPEG", quality=imageQuality, optimize=True)
            return {'index': pageIndex, 'data': byteBuffer.getvalue()}
    except Exception as error: 
        return {'index': pageIndex, 'error': str(error)}

def convertPdfsToEpub(sourceDirectory, outputFilePath, imageQuality, bookTitle, languageCode, workerCount):
    print(STRINGS['consolidating'][languageCode].format(len(os.listdir(sourceDirectory)), 'PDF'))
    pdfFiles = kalpasNatsort.natsorted([os.path.join(sourceDirectory, f) for f in os.listdir(sourceDirectory) if f.lower().endswith('.pdf')])
    
    tasks, pageCounter = [], 0
    for path in pdfFiles:
        try:
            with elysiaFitz.open(path) as doc:
                for pageNum in range(len(doc)):
                    tasks.append((pageCounter, path, pageNum, imageQuality))
                    pageCounter += 1
        except Exception as error: 
            print(f"Skipping corrupt file {path}: {error}")

    if not tasks:
        raise FileNotFoundError(STRINGS['error_no_files'][languageCode].format(sourceDirectory, 'PDF'))
    
    print(STRINGS['preparing_pages'][languageCode].format(len(tasks)))
    
    griseoEpubBook = griseoEpub.EpubBook()
    griseoEpubBook.set_identifier(f'id_{os.path.basename(outputFilePath)}')
    griseoEpubBook.set_title(bookTitle)
    griseoEpubBook.set_language(languageCode)
    griseoEpubBook.add_author('File Converter')
    
    styleSheet = griseoEpub.EpubItem(uid="main_style", file_name="style/main.css", media_type="text/css", content='body{text-align:center;}img{max-width:100%;height:auto;}')
    griseoEpubBook.add_item(styleSheet)
    griseoEpubBook.spine = ['nav']
    
    processedResults, nextToWriteIndex, processedCounter = {}, 0, 0
    with kevinConcurrent.ThreadPoolExecutor(max_workers=workerCount) as executor:
        futureToTask = {executor.submit(processPageWorker, task): task for task in tasks}
        with villVTqdm(total=len(tasks), desc=STRINGS['processing_and_writing'][languageCode].format(workerCount, '','')) as pbar:
            for future in kevinConcurrent.as_completed(futureToTask):
                pbar.update(1)
                result = future.result()
                resultIndex = result['index']
                processedResults[resultIndex] = result
                
                while nextToWriteIndex in processedResults:
                    currentResult = processedResults.pop(nextToWriteIndex)
                    if 'error' not in currentResult and currentResult['data']:
                        index, data = currentResult['index'], currentResult['data']
                        imageFileName = f"images/img_{index+1:04d}.jpg"
                        chapterTitle = f"Page {index+1}"
                        
                        epubImageItem = griseoEpub.EpubItem(uid=f"img_{index+1}", file_name=imageFileName, media_type="image/jpeg", content=data)
                        griseoEpubBook.add_item(epubImageItem)
                        
                        chapterFileName = f"pages/p_{index+1:04d}.xhtml"
                        epubHtmlChapter = griseoEpub.EpubHtml(title=chapterTitle, file_name=chapterFileName, lang=languageCode)
                        epubHtmlChapter.content = f'<!DOCTYPE html><html><head><title>{chapterTitle}</title><link rel="stylesheet" type="text/css" href="../style/main.css" /></head><body><div><img src="../{imageFileName}" alt="{chapterTitle}"/></div></body></html>'
                        griseoEpubBook.add_item(epubHtmlChapter)
                        griseoEpubBook.spine.append(epubHtmlChapter)
                    nextToWriteIndex += 1
    
    print(STRINGS['finalizing_file'][languageCode])
    griseoEpubBook.toc = [griseoEpub.Link(f"pages/p_{i+1:04d}.xhtml", f"Page {i+1}", f"chap_{i+1}") for i in range(len(tasks))]
    griseoEpubBook.add_item(griseoEpub.EpubNcx())
    griseoEpubBook.add_item(griseoEpub.EpubNav())
    griseoEpub.write_epub(outputFilePath, griseoEpubBook, {})
    print(STRINGS['consolidation_complete'][languageCode])

def convertCbzsToEpub(sourceDirectory, outputFilePath, imageQuality, bookTitle, languageCode, workerCount):
    print(STRINGS['consolidating'][languageCode].format(len(os.listdir(sourceDirectory)), 'CBZ/CBR'))
    cbzFiles = kalpasNatsort.natsorted([os.path.join(sourceDirectory, f) for f in os.listdir(sourceDirectory) if f.lower().endswith(('.cbz', '.cbr'))])
    if not cbzFiles:
        raise FileNotFoundError(STRINGS['error_no_files'][languageCode].format(sourceDirectory, 'CBZ/CBR'))
    
    griseoEpubBook = griseoEpub.EpubBook()
    griseoEpubBook.set_identifier(f'id_{os.path.basename(outputFilePath)}'); griseoEpubBook.set_title(bookTitle); griseoEpubBook.set_language(languageCode); griseoEpubBook.add_author('File Converter')
    styleSheet = griseoEpub.EpubItem(uid="main_style", file_name="style/main.css", media_type="text/css", content='body{text-align:center;}img{max-width:100%;height:auto;}'); griseoEpubBook.add_item(styleSheet); griseoEpubBook.spine = ['nav']
    
    allImagePaths, tempDirectories = [], []
    
    for cbzPath in cbzFiles:
        tempDirName = f"temp_{os.path.basename(cbzPath)}"; tempDirectories.append(tempDirName)
        with zipfile.ZipFile(cbzPath, 'r') as zipFileHandle:
            zipFileHandle.extractall(tempDirName); allImagePaths.extend(kalpasNatsort.natsorted([os.path.join(tempDirName, f) for f in zipFileHandle.namelist() if f.lower().endswith(('jpg', 'jpeg', 'png', 'webp'))]))
    
    print(STRINGS['preparing_pages'][languageCode].format(len(allImagePaths)))
    with villVTqdm(total=len(allImagePaths), desc=STRINGS['processing_and_writing'][languageCode].format(1, '', '')) as pbar:
        for index, imagePath in enumerate(allImagePaths):
            pbar.update(1)
            imageObject = edenImage.open(imagePath)
            if imageObject.mode in ("P", "RGBA"): imageObject = imageObject.convert("RGB")
            
            imageBuffer = io.BytesIO(); imageObject.save(imageBuffer, format="JPEG", quality=imageQuality)
            imageBytes = imageBuffer.getvalue()
            
            imageFileName = f"images/img_{index:04d}.jpg"; epubImageItem = griseoEpub.EpubItem(uid=f"img_{index}", file_name=imageFileName, media_type="image/jpeg", content=imageBytes); griseoEpubBook.add_item(epubImageItem)
            chapterFileName, chapterTitle = f"pages/p_{index:04d}.xhtml", f"Page {index+1}"; epubHtmlChapter = griseoEpub.EpubHtml(title=chapterTitle, file_name=chapterFileName, lang=languageCode); epubHtmlChapter.content = f'<!DOCTYPE html><html><head><title>{chapterTitle}</title><link rel="stylesheet" type="text/css" href="../style/main.css" /></head><body><div><img src="../{imageFileName}" alt="{chapterTitle}"/></div></body></html>'; griseoEpubBook.add_item(epubHtmlChapter); griseoEpubBook.spine.append(epubHtmlChapter)
    
    print(STRINGS['finalizing_file'][languageCode])
    griseoEpubBook.toc = [griseoEpub.Link(f"pages/p_{i:04d}.xhtml", f"Page {i+1}", f"chap_{i}") for i in range(len(allImagePaths))]
    griseoEpubBook.add_item(griseoEpub.EpubNcx()); griseoEpubBook.add_item(griseoEpub.EpubNav())
    griseoEpub.write_epub(outputFilePath, griseoEpubBook, {})
    print(STRINGS['consolidation_complete'][languageCode])
    
    for tempDir in tempDirectories:
        if os.path.isdir(tempDir): shutil.rmtree(tempDir)

def mergeEpubsWithCalibre(sourceDirectory, outputFilePath, bookTitle, languageCode):
    print(STRINGS['epub_merge_notice_calibre'][languageCode])
    
    calibreExecutable = ensureCalibreTool('ebook-convert.exe', languageCode, isInteractive=True)
    if not calibreExecutable:
        return False, 0

    epubFiles = kalpasNatsort.natsorted([os.path.join(sourceDirectory, f) for f in os.listdir(sourceDirectory) if f.lower().endswith('.epub')])
    if not epubFiles:
        raise FileNotFoundError(STRINGS['error_no_files'][languageCode].format(sourceDirectory, 'EPUB'))
    
    print(f"{STRINGS['consolidating'][languageCode].format(len(epubFiles), 'EPUB')}... ", end="", flush=True)

    command = [calibreExecutable] + epubFiles + [outputFilePath]
    if bookTitle:
        command.extend(['--title', bookTitle])
    
    start_time = time.time()
    try:
        processResult = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        duration = time.time() - start_time
        print(STRINGS['calibre_conversion_timed'][languageCode].format(duration))
        print(STRINGS['consolidation_complete'][languageCode])
        return True, duration
    except subprocess.CalledProcessError as processError: 
        print(f"\n{STRINGS['epub_merge_fail_calibre'][languageCode]}: {processError.stderr if hasattr(processError, 'stderr') else processError}")
        return False, 0
    except Exception as error: 
        print(f"\n{STRINGS['epub_merge_fail_calibre'][languageCode]}: {error}")
        return False, 0

def FilesToPdf(sourceDirectory, outputDirectory, languageCode, isInteractive):
    print(STRINGS['novel_step1_convert_to_pdf'][languageCode])
    calibreExecutable = ensureCalibreTool('ebook-convert.exe', languageCode, isInteractive)
    if not calibreExecutable: return False, 0

    supportedExtensions = ('.epub', '.mobi', '.azw3', '.docx', '.txt', '.kepub', '.fb2', 
                             '.lit', '.lrf', '.pdb', '.pmlz', '.rb', '.rtf', '.tcr', 
                             '.txtz', '.htmlz')
    
    sourceFiles = kalpasNatsort.natsorted([
        os.path.join(sourceDirectory, f) for f in os.listdir(sourceDirectory) 
        if f.lower().endswith(supportedExtensions)
    ])

    if not sourceFiles:
        print("No non-PDF files requiring conversion were found.")
        return True, 0

    os.makedirs(outputDirectory, exist_ok=True)
    
    total_duration = 0
    files_to_process = list(sourceFiles) 

    with villVTqdm(total=len(files_to_process), desc="Converting to PDF") as pbar:
        for sourceFile in files_to_process:
            conversion_successful = False
            while not conversion_successful:
                baseName = os.path.splitext(os.path.basename(sourceFile))[0]
                outputFile = os.path.join(outputDirectory, f"{baseName}.pdf")
                command = [calibreExecutable, sourceFile, outputFile]
                start_time = time.time()
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                    total_duration += time.time() - start_time
                    conversion_successful = True
                except subprocess.CalledProcessError as processError:
                    pbar.write(f"\n{STRINGS['calibre_conversion_error'][languageCode]}")
                    pbar.write(f"Calibre Error: {processError.stderr}")
                    
                    if isInteractive:
                        while True:
                            user_choice = input(STRINGS['prompt_skip_failed_file'][languageCode].format(os.path.basename(sourceFile))).strip().lower()
                            if user_choice in ['r', 'retry']:
                                pbar.write("Retrying conversion...")
                                break 
                            elif user_choice in ['s', 'skip', 'y', 'yes']:
                                conversion_successful = True # Mark as "successful" to exit the retry loop and skip the file
                                break
                            elif user_choice in ['a', 'abort', 'n', 'no']:
                                return False, total_duration
                            else:
                                pbar.write(STRINGS['error_invalid_choice'][languageCode])
                        if user_choice in ['r', 'retry']:
                            continue # Retry the conversion
                        else: # Skip
                            break 
                    else: # Non-interactive mode
                        return False, total_duration
            pbar.update(1)
            
    return True, total_duration

def mergePdfs(sourceDirectory, outputFilePath, languageCode):
    print(STRINGS['novel_step2_merge_pdf'][languageCode])
    pdfFiles = kalpasNatsort.natsorted([os.path.join(sourceDirectory, f) for f in os.listdir(sourceDirectory) if f.lower().endswith('.pdf')])
    if not pdfFiles:
        print("No PDF files found to merge.")
        return False
    
    try:
        mergedDoc = elysiaFitz.open()
        for path in villVTqdm(pdfFiles, desc="Merging PDFs"):
            with elysiaFitz.open(path) as doc:
                mergedDoc.insert_pdf(doc)
        mergedDoc.save(outputFilePath)
        mergedDoc.close()
        print(STRINGS['pdf_merge_success'][languageCode].format(outputFilePath))
        return True
    except Exception as error: 
        print(STRINGS['pdf_merge_fail'][languageCode].format(error))
        return False

def convertEpubToCbz(sourceFile, outputFilePath, imageQuality, languageCode):
    print(STRINGS['creating_cbz'][languageCode])
    readEpubBook = griseoEpub.read_epub(sourceFile)
    imageList = []
    
    for item in readEpubBook.get_items():
        if item.get_type() == griseoEpub.ITEM_IMAGE:
            imageList.append(item.get_content())

    if not imageList:
        print("Warning: No images found in the EPUB. Cannot create CBZ.")
        return

    print(STRINGS['preparing_pages'][languageCode].format(len(imageList)))
    with zipfile.ZipFile(outputFilePath, 'w', zipfile.ZIP_DEFLATED) as zipFileHandle:
        with villVTqdm(total=len(imageList), desc=STRINGS['processing_and_writing'][languageCode].format(1, '', '')) as pbar:
            for index, imageData in enumerate(imageList):
                pbar.update(1)
                try:
                    imageObject = edenImage.open(io.BytesIO(imageData))
                    if imageObject.mode in ("P", "RGBA"):
                        imageObject = imageObject.convert("RGB")
                    imageBuffer = io.BytesIO()
                    imageObject.save(imageBuffer, "JPEG", quality=imageQuality)
                    zipFileHandle.writestr(f"page_{index:04d}.jpg", imageBuffer.getvalue())
                except Exception as error: 
                    print(f"\nSkipping an image due to processing error: {error}")

    print(STRINGS['finalizing_file'][languageCode])
    print(STRINGS['task_complete'][languageCode].format(outputFilePath))

class MyHelpFormatter(argparse.HelpFormatter):
    def format_help(self):
        helpText = super().format_help()
        programName = self._prog
        exampleUsageText = f"""
-------------------------------------------------------------------
用法示例 (中文):
  # [漫画模式] 将 "C:\\MyScans" 中的PDF转为图片优先的EPUB和PDF
  python {programName} -p "C:\\MyScans" -f pdf --mode comic
  
  # [小说模式] 将 "D:\\Novels" 中的EPUB文件(文本优先)整合并创建MOBI
  python {programName} -p "D:\\Novels" -f mobi -o "MyNovel" --mode novel

  # [多文件夹模式] 分别处理 "C:\\A" 和 "D:\\B"，并将结果都保存到 "E:\\Output"
  python {programName} -p "C:\\A" "D:\\B" -f epub --mode novel -op "E:\\Output"

  # 使用数字选择格式, 将 "C:\\Comics" 转为 KEPUB
  python {programName} -p "C:\\Comics" -f 8 --mode comic
-------------------------------------------------------------------
"""
        return helpText + exampleUsageText

def createArgumentParser():
    griseoParser = argparse.ArgumentParser(description="批量将文件夹内的文档转换为各种电子书格式。", formatter_class=MyHelpFormatter, add_help=False)
    requiredGroup = griseoParser.add_argument_group('必要参数')
    optionalGroup = griseoParser.add_argument_group('可选参数')
    
    validFormatInputs = ALL_FORMAT_VALUES + list(FORMAT_CHOICE_MAP.keys())

    requiredGroup.add_argument('-p', '--path', type=str, required=True, nargs='+', help="一个或多个包含源文件(PDF, CBZ, EPUB等)的输入文件夹路径。")
    requiredGroup.add_argument('-f', '--format', type=str, required=True, choices=validFormatInputs, help="目标输出格式。可以是格式名(如 epub)或菜单数字(如 1)。")
    requiredGroup.add_argument('-m', '--mode', type=str, required=True, choices=['comic', 'novel'], help="处理模式: 'comic' (图片优先) 或 'novel' (文本优先)。")
    
    optionalGroup.add_argument('-o', '--output', type=str, help="输出文件的基础名称。在多文件夹模式下会被忽略。默认为输入文件夹的名称。")
    optionalGroup.add_argument('-op', '--outputpath', type=str, help="所有输出文件的统一存放目录。如果未指定，则输出到每个源文件夹的父目录中。")
    optionalGroup.add_argument('-q', '--quality', type=int, default=85, choices=range(1, 101), help="图片压缩质量 (1-100)。默认: 85。")
    optionalGroup.add_argument('-t', '--title', type=str, help="电子书元数据中的标题。在多文件夹模式下会被忽略。默认为输出文件名。")
    optionalGroup.add_argument('-l', '--lang', type=str, default='zh', choices=['zh', 'en', 'ja'], help="提示信息的语言。默认: zh。")
    optionalGroup.add_argument('-w', '--workers', type=int, default=os.cpu_count(), help=f"并行处理的线程数。默认: {os.cpu_count()}。")
    optionalGroup.add_argument('-h', '--help', action='help', help="显示此帮助信息并退出。")
    return griseoParser

def runTask(villV_Args):
    if villV_Args.outputpath:
        os.makedirs(villV_Args.outputpath, exist_ok=True)
        print(f"所有文件将输出到 (All files will be output to): {villV_Args.outputpath}")

    for sourceDirectory in villV_Args.path:
        folder_start_time = time.time()
        calibre_time_total = 0.0
        print(f"\n{'='*20}\n开始处理文件夹 (Processing folder): {sourceDirectory}\n{'='*20}")

        if not os.path.isdir(sourceDirectory):
            print(STRINGS['error_dir_not_exist'][villV_Args.lang].format(sourceDirectory))
            continue 

        fileList = os.listdir(sourceDirectory)
        
        pdfCount = len([f for f in fileList if f.lower().endswith('.pdf')])
        cbzCount = len([f for f in fileList if f.lower().endswith(('.cbz', '.cbr'))])
        nativeEbookCount = len([f for f in fileList if f.lower().endswith(('.epub', '.mobi', '.azw3'))])
        calibreRequiredCount = len([f for f in fileList if f.lower().endswith(('.docx', '.txt', '.kepub', '.fb2', '.lit', '.lrf', '.pdb', '.pmlz', '.rb', '.rtf', '.tcr', '.txtz', '.htmlz'))])

        majorType = 'none'
        counts = {'epub': nativeEbookCount, 'pdf': pdfCount, 'cbz': cbzCount, 'text': calibreRequiredCount}
        if any(count > 0 for count in counts.values()):
            if villV_Args.mode == 'novel':
                if nativeEbookCount > 0 or calibreRequiredCount > 0:
                    majorType = 'text' 
                else:
                    majorType = max(counts, key=counts.get)
            else:
                majorType = max(counts, key=counts.get)

        if majorType == 'none':
            print(STRINGS['error_no_files'][villV_Args.lang].format(sourceDirectory, 'supported files'))
            continue

        if villV_Args.outputpath:
            outputDirectory = villV_Args.outputpath
        else:
            outputDirectory = os.path.dirname(villV_Args.path[0]) if len(villV_Args.path) == 1 and getattr(villV_Args, 'interactive', False) else os.path.dirname(sourceDirectory)
            outputDirectory = outputDirectory or '.'


        is_multi_folder = len(villV_Args.path) > 1 and not getattr(villV_Args, 'interactive', False)
        if is_multi_folder and (villV_Args.output or villV_Args.title):
            if villV_Args.output:
                print(STRINGS['warn_multi_folder_output_ignored'][villV_Args.lang].format(villV_Args.output))
            if villV_Args.title:
                print(STRINGS['warn_multi_folder_title_ignored'][villV_Args.lang].format(villV_Args.title))
            outputBaseName = os.path.basename(os.path.normpath(sourceDirectory))
            bookTitle = outputBaseName
        else:
            outputBaseName = villV_Args.output or os.path.basename(os.path.normpath(sourceDirectory))
            bookTitle = villV_Args.title or outputBaseName

        edenTempFiles = []
        edenTempDirectories = []
        
        try:
            finalTempPath = ""
            
            if villV_Args.mode == 'comic':
                print(f"漫画模式: 检测到主要文件类型为 '{majorType.upper()}'")
                tempComicEpubPath = os.path.join(outputDirectory, f"{outputBaseName}_temp_comic.epub")
                edenTempFiles.append(tempComicEpubPath)

                if majorType == 'pdf':
                    convertPdfsToEpub(sourceDirectory, tempComicEpubPath, villV_Args.quality, bookTitle, villV_Args.lang, villV_Args.workers)
                elif majorType == 'cbz':
                    convertCbzsToEpub(sourceDirectory, tempComicEpubPath, villV_Args.quality, bookTitle, villV_Args.lang, villV_Args.workers)
                elif majorType == 'epub' or majorType == 'text':
                    success, duration = mergeEpubsWithCalibre(sourceDirectory, tempComicEpubPath, bookTitle, villV_Args.lang)
                    if success:
                        calibre_time_total += duration
                    else:
                        continue
                finalTempPath = tempComicEpubPath

            elif villV_Args.mode == 'novel':
                print(STRINGS['novel_mode_intro'][villV_Args.lang])
                
                tempPdfsDirectory = os.path.join(outputDirectory, f"{outputBaseName}_temp_pdfs_for_merge")
                tempMergedPdfPath = os.path.join(outputDirectory, f"{outputBaseName}_temp_merged.pdf")
                tempNovelEpubPath = os.path.join(outputDirectory, f"{outputBaseName}_temp_novel.epub")
                edenTempDirectories.append(tempPdfsDirectory)
                edenTempFiles.extend([tempMergedPdfPath, tempNovelEpubPath])
                
                os.makedirs(tempPdfsDirectory, exist_ok=True)

                any_non_pdf_files = nativeEbookCount > 0 or calibreRequiredCount > 0
                
                if any_non_pdf_files:
                    success, duration = FilesToPdf(sourceDirectory, tempPdfsDirectory, villV_Args.lang, villV_Args.interactive)
                    if success:
                        calibre_time_total += duration
                    else:
                        continue
                else:
                    print(STRINGS['novel_step1_skip_convert'][villV_Args.lang])
                
                for f in os.listdir(sourceDirectory):
                    if f.lower().endswith('.pdf'):
                        shutil.copy(os.path.join(sourceDirectory, f), tempPdfsDirectory)

                if not mergePdfs(tempPdfsDirectory, tempMergedPdfPath, villV_Args.lang):
                    continue
                
                print(f"{STRINGS['novel_step3_convert_to_epub'][villV_Args.lang]}... ", end="", flush=True)
                calibreExecutable = ensureCalibreTool('ebook-convert.exe', villV_Args.lang, villV_Args.interactive)
                if not calibreExecutable: continue
                
                start_time = time.time()
                try:
                    subprocess.run([calibreExecutable, tempMergedPdfPath, tempNovelEpubPath, '--title', bookTitle], check=True, capture_output=True, text=True, encoding='utf-8')
                    duration = time.time() - start_time
                    calibre_time_total += duration
                    print(STRINGS['calibre_conversion_timed'][villV_Args.lang].format(duration))
                    
                    finalTempPath = tempNovelEpubPath
                    print(STRINGS['consolidation_complete'][villV_Args.lang])
                except Exception as error: 
                    print(f"\nPDF到EPUB转换失败: {error.stderr if hasattr(error, 'stderr') else error}")
                    continue

            if os.path.exists(finalTempPath):
                print(f"\n{STRINGS['distributing'][villV_Args.lang]}")
                
                resolvedFormat = FORMAT_CHOICE_MAP.get(villV_Args.format, villV_Args.format)

                targetFormats = []
                if resolvedFormat == 'all_native':
                    targetFormats = ['epub', 'pdf', 'cbz']
                else:
                    targetFormats = [resolvedFormat]
                
                for formatUnit in targetFormats:
                    finalFilePath = os.path.join(outputDirectory, f"{outputBaseName}.{formatUnit}")
                    print(f"\n{'='*10} 正在创建: {finalFilePath.upper()} {'='*10}")

                    if formatUnit == 'epub':
                        shutil.copy(finalTempPath, finalFilePath)
                        print(STRINGS['task_complete'][villV_Args.lang].format(finalFilePath))
                    elif formatUnit == 'cbz':
                        convertEpubToCbz(finalTempPath, finalFilePath, villV_Args.quality, villV_Args.lang)
                    
                    else:
                        calibreExecutable = ensureCalibreTool('ebook-convert.exe', villV_Args.lang, villV_Args.interactive)
                        if not calibreExecutable:
                            print(f"跳过 {formatUnit.upper()} 创建，因为Calibre不可用。")
                            continue
                        
                        message = f"正在使用Calibre将临时文件转换为 {formatUnit.upper()}"
                        print(f"{message}... ", end="", flush=True)

                        command = [calibreExecutable, finalTempPath, finalFilePath]
                        if formatUnit == 'pdf':
                            command.append('--pdf-add-toc')
                        
                        start_time = time.time()
                        try:
                            subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                            duration = time.time() - start_time
                            calibre_time_total += duration
                            
                            print(f"\r{message}... {STRINGS['calibre_conversion_timed'][villV_Args.lang].format(duration)}")
                            print(STRINGS['task_complete'][villV_Args.lang].format(finalFilePath))
                        except Exception as error: 
                            print(f"\nCalibre转换失败: {error.stderr if hasattr(error, 'stderr') else error}")

        finally:
            print("\n正在清理当前文件夹的临时文件和目录...")
            for filePath in edenTempFiles:
                if os.path.exists(filePath):
                    os.remove(filePath)
                    print(f"已删除临时文件: {filePath}")
            for dirPath in edenTempDirectories:
                if os.path.exists(dirPath):
                    shutil.rmtree(dirPath)
                    print(f"已删除临时目录: {dirPath}")

            total_folder_time = time.time() - folder_start_time
            print("\n" + STRINGS['congratulations_complete'][villV_Args.lang].format(outputBaseName, total_folder_time, calibre_time_total))

    print(f"\n{'='*20}\n所有指定的文件夹均已处理完毕。\nAll specified folders have been processed.\n{'='*20}")


def confirmUserInput(languageCode, promptKey, promptValue):
    while True:
        confirmedInput = input(STRINGS[promptKey][languageCode].format(promptValue)).strip().lower()
        if confirmedInput in ['y', 'yes']:
            return True
        elif confirmedInput in ['n', 'no']:
            return False
        else:
            print(STRINGS['invalid_confirmation'][languageCode])

def presentFileSummaryAndGetChoice(sourceDirectory, languageCode):
    supportedExtensions = ('.pdf', '.cbz', '.cbr', '.epub', '.mobi', '.azw3', '.docx', 
                             '.txt', '.kepub', '.fb2', '.lit', '.lrf', '.pdb', '.pmlz', 
                             '.rb', '.rtf', '.tcr', '.txtz', '.htmlz')
    
    allFiles = kalpasNatsort.natsorted([f for f in os.listdir(sourceDirectory) if f.lower().endswith(supportedExtensions)])
    if not allFiles:
        print(STRINGS['error_no_files'][languageCode].format(sourceDirectory, 'supported files'))
        return None

    filesWithDecimals = [f for f in allFiles if re.search(r'\d+\.\d+', f)]
    
    formatCounts = {}
    for f in allFiles:
        ext = os.path.splitext(f)[1].lower()
        formatCounts[ext] = formatCounts.get(ext, 0) + 1
    
    breakdownStr = ""
    for ext, count in formatCounts.items():
        breakdownStr += f"    - {ext.upper()}: {count}\n"

    numericParts = [re.findall(r'(\d+)', f) for f in allFiles]
    numericParts = [int(p[0]) for p in numericParts if p]
    minNum, maxNum = (min(numericParts), max(numericParts)) if numericParts else ('N/A', 'N/A')

    summary = STRINGS['prompt_file_summary'][languageCode].format(
        total_count=len(allFiles),
        min_num=minNum,
        max_num=maxNum,
        breakdown=breakdownStr,
        decimal_count=len(filesWithDecimals)
    )
    print("\n" + "="*20)
    print(summary)
    print("="*20 + "\n")

    while True:
        choice = input(STRINGS['prompt_confirm_decimal_ignore'][languageCode]).strip().lower()
        if choice in ['y', 'yes']:
            return [os.path.join(sourceDirectory, f) for f in allFiles]
        elif choice in ['n', 'no']:
            return [os.path.join(sourceDirectory, f) for f in allFiles if f not in filesWithDecimals]
        else:
            print(STRINGS['error_invalid_choice'][languageCode])

def runInteractiveMode(globalLanguage='zh'): 
    print("\n--- 欢迎进入交互模式 ---")

    while True:
        modeChoice = input(f"{STRINGS['prompt_mode_select'][globalLanguage]}\n> ").strip()
        if modeChoice in ['1', '2']:
            selectedMode = 'comic' if modeChoice == '1' else 'novel'
            modeDisplayName = STRINGS[f'{selectedMode}_mode_name'][globalLanguage]
            if confirmUserInput(globalLanguage, 'prompt_confirm_mode', modeDisplayName):
                break
        else:
            print(STRINGS['error_invalid_choice'][globalLanguage])
    
    sourcePath = ""
    while True:
        print(STRINGS['multi_folder_tip'][globalLanguage])
        path = input(f"{STRINGS['prompt_input_path'][globalLanguage]}\n> ").strip().replace('"', '')
        if os.path.isdir(path):
            if confirmUserInput(globalLanguage, 'prompt_confirm_path', path):
                sourcePath = path
                break
        else:
            print(STRINGS['error_dir_not_exist'][globalLanguage].format(path))

    filesToProcess = presentFileSummaryAndGetChoice(sourcePath, globalLanguage)
    if not filesToProcess:
        print("No files to process. Exiting interactive mode.")
        return
    
    pardofelisTempDir = os.path.join(os.path.dirname(sourcePath), f"temp_processing_{int(time.time())}")
    os.makedirs(pardofelisTempDir, exist_ok=True)
    
    try:
        for f_path in filesToProcess:
            shutil.copy(f_path, pardofelisTempDir)
        
        processingPath = pardofelisTempDir

        while True:
            print(STRINGS['prompt_final_format'][globalLanguage])
            formatChoice = input("> ").strip()
            if formatChoice in FORMAT_CHOICE_MAP:
                formatName = FORMAT_CHOICE_MAP[formatChoice]
                if formatName == 'all_native':
                    formatDisplay = "全部原生格式 (EPUB+PDF+CBZ)"
                else:
                    formatDisplay = formatName.upper()
                if confirmUserInput(globalLanguage, 'prompt_confirm_format', formatDisplay):
                    break
            else:
                print(STRINGS['error_invalid_choice'][globalLanguage])
        
        sakuraParams = argparse.Namespace()
        sakuraParams.mode = selectedMode
        sakuraParams.path = [processingPath]
        sakuraParams.format = formatChoice
        sakuraParams.lang = globalLanguage
        sakuraParams.outputpath = None
        
        defaultBaseName = os.path.basename(os.path.normpath(sourcePath))
        outputBaseName = input(f"请输入输出文件的基础名称 (回车使用默认: '{defaultBaseName}'):\n> ").strip() or defaultBaseName
        sakuraParams.output = outputBaseName
        
        defaultQuality = 85
        qualityInput = input(f"请输入图片质量 (1-100, 回车使用默认: {defaultQuality}):\n> ").strip()
        sakuraParams.quality = int(qualityInput) if qualityInput.isdigit() and 1 <= int(qualityInput) <= 100 else defaultQuality
        
        defaultTitle = sakuraParams.output or os.path.basename(os.path.normpath(sourcePath))
        titleInput = input(f"请输入电子书标题 (回车使用默认: '{defaultTitle}'):\n> ").strip() or defaultTitle
        sakuraParams.title = titleInput
        
        defaultWorkers = os.cpu_count() or 1
        workersInput = input(f"请输入并行处理的线程数 (回车使用默认: {defaultWorkers}):\n> ").strip()
        sakuraParams.workers = int(workersInput) if workersInput.isdigit() and int(workersInput) > 0 else defaultWorkers

        sakuraParams.interactive = True 
        
        print(STRINGS['starting_task'][globalLanguage])
        runTask(sakuraParams)

    finally:
        if os.path.exists(pardofelisTempDir):
            shutil.rmtree(pardofelisTempDir)
            print(f"已清理临时处理文件夹: {pardofelisTempDir}")

def showMainMenu(argumentParser): 
    while True:
        print(f"{STRINGS['prompt_main_menu']['en']}\n{STRINGS['prompt_main_menu']['zh']}\n{STRINGS['prompt_main_menu']['ja']}")
        choice = input("> ").strip()
        if choice == '1':
            print("\n请选择语言 (Select Language):")
            print("1) 中文 (Chinese)")
            print("2) English")
            print("3) 日本語 (Japanese)")
            langChoice = input("> ").strip()
            if langChoice == '1':
                globalLanguage = 'zh'
            elif langChoice == '2':
                globalLanguage = 'en'
            elif langChoice == '3':
                globalLanguage = 'ja'
            else:
                globalLanguage = 'zh'  
            runInteractiveMode(globalLanguage)
            break
        elif choice == '2':
            argumentParser.print_help()
            break
        elif choice == '3':
            print(f"{STRINGS['exiting']['en']} / {STRINGS['exiting']['zh']} / {STRINGS['exiting']['ja']}")
            break
        else:
            print(STRINGS['error_invalid_choice']['en'])

if __name__ == '__main__':
    checkDependencies()
    suParser = createArgumentParser()
    if len(sys.argv) == 1: 
        showMainMenu(suParser)
    else:
        try:
            kosmaArgs = suParser.parse_args()
            kosmaArgs.interactive = False
            runTask(kosmaArgs)
        except argparse.ArgumentError as error: 
            print(f"参数错误 (Argument Error): {error}")
        except SystemExit as error: 
             if error.code != 0:
                 print("解析参数时出错。(Error parsing arguments.)")