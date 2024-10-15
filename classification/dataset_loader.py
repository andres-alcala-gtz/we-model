import PIL
import math
import numpy
import pathlib
import tensorflow
import sklearn.model_selection


class DatasetLoader(tensorflow.keras.utils.Sequence):


    def __init__(self, xl_set: list[pathlib.Path], yl_set: list[str], labels: list[str], image_size: int, batch_size: int, **kwargs) -> None:

        super().__init__(**kwargs)

        self.xl_set = xl_set
        self.yl_set = yl_set
        self.labels = labels
        self.image_size = image_size
        self.batch_size = batch_size


    def __len__(self) -> int:

        return math.ceil(len(self.xl_set) / self.batch_size)


    def __getitem__(self, index: int) -> tuple[numpy.ndarray[int], numpy.ndarray[int]]:

        index_beg = index * self.batch_size
        index_end = min(index_beg + self.batch_size, len(self.xl_set))

        xl_batch = self.xl_set[index_beg:index_end]
        yl_batch = self.yl_set[index_beg:index_end]

        x_array = []
        y_array = []

        for xl, yl in zip(xl_batch, yl_batch):

            x = numpy.array(PIL.Image.open(xl).convert("RGB"))
            x = numpy.array(tensorflow.image.resize(x, (self.image_size, self.image_size)))
            x_array.append(x)

            y = self.labels.index(yl)
            y_array.append(y)

        x_array = numpy.array(x_array)
        y_array = numpy.array(y_array)

        return x_array, y_array


    def length(self) -> int:

        return len(self.xl_set)


    def y(self) -> numpy.ndarray[int]:

        y_array = []

        for index in range(self.__len__()):

            _, y = self.__getitem__(index)
            y_array.append(y)

        y_array = numpy.array(numpy.concatenate(y_array, axis=0))

        return y_array


    @classmethod
    def from_directory(cls, directory: pathlib.Path, image_size: int, batch_size: int) -> tuple["DatasetLoader", "DatasetLoader", "DatasetLoader", str, list[str]]:

        xl_all = []
        yl_all = []

        for location in directory.rglob("*"):
            if location.is_file():
                xl_all.append(location)
                yl_all.append(location.parent.stem)

        xl_train, xl_temp, yl_train, yl_temp = sklearn.model_selection.train_test_split(xl_all, yl_all, train_size=0.80)
        xl_test, xl_val, yl_test, yl_val = sklearn.model_selection.train_test_split(xl_temp, yl_temp, train_size=0.50)

        title = directory.stem
        labels = list(set(yl_all))

        dl_train = cls(xl_train, yl_train, labels, image_size, batch_size)
        dl_test = cls(xl_test, yl_test, labels, image_size, batch_size)
        dl_val = cls(xl_val, yl_val, labels, image_size, batch_size)

        return dl_train, dl_test, dl_val, title, labels