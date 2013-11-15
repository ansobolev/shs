class PlotData(object):
    pass

class FunctionData(PlotData):

    def __init__(self, data):
        self.title = data.title
        self.x = data.x
        self.x_title = data.x_title
        self.y = data.y
        self.y_titles = tuple(data.y_titles)

class HistogramData(PlotData):
    pass

class TimeEvolData(PlotData):
    pass
