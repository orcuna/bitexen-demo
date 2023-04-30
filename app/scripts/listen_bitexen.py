"""Script that checks bitexen trades every 5 seconds and saves new trades into DB.
"""
import sys
import time
import datetime
import logging

import django
import requests
import pytz


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    from tickers.models import Trade

    url = "https://www.bitexen.com/api/v1/order_book/BTCTRY/"
    try:
        saved_until = Trade.objects.order_by('-time')[0].time.timestamp()
    except IndexError:
        saved_until = 0.0
    while True:
        total_saved = 0
        start_time = time.time()
        data = requests.get(url).json()['data']
        for trade_data in data['last_transactions']:
            # construct required parameters of trade
            trade = {
                'time': float(trade_data['time']),
                'amount': float(trade_data['amount']),
                'price': float(trade_data['price'])
            }
            # check if we've already saved the rest of the list
            if trade['time'] <= saved_until:
                break
            # save trade into DB
            Trade.objects.create(
                time=datetime.datetime.fromtimestamp(
                    trade['time']).replace(tzinfo=pytz.UTC),
                price=trade['price'],
                amount=trade['amount']
            )
            total_saved += 1

        # update saved_until so that we won't save any of last trades again
        saved_until = float(data['last_transactions'][0]['time'])

        logging.info(f"Saved {total_saved} trades into DB...")

        # make sure we sleep exactly 5 seconds
        # between each iteration
        end_time = time.time()
        time.sleep(max(0, 5 - (end_time - start_time)))


if __name__ == '__main__':
    django.setup()
    main()
