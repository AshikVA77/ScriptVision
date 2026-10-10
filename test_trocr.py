from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

print("Loading TrOCR model... (first time may take a few minutes)")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

image = Image.open(r"Assets/Tests/Sample.jpeg").convert("RGB")

pixel_values = processor(images=image, return_tensors="pt").pixel_values

generated_ids = model.generate(pixel_values)

generated_text = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True
)[0]

print("\n===== EXTRACTED TEXT =====\n")
print(generated_text)