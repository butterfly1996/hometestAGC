import tensorflow as tf
import numpy as np
import time
import pandas as pd
import json
import pickle
# vocabularies["WEEKDAY"], weekday_indices = np.unique(weekdays, return_inverse=True)
def build_model():
    product_metadata = tf.keras.layers.Input(shape=(1,), name="PRODUCT_METADATA")
    product_metadata_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["PRODUCT_METADATA"]) + 1,
                                                     output_dim=32)(product_metadata)

    store_type = tf.keras.layers.Input(shape=(1,), name="STORE_TYPE")
    store_type_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["STORE_TYPE"]) + 1, output_dim=32)(store_type)

    region_id = tf.keras.layers.Input(shape=(1,), name="REGION_ID")
    region_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["REGION_ID_x"]) + 1, output_dim=32)(region_id)

    brand_id = tf.keras.layers.Input(shape=(1,), name="BRAND_ID")
    brand_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["BRAND_ID"]) + 1, output_dim=32)(brand_id)

    product_id = tf.keras.layers.Input(shape=(1,), name="PRODUCT_ID")
    product_id_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["PRODUCT_ID"]) + 1, output_dim=32)(product_id)

    store_id = tf.keras.layers.Input(shape=(1,), name="STORE_ID_x")
    store_id_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["STORE_ID_x"]) + 1, output_dim=32)(store_id)

    store_size = tf.keras.layers.Input(shape=(1,), name="STORE_SIZE")
    store_size_emb = tf.keras.layers.Embedding(input_dim=len(vocabularies["STORE_SIZE"]) + 1, output_dim=32)(store_size)

    quantities = tf.keras.layers.Input(shape=(1, windows_size,), name="QUANTITY")
    quantities_norm = tf.keras.layers.LayerNormalization(epsilon=1e-6)(quantities)
    transformer_multihead = tf.keras.layers.MultiHeadAttention(
        key_dim=2, num_heads=2
    )(quantities_norm, quantities_norm)
    res = transformer_multihead + quantities
    x = tf.keras.layers.GlobalAveragePooling1D()(res)
    quantities_feature = tf.keras.layers.Dense(32, activation="relu")(x)
    quantities_feature = tf.keras.layers.Reshape((1, 32))(quantities_feature)
    concatenate_layer = tf.keras.layers.concatenate([
        product_metadata_emb, store_type_emb, region_emb, brand_emb,
        product_id_emb, store_id_emb, store_size_emb, quantities_feature])

    dense_1 = tf.keras.layers.Dense(32, activation="relu")(concatenate_layer)
    output = tf.keras.layers.Dense(1, activation="relu")(dense_1)
    return tf.keras.Model(
        inputs=[
            product_metadata, store_type, region_id, brand_id,
            product_id, store_id, store_size, quantities
        ],
        # inputs=[
        #     quantities
        # ],
        outputs=[output])


