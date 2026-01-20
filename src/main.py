from scrapper.result_scrapper import scrape_lottery_result
from flask import Flask, jsonify


app = Flask(__name__)

@app.route("/", methods=["GET"])
def run_lottery_scrapper():
    result = scrape_lottery_result()
    return jsonify({"status": "SUCCESS", "message" : result}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8080, debug=False)