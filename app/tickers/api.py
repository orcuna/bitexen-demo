# myapp/api.py
from tastypie.resources import ModelResource
from tickers.models import StatsAggregation, StatsAggregationTypes


class StatsResource(ModelResource):

    def build_filters(self, filters=None, **kwargs):
        if filters is None:
            filters = {}

        orm_filters = super(StatsResource, self).build_filters(filters, **kwargs)

        if "type" in filters:
            orm_filters['type__exact'] = getattr(StatsAggregationTypes, filters['type'])
        else:
            orm_filters['type__in'] = [1, 2, 3]

        if not "full_name" in filters:
            orm_filters['full_name'] = 'btc/tl::bitexen'

        return orm_filters

    class Meta:
        limit = 3
        max_limit = None
        queryset = StatsAggregation.objects.all()
        resource_name = 'stats'
        allowed_methods = ['get']
        fields = ['low', 'high', 'average', 'volume', 'type']
        filtering = {
            "type": ('exact', 'in'),
            'full_name': ('exact', ),
        }
