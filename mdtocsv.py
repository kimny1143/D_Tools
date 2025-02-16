import streamlit as st
import pandas as pd
import io
import base64
import re

def markdown_to_dataframe(markdown_content):
    def parse_table_row(row):
        # '|'で分割し、先頭と末尾の空要素を削除
        cells = row.split('|')[1:-1]
        return [cell.strip() for cell in cells]

    lines = [line.strip() for line in markdown_content.strip().split('\n') if line.strip()]
    
    # ヘッダー行を探す
    header_index = next((i for i, line in enumerate(lines) if '|' in line and not line.startswith('|--')), None)
    if header_index is None:
        st.error("有効なMarkdownテーブルが見つかりません。")
        return pd.DataFrame()

    header = parse_table_row(lines[header_index])
    
    # データ行を解析（ヘッダー行とセパレーター行をスキップ）
    data = [parse_table_row(line) for line in lines[header_index+2:] if '|' in line and not line.startswith('|--')]
    
    # デバッグ情報
    st.write(f"ヘッダー: {header}")
    st.write(f"ヘッダーの列数: {len(header)}")
    st.write(f"データ行数: {len(data)}")
    if data:
        st.write(f"最初のデータ行の列数: {len(data[0])}")
        st.write(f"最初のデータ行: {data[0]}")

    # ヘッダーとデータの列数が一致しない場合の処理
    if data:
        max_columns = max(len(header), max(len(row) for row in data))
        header = header + ['Column'+str(i+1) for i in range(len(header), max_columns)]
        data = [row + [''] * (max_columns - len(row)) for row in data]

    df = pd.DataFrame(data, columns=header)
    
    # 必要な列のみを抽出し、新しい順序で並べ替え
    columns_to_keep = ['№', '楽曲名', '歌手名', 'DK№', 'OrgTime']
    # 「備考」を含む列名を検索
    note_column = next((col for col in df.columns if '備考' in col), None)
    if note_column:
        columns_to_keep.append(note_column)
    
    df_reshaped = df[[col for col in columns_to_keep if col in df.columns]]
    
    # 列名を変更（必要に応じて）
    df_reshaped = df_reshaped.rename(columns={
        '楽曲名': '曲名',
        '備考': 'RecSheet備考'
    })
    
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
        try:
            df = markdown_to_dataframe(content)
            if not df.empty:
                st.write("変換されたデータのプレビュー:")
                st.dataframe(df)
                
                st.markdown("### CSVファイルのダウンロード")
                st.markdown("1. UTF-8 with BOM (推奨):")
                st.markdown(get_csv_download_link(df, 'utf-8-sig'), unsafe_allow_html=True)
                
                st.markdown("2. Shift-JIS/CP932 (Excel互換):")
                st.markdown(get_csv_download_link(df, 'shift_jis'), unsafe_allow_html=True)
            else:
                st.error("データの変換に失敗しました。Markdownの形式を確認してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

st.markdown("""
### 使用方法
0.まずは高精度な生成AIを使ってPDFからMarkdownに変換してください。Claude.aiを使うと簡単です。
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