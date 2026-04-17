import onnxruntime as ort
import numpy as np

# Load the ONNX model
onnx_model_path = "fraud_detection_model.onnx"
session = ort.InferenceSession(onnx_model_path)

# Example input based on the 6 input features we trained on
# The shape is [1, 6], using dtype float32
dummy_input = np.random.randn(1, 6).astype(np.float32)

# Find input name
input_name = session.get_inputs()[0].name
print(f"Input name: {input_name}")

# Run inference
output = session.run(None, {input_name: dummy_input})
print(f"Predicted Fraud Probability: {output[0][0][0]:.4f}")

if output[0][0][0] > 0.5:
    print("Warning: Potential fraud detected!")
else:
    print("Transaction appears safe.")
