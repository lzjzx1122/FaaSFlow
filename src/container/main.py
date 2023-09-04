def main():
    data_1 = store.get_input_data('data_1')
    store.post('data_3', data_1 + 1)
    data_2 = store.get_input_data('data_2')
    store.post('data_4', data_2 + 2)
