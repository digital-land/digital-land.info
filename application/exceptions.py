class DigitalLandValidationError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DatasetValueNotFound(DigitalLandValidationError):
    dataset_names: list

    def __init__(self, *args, dataset_names: list, **kwargs):
        self.dataset_names = dataset_names
        super().__init__(*args, **kwargs)


class TypologyValueNotFound(DigitalLandValidationError):
    typology_names: list

    def __init__(self, *args, dataset_names: list, **kwargs):
        self.dataset_names = dataset_names
        super().__init__(*args, **kwargs)


class InvalidGeometry(DigitalLandValidationError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
