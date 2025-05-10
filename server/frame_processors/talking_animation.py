from PIL import Image
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    OutputImageRawFrame,
    SpriteFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


class TalkingAnimation(FrameProcessor):
    """ボットの視覚的なアニメーション状態を管理します。

    ボットの現在の発話状態に基づいて、静的（聞き取り中）と
    アニメーション（発話中）の状態を切り替えます。
    """

    def __init__(self):
        super().__init__()
        self._is_talking = False
        sprites = []
        for i in range(0, 300, 3):
            # 画像ファイルへのフルパスを構築
            full_path = "/app/assets/gemmy_{:05}.png".format(i)
            # 画像を開き、OutputImageRawFrameに変換
            with Image.open(full_path) as img:
                sprites.append(OutputImageRawFrame(image=img.tobytes(), size=img.size, format=img.format))


        # 静的およびアニメーション状態をインスタンス変数として定義
        # これらはクラスインスタンス作成時に一度だけ初期化される
        self.quiet_frame = sprites[0]  # ボットが聞き取り中の静止フレーム
        self.talking_frame = SpriteFrame(images=sprites)  # ボットが発話中のアニメーションシーケンス

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """入力フレームを処理し、アニメーション状態を更新します。

        Args:
            frame: 処理する入力フレーム
            direction: パイプライン内のフレームの流れの方向
        """
        await super().process_frame(frame, direction)

        # ボットが話し始めたら、発話アニメーションに切り替え
        if isinstance(frame, BotStartedSpeakingFrame):
            if not self._is_talking:
                # 発話フレームにはインスタンス変数を使用
                await self.push_frame(self.talking_frame)
                self._is_talking = True
        # ボットが話し終えたら、静止フレームに戻す
        elif isinstance(frame, BotStoppedSpeakingFrame):
             # 静止フレームにはインスタンス変数を使用
            await self.push_frame(self.quiet_frame)
            self._is_talking = False

        # フレームの種類に関係なく、元のフレームをそのまま通過させる
        await self.push_frame(frame, direction)
