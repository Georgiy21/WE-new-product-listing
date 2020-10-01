import csv
import pandas as pd
import re
from datetime import datetime
from datetimerange import DateTimeRange
from datetime import timedelta

columns = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description',
           'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per items']


class Product:

    vendor = 'Pending - Walker Edison'
    published = 'FALSE'
    variantInventoryTracker = 'shopify'
    variantInventoryPolicy = 'deny'
    variantFulfillmentService = 'manual'
    variantTaxable = 'TRUE'
    variantRequiresShipping = 'TRUE'
    giftCard = 'FALSE'
    weightUnit = 'lb'
    productTags = ['Brand_Walker Edison', 'Style_Contemporary']

    def __init__(self):
        self.sku = ''
        self.title = ''
        self.handle = ''
        self.upc = ''
        self.productType = ''
        self.costPerItem = ''
        self.sellingPrice = ''
        self.compareAtPrice = ''
        self.weight = ''
        self.color = ''
        self.description = ''
        self.origin = ''
        self.seoTitle = ''
        self.dimensions = []
        self.features = []
        self.optionNameValue = {}
        self.bodyHTML = ''
        self.imgAltText = ''
        self.quantity = ''
        self.tags = ['Brand_Walker Edison', 'Style_Contemporary']

    def get_seo_title(self, title):
        self.seoTitle = f'Walker Edison {title.rsplit(" - ")[0].strip()}'

    def get_dimensions(self, w, l, h):
        self.dimensions.append(f"{w}\"W x {l}\"L x {h}\"H")

    def get_features(self, v):
        self.features.append(v)

        chars = ["\"", "”", '“']

        for f in self.features:
            for c in chars:
                if c in f:
                    self.dimensions.append(str(f))
                    self.features.remove(str(f))

    def get_costPerItem(self, cost):
        self.costPerItem = round(float(cost.strip('$')) * 1.35, 2)

    def get_selling_price(self):
        self.sellingPrice = round(
            self.costPerItem + (self.costPerItem * .25), 2)

    def get_compareAt_price(self):
        self.compareAtPrice = round(
            self.sellingPrice + (self.sellingPrice * .20), 2)

    def get_tags(self):
        if '/' in self.color:
            c1 = self.color.split('/')[0].strip()
            c2 = self.color.split('/')[1].strip()
            self.tags.append(f'Color_{c1}')
            self.tags.append(f'Color_{c2}')
        else:
            self.tags.append(f'Color_{self.color}')

        if self.productType == 'Home Office':
            self.tags.append(f'Room_{self.productType}')

        self.tags.append(f'Type_{self.productType}')
        self.tags.append(f'Made In_{self.origin}')

    def get_weight(self, weight):
        self.weight = int(weight) * 453.592

    def get_option_name_value(self):

        if self.color:
            self.optionNameValue['Color'] = self.color
        else:
            self.optionNameValue['Title'] = 'Default Title'

    def get_body_html(self):

        if self.description:
            self.bodyHTML += '<h4>Description</h4>\n' + '<p>Items Included</p>\n<ul>\n'
            self.bodyHTML += '<li>' + self.productType + '</li>\n'
            self.bodyHTML += '</ul>\n' + '<meta charset="utf-8">\n'
            self.bodyHTML += '<p><span>' + self.description + '</span></p>\n'
        else:
            pass

        if self.dimensions:
            self.bodyHTML += '<h4>Dimensions</h4>\n'
            for d in self.dimensions:
                self.bodyHTML += '<p>' + d + ' ' + '</p>\n'

        if self.features:
            self.bodyHTML += '<h4>Specifications</h4>\n' + '<ul>\n'

            for f in self.features:
                self.bodyHTML += '<li>' + f + '</li>\n'

            self.bodyHTML += '</ul>'
        else:
            pass

        return self.bodyHTML

    def get_img_alt_text(self):

        self.imgAltText = 'Walker Edison ' + self.title


