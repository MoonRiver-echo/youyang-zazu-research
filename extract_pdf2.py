import PyPDF2
import sys

def extract_pdf_content(pdf_path, output_path, pages=20):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"PDF总页数: {num_pages}")
            
            # 读取指定页数的内容
            text = ""
            for i in range(min(pages, num_pages)):
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text += f"\n===== 第{i+1}页 =====\n" + page_text
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(text)
            
            print(f"内容已保存到: {output_path}")
            return text
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 2:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2]
        pages = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        extract_pdf_content(pdf_path, output_path, pages)
    else:
        print("Usage: python extract_pdf.py <pdf_path> <output_path> [pages]")
