from flask import Flask, request, jsonify
from urllib.parse import urlencode
import requests
import json
from urllib.parse import unquote

app = Flask(__name__)


# @app.route('/webhook', methods=['POST'])


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # 获取所有查询参数
    args = request.args.to_dict()
    raw_target_url = args.pop('target_url', None)

    if not raw_target_url:
        return jsonify({"error": "Target URL is required in query parameters"}), 400

    # 将多余的查询参数重新拼接到 target_url
    additional_query = urlencode(args)
    if additional_query:
        full_target_url = f"{raw_target_url}&{additional_query}"
    else:
        full_target_url = raw_target_url

    print(f"Decoded full target URL: {full_target_url}")

    # def handle_webhook():
    #     # 获取未编码的 target_url
    #     raw_target_url = request.args.get('target_url')
    #     if not raw_target_url:
    #         return jsonify({"error": "Target URL is required in query parameters"}), 400
    #
    #     # 解码 target_url
    #     target_url = unquote(raw_target_url)
    #     print(f"Decoded target URL: {target_url}")

    # 打印接收到的请求体
    incoming_data = request.json
    if not incoming_data:
        return jsonify({"error": "Invalid payload, JSON data required"}), 400

    # 转换 JSON 数据为文本
    def convert_to_text(data):
        if isinstance(data, dict):
            return "\n".join([f"{key}:{convert_to_text(value)}" for key, value in data.items()])
        elif isinstance(data, list):
            return ", ".join([convert_to_text(item) for item in data])
        else:
            return str(data)

    transformed_text = convert_to_text(incoming_data)
    opayload = {
        "text": transformed_text
    }

    # 构造请求体
    payload_data = f"payload={json.dumps(opayload)}"

    try:
        response = requests.post(
            #target_url,
            full_target_url,
            data=payload_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(payload_data)
        return jsonify({
            "status": "success",
            "target_status_code": response.status_code,
            "target_response": response.text
        }), 200
    except requests.RequestException as e:
        return jsonify({"error": "Failed to forward request", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
