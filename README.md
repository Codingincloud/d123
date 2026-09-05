# NutriAI — AI-Powered Personalized Nutrition & Calorie Tracking System

> **Department of Computer Engineering | 7th Semester Undergraduate Engineering Project**  
> **Khwopa Engineering College (Affiliated with Purbanchal University), Libali-08, Bhaktapur, Nepal**

[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost_3.3-EB5B28?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Groq](https://img.shields.io/badge/GenAI-Groq_Tool_Calling-F55036)](https://groq.com/)
[![Tests](https://img.shields.io/badge/Tests-10%2F10_Unit_%7C_32%2F32_E2E-success)](test_personas_e2e.py)
[![Documentation](https://img.shields.io/badge/Report-LaTeX_%26_PDF-blue)](docs/nutriai_mid_defense_report.pdf)

---

## 👥 Project Team & Technical Specializations

| Student Name | Roll No. | Academic Designation | Primary Technical Contributions |
|---|---|---|---|
| **Dristi Shrestha** | **790312** | **Frontend Lead** | Responsive Django templates, macro progress bars, AI recommendation cards, UX & styling, bilingual Devanagari labels |
| **Prashant Ghimire** | **790328** | **Backend Lead** | Django architecture, pure SQLite configuration, Mifflin-St Jeor BMR/TDEE calculation engine, REST API endpoints, unit test suite |
| **Romina Koju** | **790332** | **ML Engineer** | NepaliNutriDB curation, XGBoost & Random Forest training pipeline, evaluation benchmarks, hybrid recommendation algorithm, hard safety allergen filtering |
| **Shrijan Sainju** | **790338** | **System Integration & GenAI** | Groq multi-tool function calling agent, offline domain RAG fallback engine, interactive suggestion chips, multi-persona QA simulation |

---

## 🎯 Project Overview & Academic Significance

Commercial calorie tracking applications (such as MyFitnessPal, LoseIt, and HealthifyMe) are predominantly calibrated for Western or general Indian foods, offering virtually zero support for authentic Nepali dishes, portion sizes, or household cooking conventions. Furthermore, existing AI apps often use "black-box" heuristics or attempt to predict calories directly from photos, violating clinical safety constraints.

**NutriAI** resolves these challenges through a strict **Separation of Concerns**:
1. **NepaliNutriDB**: An authoritative database of **129 verified Nepali food items** (Dal Bhat, Dhido, Kwati, Gundruk, Chiura, Momo, Sel Roti, Choila, etc.) with complete micronutrients (fiber, sugar, sodium), calibrated household serving sizes, Devanagari names, and verifiable academic data sources (FAO Nepal 2012, NARC, USDA FoodData Central).
2. **Deterministic Clinical Safety Layer**: Strict allergen pre-filtering with synonym expansion (e.g. `dairy`, `lactose`, `milk`, `gluten`, `wheat`, `peanuts`) and dietary tags (Vegetarian, Vegan, Gluten-Free) ensuring **zero false-positive bypass**.
3. **Hybrid ML Recommendation Engine**: An **XGBoost Regressor** ($R^2 = 0.7615$, $92.86\%$ accuracy, $100\%$ precision) combining nutrient density, remaining daily calorie/macro budget fit, and user behavioral feedback.
4. **Multi-Tool Conversational Assistant**: Grounded Groq LLM tool calling (`get_user_health_profile`, `get_today_nutrition_summary`, `get_meal_recommendations`) with an offline domain RAG engine guaranteeing zero hallucination.

---

## 🏗️ System Architecture

```
                                  [ User / Client Browser ]
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
              - Goal Macro Budget   - Budget Cosine Sim  - get_meal_recommendations
                        │                 │                         │
                        └─────────────────┼─────────────────────────┘
                                          ▼
                               [ Pure SQLite Database ]
                             ├── UserProfile & Logs
                             ├── NepaliNutriDB (129 Foods)
                             └── RecommendationHistory
```

---

## 🔬 Machine Learning & Evaluation (XGBoost vs. Random Forest)

The recommendation engine scores candidate foods based on multidimensional nutrient density:
$$\text{Nutrient Score} = 0.35 \times \frac{\text{Protein}}{50} + 0.35 \times \frac{\text{Fiber}}{25} - 0.15 \times \frac{\text{Sugar}}{30} - 0.15 \times \frac{\text{Sodium}}{1500}$$

### Empirical Performance Comparison on NepaliNutriDB

| Evaluation Metric | XGBoost Regressor (Primary) | Random Forest Regressor (Benchmark) |
|---|---|---|
| **$R^2$ Score** | **0.7615** | 0.5858 |
| **Mean Absolute Error (MAE)** | **0.0358** | 0.0456 |
| **Root Mean Squared Error (RMSE)** | **0.0707** | 0.0931 |
| **Classification Accuracy ($\tau \ge 0.50$)** | **92.86%** | 89.29% |
| **Precision** | **1.0000** | 1.0000 |
| **Recall** | **0.6667** | 0.5000 |
| **F1 Score** | **0.8000** | 0.6667 |

### Feature Importances (XGBoost)
1. **Dietary Fiber**: 38.4% (rewards complex staples like Kwati, Gundruk)
2. **Sugar**: 26.7% (penalizes sweets and ultra-processed foods)
3. **Fat**: 9.7% (differentiates lean vs. deep-fried items)
4. **Carbohydrates**: 7.7% (glycemic energy balance)
5. **Calories**: 6.7% (portion suitability)
6. **Protein**: 6.1% (rewards pulses, legumes, lean meats)
7. **Sodium**: 4.7% (penalizes excessively salted preserved foods)

### Hybrid Recommendation Scoring
$$\text{Final Score} = 0.50 \times S_{\text{ML}} + 0.30 \times S_{\text{Budget Fit}} + 0.20 \times S_{\text{Behavioral}}$$

---

## 🧮 Biometric Nutrition Formulas (Mifflin-St Jeor)

### 1. Basal Metabolic Rate (BMR)
- **Male**: $\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} + 5$
- **Female**: $\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} - 161$

### 2. Total Daily Energy Expenditure (TDEE)
$$\text{TDEE} = \text{BMR} \times k_{\text{activity}}$$
- Sedentary: $1.20$ | Light: $1.375$ | Moderate: $1.55$ | Very Active: $1.725$

### 3. Goal-Tailored Calorie & Macronutrient Targets
- **Weight Loss**: $\text{TDEE} - 500\text{ kcal}$ (safe 0.5 kg/week deficit, floor 1200 kcal)
- **Weight Gain**: $\text{TDEE} + 500\text{ kcal}$ (lean mass surplus)
- **Maintenance**: $\text{TDEE}$
- **Macronutrient Splits**:
  - *Standard / Weight Loss*: 25% Protein (4 kcal/g), 50% Carbs (4 kcal/g), 25% Fat (9 kcal/g)
  - *Muscle Gain*: 30% Protein (4 kcal/g), 45% Carbs (4 kcal/g), 25% Fat (9 kcal/g)

---

## 👥 Multi-Persona Demo & Verification Guide

NutriAI includes pre-configured personas to demonstrate distinct real-world behaviors during college evaluation:

| Persona | Username | Password | Goal & Constraints | Tested & Verified Behaviors |
|---|---|---|---|---|
| **Aayush Sharma** | `aayush_fit` | `password123` | Weight Loss (Deficit) | Sedentary, BMR 1760, TDEE 2112, Target 1612 kcal (-500 kcal). Water & weight logged. Chatbot returned tailored weight loss advice. |
| **Pooja Karki** | `pooja_veg` | `password123` | Vegetarian + Dairy Allergy | **Hard Safety Filter:** ZERO dairy (Milk, Paneer, Dahi) & ZERO meats recommended. Recommended Masoor Dal, Kwati. 1-click log updated behavioral feedback. |
| **Bikram Thapa** | `bikram_diabetic` | `password123` | Diabetic + Gluten-Free | **Celiac Safety:** ZERO gluten/wheat (Puri, Naan, Chowmein) recommended. Recommended low-GI legumes. Chatbot gave specialized Dhido advice. |
| **Sneha Adhikari** | `sneha_student` | `password123` | Muscle Gain (Surplus) | Very active gym student. BMR 1196, TDEE 2063, Target 2563 kcal (+500 surplus, >190g protein). Profile edit updated weight to 49kg. |
| **Prashant Ghimire** | `prashant` | `password123` | Lead Developer | Full meal log history, daily summary tracking, and active recommendations. |

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/Codingincloud/d123.git
cd d123

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Database & Migrations
The project uses **pure SQLite** (`db.sqlite3`), completely avoiding local PostgreSQL connection errors:
```bash
# Apply migrations
python manage.py migrate

# Seed 129 verified Nepali foods and categories
python manage.py seed_demo_data

# Train ML recommendation models
python myapp/ml/train_models.py
```

### 4. Run Automated Test Suites
```bash
# 1. Standard Django Unit Tests (10/10 Passed)
python manage.py test myapp

# 2. Multi-Persona End-to-End Simulation (32/32 Passed)
python test_personas_e2e.py
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 📡 REST API Endpoints

In addition to responsive server-rendered views, NutriAI provides modular REST endpoints:

- `POST /api/users/login/` — JSON user authentication
- `POST /api/users/register/` — User registration and automatic profile creation
- `GET /api/nutrition/foods/?q=dal` — Search foods by name or category
- `GET /api/recommendations/` — Returns top ML-ranked food recommendations with match scores and explanations
- `POST /api/assistant/chat/` — Conversational assistant with tool calling and offline RAG

---

## 📄 Academic Project Report & Documentation

The complete 7th-semester mid-defense project report adhering to Purbanchal University / Khwopa Engineering College formatting is included:
- **LaTeX Source**: [`docs/mid_defense_report.tex`](docs/mid_defense_report.tex)
- **Publication PDF**: [`docs/nutriai_mid_defense_report.pdf`](docs/nutriai_mid_defense_report.pdf)
- **PDF Compilation Script**: [`docs/generate_report_pdf.py`](docs/generate_report_pdf.py)

---

## 🎓 Viva Defense / Q&A Quick Sheet

- **Q: Where did you get the Nepali food data?**  
  *A (Romina):* We constructed **NepaliNutriDB** using official tables from FAO Nepal (2012) and NARC, cross-verified against USDA FoodData Central for raw ingredients, and calibrated to authentic household serving sizes.
- **Q: Why XGBoost over Deep Neural Networks?**  
  *A (Romina):* With tabular nutrition data (129 verified foods, 7 features), gradient boosted decision trees (XGBoost) prevent overfitting on small-to-medium sample sizes while providing transparent, clinically defensible feature importances ($R^2 = 0.7615$, $100\%$ precision).
- **Q: How does the system prevent AI chatbot hallucinations?**  
  *A (Shrijan):* We implemented **Function Calling (Tool Calling)**. The LLM does not generate numbers from thin air; it calls Python tools (`get_user_health_profile`, `get_today_nutrition_summary`, `get_meal_recommendations`) that query our verified Django database. In offline mode, a deterministic RAG fallback handles questions without crashing.
- **Q: How are medical conditions and food allergies safeguarded?**  
  *A (Prashant):* We enforce **Hard Safety Filtering** in the pre-filtering query stage before any ML ranking occurs. Allergen synonyms (`dairy`/`lactose` $\rightarrow$ `Milk`, `gluten` $\rightarrow$ `Gluten`, `Wheat`) guarantee zero hazardous food suggestions.
- **Q: How does the frontend assist user adherence?**  
  *A (Dristi):* The dashboard integrates visual macro breakdown bars (Calories, Protein, Carbs, Fat), AI recommendation cards with bilingual Devanagari names, match percentages, and one-click meal logging.

---

## 📜 License & Acknowledgement

Developed as a 7th-Semester Undergraduate Project under the Department of Computer Engineering, Khwopa Engineering College, Purbanchal University.
