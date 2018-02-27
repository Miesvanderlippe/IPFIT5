from Utils.Store import Store


class StoreTest:
    def __init__(self):
        self.store = Store()
        self.store.image_store.subscribe(lambda: print(
            self.store.image_store.get_state()
        ))


class StoreTest2:
    def __init__(self):
        self.store = Store()
        self.store.image_store.dispatch({'type': 'set_image', 'image': "Test"})


if __name__ == '__main__':
    StoreTest()
    StoreTest2()