def collect_data():
    data_orders = pd.read_csv("pod_foods_data_example/data_order.csv")
    product_metada = pd.read_csv("pod_foods_data_example/data_metadata_product.csv")
    store_metada = pd.read_csv("pod_foods_data_example/data_metadata_store.csv")
    data_orders['PRODUCT_ID'] = data_orders['PRODUCT_ID'].astype(str)
    product_metada['PRODUCT_ID'] = product_metada['PRODUCT_ID'].astype(str)
    product_metadata_combine = product_metada.groupby(['PRODUCT_ID']).agg(
        {'PRODUCT_METADATA': lambda x: '+'.join(set(x.str.strip()))}).reset_index()
    product_metadata_combine.head(10)
    data_orders['STORE_ID'] = data_orders['STORE_ID'].astype(str)
    store_metada['STORE_ID'] = store_metada['STORE_ID'].astype(str)
    store_metada['REGION_ID'] = store_metada['REGION_ID'].astype(str)
    df = data_orders.groupby(
        ['PRODUCT_ID', 'STORE_ID', 'REGION_ID', 'BRAND_ID', 'VARIANT_CASE_PRICE_CENTS', 'CHECKOUT_DATE'])[
        'QUANTITY'].sum().reset_index()
    df = df.merge(product_metadata_combine, left_on='PRODUCT_ID', right_on='PRODUCT_ID', how='left')
    df = df.merge(store_metada, left_on='STORE_ID', right_on='STORE_ID', how='left')
    df['CHECKOUT_DATE'] = pd.to_datetime(df['CHECKOUT_DATE'])
    df['WEEKDAY'] = df["CHECKOUT_DATE"].dt.weekday
    product_metadatas, product_ids, brand_ids, variant_case_price_cents = [], [], [], []
    store_id_xs, store_types, region_id_xs, store_sizes = [], [], [], []
    weekdays, quantities = [], []
    targets = []
    start_time = time.time()
    for index, row in df.iterrows():
        base_date = row['CHECKOUT_DATE']
        start_date = base_date + np.timedelta64(np.random.randint(-10, 10), 'D')
        start_weekday = start_date.weekday()
        if start_date < np.datetime64('2022-02-15T00:00:00.00'):
            product_metadatas.append('+'.join(sorted(row['PRODUCT_METADATA'].split('+'))))
            if row['STORE_TYPE'] and row['STORE_TYPE']==row['STORE_TYPE']:
                store_types.append(row['STORE_TYPE'])
            else:
                store_types.append('Others')
            if row['REGION_ID_x'] and row['REGION_ID_x']==row['REGION_ID_x']:
                region_id_xs.append(row['REGION_ID_x'])
            else:
                region_id_xs.append(-1)
            brand_ids.append(row['BRAND_ID'])
            product_ids.append(row['PRODUCT_ID'])
            store_id_xs.append(row['STORE_ID'])
            if row['STORE_SIZE']:
                store_sizes.append(row['STORE_SIZE'])
            else:
                store_sizes.append(6)
            tmp_week_days = [(start_weekday + i) % 7 for i in range(windows_size)]
            weekdays.append(tmp_week_days)
            tmp = df[
                (df['PRODUCT_ID'] == row['PRODUCT_ID']) &
                (df['STORE_ID'] == row['STORE_ID']) &
                (start_date <= df['CHECKOUT_DATE']) &
                (df['CHECKOUT_DATE'] < start_date + np.timedelta64(windows_size, 'D'))]
            tmp_quantities = [0] * windows_size
            tmp_variant_case_price_cents = [0] * windows_size
            for tmp_index, tmp_row in tmp.iterrows():
                tmp_quantities[int((tmp_row['CHECKOUT_DATE'] - start_date) / np.timedelta64(1, "D"))] = tmp_row[
                    'QUANTITY']
                tmp_variant_case_price_cents[int((tmp_row['CHECKOUT_DATE'] - start_date) / np.timedelta64(1, "D"))] = \
                    tmp_row['VARIANT_CASE_PRICE_CENTS']
            tmp_variant_price = row['VARIANT_CASE_PRICE_CENTS']
            for i in range(windows_size):
                if tmp_variant_case_price_cents[i] == 0:
                    tmp_variant_case_price_cents[i] = tmp_variant_price
                else:
                    tmp_variant_price = tmp_variant_case_price_cents[i]
            variant_case_price_cents.append(tmp_variant_case_price_cents)
            quantities.append(tmp_quantities)
            target = df[
                (df['PRODUCT_ID'] == row['PRODUCT_ID']) &
                (df['STORE_ID'] == row['STORE_ID']) &
                (start_date + np.timedelta64(windows_size, 'D') <= df['CHECKOUT_DATE']) &
                (df['CHECKOUT_DATE'] <= start_date + np.timedelta64(windows_size + 29, 'D'))
                ]['QUANTITY'].sum()
            targets.append(target)
        if index % 5000 == 0:
            print("count: ", index, time.time() - start_time)
            start_time = time.time()

    return product_metadatas, store_types, region_id_xs, brand_ids, product_ids, store_id_xs, store_sizes, quantities, targets



if __name__ == '__main__':

    windows_size = 60
    product_metadatas, store_types, region_id_xs, brand_ids, product_ids, store_id_xs, store_sizes, quantities, targets = collect_data()

    vocabularies = dict()
    vocabularies["PRODUCT_METADATA"], product_metadata_indices = np.unique(product_metadatas, return_inverse=True)
    vocabularies["STORE_TYPE"], store_type_indices = np.unique(store_types, return_inverse=True)
    vocabularies["REGION_ID_x"], region_id_indices = np.unique(region_id_xs, return_inverse=True)
    vocabularies["BRAND_ID"], brand_id_indices = np.unique(brand_ids, return_inverse=True)
    vocabularies["PRODUCT_ID"], product_id_indices = np.unique(product_ids, return_inverse=True)
    vocabularies["STORE_ID_x"], store_id_indices = np.unique(store_id_xs, return_inverse=True)
    vocabularies["STORE_SIZE"], store_size_indices = np.unique(store_sizes, return_inverse=True)
    with open("/Users/lap02342/PycharmProjects/pod_foods/resources/vocabularies.pkl","wb") as vocab_file:
        pickle.dump(vocabularies, vocab_file)
    model = build_model()
    model.summary()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        metrics=["accuracy"],
        loss = tf.keras.losses.MeanAbsoluteError(),
    )
    model.fit(
        x=[
            np.array(product_metadata_indices),
            np.array(store_type_indices),
            np.array(region_id_indices),
            np.array(brand_id_indices),
            np.array(product_id_indices),
            np.array(store_id_indices),
            np.array(store_size_indices),
            np.expand_dims(np.array(quantities), axis=1)
        ],
        y=np.array(targets),
        batch_size=4,
        epochs=1,
        # validation_split=0.1,
        use_multiprocessing=True,
    )
    # model.save("/Users/lap02342/PycharmProjects/pod_foods/resources/")
    model.save("/Users/lap02342/PycharmProjects/pod_foods/resources/model.h5", save_format="h5")
