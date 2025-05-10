from typing import List, Dict
import os

from loguru import logger
from pipecat.frames.frames import (
    Frame,
    TextFrame,
    TTSStoppedFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

class TextFrameLogger(FrameProcessor):
    """
    LLMから出力されたテキストフレームをロギングする。
    """
    def __init__(self):
        super().__init__()
        self.message_chunks: List[str] = []
        self.messages: List[Dict[str, str]] = []

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)

        if isinstance(frame, TextFrame):
            is_user_text = hasattr(frame, 'user_id') and frame.user_id == 'user'
            if is_user_text:
                user_message = frame.text
                self.messages.append({'user': user_message})
                logger.info(f'user: {user_message}')
            else:
                if not self.message_chunks:
                    self.message_chunks.append(frame.text)
                elif self.message_chunks[-1] == frame.text: # なぜか同じframeが必ず2連続で来る現象があるのでその対応策
                    pass
                else:
                    self.message_chunks.append(frame.text)

        if isinstance(frame, TTSStoppedFrame):
            ai_message = ''.join(self.message_chunks)
            logger.info(f'Gemmy: {ai_message}')
            self.messages.append({'Gemmy':ai_message})
            self.message_chunks = []
