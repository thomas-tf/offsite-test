import numpy as np
import pandas as pd
import pycantonese

from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline


class CantoneseTokenizer:
    """
    uses pyCantonese to help segment cantonese words
    this increases f-1 score by 4% comparing to ngrams of each character (defaults of CountVectorizer)
    """

    def __init__(self):
        self.stop_words = pycantonese.stop_words()
        self.punctuations = "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜" \
                            "〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."

    def tokenize(self, text):
        # lower all english character
        text = text.lower()

        words = pycantonese.segment(text)
        # return [word for word in words if word not in self.stop_words and word not in self.punctuations]
        return [word for word in words if word not in self.stop_words and word not in self.punctuations]


def main():

    TUNING = False

    train = pd.read_csv(r'offsite-tagging-training-set.csv')
    test = pd.read_csv(r'offsite-tagging-test-set.csv')

    text = train['text'].to_numpy(dtype=str)
    label = train['tag'].to_numpy(dtype=str)

    test_text = test['text'].to_numpy(dtype=str)

    misclassifications = []

    skf = StratifiedKFold(n_splits=5, random_state=420, shuffle=True)

    for i, (train_index, valid_index) in enumerate(skf.split(text, label), start=1):

        train_text = text[train_index]
        train_label = label[train_index]

        valid_text = text[valid_index]
        valid_label = label[valid_index]

        tokenizer = CantoneseTokenizer()

        # get frequencies of tokens as feature. Keep only features with document frequency >= 0.01 and <= 0.8
        text_count_vectorizer = CountVectorizer(tokenizer=tokenizer.tokenize, min_df=0.05, max_df=0.8)

        X_train = text_count_vectorizer.fit_transform(train_text)
        X_valid = text_count_vectorizer.transform(valid_text)

        y_train = train_label
        y_valid = valid_label

        # fit model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=420,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # prediction
        pred = model.predict(X_valid)

        # calculate F-1 macro score
        accuracy_score = metrics.accuracy_score(y_valid, pred)
        print(f"CV #{i} - Accuracy Score: {accuracy_score}")

        # find indices of misclassifications
        misclassified_indices = np.where(pred != y_valid)[0]

        # save misclassifications for analysis
        misclassifications.extend(
            [{'text': valid_text[index], 'pred': pred[index], 'label': y_valid[index]} for index in
             misclassified_indices])

    print('Misclassifications:')
    for i, misclassification in enumerate(misclassifications, start=1):
        print(f'#{i} - text:{misclassification["text"]}')
        print(f'#{i} - pred:{misclassification["pred"]}')
        print(f'#{i} - label:{misclassification["label"]}')
        print()

    tokenizer = CantoneseTokenizer()

    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenizer.tokenize)),
        ('clf', RandomForestClassifier())
    ])

    parameters = [{
        'vect__min_df': [0.01, 0.05, 0.1],
        'vect__max_df': [0.8, 0.9],
        'clf__n_estimators': [50, 100, 200],
        'clf__max_depth': [8, 10, 12]
    }]

    # best parameters found using gridsearch + Stratified K Fold of 5 splits
    best_parameters = [{
        'vect__min_df': [0.05],
        'vect__max_df': [0.8],
        'clf__n_estimators': [100],
        'clf__max_depth': [10]
    }]

    if TUNING:
        gs = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=3, cv=skf, scoring='accuracy')
    else:
        gs = GridSearchCV(pipeline, best_parameters, n_jobs=-1, verbose=3, cv=skf, scoring='accuracy')

    gs.fit(text, label)

    # analysis feature importance
    word_lookup = gs.best_estimator_.named_steps["vect"].vocabulary_
    # reverse key and value to {index: word}
    word_lookup = {v: k for k, v in word_lookup.items()}

    top_50_important_words_index = gs.best_estimator_.named_steps["clf"].feature_importances_.argsort()[-50:][::-1]
    top_50_important_words = [word_lookup[index] for index in top_50_important_words_index]
    print(f'Top 50 significant words learnt by RF (in desc order): {top_50_important_words}')

    test_predictions = gs.predict(test_text)

    test['predicted_tag'] = test_predictions

    test.to_csv('prediction.csv', index=False)


if __name__ == '__main__':
    main()
