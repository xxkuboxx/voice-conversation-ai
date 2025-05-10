from loguru import logger


def generate_conversation_log(logger_messages):
    conversation_log = ''
    for entry in logger_messages:
        for speaker, message in entry.items():
            formatted_message = message.strip()
            conversation_log += f"{speaker}: {formatted_message}\n\n"
    return conversation_log
