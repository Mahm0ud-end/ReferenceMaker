import os
import sys
from pathlib import Path
import fitz  
from pydantic import BaseModel
from openai import OpenAI
import instructor
from dotenv import load_dotenv
def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(get_executable_dir(), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()  
class PaperInfo(BaseModel):
    title: str
    authors: list[str]
    year: int
    DOI: str
class PaperSummary(BaseModel):
    summary: str
class BibEntry(BaseModel):
    entry_type: str  
    key: str  
    title: str
    authors: list[str]
    year: int
    journal: str = ""
    booktitle: str = ""
    volume: str = ""
    number: str = ""
    pages: str = ""
    publisher: str = ""
    doi: str = ""
    url: str = ""
class AITextExtractor:
    def __init__(self, api_key: str):
        self.client = instructor.patch(OpenAI(api_key=api_key))
    def extract_paper_info(self, text:str, output_str:bool = True):
        result = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Extract title, authors, year, and DOI from the following text:\n\n{text}"},
            ],
            response_model=PaperInfo
        )
        if output_str:
            return f"Title: {result.title}\nAuthors: {', '.join(result.authors)}\nYear: {result.year}\nDOI: {result.DOI}"
        else:
            return result
    def generate_bib_entry(self, paper_info: PaperInfo) -> BibEntry:
        prompt = f"""
        CRITICAL: You MUST search online and find the OFFICIAL BibTeX citation for this paper. This is the highest priority approach.
        Paper Information:
        Title: {paper_info.title}
        Authors: {', '.join(paper_info.authors)}
        Year: {paper_info.year}
        DOI: {paper_info.DOI}
        SEARCH STRATEGY (in order of preference):
        1. **PRIMARY GOAL**: Find and use the OFFICIAL BibTeX citation from the paper's publisher website
           - Search publisher sites (IEEE, ACM, Springer, Elsevier, etc.)
           - Look for "Cite this paper" or "Export citation" buttons
           - Download/copy the official BibTeX entry provided by the publisher
        2. **SECONDARY**: Search academic databases (Google Scholar, DBLP, arXiv, PubMed, etc.)
           - These often provide official BibTeX exports
           - Use the exact citation format they provide
        3. **IF DOI EXISTS**: Use the DOI to find the official publication page and get their BibTeX
        4. **LAST RESORT**: Only if no official citation exists, manually construct one with accurate details
        REQUIREMENTS:
        - PRIORITIZE official publisher BibTeX over manual construction
        - If you find an official BibTeX, use it EXACTLY as provided (even if citation key format differs)
        - Use appropriate entry type (article, inproceedings, book, etc.) as found in official citation
        - Include ALL fields present in the official BibTeX
        - Only modify citation key to format: firstauthorlastname{paper_info.year} if absolutely necessary
        - Preserve all original publisher metadata, page ranges, volume/issue numbers, etc.
        The goal is to get the most authentic, publisher-approved citation possible.
        """
        result = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_model=BibEntry
        )
        return result
    def generate_paper_summary(self, text_content: str) -> str:
        prompt = f"""
        Based on the following paper text, generate a concise 2-3 sentence summary that captures:
        1. The main research objective/problem addressed
        2. The key methodology or approach used
        3. The main findings or contributions
        Text content:
        {text_content[:4000]}...  
        """
        result = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_model=PaperSummary
        )
        return result.summary
client = AITextExtractor(api_key=os.getenv("OPENAI_API_KEY"))
def read_pdf_text(filepath: str, num_pages: int = -1) -> str:
    doc = fitz.open(filepath)
    total_pages = len(doc)
    pages_to_read = total_pages if num_pages == -1 else min(num_pages, total_pages)
    text_output = []
    for page_index in range(pages_to_read):
        page = doc[page_index]
        text_output.append(page.get_text())
    doc.close()
    return "\n".join(text_output)
def find_all_pdfs(directory):
    pdf_files = []
    directory_path = Path(directory)
    for pdf_file in directory_path.rglob("*.pdf"):
        if pdf_file.is_file():
            pdf_files.append(pdf_file)
    return sorted(pdf_files)  
