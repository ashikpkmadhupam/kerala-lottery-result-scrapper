from .firebase_config import firestore_db, messaging
import datetime
import logging

def publish_lottery_result(lottery_name: str, result: dict):
    today = datetime.date.today().strftime("%Y-%m-%d")

    firestore_db \
        .collection("lottery_results") \
        .document(lottery_name) \
        .set(result)

    logging.info("Firestore upload successful")

def get_last_notified_result():
    doc_ref  = firestore_db \
        .collection("last_sent_notification") \
        .document("details")
    doc  = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        last_notified = data.get("last_notified_result")
        logging.info(f"Last notified result : {last_notified}")
        return last_notified
    else:
        logging.info(f"Last notified result not exists!")
        return None
    
def push_last_notified_result(lottery_name, date):

    notification_details = {"last_notified_result" : lottery_name+"_"+date}
    firestore_db \
        .collection("last_sent_notification") \
        .document("details") \
        .set(notification_details)

    logging.info("Firestore last_notified update successful")


def push_fcm_notification(lottery_name, draw_date):
    notification_title = "💰 Did You Win Today?"
    notification_body = f"{lottery_name} draw results ({draw_date}) are published. Tap to check your prize instantly!"
    message = messaging.Message(notification=messaging.Notification(notification_title, notification_body), android=messaging.AndroidConfig(
        priority="high",
        notification=messaging.AndroidNotification(
            channel_id="high_priority_channel"
        )
    ), topic="lottery_result_notifications")
    response = messaging.send(message)
    logging.info(f"FCM Notification push successful {response}")

            