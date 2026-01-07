from .firebase_config import firestore_db
import datetime

def publish_lottery_result(lottery_name: str, result: dict):
    today = datetime.date.today().strftime("%Y-%m-%d")

    firestore_db \
        .collection("lottery_results") \
        .document(lottery_name) \
        .set(result)

    print("✅ Firestore upload successful")