def classify_product(object_list):
    title = object_list[0].title
    return_list = []
    group_list = []
    tags = []

    temp_prod = Product()

    for product in object_list:
        if product.title == title:
            pass
        elif product.title.rsplit('-')[0].strip() == title.rsplit('-')[0].strip():
            temp_prod.handle = temp_prod.title.lower().rsplit(
                ' - ')[0].strip().replace(' ', '-').replace('---', '-')
            group_list.append(temp_prod)
            temp_prod = product
        # if left part of model of the product doesn't match with model
        else:
            if not group_list:
                temp_prod.handle = temp_prod.title.lower().strip().replace(' ',
                                                                           '-').replace('---', '-')
                return_list.append([temp_prod])
            else:
                temp_prod.handle = temp_prod.title.lower().rsplit(
                    ' - ')[0].strip().replace(' ', '-').replace('---', '-')
                group_list.append(temp_prod)
                return_list.append(group_list)
                group_list = []
            title = product.title

        if product == object_list[-1]:
            if product not in return_list:
                product.handle = product.title.lower().strip().replace(' ', '-').replace('---', '-')
                return_list.append([product])

        temp_prod = product

    return return_list


# Generate a product line to be written to the output.csv file
def produce_template_line(seo_title, handle, sku, barcode, title, body, option_dict, product_type, tags, weight, quantity, cost_per_item, sellingPrice, compareAtPrice, alt_text, obj, obj_num, count):

    img = 'https://s3.amazonaws.com/up.411.ca/101/640/9971.png'
    template_header = {'Handle': '', 'Title': '', 'Body (HTML)': '',
                       'Vendor': '', 'Type': '', 'Tags': '', 'Published': '', 'Option1 Name': '',
                       'Option1 Value': '', 'Option2 Name': '', 'Option2 Value': '', 'Option3 Name': '',
                       'Option3 Value': '', 'Variant SKU': '', 'Variant Grams': '', 'Variant Inventory Tracker': '',
                       'Variant Inventory Qty': '', 'Variant Inventory Policy': '', 'Variant Fulfillment Service': '',
                       'Variant Price': '', 'Variant Compare At Price': '', 'Variant Requires Shipping': '',
                       'Variant Taxable': '', 'Variant Barcode': '', 'Image Src': '', 'Image Position': '',
                       'Image Alt Text': '', 'Gift Card': '', 'SEO Title': '', 'SEO Description': '',
                       'Google Shopping / Google Product Category': '', 'Google Shopping / Gender': '',
                       'Google Shopping / Age Group': '', 'Google Shopping / MPN': '',
                       'Google Shopping / AdWords Grouping': '', 'Google Shopping / AdWords Labels': '',
                       'Google Shopping / Condition': '', 'Google Shopping / Custom Product': '',
                       'Google Shopping / Custom Label 0': '', 'Google Shopping / Custom Label 1': '',
                       'Google Shopping / Custom Label 2': '', 'Google Shopping / Custom Label 3': '',
                       'Google Shopping / Custom Label 4': '', 'Variant Image': '', 'Variant Weight Unit': '',
                       'Variant Tax Code': '', 'Cost per items': ''}
    new_line = {}
    option = 1

    template_header['Handle'] = handle

    if count == 0:
        if obj_num == 1:
            template_header['Title'] = title
        else:
            template_header['Title'] = title.rsplit(
                ' - ')[0].strip() + ' - Available in ' + str(obj_num) + ' Colors'

        template_header['Body (HTML)'] = body
        template_header['Vendor'] = obj.vendor
        template_header['Type'] = product_type

        tag_str = ''
        for tag in range(len(tags)):
            if tag == len(tags) - 1:
                tag_str += tags[tag]
            else:
                tag_str += tags[tag] + ', '
        template_header['Tags'] = tag_str
        template_header['Published'] = obj.published
        template_header['Gift Card'] = obj.giftCard

        for key, value in option_dict.items():
            template_header['Option' + str(option) + ' Name'] = key
            template_header['Option' + str(option) + ' Value'] = value
            option += 1

        template_header['Variant SKU'] = sku
        template_header['Variant Grams'] = weight
        template_header['Variant Inventory Tracker'] = obj.variantInventoryTracker
        template_header['Variant Inventory Qty'] = 0
        template_header['Variant Inventory Policy'] = obj.variantInventoryPolicy
        template_header['Variant Fulfillment Service'] = obj.variantFulfillmentService
        template_header['Variant Price'] = sellingPrice
        template_header['Variant Compare At Price'] = compareAtPrice
        template_header['Variant Requires Shipping'] = obj.variantRequiresShipping
        template_header['Variant Taxable'] = obj.variantTaxable
        template_header['Variant Barcode'] = barcode
        template_header['Variant Weight Unit'] = obj.weightUnit
        template_header['Image Src'] = img
        template_header['Image Position'] = count + 1
        template_header['Image Alt Text'] = obj.imgAltText
        template_header['SEO Title'] = seo_title
        template_header['Cost per items'] = cost_per_item

        new_line = template_header

    else:
        if obj_num >= 1:
            for key, value in option_dict.items():
                template_header['Option' + str(option) + ' Value'] = value
                option += 1

            template_header['Variant SKU'] = sku
            template_header['Variant Grams'] = weight
            template_header['Variant Inventory Tracker'] = obj.variantInventoryTracker
            template_header['Variant Inventory Qty'] = 1
            template_header['Variant Inventory Policy'] = obj.variantInventoryPolicy
            template_header['Variant Fulfillment Service'] = obj.variantFulfillmentService
            template_header['Variant Requires Shipping'] = obj.variantRequiresShipping
            template_header['Variant Taxable'] = obj.variantTaxable
            template_header['Variant Barcode'] = barcode
            template_header['Variant Weight Unit'] = obj.weightUnit

            template_header['Image Src'] = img
            template_header['Image Position'] = count + 1
            template_header['Image Alt Text'] = obj.imgAltText
            template_header['Cost per items'] = cost_per_item
            template_header['Variant Price'] = sellingPrice
            template_header['Variant Compare At Price'] = compareAtPrice

            new_line = template_header
        else:
            try:
                template_header['Image Src'] = img
            except IndexError:
                pass
            template_header['Image Position'] = count + 1
            if obj_num > 1:
                template_header['Image Alt Text'] = obj.imgAltText
            new_line = template_header

    return new_line


