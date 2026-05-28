import PyPDF2
import sys

def extract_pdf_content(pdf_path, pages=10):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"PDF总页数: {num_pages}")
            
            # 读取指定页数的内容
            text = ""
            for i in range(min(pages, num_pages)):
                page = pdf_reader.pages[i]
                text += page.extract_text() + "\n\n"
            
            print("="*50)
            print(f"前{pages}页内容:")
            print("="*50)
            print(text[:10000])  # 限制输出长度
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        pages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        extract_pdf_content(pdf_path, pages)
    else:
        print("Usage: python extract_pdf.py <pdf_path> [pages]")
