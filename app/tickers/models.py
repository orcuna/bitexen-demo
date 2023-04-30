from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class AbstractTimescaleModel(models.Model):
    """
    A helper class for using Timescale within Django, has the TimescaleManager and
    TimescaleDateTimeField already present. This is an abstract class it should
    be inheritted by another class for use.
    """
    time = TimescaleDateTimeField(interval="1 hour")

    objects = TimescaleManager()

    class Meta:
        abstract = True


class Trade(AbstractTimescaleModel):
    """Trade hypertable to store all trades in a time-series fashion.
    """
    full_name = models.CharField(default='btc/tl::bitexen', max_length=100)
    price = models.DecimalField(decimal_places=10, max_digits=100)
    amount = models.DecimalField(decimal_places=10, max_digits=100)

    def __repr__(self):
        return f"<Trade '{self.full_name}' at {self.time}>"

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__repr__()


class StatsAggregationTypes:
    HOURLY = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3

    @staticmethod
    def get_choices():
        return dict([(0, 'HOURLY'), (1, 'DAILY'), (2, 'WEEKLY'), (3, 'MONTHLY')])


class StatsAggregation(models.Model):
    """Daily, weekly, monthly, hourly stats aggregations.
    """
    full_name = models.CharField(default='btc/tl::bitexen', max_length=100)
    type = models.SmallIntegerField(
            choices=StatsAggregationTypes.get_choices().items())
    time = models.DateTimeField(blank=True, null=True)

    low = models.DecimalField(decimal_places=10, max_digits=100,
                              blank=True, null=True)
    high = models.DecimalField(decimal_places=10, max_digits=100,
                               blank=True, null=True)
    average = models.DecimalField(decimal_places=10, max_digits=100,
                                  blank=True, null=True)
    volume = models.DecimalField(decimal_places=10, max_digits=100,
                                 blank=True, null=True)

    luigi_flag = models.BigIntegerField(blank=True, null=True)

    class Meta:
        index_together = [
            ["full_name", 'type', "time", "luigi_flag"],
        ]
        unique_together = [
            ('full_name', 'type', 'time')
        ]

    @property
    def type_str(self):
        return StatsAggregationTypes.get_choices()[self.type]

    def __repr__(self):
        return (f"<StatsAggregation "
                f"'{StatsAggregationTypes.get_choices()[self.type]}' "
                f"at {self.time}>")

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__repr__()
