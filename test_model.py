from utils.CheckModel import CheckModel
# from utils import nltk_utils
import joblib

# ---------| Failed: failed load model |-----------
# TYPE = "NN_Pytorch"
# PATH_DATA = 'data/intents_3.json'
# PATH_MODEL = 'code/cross code/torch_model.pth'
# PATH_METADATA = 'code/cross code/torch_metadata.json'
# PATH_VECTORIZER = None

# ---------| Failed: failed load vectorizer |-----------
TYPE = "NN_Tensorflow_Tf-idf"
PATH_DATA = 'data/intents_3.json'
PATH_MODEL = 'code/cross code/tf_model.pkl'
PATH_METADATA = 'code/cross code/tf_metadata_tf-idf.json'
PATH_VECTORIZER = 'code/cross code/tf_vectorizer.pkl'

# ---------| Success |-----------
# TYPE = "NN_Tensorflow"
# PATH_DATA = 'data/intents_3.json'
# PATH_MODEL = 'code/cross code/tf_model_le.pkl'
# PATH_METADATA = 'code/cross code/tf_metadata_le.json'
# PATH_VECTORIZER = 'code/cross code/tf_vectorizer.pkl'

# Load the TF-IDF vectorizer
if PATH_VECTORIZER != None:
    print("\n Start load vectorizer-----")
    vectorizer = joblib.load(PATH_VECTORIZER)
    # with open(PATH_VECTORIZER, 'rb') as f:
    #     vectorizer = pickle.load(f)
    print("\n Success load vectorizer-----")

check_model = CheckModel(TYPE, PATH_MODEL, PATH_METADATA, PATH_DATA, vectorizer)
check_model.test_model()
# check_model.check_nltk_utils()