def format_bib_entry(bib_entry: BibEntry) -> str:
    bib_lines = [f"@{bib_entry.entry_type}{{{bib_entry.key},"]
    if bib_entry.title:
        bib_lines.append(f"  title = {{{bib_entry.title}}},")
    if bib_entry.authors:
        authors_str = " and ".join(bib_entry.authors)
        bib_lines.append(f"  author = {{{authors_str}}},")
    if bib_entry.year:
        bib_lines.append(f"  year = {{{bib_entry.year}}},")
    if bib_entry.journal:
        bib_lines.append(f"  journal = {{{bib_entry.journal}}},")
    elif bib_entry.booktitle:
        bib_lines.append(f"  booktitle = {{{bib_entry.booktitle}}},")
    if bib_entry.volume:
        bib_lines.append(f"  volume = {{{bib_entry.volume}}},")
    if bib_entry.number:
        bib_lines.append(f"  number = {{{bib_entry.number}}},")
    if bib_entry.pages:
        bib_lines.append(f"  pages = {{{bib_entry.pages}}},")
    if bib_entry.publisher:
        bib_lines.append(f"  publisher = {{{bib_entry.publisher}}},")
    if bib_entry.doi:
        bib_lines.append(f"  doi = {{{bib_entry.doi}}},")
    if bib_entry.url:
        bib_lines.append(f"  url = {{{bib_entry.url}}},")
    if bib_lines[-1].endswith(','):
        bib_lines[-1] = bib_lines[-1][:-1]
    bib_lines.append("}")
    return "\n".join(bib_lines)
def main():
    executable_dir = get_executable_dir()
    literature_dir = executable_dir
    output_file = os.path.join(executable_dir, "output.txt")
    bib_file = os.path.join(executable_dir, "references.bib")
    print(f"Executable located at: {executable_dir}")
    print(f"Searching for PDF files in: {literature_dir}")
    pdf_files = find_all_pdfs(literature_dir)
    print(f"Found {len(pdf_files)} PDF files.")
    if not pdf_files:
        print("No PDF files found in the directory.")
        return
    print(f"Found {len(pdf_files)} PDF files. Processing...")
    with open(output_file, 'w', encoding='utf-8') as f, open(bib_file, 'w', encoding='utf-8') as bib_f:
        bib_f.write("% Generated bibliography from PDF extraction\n")
        bib_f.write("% Each entry includes a summary comment\n\n")
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_path.name}")
            f.write("-" * 50 + "\n")
            f.write(f"File #{i}\n")
            f.write(f"Path: {pdf_path}\n")
            f.write("-" * 50 + "\n")
            text_content = read_pdf_text(str(pdf_path), num_pages=3)
            if not text_content.strip():
                print(f"Warning: No text extracted from {pdf_path.name}.")
                f.write("No text extracted from this file.\n")
                f.flush()  
            else:
                paper_info = client.extract_paper_info(text_content, output_str=False)
                paper_info_str = f"Title: {paper_info.title}\nAuthors: {', '.join(paper_info.authors)}\nYear: {paper_info.year}\nDOI: {paper_info.DOI}"
                print(f"Extracted paper info: {paper_info_str}")
                f.write(paper_info_str + "\n\n")
                f.flush()  
                print(f"Generating BibTeX entry for: {paper_info.title}")
                try:
                    bib_entry = client.generate_bib_entry(paper_info)
                    formatted_bib = format_bib_entry(bib_entry)
                    print(f"Generating summary for: {paper_info.title}")
                    summary = client.generate_paper_summary(text_content)
                    bib_f.write(formatted_bib)
                    bib_f.write(f"% Summary: {summary}\n")
                    bib_f.write(f"% Source file: {pdf_path}\n")
                    bib_f.write("\n")
                    bib_f.flush()  
                    print(f"Added BibTeX entry for: {bib_entry.key}")
                except Exception as e:
                    print(f"Error generating BibTeX entry for {paper_info.title}: {e}")
                    bib_f.write(f"% Error generating entry for: {paper_info.title}\n")
                    bib_f.write(f"% {str(e)}\n\n")
                    bib_f.flush()  
    print(f"\nProcessing complete!")
    print(f"Output saved to: {output_file}")
    print(f"Bibliography saved to: {bib_file}")
    print(f"Processed {len(pdf_files)} PDF files.")
if __name__ == "__main__":
    main()