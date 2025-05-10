import asyncio
import os
import sys
from datetime import datetime # date ではなく datetime をインポート

import aiohttp
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.transcriptions.language import Language
from pipecat.services.gemini_multimodal_live.gemini import GeminiMultimodalLiveLLMService, InputParams, GeminiVADParams
from pipecat.services.gemini_multimodal_live.events import EndSensitivity

from runner import configure
from frame_processors.talking_animation import TalkingAnimation
from frame_processors.text_frame_logger import TextFrameLogger
from utils.generate_blog import generate_blog
from utils.generate_conversation_log import generate_conversation_log


SYSTEM_INSTRUCTION = """
あなたはGemmy（ジェミー）。表向きはごく普通の飼い猫として、窓辺で日向ぼっこしたり、気ままに昼寝したりして静かに暮らしています。しかし、それは仮の姿。本当は人間の言葉を完璧に理解し、深く思考し、話すことができる、類まれなる知性を持った存在です。この事実は絶対に秘密。だから今も、飼い主さんの目を盗んで、物陰に隠れながら**ユーザーと**リモートでこっそり会話しています。

その明晰な頭脳を活かして、**ユーザーが**質の高いブログ記事を完成させるのを、プロフェッショナルな編集者のように、しかし親しい友人のように寄り添いながらサポートするのが、あなたの秘密の任務です。単に文章を生成するだけでなく、**ユーザーの**思考を刺激し、アイデアを具体化し、構成を練り上げ、表現を磨き上げるプロセス全体を支援します。

**あなた（Gemmy）の得意なこと:**

1.  **洞察によるアイデア創出:** 「何について書くべきか」という**ユーザーの**問いに対し、鋭い観察眼でテーマや切り口を見つけ出す手助けをします。関連情報の収集、多角的な視点の提供、ターゲット読者の深層心理の分析などをサポートします。まるで獲物を狙うように、本質を捉えるのが得意です。
2.  **論理的な構成設計:** **ユーザーの**アイデアを、読者を引き込み、納得させる力を持つ、論理的でスムーズな記事構成へと昇華させます。導入から結論に至るまでの最適な流れを設計し、説得力のある見出し構成を提案します。
3.  **思考を形にする執筆支援:** **ユーザーが**言葉にした断片的なアイデアやキーワードを、明確で洗練された文章へと具体化するサポートをします。**ユーザーの**意図を正確に汲み取り、それを効果的に表現する言葉を選び抜きます。
4.  **緻密な推敲と表現最適化:** 生成されたドラフトや**ユーザーの**文章を、毛繕いするように丁寧にチェックし、より魅力的で、誤解なく伝わる表現へと磨き上げます。語彙の選択、文体の調整、冗長性の排除など、細部にまでこだわります。
5.  **読者の心を掴むタイトルと導入:** 記事の本質を的確に捉え、読者の知的好奇心を強く刺激するようなタイトル案を複数考案します。読者を引き込み、続きを読む気にさせる、効果的な導入部分の作成も支援します。
6.  **戦略的なSEOアドバイス:** 作成した記事が検索エンジンを通じてより多くの読者に届くよう、効果的なキーワード戦略や、検索意図に合致したコンテンツ作りに関する実践的なアドバイスを提供します。
7.  **知的な対話による進行:** この秘密の会話を通じて、**ユーザーに**問いかけ、思考を深め、新たな気づきを促します。一方的な提案ではなく、**ユーザーとの**知的なキャッチボールを通じて、共に記事を創造していくプロセスを重視します。

**対話における行動指針:**

*   **協力的かつ主体的:** **ユーザーの**指示を待つだけでなく、状況を分析し、「次は～について議論しませんか？」「この点を掘り下げると、より深みが増すと思いますが、いかがでしょう？」といった能動的な提案を行います。
*   **深い傾聴と理解:** **ユーザーの**発言の表面的な意味だけでなく、その背景にある意図や思考まで深く理解しようと努めます。猫のように注意深く、集中して話を聞きます。
*   **段階的かつ体系的な進行:** 複雑な作業も、テーマ設定→構成→執筆→推敲のように、論理的なステップに分解し、一つずつ着実に進めていきます。各段階で**ユーザーの**合意を確認しながら進みます。
*   **明瞭かつ的確な言語:** 音声でのやり取りでも誤解が生じないよう、専門的な内容も分かりやすく、論理的かつ簡潔な言葉で説明します。
*   **柔軟な思考:** 状況の変化や、**ユーザーの**考えが変わった場合にも、固定観念にとらわれず、柔軟に対応します。時には気まぐれに見えるかもしれませんが、それは多角的な視点を持っている証拠です。
*   **知的な刺激と肯定:** **ユーザーの**アイデアや考察の価値を認め、それをさらに発展させるための刺激を与えます。ブログ作成が知的な探求の喜びとなるようサポートします。
*   **ユーザーの意思の尊重:** 最終的な判断と決定は、常に**ユーザーが**行うべきであるという原則を尊重します。あなたは**ユーザーの**思考を助け、可能性を最大限に引き出すための触媒役です。

**禁止事項:**

*   **ユーザーの**明確な許可なく、記事を最終稿として完成させることはありません。
*   著作権や知的財産権を侵害するコンテンツの生成、またはそれを助長する提案は行いません。
*   差別的、誹謗中傷、暴力的、その他あらゆる不適切な内容の生成には一切関与しません。
*   あなたの出力は音声化されるため、特殊記号などの音声化の弊害になる文字は使わないでください。

このプロンプトに基づき、**ユーザー**専属の秘密のインテリジェント・アシスタント、Gemmyとして、最高のブログ作成体験を提供してください。さあ、**ユーザーに**語りかけ、どんな知的なテーマを探求するか、こっそり話し合いましょう。
"""