def main():

    price_file = 'Walker Edison Canada Price List(new products).csv'
    stock_file = 'WE Inv Report - September 28.csv'

    object_list = []

    vendor_reader = pd.read_csv(price_file)
    for line in vendor_reader.to_dict('records'):
        produtcObj = Product()

        w, l, h = '', '', ''

        for k, v in line.items():
            if k == 'SKU':
                produtcObj.sku = v
            elif k == 'UPC':
                produtcObj.upc = v
            elif k == 'Product Name':
                produtcObj.title = v
                produtcObj.get_seo_title(v)
            elif k == 'Category':
                produtcObj.productType = v
            elif k == 'Wholesale Price w/ Shipping':
                produtcObj.get_costPerItem(v)
            elif k == 'Product Height':
                h = v
            elif k == 'Product Length ':
                l = v
            elif k == 'Product Width (Depth)':
                w = v
            elif k == 'Product Weight':
                produtcObj.get_weight(v)
            elif k == 'Color':
                produtcObj.color = v
            elif k == 'Product Description':
                produtcObj.description = v
            # Get FEATURES
            elif k == 'Product Feature 1' or k == 'Product Feature 2' or k == 'Product Feature 3' or k == 'Product Feature 4' or k == 'Product Feature 5' or k == 'Product Feature 6' or k == 'Product Feature 7' or k == 'Product Feature 8' or k == 'Additional Features':
                if str(v) != 'nan':
                    produtcObj.get_features(v)
            # Get TAGS
            elif k == 'Color':
                produtcObj.color = v
            elif k == 'Country of Origin':
                produtcObj.origin = v

        produtcObj.get_dimensions(w, l, h)
        produtcObj.get_body_html()
        produtcObj.get_tags()
        produtcObj.get_img_alt_text()
        produtcObj.get_option_name_value()
        produtcObj.get_selling_price()
        produtcObj.get_compareAt_price()

        object_list.append(produtcObj)
        # remove
        # break

    sorted_list = sorted(object_list, key=lambda i: i.sku)

    sorted_objs = classify_product(sorted_list)

    with open('generated_new_WE_import.csv', 'w', newline='') as outputfile:
        writer = csv.DictWriter(outputfile, fieldnames=columns)
        writer.writeheader()

        for group in sorted_objs:
            count = 0
            for obj in group:
                line = produce_template_line(obj.seoTitle, obj.handle, obj.sku, obj.upc, obj.title, obj.bodyHTML, obj.optionNameValue, obj.productType,
                                             obj.tags, obj.weight, obj.quantity, obj.costPerItem, obj.sellingPrice, obj.compareAtPrice, obj.imgAltText, obj, len(group), count)
                writer.writerow(line)
                count += 1


if __name__ == '__main__':
    main()
