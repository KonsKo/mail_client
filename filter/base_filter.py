"""Base filter."""
from filter.filter_alchemy_new import FilterBuilder

PYTHON_DIVIDER = '_'
TS_DIVIDER = '.'


class BaseAlchemyFilter(object):
    """Base filter for SQLAlchemy."""

    _filter_class = None
    _alchemy_filter_builder = FilterBuilder

    def __init__(self):
        """
        Init class instance.

        Raises:
            NotImplementedError: if filter class not provided

        """
        if not self._filter_class:
            raise NotImplementedError
        self.filter_class = self._filter_class()
        self.alchemy_filter_builder = self._alchemy_filter_builder(
            table=self.filter_class.model,
        )
        self.filter_data = []

    def load_from_query(self, query_dict: dict):
        """
        Load query data and process it with static filter.

        Args:
            query_dict (dict): filter data

        """
        for qkey, qvalue in query_dict.items():
            filter_for_field = self.filter_class.dict().get(
                'ff_{0}'.format(
                    qkey.replace(
                        TS_DIVIDER,
                        PYTHON_DIVIDER,
                    ).lower(),
                ),
            )
            if filter_for_field:
                filter_for_field['field_value'] = qvalue
                self.filter_data.append(filter_for_field)

    def create_alchemy_filters(self, query_dict: dict) -> list:
        """
        Create SQL Alchemy filter representation for query.

        Args:
            query_dict (dict): filter data

        Returns:
            filters (list): SQL Alchemy filter expressions

        """
        self.load_from_query(query_dict=query_dict)
        self.alchemy_filter_builder.build(
            filter_set=self.filter_data,
        )
        return self.alchemy_filter_builder.filter.list_filters()