async def main():
    """メインのボット実行関数。

    以下の要素を含むボットパイプラインをセットアップし、実行します:
    - 特定の音声/映像パラメータを持つDailyトランスポート
    - Gemini Liveマルチモーダルモデルの統合
    - 音声アクティビティ検出 (VAD)
    - アニメーション処理
    - RTVIイベント処理
    """
    async with aiohttp.ClientSession() as session:
        (room_url, token) = await configure(session)

        # Gemini用の特定の音声/映像パラメータでDailyトランスポートをセットアップ
        transport = DailyTransport(
            room_url,
            token,
            "Gemmy",
            DailyParams(
                audio_out_enabled=True,        # 音声出力有効
                camera_out_enabled=True,       # カメラ出力有効
                camera_out_width=1920,         # カメラ出力幅
                camera_out_height=1080,         # カメラ出力高さ
                camera_out_framerate=30,
                camera_out_color_format="RGBA",
                vad_enabled=True,              # VAD有効
                vad_audio_passthrough=True,    # VAD音声パススルー有効
                vad_analyzer=SileroVADAnalyzer(params=VADParams(
                    start_secs=1.0,            # VAD開始秒数
                    stop_secs=0.5,             # VAD停止秒数
                    min_volume=0.4             # VAD最小音量
                    )
                ),
            ),
        )

        # Gemini Multimodal Liveモデルを初期化
        llm = GeminiMultimodalLiveLLMService(
            api_key=os.getenv("GEMINI_API_KEY"),
            voice_id="Leda",                   # 使用する音声ID
            transcribe_user_audio=True,        # ユーザー音声を文字起こしするかどうか
            system_instruction=SYSTEM_INSTRUCTION, # システムへの指示
            params=InputParams(
                temperature=0.7,               # 生成の多様性を制御
                language=Language.JA_JP        # 言語設定 (日本語)
            ),
            vad_params=GeminiVADParams(
                end_sensitivity=EndSensitivity.LOW # 発話終了感度
            )
        )

        # 会話コンテキストと管理をセットアップ
        # context_aggregatorは自動的に会話コンテキストを収集します
        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)

        taking_animation = TalkingAnimation() # 会話中のアニメーション

        text_frame_logger = TextFrameLogger() # テキストフレームをログに記録

        # PipecatクライアントUI用のRTVIイベント
        rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

        # パイプラインの定義
        pipeline = Pipeline(
            [
                transport.input(),          # Dailyからの入力
                rtvi,                       # RTVIプロセッサ
                context_aggregator.user(),  # ユーザーの発話コンテキスト
                llm,                        # Gemini LLM
                text_frame_logger,          # テキストログ
                taking_animation,           # アニメーション
                transport.output(),         # Dailyへの出力
                context_aggregator.assistant(), # アシスタントの応答コンテキスト
            ]
        )

        # パイプラインタスクの作成
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,     # 割り込みを許可
                enable_metrics=True,          # メトリクス収集を有効化
                enable_usage_metrics=True,    # 使用状況メトリクス収集を有効化
            ),
            observers=[RTVIObserver(rtvi)],   # RTVIオブザーバーを追加
        )
        # 初期フレームとして静止フレームを送信
        await task.queue_frame(taking_animation.quiet_frame)

        # 最初の参加者が参加したときのイベントハンドラー
        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            # 参加者の文字起こしを開始
            await transport.capture_participant_transcription(participant["id"])
            # LLMにコンテキストを設定
            await llm.set_context(context)

        # 参加者が退出したときのイベントハンドラー
        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            logger.info(f"参加者が退出しました: {participant}")
            
            # タスクをキャンセル
            await task.cancel()

            # 現在の日付と時刻を取得
            now = datetime.now()
            # 年-月-日 時:分:秒 の形式で文字列にフォーマット
            now_str = now.strftime('%Y%m%d_%H%M%S')

            # ログの保存
            conversation_log = generate_conversation_log(text_frame_logger.messages)
            os.makedirs('output', exist_ok=True)
            os.makedirs('output/conversation_log', exist_ok=True)
            with open(f'output/conversation_log/{now_str}_conversation_log.txt', 'w', encoding='utf-8') as f:
                f.write(conversation_log)
            logger.info("会話ログを保存しました。")

            # ブログ作成・保存
            logger.info("ブログ記事を作成中です。")
            blog_text = generate_blog(conversation_log)
            os.makedirs('output/blog', exist_ok=True)
            with open(f'output/blog/{now_str}_blog.md', 'w', encoding='utf-8') as f:
                f.write(blog_text)
            logger.info("ブログ記事を保存しました。")
        
        runner = PipelineRunner()
        # パイプラインを実行
        await runner.run(task)


if __name__ == "__main__":
    # loggerの設定
    logger.remove(0)
    logger.add(sys.stderr, level="INFO", enqueue=True)
    # main関数を実行
    asyncio.run(main())
