import joblib

pipeline = joblib.load("models/oscar_pipeline.pkl")
print(hasattr(pipeline, "feature_names_in_"))
if hasattr(pipeline, "feature_names_in_"):
    print(len(pipeline.feature_names_in_))
    print(list(pipeline.feature_names_in_)[:10])
