import numpy as np
from PIL import Image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import Model

# ── Load MobileNetV2 once when the server starts ──────────────────────────────
# include_top=False  → removes the final classification layer
# pooling='avg'      → flattens output into a single 1280-dim vector
# weights='imagenet' → uses pre-trained weights, no training needed from us
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3),
    pooling='avg'
)
embedding_model = Model(inputs=base_model.input, outputs=base_model.output)

print("MobileNetV2 loaded successfully.")


def load_and_preprocess(image_path: str) -> np.ndarray:
    """
    Opens an image file, resizes it to 224x224 (what MobileNetV2 expects),
    converts to RGB, and normalizes pixel values to the range [-1, 1].
    Returns a numpy array of shape (1, 224, 224, 3) — the '1' is the batch size.
    """
    img = Image.open(image_path).convert("RGB")   # ensure 3 color channels
    img = img.resize((224, 224))                   # MobileNetV2 needs 224x224
    img_array = np.array(img, dtype=np.float32)    # convert to numbers
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension → (1,224,224,3)
    img_array = preprocess_input(img_array)        # normalize to [-1, 1]
    return img_array


def get_embedding(image_path: str) -> list:
    """
    Takes a path to a dog photo.
    Returns a list of 1280 numbers (the embedding vector).
    This vector is a numerical "fingerprint" of the dog's appearance.
    We store this in the database when a dog is registered.
    """
    img_array = load_and_preprocess(image_path)
    vector = embedding_model.predict(img_array, verbose=0)[0]  # shape (1280,)
    return vector.tolist()  # convert numpy array to plain Python list for JSON storage


def cosine_similarity(a: list, b: list) -> float:
    """
    Measures how similar two embedding vectors are.
    Returns a value between 0 and 1:
      1.0 = identical
      0.9+ = very likely same dog
      0.7-0.9 = possibly same dog, needs human review
      below 0.7 = different dog
    
    How it works: instead of comparing raw numbers, it compares the
    "direction" of the vectors. Two photos of the same dog from different
    angles will point in a similar direction even if pixel values differ.
    """
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_best_match(new_embedding: list, all_dogs: list) -> tuple:
    """
    Compares a new dog photo's embedding against every dog in the registry.
    
    Parameters:
      new_embedding : the 1280-dim vector from the uploaded photo
      all_dogs      : list of Dog objects from the database
    
    Returns:
      (best_matching_dog, confidence_score_as_percentage)
    
    Example return: (<Dog DOG-0041>, 94.3)
    """
    if not all_dogs:
        return None, 0.0

    best_dog   = None
    best_score = -1.0

    for dog in all_dogs:
        if dog.embedding_vector is None:
            continue  # skip dogs with no photo on file

        score = cosine_similarity(new_embedding, dog.embedding_vector)

        if score > best_score:
            best_score = score
            best_dog   = dog

    confidence_percent = round(best_score * 100, 1)
    return best_dog, confidence_percent