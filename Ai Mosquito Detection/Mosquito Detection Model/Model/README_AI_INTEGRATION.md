## AI Mosquito Detection Integration

Files included:
- model/dengue_mosquito_model.h5
- predictor.py

Function:
predict_mosquito(image_path)

Returns:
{
  prediction: string,
  confidence: float,
  warning_level: HIGH | MEDIUM | LOW
}

Image input:
- JPG / PNG / JPEG / JFIF
- Auto-resized to 224x224
