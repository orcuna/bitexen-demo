import datetime
import random
import time

import django
from django.db.models import Avg, Min, Max, Sum
import luigi
import pandas as pd
import pytz


class DatabaseTarget(luigi.Target):
    """Aggregation DB target to be used in output and require methods.
    """

    def __init__(self, full_name, type, time, luigi_flag):
        self.full_name = full_name
        self.type = type
        self.time = time
        self.luigi_flag = luigi_flag

    def get(self):
        try:
            return StatsAggregation.objects.get(
                full_name=self.full_name, type=self.type, time=self.time
            )
        except StatsAggregation.DoesNotExist:
            return None

    def save(self, stats):
        agg = self.get()
        if not agg:
            agg = StatsAggregation(
                full_name=self.full_name, type=self.type, time=self.time
            )
        agg.full_name = self.full_name
        agg.type = self.type
        agg.low = stats['low'] if not pd.isna(stats['low']) else None
        agg.high = stats['high'] if not pd.isna(stats['high']) else None
        agg.average = stats['average'] if not pd.isna(stats['average']) else None
        agg.volume = stats['volume'] if not pd.isna(stats['volume']) else None
        agg.luigi_flag = self.luigi_flag
        agg.save()

    def exists(self):
        agg = self.get()
        if not agg or agg.luigi_flag != self.luigi_flag:
            return False
        return True


class StatsMixin:
    """Mixin to create aggregate stats from list of stats.
    """

    def agg(self, lst_of_stats):
        df = pd.DataFrame(
            [(stats['low'], stats['high'],
              stats['average'], stats['volume'])
             for stats in lst_of_stats],
            columns=['low', 'high', 'average', 'volume']
        )
        df.dropna(inplace=True)
        return {
            'low': df['low'].min(),
            'high': df['high'].max(),
            'average': df['average'].mean(),
            'volume': df['volume'].sum()
        }


class HourlyStatsTask(luigi.Task, StatsMixin):
    """Luigi task that creates hourly stats by reading trades from DB.
    """

    time = luigi.Parameter()
    full_name = luigi.Parameter()
    luigi_flag = luigi.IntParameter()

    def output(self):
        luigi_flag = 0 if self.time < datetime.datetime.now(tz=pytz.UTC).replace(
                minute=0, second=0, microsecond=0) else self.luigi_flag
        return DatabaseTarget(
                type=StatsAggregationTypes.HOURLY,
                time=self.time, full_name=self.full_name, luigi_flag=luigi_flag
        )

    def run(self):
        hour = self.time
        hour_plus = self.time + datetime.timedelta(hours=1)
        buckets = Trade.objects.filter(time__range=(hour, hour_plus)).time_bucket(
                'time', '1 hour').annotate(
                    Avg('price'), Min('price'), Max('price'), Sum('amount'))
        lst_of_stats = [{
            'average': bucket['price__avg'],
            'low': bucket['price__min'],
            'high': bucket['price__max'],
            'volume': bucket['amount__sum'],
        } for bucket in buckets]
        self.output().save(self.agg(lst_of_stats))


class DailyStatsTask(luigi.Task, StatsMixin):
    """Luigi task that creates daily stats.
    """

    full_name = luigi.Parameter()
    luigi_flag = luigi.IntParameter()

    def requires(self):
        time = datetime.datetime.now(tz=pytz.UTC).replace(
                    minute=0, second=0, microsecond=0)
        return [
            HourlyStatsTask(
                time=time - datetime.timedelta(hours=i),
                full_name=self.full_name,
                luigi_flag=self.luigi_flag
            )
            for i in range(24)
        ]

    def output(self):
        return DatabaseTarget(
            type=StatsAggregationTypes.DAILY,
            time=None, full_name=self.full_name,
            luigi_flag=self.luigi_flag
        )

    def run(self):
        lst_of_stats = []
        for task in self.requires():
            aggregation = task.output().get()
            lst_of_stats.append({
                'low': aggregation.low,
                'high': aggregation.high,
                'average': aggregation.average,
                'volume': aggregation.volume
            })
        self.output().save(self.agg(lst_of_stats))


class WeeklyStatsTask(luigi.Task, StatsMixin):
    """Luigi task that creates weekly stats.
    """

    full_name = luigi.Parameter()
    luigi_flag = luigi.IntParameter()

    def requires(self):
        time = datetime.datetime.now(tz=pytz.UTC).replace(
            minute=0, second=0, microsecond=0)
        return [
            HourlyStatsTask(
                time=time - datetime.timedelta(hours=i),
                full_name=self.full_name,
                luigi_flag=self.luigi_flag
            )
            for i in range(7*24)
        ]

    def output(self):
        return DatabaseTarget(
            type=StatsAggregationTypes.WEEKLY,
            time=None, full_name=self.full_name,
            luigi_flag=self.luigi_flag
        )

    def run(self):
        lst_of_stats = []
        for task in self.requires():
            aggregation = task.output().get()
            lst_of_stats.append({
                'low': aggregation.low,
                'high': aggregation.high,
                'average': aggregation.average,
                'volume': aggregation.volume
            })
        self.output().save(self.agg(lst_of_stats))


class MonthlyStatsTask(luigi.Task, StatsMixin):
    """Luigi task that creates monthly stats.
    """

    full_name = luigi.Parameter()
    luigi_flag = luigi.IntParameter()

    def requires(self):
        time = datetime.datetime.now(tz=pytz.UTC).replace(
            minute=0, second=0, microsecond=0)
        return [
            HourlyStatsTask(
                time=time - datetime.timedelta(hours=i),
                full_name=self.full_name,
                luigi_flag=self.luigi_flag
            )
            for i in range(30*24)
        ]

    def output(self):
        return DatabaseTarget(
            type=StatsAggregationTypes.MONTHLY,
            time=None, full_name=self.full_name,
            luigi_flag=self.luigi_flag
        )

    def run(self):
        lst_of_stats = []
        for task in self.requires():
            aggregation = task.output().get()
            lst_of_stats.append({
                'low': aggregation.low,
                'high': aggregation.high,
                'average': aggregation.average,
                'volume': aggregation.volume
            })
        self.output().save(self.agg(lst_of_stats))


if __name__ == '__main__':
    django.setup()
    from tickers.models import Trade, StatsAggregationTypes, StatsAggregation
    while 1:
        luigi_flag = random.randrange(1000000000000000)
        luigi.build(
            [
                DailyStatsTask(
                    full_name='btc/tl::bitexen', luigi_flag=luigi_flag),
                WeeklyStatsTask(
                    full_name='btc/tl::bitexen', luigi_flag=luigi_flag),
                MonthlyStatsTask(
                    full_name='btc/tl::bitexen', luigi_flag=luigi_flag),
            ],
            workers=1,
            local_scheduler=True
        )
        time.sleep(5)
