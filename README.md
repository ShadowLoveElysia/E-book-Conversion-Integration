# Batch E-book Converter

**Other Languages / 其他语言 / 他の言語:**
- [中文版本 (Chinese)](docx/README_中文.md)
- [日本語版 (Japanese)](docx/README_日本語.md)

---

A powerful Python tool for batch converting various document formats into different e-book formats. Supports both comic mode (image-first) and novel mode (text-first) processing.

## Features

- **Multi-format Support**: Convert between PDF, EPUB, CBZ, MOBI, AZW3, and many other formats
- **Dual Processing Modes**: 
  - Comic Mode: Optimized for scanned documents and image-heavy content
  - Novel Mode: Optimized for text-based e-books
- **Batch Processing**: Process entire folders of documents at once
- **Parallel Processing**: Multi-threaded conversion for faster performance
- **Interactive & Command-line**: Both GUI-like interactive mode and command-line interface
- **Multi-language Support**: Chinese, English, and Japanese interfaces
- **Automatic Calibre Integration**: Automatic download and setup of Calibre tools
- **Quality Control**: Adjustable image quality settings

## Installation

### Prerequisites

Install the required Python packages:

```bash
pip install PyMuPDF Pillow EbookLib requests tqdm natsort
```

### Calibre Integration

The tool handles Calibre installation:
- **Windows**: Automatic download and setup of portable Calibre (only Windows supports automatic installation)
- **Linux/macOS**: Manual installation required - you need to configure Calibre path manually
- **Native Formats**: CBZ and PDF consolidation to EPUB (comic mode only) works without Calibre

**Note**: For Linux and macOS users, you need to manually install Calibre and ensure the `ebook-convert` tool is in your system PATH. The native CBZ and PDF to EPUB conversion (comic mode only) does not require Calibre.

## Usage

### Interactive Mode

Run without arguments for interactive mode:

```bash
python 批量电子书整合.py
```

### Command-line Mode

```bash
python 批量电子书整合.py -p "path/to/source" -f epub -m comic
```

#### Parameters

**Required:**
- `-p, --path`: Source folder path containing files to convert
- `-f, --format`: Target output format (epub, pdf, cbz, mobi, etc.)
- `-m, --mode`: Processing mode (`comic` or `novel`)

**Optional:**
- `-o, --output`: Output file base name (default: folder name)
- `-q, --quality`: Image quality 1-100 (default: 85)
- `-t, --title`: E-book title in metadata
- `-l, --lang`: Interface language (zh/en/ja, default: zh)
- `-w, --workers`: Number of parallel threads (default: CPU count)

### Format Options

**Common Formats:**
- `epub` - Universal e-book format
- `pdf` - Universal document format  
- `cbz` - Comic book archive

**Kindle Formats:(requires Calibre)**
- `mobi` - Old Kindle format
- `azw3` - New Kindle format

**Other Formats (requires Calibre):**
- `docx`, `txt`, `kepub`, `fb2`, `lit`, `lrf`, `pdb`, `pmlz`, `rb`, `rtf`, `tcr`, `txtz`, `htmlz`

**Special:**
- `all_native` - Generate EPUB + PDF + CBZ simultaneously

## Examples

### Comic Mode Examples

```bash
# Convert PDF scans to EPUB
python 批量电子书整合.py -p "C:\MyScans" -f epub --mode comic

# Convert CBZ comics to PDF
python 批量电子书整合.py -p "D:\Comics" -f pdf --mode comic

# Convert to multiple formats
python 批量电子书整合.py -p "C:\Comics" -f all_native --mode comic
```

### Novel Mode Examples

```bash
# Convert EPUB novels to MOBI for Kindle
python 批量电子书整合.py -p "D:\Novels" -f mobi --mode novel

# Convert mixed formats to EPUB
python 批量电子书整合.py -p "E:\Books" -f epub --mode novel

# High quality conversion
python 批量电子书整合.py -p "F:\Library" -f azw3 --mode novel -q 95
```

## Processing Modes

### Comic Mode
- **Best for**: Scanned documents, manga, comics, image-heavy content
- **Process**: Files → Images → EPUB → Final format
- **Optimization**: Image quality and layout preservation

### Novel Mode  
- **Best for**: Text-based e-books, novels, documents
- **Process**: Files → PDF → Merged PDF → EPUB → Final format
- **Optimization**: Text flow and reading experience

## Supported Input Formats

- **PDF**: Scanned documents, digital PDFs
- **CBZ/CBR**: Comic book archives
- **EPUB**: Digital e-books
- **MOBI/AZW3**: Kindle formats
- **Other**: Any format supported by Calibre

## Output Quality

- **Image Quality**: Adjustable 1-100 (default: 85)
- **Parallel Processing**: Multi-threaded for speed
- **Format Preservation**: Maintains original layout and formatting
- **Metadata**: Preserves book titles and author information

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Install required packages with pip
2. **Calibre Not Found**: Use interactive mode for automatic download
3. **Permission Errors**: Run as administrator or check folder permissions
4. **DRM Protected Files**: Cannot process DRM-protected content

### Performance Tips

- Use SSD storage for faster processing
- Adjust worker count based on CPU cores
- Lower image quality for faster processing
- Close other applications during large conversions

## Acknowledgments

This project relies on several excellent open-source libraries and tools:

### Core Dependencies
- **[Calibre](https://calibre-ebook.com/)**: The powerful e-book management and conversion suite that enables format conversions
- **[PyMuPDF](https://pymupdf.readthedocs.io/)**: High-performance PDF and image processing
- **[Pillow](https://python-pillow.org/)**: Python Imaging Library for image manipulation
- **[EbookLib](https://github.com/aerkalov/ebooklib)**: E-book creation and manipulation library

### Additional Libraries
- **requests**: HTTP library for web requests
- **tqdm**: Progress bar library for user experience
- **natsort**: Natural sorting for file organization
- **argparse**: Command-line argument parsing

### Special Thanks
- **Calibre Team**: For providing the most comprehensive e-book conversion tools
- **Open Source Community**: For maintaining and improving these essential libraries
- **Contributors**: Everyone who has helped improve this tool

This tool would not be possible without the excellent work of these open-source projects and their maintainers.
