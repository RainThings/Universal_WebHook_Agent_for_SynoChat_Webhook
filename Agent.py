from flask import Flask, request, jsonify
from urllib.parse import urlencode
import requests
import json
import time
from queue import Queue
from threading import Thread

app = Flask(__name__)

# 配置参数
SEND_INTERVAL_MS = 500  # 每条消息发送间隔，单位为毫秒
MAX_MESSAGE_LENGTH = 1500  # 最大消息长度，超过此长度则拆分

# 消息队列
message_queue = Queue()


# 处理消息发送的函数
def send_message():
    last_sent_time = time.time()  # 记录上次发送时间

    while True:
        # 阻塞等待消息队列
        message = message_queue.get(block=True)

        # 计算与上次发送的时间间隔
        elapsed_time = (time.time() - last_sent_time) * 1000  # 转换为毫秒
        if elapsed_time < SEND_INTERVAL_MS:
            time.sleep((SEND_INTERVAL_MS - elapsed_time) / 1000)

        # 发送消息
        try:
            response = requests.post(
                message['target_url'],
                data=message['payload'],
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"Sent message: {message['payload']}")
            print(f"Response: {response.status_code}, {response.text}")
        except requests.RequestException as e:
            print(f"Error sending message: {e}")

        last_sent_time = time.time()  # 更新上次发送时间


# 启动消息发送线程
thread = Thread(target=send_message)
thread.daemon = True
thread.start()


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    args = request.args.to_dict()
    raw_target_url = args.pop('target_url', None)

    if not raw_target_url:
        return jsonify({"error": "Target URL is required in query parameters"}), 400

    additional_query = urlencode(args)
    full_target_url = f"{raw_target_url}&{additional_query}" if additional_query else raw_target_url

    print(f"Decoded full target URL: {full_target_url}")

    incoming_data = request.json
    if not incoming_data:
        return jsonify({"error": "Invalid payload, JSON data required"}), 400

    # 转换 JSON 数据为文本
    def convert_to_text(data):
        if isinstance(data, dict):
            return "\n".join([f"{key}: {convert_to_text(value)}" for key, value in data.items()])
        elif isinstance(data, list):
            return ", ".join([convert_to_text(item) for item in data])
        else:
            return str(data)

    transformed_text = convert_to_text(incoming_data)

    # 拆分消息，如果消息长度超过最大限制
    def split_message(message_text, max_length):
        parts = []
        while len(message_text) > max_length:
            split_index = message_text.rfind("\n", 0, max_length)
            if split_index == -1:
                split_index = max_length
            parts.append(message_text[:split_index])
            message_text = message_text[split_index:].lstrip()
        if message_text:
            parts.append(message_text)
        return parts

    # 拆分长消息
    if len(transformed_text) > MAX_MESSAGE_LENGTH:
        message_parts = split_message(transformed_text, MAX_MESSAGE_LENGTH)
    else:
        message_parts = [transformed_text]

    # 加入队列，构造符合要求的 payload
    for part in message_parts:
        payload_data = f"payload={json.dumps({'text': part}, ensure_ascii=False)}"
        message_queue.put({
            "target_url": full_target_url,
            "payload": payload_data
        })

    return jsonify({"status": "success", "message": "Message is being processed"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
