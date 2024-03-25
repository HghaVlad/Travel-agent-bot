from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd


def get_date(date_string):
    try:
        return datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        return False


def users_to_recommend(user_id, users):
    data = [[user.id, user.city, user.country, user.bio, ''.join(user.locations)] for user in users]
    df = pd.DataFrame(data, columns=["id", "city", "country", "bio", "locations"])
    text_transformer = TfidfVectorizer()
    x_text = text_transformer.fit_transform(df[["city", "country", "bio", "locations"]])
    x_int = [user.age for user in users]
    X = pd.concat([pd.DataFrame(x_text.toarray()), pd.DataFrame(x_int)], axis=1)
    kmeans = KMeans(n_clusters=min(len(X) // 10 + 1, 5), random_state=42)
    df['cluster'] = kmeans.fit_predict(X)
    selected_user_cluster = df[df["id"] == user_id]["cluster"].values[0]

    return df[(df["cluster"] == selected_user_cluster)& (df["id"] != user_id)]["id"]

