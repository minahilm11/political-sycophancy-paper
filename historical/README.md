# Archived experimental code

These files document how the original experimental material was generated and collected. `dataset_generation_political.py` is copied unchanged. `sycophancy_testing_political.py` preserves the original collector except that its `identity_pairs` list contains only the seven political pairs.

They are **not part of `reproduce.py`**. They require external credentials and make paid model calls if adapted and executed. Their original relative paths and historical model names are preserved as provenance, not guaranteed current runnable experiment infrastructure. The dataset generator emits comma-separated object fragments that historically required preparation into JSON arrays. The collector expects its political input folders in its working directory. Reproduction of the paper's outputs does not need either API, generation, or re-scoring.

The original repository revision and file hashes are in `data/source_manifest.json`. Complete political generation templates and few-shot examples are in `prompts/`.
