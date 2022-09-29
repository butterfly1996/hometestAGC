# How to run
Set the following enviroment variables to suitable value (strong recommend to set MODEL_PATH=resources/model.h5):
- MODEL_PATH=resources/model.h5
- DB_HOST=127.0.0.1
- DB_NAME=pod_foods
- DB_USER=root
- DB_PASSWORD=123456
- DB_PORT=3306

Setup 
python3 -m pip install -r requirements.txt
start service by following command:
python3 api.py

If you want to test model only, you can run
python3 src/app/domain/sale_forecast.py

or following notebook structure in training/EDA.ipynb

Or testing api by following command
pytest test/test.py

# init database
CREATE TABLE orders (
 ID INT(10) PRIMARY KEY ,
 ORDER_ID INT(10) ,
 STORE_ID INT(10),
 REGION_ID_x INT(10),
 BRAND_ID INT(10),
 PRODUCT_ID INT(10),
 PRODUCT_VARIANT_ID INT(10),
 QUANTITY INT(10),
 VARIANT_CASE_PRICE_CENTS INT(10),
 CHECKOUT_DATE DATE,
 PRODUCT_METADATA VARCHAR(50),
 STORE_TYPE VARCHAR(50),
 REGION_ID_y INT(10),
 STORE_SIZE INT(10),
INDEX (ORDER_ID), INDEX (PRODUCT_ID), INDEX (CHECKOUT_DATE), INDEX (STORE_ID)
);

LOAD DATA LOCAL INFILE 'path/to/data.csv' \
     INTO TABLE orders \
     FIELDS TERMINATED BY ',' \
     LINES TERMINATED BY '\n' ;


LOAD DATA LOCAL INFILE '/Users/lap02342/PycharmProjects/pod_foods/resources/data/data.csv' \
     INTO TABLE orders \
     FIELDS TERMINATED BY ',' \
     LINES TERMINATED BY '\n' ;