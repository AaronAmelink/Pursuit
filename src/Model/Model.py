import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
import random



class LikeModel:
    def __init__(self, vectorizer=None, model=None, model_type="RandomForest", min_samples=20):
        self.min_samples = min_samples
        self.vectorizer = vectorizer
        self.model = model
        self.current_job = None
        self.feedback_data = [] 
        self.batch_size = 5
        self.model_type = model_type

        if model_type not in ["LogisticRegression", "SGDClassifier", "RandomForest"]:
            raise ValueError("Invalid model type. Choose 'LogisticRegression', 'SGDClassifier', or 'RandomForest'.")

    def give_feedback(self, liked: bool) -> None:
        """
        Give feedback on the current job. If the model is SGDClassifier, it will use partial_fit.
        For other models, it will retrain the model with the new feedback data.
        """

        if self.current_job is None:
            raise ValueError("No current job to give feedback on.")
        
        if self.model_type in ["SGDClassifier"]:
            self.feedback_data = []  # Reset feedback data for models that don't use incremental learning

        keywords = self.current_job.keywords.copy()
        random.shuffle(keywords)
        step = max(1, len(keywords) // self.batch_size)
        batches = [" ".join(keywords[i:i+step]) for i in range(0, len(keywords), step)]

        for batch in batches:
            self.feedback_data.append({"keywords": batch, "label": int(liked)})

        self.train_model()

    def train_model(self):
        if (len(self.feedback_data) < self.min_samples) and self.model_type != "SGDClassifier":
            return
        
        print(f"Training model with {len(self.feedback_data)} samples...")

        df = pd.DataFrame(self.feedback_data)

        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            X = self.vectorizer.fit_transform(df['keywords'])
        else:
            X = self.vectorizer.transform(df['keywords'])

        y = df['label']

        if len(set(y)) < 2 and self.model_type != "SGDClassifier":
            print("Skipping training: only one class present in feedback.")
            return

        if X.shape[1] == 0:
            print("Skipping training: TF-IDF vectorizer returned no features.")
            return

        if self.model_type == "LogisticRegression":
            self.model = LogisticRegression(
                class_weight='balanced',
                penalty='l2',
                solver='liblinear',
                max_iter=1000,
                random_state=42
            )
            self.model.fit(X, y)
        elif self.model_type == "SGDClassifier":
            if self.model is None:
                self.model = SGDClassifier(loss='log_loss', class_weight={0: 6, 1: 8}, random_state=42)
                self.model.partial_fit(X, y, classes=[0, 1])
            else:
                self.model.partial_fit(X, y)
        elif self.model_type == "RandomForest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                class_weight='balanced',
                max_depth=5,
                random_state=42
            )
            self.model.fit(X, y)

    def predict(self, keywords: list) -> float:
        """
        Predict the likelihood of a job being liked based on the keywords.
        Returns a float between 0 and 1, where 1 means the job is likely to be liked.
        """
        if self.model is None or self.vectorizer is None:
            print("Model or vectorizer not initialized. Cannot predict job.")
            return 0.5  # Neutral prediction

        processed = [" ".join(keywords)]
        X = self.vectorizer.transform(processed)
        
        # RandomForest doesn't have predict_proba by default in some versions
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)[0][1]
        else:
            # Fallback for models that don't have predict_proba
            return float(self.model.predict(X)[0])

    def predict_keyword(self, keyword: str) -> float:
        """
        Predict the likelihood of a keyword being liked based on the model.
        Returns a float between 0 and 1, where 1 means the keyword is likely to be liked.
        """
        if self.model is None or self.vectorizer is None:
            print("Model or vectorizer not initialized. Cannot predict keyword.")
            return 0.5

        X = self.vectorizer.transform([keyword])
        
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)[0][1]
        else:
            return float(self.model.predict(X)[0])
        