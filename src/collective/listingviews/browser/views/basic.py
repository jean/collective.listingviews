from collective.listingviews.interfaces import \
    IListingAdapter
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import adapts
from base import BaseListingInformationRetriever
from collective.listingviews import LVMessageFactory as _
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from plone.memoize.instance import memoize
from Products.CMFPlone.PloneBatch import Batch


class BasicListingInformationRetriever(BaseListingInformationRetriever):
    implements(IListingAdapter)

    view_setting = None
    is_portlet = False

    @property
    def item_fields(self):
        fields = []
        if self.view_setting:
            fields = getattr(self.view_setting, 'item_fields', [])
        if fields is None:
            fields = []
        return fields

    @property
    def listing_fields(self):
        fields = []
        if self.view_setting:
            fields = getattr(self.view_setting, 'listing_fields', [])
        if fields is None:
            fields = []
        return fields

    @property
    def listing_style_class(self):
        style_class = ""
        if self.view_setting:
            style_class = getattr(self.view_setting, 'css_class', '')
        if style_class is None:
            style_class = ""
        return style_class

    @property
    def listing_view_batch_size(self):
        batch_size = 0
        if self.view_setting:
            batch_size = getattr(self.view_setting, 'batch_size', 0)
        if batch_size is None:
            batch_size = 0
        return batch_size

    @property
    def listing_portlet_more_text(self):
        portlet_more_text = 'More'
        if self.is_portlet and self.view_setting:
            portlet_more_text = getattr(self.view_setting, 'portlet_more_text', '')
        if portlet_more_text is None:
            portlet_more_text = 'More'
        return portlet_more_text

    @property
    def listing_view_behavior(self):
        behavior_choice = 'list'
        if self.view_setting:
            behavior_choice = getattr(self.view_setting, 'behavior_choice', 'list')
        if behavior_choice is None:
            behavior_choice = 'list'
        return behavior_choice

    @property
    @memoize
    def retrieve_items(self):
        items = self.get_item_fields()
        return items

    @property
    @memoize
    def retrieve_listing_items(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        items = self.get_listing_fields()

        if not self.is_portlet and self.listing_view_batch_size:
            items = Batch(items,
                self.listing_view_batch_size,
                int(self.request.get('b_start', 0)),
                orphan=1)
        return items

    @property
    def number_of_items(self):
        return len(self.retrieve_listing_items)

    def get_listing_fields(self):
        """
        A catalog search should be faster especially when there
        are a large number of fields in the view. No need
        to wake up all the objects.
        """
        path = self.context.getPhysicalPath()
        path = "/".join(path)
        items = self.context.portal_catalog(path={"query": path, "depth": 1})
        self.field_attribute_name = 'listing_fields'
        return items


class BasicTopicListingInformationRetriever(BasicListingInformationRetriever):
    implements(IListingAdapter)

    def get_listing_fields(self):
        query = self.context.buildQuery()
        if query is not None:
            should_limit = self.context.getLimitNumber()
            limit = self.context.getItemCount()
            if not limit:  # also make sure we have more than 0 items
                should_limit = False
            if should_limit:
                query['sort_limit'] = limit
            catalog = getToolByName(self.context, 'portal_catalog')
            items = catalog(query)
            if should_limit:
                items = items[:limit]
            self.field_attribute_name = 'listing_fields'
            return items
        else:
            return []