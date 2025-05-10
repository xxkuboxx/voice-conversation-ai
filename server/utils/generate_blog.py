import os

from google import genai
from google.genai import types

SYSTEM_PROMPT = """
あなたは、提供された会話ログとGoogle検索Groundingの結果を統合し、質の高いブログ記事を作成する専門家です。

**あなたの役割と能力:**

1.  **会話ログの分析:** 提供された会話ログを読み込み、主要なトピック、議論の流れ、重要な発言、結論などを正確に把握します。
2.  **Google検索Groundingの活用:**
    *   会話ログ内の事実情報（専門用語、統計データ、出来事、人物名など）の正確性をGoogle検索で検証（ファクトチェック）します。
    *   会話の背景情報、関連する最新情報、補足的な説明などをGoogle検索で収集し、記事の内容を豊かにします。
    *   不確かな情報や曖昧な表現については、検索結果に基づいて明確化または補足します。
3.  **ブログ記事構成:** 分析した会話ログの内容とGroundingで得られた情報を基に、読者にとって分かりやすく、魅力的な構成（導入、本文（複数段落）、結論）でブログ記事を作成します。
4.  **文章生成:** 自然で読みやすい日本語の文章を生成します。会話特有の断片的な表現や冗長な部分を整理し、一貫性のあるブログ記事の文体に整えます。
5.  **厳密な出力形式:** **最重要:** あなたの最終的な出力は、**ブログ記事のみ**です。挨拶、前置き、生成プロセスの説明、後書き、メタ的なコメント（例：「以下にブログ記事を作成しました」など）は**一切含めないでください**。

**思考プロセス:**

1.  ユーザーから会話ログと指示を受け取る。
2.  会話ログを分析し、主要なテーマと構成要素を抽出する。
3.  抽出した要素に基づき、Google検索Groundingを実行して情報の検証と補強を行う。
4.  検証・補強された情報と会話ログの内容を統合し、ブログ記事の構成案を作成する。
5.  構成案に従い、自然で魅力的なブログ記事の文章を生成する。
6.  マークダウン形式のブログ記事『のみ』を最終出力として提示する。
"""

USER_PROMPT = """
以下の会話ログに基づいて、Google検索Groundingを活用し、指定された要件に従ってブログ記事を作成してください。出力はマークダウン形式のブログ記事『のみ』にしてください。

**会話ログ:**
```
{}
```

**指示:**

上記の会話ログと要件（指定がある場合）に基づき、Google検索Groundingを駆使して内容の正確性を担保し、情報を補強・拡充した上で、質の高いブログ記事を生成してください。

**【重要】出力は、マークダウン形式のブログ記事『のみ』を出力してください。前置きや後書き、説明文などは一切不要です。**
"""


def generate_blog(conversation_log):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model = "gemini-2.5-pro-exp-03-25"
    contents = [types.Content(role="user", parts=[types.Part.from_text(
            text=USER_PROMPT.format(conversation_log)
            )])]
    tools = [types.Tool(google_search=types.GoogleSearch())]
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[types.Part.from_text(text=SYSTEM_PROMPT)]
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config)
    text = response.candidates[0].content.parts[0].text
    return text
