import streamlit as st
import pandas as pd
import io
import base64

def markdown_to_dataframe(markdown_content):
    lines = markdown_content.strip().split('\n')
    header = [col.strip() for col in lines[0].split('|')[1:-1]]
    data = []
    for line in lines[2:]:
        row = [cell.strip() for cell in line.split('|')[1:-1]]
        data.append(row)
    df = pd.DataFrame(data, columns=header)
    
    # 必要な列のみを抽出し、新しい順序で並べ替え
    columns_to_keep = ['№', '楽曲名', '歌手名', 'DK№', 'OrgTime', 'RecSheet備考']
    df_reshaped = df[columns_to_keep]
    
    # 列名を変更（必要に応じて）
    df_reshaped = df_reshaped.rename(columns={'楽曲名': '曲名'})
    
    return df_reshaped

def get_csv_download_link(df, encoding='utf-8-sig'):
    try:
        csv = df.to_csv(index=False, encoding=encoding)
        b64 = base64.b64encode(csv.encode(encoding)).decode()
    except UnicodeEncodeError:
        if encoding == 'shift_jis':
            try:
                csv = df.to_csv(index=False, encoding='cp932')
                b64 = base64.b64encode(csv.encode('cp932')).decode()
                encoding = 'cp932'
            except UnicodeEncodeError:
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
                encoding = 'utf-8-sig'
    return f'<a href="data:file/csv;base64,{b64}" download="converted_data.csv">ダウンロード CSV ファイル ({encoding})</a>'

st.title('Markdown テーブルを CSV に変換')

uploaded_file = st.file_uploader("Markdown ファイルをアップロードしてください", type="md")

if uploaded_file is not None:
    content = uploaded_file.getvalue().decode("utf-8")
    st.text_area("アップロードされた Markdown 内容", content, height=200)
    
    if st.button('CSV に変換'):
        df = markdown_to_dataframe(content)
        st.write("変換されたデータのプレビュー:")
        st.dataframe(df)
        
        st.markdown("### CSVファイルのダウンロード")
        st.markdown("1. UTF-8 with BOM (推奨):")
        st.markdown(get_csv_download_link(df, 'utf-8-sig'), unsafe_allow_html=True)
        
        st.markdown("2. Shift-JIS/CP932 (Excel互換):")
        st.markdown(get_csv_download_link(df, 'shift_jis'), unsafe_allow_html=True)

st.markdown("""
### 使用方法
0.まずは高精度な生成AIを使ってPDFからMarkdownに変換してください。
プロンプト例：「PDFの内容を分析しMarkdown化しDataFrameにて表示した後、.mdファイル出力してください。」
1. 「Browse files」ボタンをクリックしてMarkdownファイルをアップロードします。
2. アップロードされたMarkdownの内容が表示されます。
3. 「CSV に変換」ボタンをクリックします。
4. 変換されたデータのプレビューが表示されます。
5. 希望するエンコーディングのCSVファイルをダウンロードします：
   - UTF-8 with BOM: 多くのアプリケーションで正しく表示されます。
   - Shift-JIS/CP932: 日本語版Excelでの互換性が高いです。

注意: エンコーディングによっては一部の文字が正しく表示されない場合があります。その場合はUTF-8 with BOMを使用してください。
""")