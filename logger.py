import logging


def setup_logger():
    logging.basicConfig(
        filename="sms_client.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def log_request(args):
    logging.info(f"Sending SMS: sender={args.sender}, recipient={args.recipient}, message={args.message}")


def log_response(status_code, body):
    logging.info(f"Received response: status_code={status_code}, body={body}")