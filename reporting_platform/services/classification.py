import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# نموذج مبدئي لتدريب التصنيف
def train_model():
    descriptions = [
        "تجمّع نفايات", "شخص مشبوه", "كهرباء مكشوفة", "مياه تتسرب", "ضوضاء مرتفعة"
    ]
    labels = ["نظافة", "أمني", "كهرباء", "مياه", "ضوضاء"]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(descriptions)

    model = MultinomialNB()
    model.fit(X, labels)

    with open("classifier.pkl", "wb") as f:
        pickle.dump((model, vectorizer), f)

# استخدام النموذج في التصنيف
def classify_report(description):
    try:
        with open("classifier.pkl", "rb") as f:
            model, vectorizer = pickle.load(f)

        clean_desc = re.sub(r'\W+', ' ', description.lower())
        X = vectorizer.transform([clean_desc])
        predicted = model.predict(X)
        return predicted[0]
    except Exception as e:
        print(f"خطأ في التصنيف: {e}")
        return "غير مصنّف"
