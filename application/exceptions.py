class DatasetValueNotFound(ValueError):
    dataset_names: list

    def __init__(self, *args, dataset_names: list, **kwargs):
        self.dataset_names = dataset_names
        super().__init__(*args, **kwargs)
