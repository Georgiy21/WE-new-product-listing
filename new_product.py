import csv
import pandas as pd
import re
from datetime import datetime
from datetimerange import DateTimeRange
from datetime import timedelta


class Product:

    vendor = 'Pending - Walker Edison'
    published = 'FALSE'
    variant_inventory_tracker = 'shopify'
    variant_inventory_policy = 'deny'
    variant_fulfillment_service = 'manual'
    variant_taxable = 'TRUE'
    variant_requires_shipping = 'TRUE'
    gift_card = 'FALSE'
    weight_unit = 'lb'

    def __init__(self, sku, productName, upc, category, costPerItem, height, length, width, color, produtcDescription, feature1, feature2, feature3, feature4, feature5, feature6, feature7, feature8):
        self.sku = sku
        self.productName = productName
        self.upc = upc
        self.category = category
        self.costPerItem = costPerItem
        self.height = height
        self.length = length
        self.width = width
        self.color = color
        self.produtcDescription = produtcDescription


    def get_dimensions(self):
        return f"{self.width}\"W x {self.length}\"L x {self.height}\"H"


class ProductVariant(Product):
    pass