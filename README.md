# RefMaker - Automated Academic Reference Generator

A Python tool that automatically extracts bibliographic information from PDF research papers using AI and generates properly formatted BibTeX references along with paper summaries.

## 🚀 Features

- **Automated PDF Processing**: Recursively scans directories for PDF files
- **AI-Powered Extraction**: Uses OpenAI GPT-4o-mini to extract paper metadata (title, authors, year, DOI)
- **BibTeX Generation**: Automatically generates properly formatted BibTeX entries
- **Paper Summaries**: Creates concise summaries of each paper's main contributions
- **Batch Processing**: Processes multiple PDFs in one run
- **Standalone Executable**: Can be compiled into a single executable file with PyInstaller

## 📋 Requirements

### For Running from Source
- Python 3.8+
- OpenAI API key

### Python Dependencies
- `PyMuPDF` (fitz) - PDF text extraction
- `pydantic` - Data validation and parsing
- `openai` - OpenAI API integration
- `instructor` - Structured output from AI models
- `python-dotenv` - Environment variable management

## 🛠️ Installation

### Option 1: From Source

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install PyMuPDF pydantic openai instructor python-dotenv
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Option 2: Compiled Executable

1. Download the compiled executable from releases
2. Place the `.env` file in the same directory as the executable
3. Run the executable directly
> **Note:** The compiled executable currently available is only compatible with Mac M1 (Apple Silicon) devices. However, you can package your own executable for other platforms using PyInstaller.

## 🔧 Building Executable

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build using the provided spec file:
   ```bash
   pyinstaller --onefile --clean refmaker.py
   ```

The executable will be created in the `dist/` directory.

## 📖 Usage

### Running the Tool

1. **Place PDF files**: Put your research papers (PDF files) in the same directory as the script/executable, or in subdirectories
2. **Set up API key**: Ensure your `.env` file with OpenAI API key is in the same directory
3. **Run the tool**:
   ```bash
   # From source
   python refmaker.py
   
   # Or run the executable
   ./refmaker
   ```

### Output Files

The tool generates two main output files:

1. **`output.txt`**: Contains extracted paper information for each PDF
   - File path and processing status
   - Extracted title, authors, year, and DOI
   - Processing progress and any errors

2. **`references.bib`**: BibTeX bibliography file with:
   - Properly formatted BibTeX entries
   - Paper summaries as comments
   - Source file references

### Example Output

**output.txt**:
```
--------------------------------------------------
File #1
Path: /path/to/paper.pdf
--------------------------------------------------
Title: Deep Learning for Computer Vision
Authors: John Smith, Jane Doe
Year: 2023
DOI: 10.1109/example.2023.123456
```

**references.bib**:
```bibtex
@article{smith2023,
  title = {Deep Learning for Computer Vision},
  author = {John Smith and Jane Doe},
  year = {2023},
  journal = {IEEE Transactions on Pattern Analysis},
  doi = {10.1109/example.2023.123456}
}
% Summary: This paper presents novel deep learning architectures for computer vision tasks, achieving state-of-the-art performance on benchmark datasets.
% Source file: /path/to/paper.pdf
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the same directory as the script/executable:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Customization

You can modify the following in the source code:

- **Number of pages to extract**: Change `num_pages` parameter in `read_pdf_text()`
- **AI model**: Modify the model name in `AITextExtractor` class
- **Output file names**: Change `output_file` and `bib_file` paths in `main()`

## 🔍 How It Works

1. **PDF Discovery**: Recursively finds all PDF files in the directory
2. **Text Extraction**: Extracts text from the first 3 pages of each PDF using PyMuPDF
3. **AI Analysis**: Sends extracted text to OpenAI GPT-4o-mini for metadata extraction
4. **BibTeX Generation**: Creates properly formatted bibliography entries
5. **Summary Generation**: Generates concise paper summaries
6. **File Output**: Saves results to `output.txt` and `references.bib`

## 📁 Project Structure

```
refmaker/
├── refmaker.py          # Main script
├── refmaker.spec        # PyInstaller specification
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API key)
├── README.md           # This file
└── your_pdfs/          # Place your PDF files here
```

## 🚨 Important Notes

- **API Usage**: This tool uses OpenAI's API, which incurs costs based on usage
- **PDF Quality**: Works best with text-based PDFs; may struggle with scanned documents
- **Internet Required**: Needs internet connection for AI processing
- **Rate Limits**: Respects OpenAI API rate limits; processing large batches may take time

## 🐛 Troubleshooting

### Common Issues

1. **"No text extracted"**: PDF might be scanned/image-based
2. **API errors**: Check your OpenAI API key and account credits
3. **Permission errors**: Ensure write permissions in the directory
4. **Missing .env**: Place the `.env` file in the same directory as the executable

### Error Handling

The tool includes robust error handling:
- Continues processing other files if one fails
- Logs errors to output files
- Provides detailed error messages

## 📄 License

This project is provided as-is for academic and research purposes.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

---

**Note**: This tool is designed for academic research purposes. Please respect copyright laws and publisher terms when processing research papers.
