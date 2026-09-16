# Handling Imbalanced Data

## Objective

Evaluate different techniques for addressing the severe class imbalance.

## Methods

- Baseline
- Random Over Sampling
- Random Under Sampling
- SMOTE
- Class Weighting

## Results

| Sampling Method           | Accuracy | Precision | Recall  | F1-Score | ROC-AUC  |  PR-AUC  |
|---------------------------|---------:|----------:|--------:|---------:|---------:|---------:|
| **Baseline**              | 0.999220 | 0.866667 | 0.628399 | 0.728546 | 0.983242 | 0.767756 |
| **Random Over Sampling**  | 0.952153 | 0.972898 | 0.930219 | 0.951080 | 0.990532 | 0.991857 |
| **Random Under Sampling** | 0.960725 | 0.984127 | 0.936556 | 0.959752 | 0.992552 | 0.993690 |
| **SMOTE**                 | 0.948804 | 0.971335 | 0.924903 | 0.947550 | 0.991869 | 0.992577 |

## Best Method

Random Under Sampling achieved the strongest balance between Precision and Recall while maintaining the highest PR-AUC.

## Recommendation

Use the - Random Under Sampler-balanced training data for subsequent model training.