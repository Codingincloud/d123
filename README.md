# NutriAI — AI-Powered Personalized Nutrition & Calorie Tracking System

> **Department of Computer Engineering | 7th Semester Undergraduate Project**  
> **Khwopa Engineering College, Purbanchal University**

---

## 👥 Project Team & Roles

| Name | Roll No. | Project Role | Primary Contribution |
|---|---|---|---|
| **Dristi Shrestha** | 790313 | Frontend Lead | Responsive Django templates, macro progress bars, AI recommendation cards, UX & styling |
| **Prashant Ghimire** | 790328 | Backend Lead | Database schema, Mifflin-St Jeor BMR/TDEE calculation engine, seed pipeline, unit test suite |
| **Romina Koju** | 790332 | ML Engineer | NepaliNutriDB curation, XGBoost & Random Forest training pipeline, hybrid recommendation engine |
| **Shrijan Sainju** | 790342 | Integration + GenAI | Tool-calling chatbot architecture (Groq/OpenAI), zero-hallucination database retrieval, UI chips |

---

## 🎯 Project Overview & Research Contribution

Standard calorie tracking applications (MyFitnessPal, HealthifyMe) are predominantly calibrated for Western or general Indian foods, offering virtually zero support for authentic Nepali dishes, portion sizes, or household cooking conventions.

**NutriAI** bridges this gap through two core engineering contributions:
1. **NepaliNutriDB**: A curated database of **129 verified Nepali food items** (including Dal Bhat, Dhido, Kwati, Gundruk, Chiura, Momo, Sel Roti, Choila) with complete macronutrients, fiber, sodium, sugar, Devanagari names, allergen flags, and dietary classifications derived from FAO Nepal (2012), NARC, and USDA.
2. **Hybrid ML Recommendation Engine**: An **XGBoost Regressor** trained on nutrient density profiles, coupled with calorie budget optimization and behavioral learning.

---

## 🏗️ System Architecture

```
                                  [ User / Client ]
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
             [ Web Dashboard ]                           [ AI Chatbot ]
         (Django Server Templates)                  (LLM Tool Calling Agent)
                    │                                           │
                    ├─────────────────┐                         │
                    ▼                 ▼                         ▼
         [ Nutrition Engine ]   [ ML Recommender ]   [ Function Call Bridge ]
          - Mifflin-St Jeor     - Allergen Filter    - get_user_health_profile
          - TDEE Multipliers    - XGBoost Model      - get_today_nutrition_summary
          - Macro Budgeting     - Budget Cosine Sim  - get_meal_recommendations
                    │                 │                         │
                    └─────────────────┼─────────────────────────┘
                                      ▼
                        [ SQLite / PostgreSQL ORM ]
                         ├── UserProfile & Logs
                         ├── NepaliNutriDB (129 Foods)
                         └── RecommendationHistory
```

---

## 🔬 Machine Learning & Evaluation (XGBoost vs Random Forest)

The recommendation engine scores foods based on nutritional density:
$$\text{Quality Score} = 0.35 \times \text{Protein Density} + 0.20 \times \text{Fiber} + 0.20 \times \text{Fat Balance} + 0.15 \times \text{Sugar Penalty} + 0.10 \times \text{Sodium Penalty}$$

### Model Performance on NepaliNutriDB

| Metric | XGBoost Regressor (Primary) | Random Forest Regressor (Benchmark) |
|---|---|---|
| **$R^2$ Score** | **0.7615** | 0.5858 |
| **Mean Absolute Error (MAE)** | **0.0358** | 0.0456 |
| **Root Mean Squared Error (RMSE)** | **0.0707** | 0.0931 |
| **Classification Accuracy ($\ge 0.50$)** | **92.86%** | 89.29% |
| **Precision** | **1.0000** | 1.0000 |
| **Recall** | **0.6667** | 0.5000 |
| **F1 Score** | **0.8000** | 0.6667 |

### Hybrid Recommendation Formula
$$\text{Final Score} = 0.50 \times S_{ML} + 0.30 \times S_{\text{Budget Fit}} + 0.20 \times S_{\text{Behavioral}}$$

---

## 🧮 Core Nutritional Formulas (Mifflin-St Jeor)

### 1. Basal Metabolic Rate (BMR)
- **Male**: $\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} + 5$
- **Female**: $\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} - 161$

### 2. Total Daily Energy Expenditure (TDEE)
$$\text{TDEE} = \text{BMR} \times \text{Activity Multiplier}$$
- Sedentary: $1.20$ | Light: $1.375$ | Moderate: $1.55$ | Very Active: $1.725$

### 3. Daily Calorie & Macronutrient Targets
- **Weight Loss**: $\text{TDEE} - 500\text{ kcal}$ (safe 0.5 kg/week rate)
- **Weight Gain**: $\text{TDEE} + 500\text{ kcal}$
- **Maintenance**: $\text{TDEE}$
- **Macro Split**: Protein (25%, 4 kcal/g), Carbohydrates (50%, 4 kcal/g), Fat (25%, 9 kcal/g)

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Git

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/dristi-stha/NutriAI.git
cd NutriAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database & Environment
By default, the project automatically uses **SQLite** for local development without any manual setup.
If you wish to use PostgreSQL or enable live Groq cloud LLM:
```bash
copy .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
# Optional PostgreSQL:
# DB_NAME=nutriaidb
# DB_USER=postgres
# DB_PASSWORD=your_password
```

### 4. Migrate and Seed NepaliNutriDB
```bash
# Run migrations
python manage.py migrate

# Seed 129 verified Nepali foods with Devanagari script, macros, and allergens
python manage.py seed_demo_data

# Train XGBoost & Random Forest ML recommendation models
python myapp/ml/train_models.py
```

### 5. Run Unit Test Suite
```bash
python manage.py test
```

### 6. Start the Server
```bash
python manage.py runserver
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🎓 Viva Defense / Q&A Quick Sheet

- **Q: Where did you get the Nepali food data?**  
  *A:* We built **NepaliNutriDB** using official tables from FAO Nepal (2012) and NARC, verified against USDA FoodData Central for raw ingredients, calibrated to standard Nepali household serving sizes.
- **Q: Why XGBoost over Deep Learning / Neural Networks?**  
  *A:* With tabular nutrition data (129 items, 7 features), gradient boosted decision trees (XGBoost) consistently outperform deep neural networks by avoiding overfitting on small-to-medium sample sizes while providing transparent feature importances.
- **Q: How do you prevent AI chatbot hallucinations?**  
  *A:* We implemented **Function Calling (Tool Calling)**. The LLM cannot invent user weights, calorie numbers, or food nutrients; it must execute Python tools (`get_user_health_profile`, `get_today_nutrition_summary`, `get_meal_recommendations`) that query our verified Django database.
- **Q: Does the system handle food allergies?**  
  *A:* Yes. Allergen filtering uses **strict hard exclusion** in the pre-filtering query stage (never soft penalties), ensuring items containing user allergens are completely omitted before ML ranking.
