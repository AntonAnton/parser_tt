import requests
from bs4 import BeautifulSoup


def get_page_by_url(url):
    response = requests.get(url)
    return response.text


def get_products_paths_from_catalog(catalog_url):
    page = get_page_by_url(catalog_url)
    soup = BeautifulSoup(page, features="html.parser")
    products_paths = [i.get("href") for i in soup.find_all("a", {"class": "nf842wf_plp"})]
    return products_paths


def get_product_stocks(product_id, region_id):
    lerua_stock_url="https://api.leroymerlin.ru/aem_api/v1/getProductAvailabilityInfo"
    headers = {
        "x-api-key": "VY0AKH3eBwhyGUjBM5U9rO4PyBvTG0cA",
    }
    data = {
        "productId": product_id,
        "productSource": "E-COMMERCE",
        "regionId": region_id,
    }
    response = requests.post(url=lerua_stock_url, json=data, headers=headers)
    return response.json()


def parse_product_to_dict(product_url):
    page = get_page_by_url(product_url)
    soup = BeautifulSoup(page, features="html.parser")

    stocks = get_product_stocks(
        soup.find("uc-pdp-card-ga-enriched").get("product-id"),
        soup.find("uc-pdp-card-ga-enriched").get("region-id")
    )
    stores_stocks = stocks.get("stores")

    result = dict(
        link=product_url,
        name=soup.find("h1", {"slot": "title"}).text,
        photo_url=soup.find("img", {"alt": "product image"}).get("data-origin"),
        article=soup.find("span", {"slot": "article"}).get("content"),
        price=soup.find("span", {"slot": "price"}).text,
        stocks={v.get("storeName"): v.get("stock") for _, v in stores_stocks.items()},
        characteristics={
            i.find(attrs={"class": "def-list__term"}).text:
                i.find(attrs={"class": "def-list__definition"}).text.replace("\n", "").replace("  ", "")
            for i in soup.find_all("div", {"class": "def-list__group"})
        },
    )
    return result


def save_dict_to_file(dict, file_name):
    with open(file_name , "w", encoding="utf-8") as f:
        f.write(str(dict))


def save_image_form_url(file_name, url):
    r = requests.get(url)

    with open(file_name, 'wb') as f:
        f.write(r.content)


domain_url = "https://spb.leroymerlin.ru"
catalog_path = "/catalogue/dreli-shurupoverty/"

products_paths_list = get_products_paths_from_catalog(domain_url + catalog_path)
product_dict = parse_product_to_dict(domain_url + products_paths_list[0])

save_dict_to_file(product_dict, f"product_{product_dict.get('article')}.txt")
save_image_form_url(product_dict["photo_url"].split('/')[-1], product_dict["photo_url"])
