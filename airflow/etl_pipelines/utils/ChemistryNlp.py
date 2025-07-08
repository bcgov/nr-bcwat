from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import polars as pl

class NLP:
    def __init__(self, db_conn=None):
        self.db_conn = db_conn

        self.text_clf = Pipeline(
            [
                ("vect", CountVectorizer()),
                ("tfidf", TfidfTransformer()),
                (
                    "clf",
                    SGDClassifier(
                        loss="modified_huber",
                        penalty="l2",
                        alpha=1e-3,
                        random_state=42,
                        max_iter=5,
                        tol=None,
                    ),
                ),
            ]
        )
        self.training = {
            "data": [],
            "target": [],
        }

    def train(self):
        self.text_clf.fit(self.training["data"], self.training["target"])

    def predict(self, value):
        percentages = self.text_clf.predict_proba([value])[0].tolist()
        max_percentage_index = percentages.index(max(percentages))
        percentage = percentages[max_percentage_index]
        category = self.text_clf.classes_[max_percentage_index]
        return (category, percentage)

    def get_data(self):
        query = "SELECT grouping_name, parameter_desc FROM bcwat_obs.water_quality_parameter JOIN bcwat_obs.water_quality_parameter_grouping USING (grouping_id)"
        data = pl.read_database(query=query, connection=self.db_conn)
        for row in data.rows():
            self.training["data"].append(row[1])
            self.training["target"].append(row[0])

    def run(self):
        self.get_data()
        self.train()
