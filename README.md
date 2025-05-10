## 音声会話AIプロジェクト

このプロジェクトは、GoogleのGemini Multimodal Live APIを利用した音声チャットボットです。Daily Prebuiltを通じて簡単に接続し、デモンストレーションやテストを行うことができます。

参考リポジトリ：https://github.com/pipecat-ai/pipecat/tree/main/examples/simple-chatbot

### 特徴

*   **Gemini Bot:** GoogleのGemini Multimodal Live APIを活用し、自然な音声対話を実現します。
*   **Daily Prebuilt クライアント:** Daily Prebuiltのルームを通じて簡単に接続できます。迅速なテストやデモに最適です。

### 事前準備

*   **Dailyアカウント:**
    *   [Daily.co](https://dashboard.daily.co/login) に登録します。
    *   APIキーを取得し、控えておきます (上記 `.env` ファイルの `DAILY_API_KEY` に使用)。
    *   Dailyダッシュボードで新しいルームを作成し、そのURLを控えておきます (`.env` ファイルの `DAILY_SAMPLE_ROOM_URL` に使用)。
*   **Gemini APIキー:**
    *   [Google AI Studio](https://aistudio.google.com/) などでGemini APIキーを取得し、控えておきます (`.env` ファイルの `GEMINI_API_KEY` に使用)。
*   **`.env` ファイルの作成:** 
    * 以下コマンド実行後、作成された .env ファイルをエディタで開き、必要なAPIキーなどを設定します。
      ```bash
      cp server/env.example server/.env
      ```
      
### 実行手順

1.  **Dockerイメージのビルド:**
    サーバーディレクトリ（`server/`）に移動し、コンテナイメージをビルドします。
    ```bash
    cd server
    ```
    ```bash
    docker build -t voice-conversation-ai .
    ```

2.  **Dockerコンテナの実行:**
    ビルドしたイメージを使ってコンテナを起動します。 `--env-file .env` オプションで、先ほど作成した `.env` ファイルから環境変数を読み込みます。

    ```bash
    docker run -it --rm -v /$(pwd)/output:/app/output -p 7860:7860 --env-file .env voice-conversation-ai
    ```
    *   `-p 7860:7860`: ホストOSのポート7860をコンテナのポート7860にマッピングします。`.env` で `FAST_API_PORT` を変更した場合は、ホスト側のポート番号も合わせて変更してください (例: `-p <設定したポート>:7860`)。
    *   `-it`: インタラクティブモードで実行し、コンテナのログを表示します。
    *   `--rm`: コンテナ停止時に自動的にコンテナを削除します。
    *   `--env-file .env`: `.env` ファイルから環境変数を読み込みます。

3.  **アクセス:**
    * Webブラウザで http://localhost:7860 にアクセスします。
    * Daily Prebuiltのインターフェースが表示され、自動的にDailyルームに接続されます。
    * ブラウザからマイクへのアクセス許可を求められたら、許可してください。
    * "Join meeting" ボタンなどをクリックして入室し、ボットとの会話を開始できます。

