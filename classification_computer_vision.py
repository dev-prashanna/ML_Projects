import torch
from torchvision import models, transforms
from PIL import Image
import json
import os

# === Load class names ===
with open("class_names.json", "r") as f:
    class_names = json.load(f)

num_classes = len(class_names)

# === Define transforms (must match training) ===
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# === Load the trained model ===
def load_model(weight_path, device):
    model = models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(weight_path, map_location=device))
    model.to(device)
    model.eval()
    return model

# === Predict function ===
def predict_image(image_path, model, device):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)  # Add batch dim & move to GPU/CPU

    with torch.no_grad():
        output = model(image)
        _, pred = torch.max(output, 1)
    return class_names[pred.item()]

def calculate(model, device):
    cats=dogs=0
    cat_num=dog_num=0
    cat_folder="./test/cats"
    dog_folder="./test/dogs"
    for fname in os.listdir(cat_folder):
        if fname.endswith(".jpg"):
            cat_num+=1
            image_path = os.path.join(cat_folder, fname)
            if os.path.exists(image_path):
                animal=predict_image(image_path, model, device)
                if animal=='cats':
                    cats+=1

    for fname in os.listdir(dog_folder):
        if fname.lower().endswith(".jpg"):
            dog_num+=1
            image_path = os.path.join(dog_folder, fname)
            if os.path.exists(image_path):
                animal=predict_image(image_path, model, device)
                if animal=='dogs':
                    dogs+=1
    print(f"No. of dogs predicted out of {dog_num} dogs is {dogs}")
    print(f"No. of cats predicted out of {cat_num} cats is {cats}")   

# === Entry point ===
if __name__ == "__main__":
    image_path = "./test/dogs/dog.5.jpg"       # <-- Change to your image
    weight_path = "dog_cat_classification.pth"    # <-- Your trained model file
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Model weights not found: {weight_path}")
    if not os.path.exists("class_names.json"):
        raise FileNotFoundError("Missing class_names.json. You must save it after training.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = load_model(weight_path, device)
    calculate(model, device)
    # prediction = predict_image(image_path, model, device)
    # print(f"🟢 Predicted Animal: {prediction}")
