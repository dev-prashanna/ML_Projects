# ML_Projects

**Machine Learning Projects & Experiments**

This repository is a growing collection of machine learning experiments, notebooks, scripts, and prototype implementations. It is intended as a hands-on exploration space for core ML concepts, computer vision, data pipelines, and early-stage system integration.

---

## 🧠 Overview

The goal of this repository is to:
- Experiment with machine learning algorithms in practical settings  
- Compare pipeline-based vs non-pipeline workflows  
- Explore computer vision classification tasks  
- Integrate ML logic with simple web and system components  

Each project focuses on understanding **how models work internally**, not just achieving accuracy.

---

## 📂 Repository Structure
ML_Projects/
├── Code_for_pred_using_pipeline.ipynb
├── Code_for_pred_without_pipeline.ipynb
├── classification_computer_vision.py
├── main.ipynb
├── database.py
├── index.html
├── main.html
├── new.html
├── naterida_document.pdf
├── *.txt
└── README.md

### File Description
- **`.ipynb` files** → ML experiments, training, evaluation, and prediction  
- **`.py` files** → Modular ML / CV scripts and utilities  
- **`.html` files** → Prototype frontends or UI experiments  
- **`.pdf` / `.txt` files** → Documentation, notes, or helper modules  

---

## 🚀 Key Projects

### 1️⃣ ML Prediction With Pipeline
**File:** `Code_for_pred_using_pipeline.ipynb`

- Demonstrates structured ML workflow using pipelines
- Includes preprocessing, model fitting, and prediction
- Shows best practices for scalable ML systems

---

### 2️⃣ ML Prediction Without Pipeline
**File:** `Code_for_pred_without_pipeline.ipynb`

- Direct approach to model training and prediction
- Useful for understanding raw ML flow
- Helps compare maintainability vs simplicity

---

### 3️⃣ Computer Vision Classification
**File:** `classification_computer_vision.py`

- Image classification logic
- Modular code structure for dataset loading and inference
- Can be extended to CNN-based or transfer-learning models

---

### 4️⃣ UI / Integration Experiments
**Files:** `index.html`, `main.html`, `new.html`

- Early-stage frontend experiments
- Intended for visualizing or interacting with ML outputs
- Can be extended using Flask / FastAPI backends

---

## 🛠️ Installation

Clone the repository:
```bash
git clone https://github.com/dev-prashanna/ML_Projects.git
cd ML_Projects
Create a virtual environment (recommended):

python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Linux / macOS

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


If requirements.txt is not present, generate one using:

pip install pipreqs
pipreqs .

▶️ How to Run
Run Jupyter Notebooks
jupyter notebook


Open any .ipynb file and execute cells sequentially.

Run Python Scripts
python classification_computer_vision.py


Ensure datasets and paths are correctly configured inside the script.

📊 Results & Learning Outcomes

From these projects, you will learn:

Difference between pipeline and non-pipeline ML systems

Importance of preprocessing and feature consistency

How ML models integrate with external systems

Foundations for extending projects into research or production

📈 Future Improvements

Planned extensions:

Add deep learning models (CNNs, transfer learning)

Model evaluation using cross-validation and metrics visualization

Deploy models using FastAPI or Flask

Integrate experiment tracking (MLflow / W&B)

Add dataset documentation and benchmarks

🤝 Contributing

Contributions are welcome.

Steps:

Fork the repository

Create a feature branch

git checkout -b feature-name



