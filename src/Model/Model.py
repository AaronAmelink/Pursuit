import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
import random


class LikeModel:
    def __init__(self, vectorizer=None, model=None, model_type="SGDClassifier"):
        self.vectorizer = vectorizer
        self.model = model
        self.current_job = None
        self.feedback_data = [] 
        self.batch_size = 5
        self.model_type = model_type

        if model_type not in ["LogisticRegression", "SGDClassifier"]:
            raise ValueError("Invalid model type. Choose 'LogisticRegression' or 'SGDClassifier'.")

    def give_feedback(self, liked):
        if self.current_job is None:
            raise ValueError("No current job to give feedback on.")
        
        if self.model_type == "SGDClassifier":
            self.feedback_data = []  # Reset feedback data for SGDClassifier to prevent accumulation

        keywords = self.current_job.keywords.copy()
        random.shuffle(keywords)
        step = max(1, len(keywords) // self.batch_size)
        batches = [" ".join(keywords[i:i+step]) for i in range(0, len(keywords), step)]

        for batch in batches:
            self.feedback_data.append({"keywords": batch, "label": int(liked)})

        self.train_model()

    def train_model(self, min_samples=30):
        if len(self.feedback_data) < min_samples and self.model_type != "SGDClassifier":
            return

        df = pd.DataFrame(self.feedback_data)

        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            X = self.vectorizer.fit_transform(df['keywords'])
        else:
            X = self.vectorizer.transform(df['keywords'])

        y = df['label']

        if len(set(y)) < 2:
            print("Skipping training: only one class present in feedback.")
            return

        if X.shape[1] == 0:
            print("Skipping training: TF-IDF vectorizer returned no features.")
            return

        if (self.model_type == "LogisticRegression"):
            self.model = LogisticRegression(
                class_weight='balanced',
                penalty='l2',
                solver='liblinear',
                max_iter=1000,
                random_state=42
                )
            self.model.fit(X, y)
        elif (self.model_type == "SGDClassifier"):
            if self.model is None:
                self.model = SGDClassifier(loss='log_loss', class_weight={0: 6, 1: 8}, random_state=42)
                self.model.partial_fit(X, y, classes=[0, 1])
            else:
                self.model.partial_fit(X, y)
        #print(f"Retrained Logistic Regression on {len(y)} examples.")


    def predict(self, job):
        if self.model is None or self.vectorizer is None:
            return 0.5  # Neutral prediction

        processed = [" ".join(job.keywords)]
        X = self.vectorizer.transform(processed)
        return self.model.predict_proba(X)[0][1]

    def predict_keyword(self, keyword):
        if self.model is None or self.vectorizer is None:
            return 0.5

        X = self.vectorizer.transform([keyword])
        return self.model.predict_proba(X)[0][1]
    