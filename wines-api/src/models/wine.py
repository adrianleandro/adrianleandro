class Wine:
    id: int
    name: str
    type: str
    elaborate: str
    grapes: str
    harmonize: str
    abv: float
    body: str
    acidity: str
    country: str
    region: str
    winery: str
    vintages: str
    summary: str

    def __init__(self,
                 id: int,
                 name: str,
                 type: str,
                 elaborate: str,
                 abv: float,
                 body: str,
                 country: str,
                 region: str,
                 winery: str,
                 summary: str):
        self.id = id
        self.name = name
        self.type = type
        self.elaborate = elaborate
        self.abv = abv
        self.body = body
        self.country = country
        self.region = region
        self.winery = winery
        self.summary = summary