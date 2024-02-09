from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_webhook():
    # Get the JSON data sent by the webhook
    data = request.json

    # Handle the webhook data as needed
    # Process the data, store it, or trigger specific actions based on the event
    print(f"Received webhook data: {data}")
    print(f"{request.headers.get('X-My-Custom-Header') = }")

    # Respond with a success message
    return jsonify({"message": "Webhook received successfully"}), 200


def main():
    print("Hello World")
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
