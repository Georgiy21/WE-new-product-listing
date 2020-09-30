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
    variant_inventory_tracker = 'shopify'
    variant_inventory_policy = 'deny'
    variant_fulfillment_service = 'manual'
    variant_taxable = 'TRUE'
    variant_requires_shipping = 'TRUE'
    gift_card = 'FALSE'
    weight_unit = 'lb'

    # Get 1 WEEK daterange from today's date 
    # datemask = '%m-%d-%Y'

    # future = datetime.today() + timedelta(days=7)
    # fday = datetime.strftime(future, datemask)

    # tday = datetime.today().strftime(datemask)
    # today = datetime.strptime(tday, datemask)

    # time_range = DateTimeRange(tday, fday)

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

    def get_seo_title(self, title):
        self.seoTitle =  f'Walker Edison {title.rsplit(" - ")[0].strip()}'

    def get_dimensions(self, w, l, h):
        self.dimensions.append(f"{w}\"W x {l}\"L x {h}\"H")

    def get_features(self, v):
        self.features.append(v)

        for f in self.features:
            if "\"" in str(f) or "”" in str(f) or '“' in str(f):
                self.dimensions.append(str(f))
                self.features.remove(str(f))

    def get_costPerItem(self, cost):
        self.costPerItem = float(cost.strip('$')) * 1.35

    def get_selling_price(self):
        self.sellingPrice = self.costPerItem + (self.costPerItem * .25)
    
    def get_compareAt_price(self):
        self.compareAtPrice = self.sellingPrice + (self.sellingPrice * .20)

    def get_tags(self):
        
        product_tags = ['Brand_Walker Edison', 'Style_Contemporary']

        if '/' in self.color:
            c1 = self.color.split('/')[0].strip()
            c2 = self.color.split('/')[1].strip()
            product_tags.append(f'Color_{c1}')
            product_tags.append(f'Color_{c2}')
        else:
            product_tags.append(f'Color_{self.color}')
        
        if self.productType == 'Home Office':
            product_tags.append(f'Room_{self.productType}')

        product_tags.append(f'Type_{self.productType}')
        product_tags.append(f'Made In_{self.origin}')

        return product_tags

    def get_weight(self, weight):
        self.weight = int(weight) * 453.592

    def get_option_name_value(self):
        
        if self.color:
            self.optionNameValue['Color'] = self.color
        else:
            self.optionNameValue['Title'] = 'Default Title'

        return self.optionNameValue

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

    # def get_handle(self):


# Not finished
def classify_product(object_list):
    title = object_list[0].title
    return_list = []
    group_list = []
    count = 1

    temp_prod = Product()

    for product in object_list:
        if product.title == title:
            pass
        elif product.title.rsplit(' - ') == title.rsplit(' - '):
            count += 1
            temp_prod.handle = temp_prod.title.lower().rsplit(' - ')[0].replace(' ', '-').replace('---', '-')
            group_list.append(temp_prod)
            temp_prod = product
        # if left part of model of the product doesn't match with model
        else:
            if not group_list:
                if temp_prod not in return_list:
                    return_list.append([temp_prod])
                else:
                    pass
            else:
                group_list.append(temp_prod)              
                return_list.append(group_list)
                group_list = []
                count = 0

        title = product.title   
        temp_prod = product


    return return_list

