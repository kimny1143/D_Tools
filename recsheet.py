import os
import pandas as pd
import PyPDF2
import streamlit as st
from openai import OpenAI

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_markdown_table(api_key, text):
    client = OpenAI(api_key=api_key)
    prompt = f"以下のテキストをマークダウン形式のテーブルに変換してください:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts text to markdown tables."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        n=1,
        temperature=0.5
    )
    markdown_table = response.choices[0].message.content.strip()
    return markdown_table


def convert_markdown_to_csv(markdown_table):
    from io import StringIO
    
    # マークダウンのテーブルを整形
    lines = markdown_table.split('\n')
    formatted_lines = []
    for line in lines:
        if '|' in line:
            formatted_lines.append(line.strip('|').strip())
    formatted_markdown_table = '\n'.join(formatted_lines)
    
    try:
        # マークダウンのテーブルをDataFrameに変換
        df = pd.read_csv(StringIO(formatted_markdown_table), sep="|", skipinitialspace=True)
        
        # DataFrameをCSVに変換
        csv_data = df.to_csv(index=False)
        return csv_data
    except Exception as e:
        st.error(f"CSVへの変換に失敗しました: {str(e)}")
        return None

def main():
    st.title("RecSheet Converter")
    
    # APIキーの入力フィールド
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    
    # ファイルのアップロード
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None and api_key:
        # PDFからテキストを抽出
        text = extract_text_from_pdf(uploaded_file)
        
        # マークダウン形式のテーブルを生成
        markdown_table = generate_markdown_table(api_key, text)
        
        # マークダウンのテーブルを表示
        st.markdown(markdown_table)
        
        # マークダウンのテーブルをCSVに変換
        csv_data = convert_markdown_to_csv(markdown_table)
        
        if csv_data:
            # CSVデータをダウンロードボタンとして表示
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="output.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()