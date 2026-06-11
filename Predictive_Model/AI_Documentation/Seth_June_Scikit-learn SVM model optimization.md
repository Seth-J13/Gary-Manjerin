# Seth_June_Scikit-learn SVM model optimization

## User

I am working on a python script that uses the scikit-learn svm model. I need help understanding how to use the model and api to be able to utilize the full capacity of the model

## Claude

Here's a comprehensive overview of scikit-learn's SVM API and how to use it to its fullest. SVMs have several interconnected concepts — let me walk through them with an interactive reference you can explore.

Here's what each tab covers so you can dive into what's most relevant:

**Overview** — the three SVM classes (`SVC`, `SVR`, `OneClassSVM`) and a minimal pipeline template with the most important caveat: always scale first.

**Key parameters** — every hyperparameter for `SVC`/`SVR` with what it actually does, not just the name. The two most important ones are `C` (regularization) and `gamma` (kernel width for rbf).

**Kernels** — click each kernel to see its formula, when to use it, and gotchas. The `precomputed` option is particularly powerful if you have a custom distance function.

**Methods & attributes** — all the callable methods plus the post-fit attributes like `support_vectors_`, `n_support_`, and `coef_` (linear kernel only). The `n_support_` attribute is a great diagnostic: if it's close to your training size, `C` is too high.

**Code recipes** — complete copy-paste patterns for grid search, imbalanced classes, probability calibration, feature importance, and anomaly detection.

**Tuning tips** — the C–gamma trade-off table, common failure modes, and why you should use logarithmic spacing (`scipy.stats.loguniform`) rather than linear ranges when searching.

A few things that catch people most often:

The `decision_function()` output is generally more reliable than `predict_proba()` for ranking or thresholding. The probabilities from `predict_proba=True` use Platt scaling internally and can be poorly calibrated — `CalibratedClassifierCV` wrapping an SVC gives better results if you truly need calibrated probabilities.

For any dataset over ~10k rows, `LinearSVC` is almost always the right call — it solves the primal problem directly and is vastly faster than `SVC(kernel='linear')`.

Want me to go deeper on any specific area — like building a custom kernel, multi-class strategies, or working with text data?