# Generate a product line to be written to the output.csv file
def produce_template_line(seo_title, handle, skus, barcodes, title, body, option_dicts, product_type, tags, total_weights, quantity, cost_per_item, price, main_img, alt_text, img, obj, obj_num):

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
   
    if obj == 0 and img == 0:
        template_header['Title'] = title
        template_header['Body (HTML)'] = body
        template_header['Vendor'] = vendor
        template_header['Type'] = product_type

        tag_str = ''
        for tag in range(len(tags)):
            if tag == len(tags) - 1:
                tag_str += tags[tag]
            else:
                tag_str += tags[tag] + ', '
        template_header['Tags'] = tag_str
        template_header['Published'] = published
        template_header['Gift Card'] = gift_card

        for key, value in option_dicts[img].items():
            template_header['Option' + str(option) + ' Name'] = key
            template_header['Option' + str(option) + ' Value'] = value
            option += 1

        template_header['Variant SKU'] = skus[img]

        template_header['Variant Grams'] = total_weights[img]

        template_header['Variant Inventory Tracker'] = variant_inventory_tracker
        template_header['Variant Inventory Qty'] = int(float(quantity[obj]))
        template_header['Variant Inventory Policy'] = variant_inventory_policy
        template_header['Variant Fulfillment Service'] = variant_fulfillment_service
        template_header['Variant Price'] = price[0]
        template_header['Variant Compare At Price'] = price[1]
        template_header['Variant Requires Shipping'] = variant_requires_shipping
        template_header['Variant Taxable'] = variant_taxable

        template_header['Variant Barcode'] = barcodes[img]

        template_header['Variant Weight Unit'] = weight_unit
        template_header['Image Src'] = main_img[img]
        template_header['Image Position'] = img + 1
        template_header['Image Alt Text'] = alt_text[img]
        template_header['SEO Title'] = seo_title
        template_header['Cost per items'] = int(float(cost_per_item[obj]))


        new_line = template_header

    else:
        if obj >= 1 and img == 0:

            for key, value in option_dicts[obj].items():
                template_header['Option' + str(option) + ' Value'] = value
                option += 1

            template_header['Variant SKU'] = skus[obj]
            template_header['Variant Grams'] = total_weights[obj]
            template_header['Variant Inventory Tracker'] = variant_inventory_tracker
            template_header['Variant Inventory Qty'] = int(float(quantity[obj]))
            template_header['Variant Inventory Policy'] = variant_inventory_policy
            template_header['Variant Fulfillment Service'] = variant_fulfillment_service
            template_header['Variant Requires Shipping'] = variant_requires_shipping
            template_header['Variant Taxable'] = variant_taxable
            template_header['Variant Barcode'] = barcodes[obj]
            template_header['Variant Weight Unit'] = weight_unit

            template_header['Image Src'] = main_img[img]
            template_header['Image Position'] = img + 1
            template_header['Image Alt Text'] = alt_text[obj]
            template_header['Cost per items'] = int(float(cost_per_item[obj]))
            template_header['Variant Price'] = price[0]
            template_header['Variant Compare At Price'] = price[1]


            new_line = template_header
        else:
            try:
                template_header['Image Src'] = main_img[img]
            except IndexError:
                pass
            template_header['Image Position'] = img + 1
            if obj_num > 1:
                template_header['Image Alt Text'] = alt_text[obj]
            new_line = template_header

    return new_line

def main():

    price_file = 'Walker Edison Canada Price List(new products).csv'
    stock_file = 'WE Inv Report - September 28.csv'
    p_list = []

    object_list = []

    vendor_reader = pd.read_csv(price_file)
    for line in vendor_reader.to_dict('records'):
        produtcObj = Product()

        w,l,h = '', '', ''

        for k,v in line.items():
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
        
        produtcObj.get_dimensions(w,l,h)
        produtcObj.get_body_html()
        p_list.append(line)
        
        object_list.append(produtcObj)
        # remove 
        # break

    sorted_list = sorted(p_list, key=lambda i: i['SKU'])

    with open('generated_new_WE_import.csv', 'w', newline='', encoding='utf8') as outputfile:
        writer = csv.DictWriter(outputfile, fieldnames=columns)
        writer.writeheader()



    sorted_objs = classify_product(object_list)
    print(len(sorted_objs))
    for p_c in sorted_objs:
        print(len(p_c))
        # for p in p_c:
        #     print('--------')
        #     print(p.sku)
        #     print('--------')


if __name__ == '__main__':
    main()