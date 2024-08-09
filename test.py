#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/15 17:44:02
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


import datetime


# mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
# mpv_process = subprocess.Popen(
#     mpv_command,
#     stdin=subprocess.PIPE,
#     stdout=subprocess.DEVNULL,
#     stderr=subprocess.DEVNULL,
# )

# print(mpv_process)


# audio_stream = tts(text="人会有幻觉，大型语言模型也会有幻觉。近日，OpenAI 安全系统团队负责人 Lilian Weng 更新了博客，介绍了近年来在理解、检测和克服 LLM 幻觉方面的诸多研究成果。", stream=True)


# audio = b""
# for chunk in audio_stream:
#     if chunk is not None and chunk != b'\n':
#         decoded_hex = chunk
#         mpv_process.stdin.write(decoded_hex)  # type: ignore
#         mpv_process.stdin.flush()
#         audio += decoded_hex


# # 结果保存至文件
# timestamp = int(time.time())
# file_name = f'output_total_{timestamp}.mp3'
# with open(file_name, 'wb') as file:
#     file.write(audio)


if __name__ == "__main__":
    from aifori.task import add_message2memory

    # message = MessageORM(from_role="user", to_role="ai", from_id="user_id", to_id="ai_id", content="example_data")

    message = {'id': 186, 'session_id': '7ed9b796-1322-461a-bb5b-68deeee75184', 'from_role': 'agent', 'from_id': 'fe918725-ee28-4add-834b-46cb1ecaf56b',
               'content': '作为AI，我没有个人喜好，但我可以欣赏很多歌手的才华。如果你愿意分享，我很乐意听听你喜欢的歌手，也许我们可以一起探讨他们的音乐和诗歌。你最近有没有听什么让你印象深刻的歌曲？', 'to_role': 'user', 'to_id': '34d0f275-1e7c-4899-921c-94b6338856c1', 'create_datetime': datetime.datetime(2024, 7, 30, 17, 35, 36, 408470)}
    result = add_message2memory.delay(message)
    print(f"Task sent: {result.id}")
    # print(f"Task result: {result.get()}")
