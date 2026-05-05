"""
Smart Ingredient Analyzer - FastAPI Backend
Place this file in the SAME folder as lstm_model.keras and tokenizer.pkl
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import os
import io
from PIL import Image
import pytesseract

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load LSTM model
try:
    import tensorflow as tf
    model = tf.keras.models.load_model(os.path.join(BASE_DIR, "lstm_model.keras"))
    print("LSTM model loaded successfully")
except Exception as e:
    model = None
    print(f"Could not load LSTM model: {e}")

# Load tokenizer
try:
    with open(os.path.join(BASE_DIR, "tokenizer.pkl"), "rb") as f:
        tokenizer = pickle.load(f)
    print("Tokenizer loaded successfully")
except Exception as e:
    tokenizer = None
    print(f"Could not load tokenizer: {e}")

MAX_SEQUENCE_LENGTH = 50

# Known ingredients database (229 ingredients from training data)
KNOWN_INGREDIENTS = {
    "A2 MILK POWDER": {"effect": "Source of protein and calcium; easier to digest for some individuals.", "score": 3},
    "ACRYLATES/BEHENETH-25 METHACRYLATE COPOLYMER": {"effect": "Film-former; low toxicity but poor biodegradability", "score": 5},
    "ALMOND": {"effect": "Rich in healthy fats, protein, and micronutrients.", "score": 2},
    "ALMONDS": {"effect": "Rich in healthy fats and vitamin E; supports heart health.", "score": 2},
    "ALPHA-ISOMETHYL IONONE": {"effect": "Fragrance allergen; may cause skin sensitization", "score": 7},
    "AMODIMETHICONE": {"effect": "Conditioning silicone; low direct toxicity", "score": 3},
    "AMYL CINNAMAL": {"effect": "Fragrance allergen; may cause skin reactions", "score": 7},
    "AQUA (WATER)": {"effect": "Completely safe solvent used as a base ingredient.", "score": 1},
    "ARGANIA SPINOSA (ARGAN OIL) KERNEL OIL": {"effect": "Nourishes hair and skin; rich in antioxidants", "score": 2},
    "ARGININE": {"effect": "Amino acid that supports enamel repair and oral health.", "score": 2},
    "ARTIFICIAL VANILLA FLAVOURING": {"effect": "Synthetic flavor; may cause sensitivity in some individuals.", "score": 5},
    "BEETROOT": {"effect": "Rich in antioxidants and nitrates; supports heart health.", "score": 1},
    "BENTONITE EARTH (CALCIUM BENTONITE)": {"effect": "Natural clay; safe topically but abrasive in excess.", "score": 3},
    "BENZYL ALCOHOL": {"effect": "Preservative and fragrance component; may irritate skin", "score": 6},
    "BENZYL BENZOATE": {"effect": "Fragrance component; may cause irritation", "score": 6},
    "BENZYL SALICYLATE": {"effect": "Fragrance allergen; may trigger skin reactions", "score": 7},
    "BHT": {"effect": "Antioxidant with potential endocrine disruption concerns.", "score": 8},
    "BLACK PEPPER POWDER": {"effect": "Enhances nutrient absorption and digestion.", "score": 1},
    "BLACK SALT": {"effect": "Mineral salt; excess intake may affect blood pressure.", "score": 3},
    "BUTTER": {"effect": "High in saturated fat; safe in moderation but calorie-dense.", "score": 5},
    "CALCIUM CARBONATE": {"effect": "Mild abrasive; safe for enamel at controlled levels.", "score": 3},
    "CARBOMER": {"effect": "Thickening agent; generally safe for topical use", "score": 1},
    "CARROM SEEDS (AJWAIN)": {"effect": "Supports digestion; helps relieve bloating and acidity.", "score": 1},
    "CASHEWNUTS": {"effect": "Provides healthy fats and minerals; calorie-dense if overconsumed.", "score": 2},
    "CELLULOSE GUM": {"effect": "Stabilizer that improves consistency with low toxicity.", "score": 2},
    "CERAMIDE AP": {"effect": "Improves skin hydration and resilience", "score": 2},
    "CERAMIDE EOP": {"effect": "Strengthens skin’s protective layer", "score": 2},
    "CERAMIDE NP": {"effect": "Helps restore and protect the skin barrier", "score": 2},
    "CETRIMONIUM CHLORIDE": {"effect": "Antistatic agent; toxic if ingested and irritating at high levels", "score": 6},
    "CETYLPYRIDINIUM CHLORIDE": {"effect": "Antibacterial agent; may cause staining and irritation.", "score": 8},
    "CHENOPODIUM QUINOA SEED EXTRACT": {"effect": "Rich in amino acids; nourishes hair and skin", "score": 2},
    "CHOLESTEROL": {"effect": "Supports skin barrier and moisture retention", "score": 2},
    "CI 11680": {"effect": "Artificial colorant; may irritate sensitive skin", "score": 5},
    "CI 12490": {"effect": "Synthetic dye; low toxicity but allergy risk", "score": 5},
    "CI 17200": {"effect": "Artificial colorant; low toxicity but allergy risk", "score": 5},
    "CI 21100": {"effect": "Synthetic dye; potential allergenic reactions.", "score": 8},
    "CI 42090": {"effect": "Synthetic dye; may cause irritation in sensitive users", "score": 5},
    "CI 45430": {"effect": "Synthetic dye; potential allergenic reactions.", "score": 8},
    "CI 47005": {"effect": "Artificial colorant; may cause skin reactions.", "score": 7},
    "CINNAMAL": {"effect": "Strong fragrance allergen linked to dermatitis.", "score": 8},
    "CITRAL": {"effect": "Fragrance allergen; sensitization risk", "score": 7},
    "CITRIC ACID": {"effect": "pH adjuster; may cause mild irritation on very sensitive skin", "score": 2},
    "CITRIC ACID (INS 330)": {"effect": "Food acidulant; safe at approved levels.", "score": 3},
    "CITRONELLOL": {"effect": "Fragrance allergen linked to irritation", "score": 7},
    "CLIMBAZOLE": {"effect": "Antifungal agent; may cause irritation with prolonged use", "score": 8},
    "COCAMIDE MEA": {"effect": "Foam booster; may cause irritation with prolonged exposure", "score": 6},
    "COCAMIDOPROPYL BETAINE": {"effect": "Mild surfactant; may cause allergic reactions in sensitive skin", "score": 5},
    "COCOA BEANS": {"effect": "Rich in antioxidants; beneficial for heart and brain health when consumed moderately.", "score": 1},
    "COCOA BUTTER": {"effect": "Natural fat; generally safe but calorie-dense.", "score": 2},
    "COCOA SOLIDS": {"effect": "Rich in antioxidants; beneficial when consumed in moderation.", "score": 2},
    "COCONUT": {"effect": "Provides healthy fats, supports heart health in moderation.", "score": 2},
    "CORIANDER SEED POWDER": {"effect": "Aids digestion and supports gut health.", "score": 1},
    "CORN MEAL": {"effect": "Provides energy and fiber; generally safe.", "score": 2},
    "COUMARIN": {"effect": "Potential allergen; may cause skin reactions", "score": 7},
    "CUMIN SEEDS (JEERA)": {"effect": "Aids digestion and has anti-inflammatory properties.", "score": 1},
    "CYMBOPOGON MARTINI OIL": {"effect": "Essential oil; skin sensitization risk", "score": 6},
    "DEXTROSE": {"effect": "Simple sugar; rapid increase in blood glucose.", "score": 6},
    "DIMETHICONE": {"effect": "Silicone that smooths hair and reduces moisture loss", "score": 3},
    "DIMETHICONOL": {"effect": "Silicone that smooths hair; non-toxic but non-biodegradable", "score": 3},
    "DISODIUM EDTA": {"effect": "Chelating agent; can enhance absorption of other chemicals", "score": 4},
    "DISODIUM ETIDRONATE": {"effect": "Prevents mineral buildup; low toxicity to skin.", "score": 3},
    "DMDM HYDANTOIN": {"effect": "Formaldehyde-releasing preservative; allergenic", "score": 9},
    "DOUGH CONDITIONER E223": {"effect": "Sulfite compound; may trigger allergic reactions.", "score": 7},
    "EDIBLE COMMON SALT": {"effect": "Essential mineral; excess intake raises blood pressure.", "score": 3},
    "EDIBLE SUNFLOWER OIL": {"effect": "Unsaturated fat; safe but calorie-dense when overused.", "score": 4},
    "EDIBLE VEGETABLE OIL": {"effect": "High-fat content; excessive intake linked to metabolic issues.", "score": 7},
    "EDIBLE VEGETABLE OIL (PALM)": {"effect": "High saturated fat; linked to heart disease risk.", "score": 7},
    "EMULSIFIER E322 (SOY LECITHIN)": {"effect": "Common food emulsifier; generally safe.", "score": 3},
    "EMULSIFIER E412 (GUAR GUM)": {"effect": "Natural thickener; aids digestion in small amounts.", "score": 3},
    "EMULSIFIER E471": {"effect": "Fatty acid mono- and diglycerides; safe but processed.", "score": 4},
    "EMULSIFIER E472": {"effect": "Emulsified fatty acids; moderate processing risk.", "score": 4},
    "ETHYL VANILLIN": {"effect": "Artificial flavor; safe in low food-grade quantities.", "score": 4},
    "ETIDRONIC ACID": {"effect": "Chelating agent; generally safe at cosmetic concentrations.", "score": 3},
    "EUGENOL": {"effect": "Fragrance allergen; may cause dermatitis", "score": 7},
    "FENUGREEK LEAF POWDER": {"effect": "Helps regulate blood sugar levels.", "score": 1},
    "FLAVOR": {"effect": "Generic flavoring; may cause sensitivity reactions.", "score": 7},
    "FLOUR TREATMENT AGENT (516)": {"effect": "Stabilizer; approved food additive with low toxicity.", "score": 3},
    "FOXTAIL MILLET": {"effect": "High in fiber and minerals; supports digestion and glucose control.", "score": 1},
    "FRACTIONATED VEGETABLE FAT": {"effect": "Processed fat; excessive intake linked to metabolic issues.", "score": 7},
    "FRAGRANCE": {"effect": "Common cause of allergic reactions and skin sensitivity", "score": 8},
    "GARLIC POWDER": {"effect": "Supports immunity and heart health.", "score": 1},
    "GERANIOL": {"effect": "Fragrance compound; known skin sensitizer", "score": 7},
    "GINGER POWDER": {"effect": "Helps digestion and reduces inflammation.", "score": 1},
    "GLUCOSE SYRUP": {"effect": "Refined sugar; spikes blood sugar levels.", "score": 6},
    "GLYCERIN": {"effect": "Hydrates skin and helps maintain moisture balance", "score": 1},
    "GLYCERINE": {"effect": "Moisturizes skin and supports barrier function.", "score": 2},
    "GLYCOL DISTEARATE": {"effect": "Opacifying agent; low health risk", "score": 4},
    "GRAM MEAL": {"effect": "Protein-rich legume flour; supports digestion and satiety.", "score": 2},
    "GRAPEFRUIT SEED EXTRACT": {"effect": "Natural preservative; generally safe in low doses.", "score": 3},
    "GUAR HYDROXYPROPYLTRIMONIUM CHLORIDE": {"effect": "Conditioning agent; low irritation risk", "score": 3},
    "HELIANTHUS ANNUUS (SUNFLOWER) SEED OIL": {"effect": "Nourishes skin and provides antioxidant benefits", "score": 2},
    "HEXYL CINNAMAL": {"effect": "Fragrance allergen; can cause skin sensitivity", "score": 7},
    "HIMALAYAN PINK SALT": {"effect": "Mineral salt; excessive intake may raise blood pressure.", "score": 3},
    "HIMALAYAN ROCK SALT": {"effect": "Mineral salt; excess intake may increase blood pressure.", "score": 3},
    "HYDRATED SILICA": {"effect": "Gentle polishing agent for teeth.", "score": 3},
    "HYDROGENATED VEGETABLE FATS": {"effect": "Contains trans fats; increases heart disease risk.", "score": 9},
    "HYDROGENATED VEGETABLE OIL (PALM OIL)": {"effect": "Contains unhealthy fats; linked to heart disease risk.", "score": 8},
    "HYDROLYZED CICER SEED EXTRACT": {"effect": "Strengthens hair and improves texture", "score": 2},
    "HYDROLYZED KERATIN": {"effect": "Strengthens hair structure and reduces breakage", "score": 2},
    "HYDROLYZED MILK PROTEIN": {"effect": "Strengthens hair and improves moisture retention", "score": 2},
    "HYDROXYSTEARIC ACID": {"effect": "Fatty acid derivative; stabilizes formulations", "score": 2},
    "INULIN": {"effect": "Prebiotic fiber; supports gut bacteria.", "score": 2},
    "IODISED SALT": {"effect": "Essential mineral; excessive intake may affect blood pressure.", "score": 3},
    "IODIZED SALT": {"effect": "Essential mineral; excessive intake affects blood pressure.", "score": 3},
    "ISOPROPYL ALCOHOL": {"effect": "Drying and irritating to skin.", "score": 7},
    "JAGGERY POWDER": {"effect": "Natural sweetener; provides energy but high intake may affect blood sugar.", "score": 4},
    "JASMINUM OFFICINALE (JASMINE) FLOWER EXTRACT": {"effect": "Fragrance extract; low irritation risk", "score": 3},
    "JAU (BARLEY)": {"effect": "Rich in fiber and vitamins; helps reduce cholesterol.", "score": 2},
    "JOWAR (SORGHUM)": {"effect": "High in fiber, aids digestion and controls blood sugar.", "score": 2},
    "KAOLIN": {"effect": "Mild abrasive clay; low toxicity in oral care.", "score": 4},
    "KHANDSARI SUGAR": {"effect": "Less refined sugar; still raises blood glucose when consumed in excess.", "score": 5},
    "LAURIC ACID": {"effect": "Fatty acid with cleansing and antimicrobial properties", "score": 2},
    "LENS ESCULENTA (LENTIL) SEED EXTRACT": {"effect": "Provides conditioning and antioxidant properties", "score": 2},
    "LIMONENE": {"effect": "Fragrance allergen; oxidizes and irritates skin", "score": 7},
    "LINALOOL": {"effect": "Fragrance allergen that oxidizes and irritates skin", "score": 7},
    "LITTLE MILLET": {"effect": "Low glycemic index; good for gut and metabolic health.", "score": 1},
    "LYSINE HCL": {"effect": "Amino acid that supports hair and skin conditioning", "score": 2},
    "MALTITOL (E965)": {"effect": "Sugar alcohol; low-glycemic but may cause bloating.", "score": 4},
    "MALTODEXTRIN": {"effect": "Highly processed carb; spikes blood sugar.", "score": 5},
    "MENTHA ARVENSIS LEAF OIL": {"effect": "Cooling oil; may irritate sensitive skin", "score": 6},
    "MENTHOL": {"effect": "Cooling agent; safe but irritating at higher levels.", "score": 4},
    "METHYLCHLOROISOTHIAZOLINONE": {"effect": "Strong preservative; high risk of allergic reactions", "score": 10},
    "METHYLISOTHIAZOLINONE": {"effect": "Potent allergen linked to contact dermatitis", "score": 10},
    "MICA": {"effect": "Cosmetic pigment; inhalation risk in powder form only", "score": 3},
    "MILK LIPIDS": {"effect": "Nourish skin and support moisture barrier", "score": 1},
    "MILK SOLIDS": {"effect": "Provides calcium and protein; lactose intolerance possible.", "score": 3},
    "NATURAL CEREAL FIBRE (OATS)": {"effect": "Improves gut health and satiety.", "score": 2},
    "NATURAL GLYCOLIPIDS": {"effect": "Mild surfactants; skin and oral-tissue friendly.", "score": 2},
    "NATURE-IDENTICAL FLAVOURING SUBSTANCE": {"effect": "Chemically identical to natural flavors; safe in small amounts.", "score": 4},
    "NELUMBIUM SPECIOSUM FLOWER OIL": {"effect": "Botanical oil; mild skin conditioning", "score": 3},
    "NIACINAMIDE": {"effect": "Supports skin barrier and improves scalp health", "score": 2},
    "ORANGE EXTRACT": {"effect": "Natural extract; provides flavor and antioxidants.", "score": 3},
    "ORGANIC JAGGERY": {"effect": "Natural sweetener; retains minerals but still raises blood sugar.", "score": 3},
    "PARFUM (FRAGRANCE)": {"effect": "Common allergen; may cause irritation and headaches.", "score": 7},
    "PEANUTS": {"effect": "Protein-rich; safe for most but allergenic for some individuals.", "score": 2},
    "PEARL MILLET": {"effect": "Rich in iron and magnesium; supports heart health.", "score": 1},
    "PEG-4": {"effect": "Solubilizer; increases skin permeability.", "score": 5},
    "PEG-40 HYDROGENATED CASTOR OIL": {"effect": "Emulsifier; may irritate sensitive skin", "score": 4},
    "PEG-45M": {"effect": "Thickener; generally safe but may enhance ingredient penetration", "score": 3},
    "PEG-8": {"effect": "Solvent and humectant; low irritation risk", "score": 3},
    "PEPPERMINT ESSENTIAL OIL": {"effect": "Flavoring oil; may irritate sensitive tissues.", "score": 4},
    "PERFUME (FRAGRANCE)": {"effect": "Common allergen; may cause skin sensitization", "score": 8},
    "PHYTOSPHINGOSINE": {"effect": "Supports skin barrier and has antimicrobial benefits", "score": 2},
    "PIROCTONE OLAMINE": {"effect": "Antifungal agent; may irritate with prolonged exposure", "score": 6},
    "POLYSORBATE 20": {"effect": "Emulsifier; low toxicity", "score": 3},
    "POTASSIUM NITRATE": {"effect": "Reduces tooth sensitivity; safe at regulated levels.", "score": 4},
    "PROPYLENE GLYCOL": {"effect": "Humectant; may cause irritation in sensitive skin", "score": 4},
    "PRUNUS AMYGDALUS DULCIS (SWEET ALMOND) OIL": {"effect": "Emollient that nourishes and softens skin", "score": 2},
    "PRUNUS ARMENIACA (APRICOT) KERNEL OIL": {"effect": "Softens skin and improves moisture retention", "score": 2},
    "PUMPKIN SEEDS": {"effect": "Excellent source of healthy fats, zinc, and antioxidants.", "score": 1},
    "PURIFIED AQUA (WATER)": {"effect": "Safe base solvent with no known health risks.", "score": 1},
    "PURIFIED STEVIA EXTRACT": {"effect": "Natural sweetener; safe in small oral-care amounts.", "score": 1},
    "PYRIDOXINE HCL": {"effect": "Vitamin B6 derivative; supports skin metabolism", "score": 2},
    "RAGI FLOUR": {"effect": "Rich in fiber, calcium, and iron; supports digestion and bone health.", "score": 1},
    "RAISING AGENT": {"effect": "Chemical leavening; generally safe in small amounts, excessive may cause digestive discomfort.", "score": 6},
    "RAISING AGENT (500(II))": {"effect": "Baking soda; safe leavening agent at food-grade levels.", "score": 3},
    "RAISING AGENTS (503(II), 500(II), 450(I))": {"effect": "Food leavening agents; safe at approved levels.", "score": 3},
    "RED CHILLI": {"effect": "Adds flavor; excessive intake may irritate the stomach.", "score": 3},
    "REFINED WHEAT FLOUR (MAIDA)": {"effect": "Highly refined carb; low nutrition and blood sugar spikes.", "score": 6},
    "RICE BRAN OIL": {"effect": "Contains healthy fats; beneficial in moderation.", "score": 3},
    "RICE MEAL": {"effect": "Easily digestible carbohydrate; safe when consumed moderately.", "score": 2},
    "ROCK SALT": {"effect": "Contains minerals; excessive intake may raise blood pressure.", "score": 3},
    "ROLLED OATS": {"effect": "Whole grain; supports digestion and heart health.", "score": 2},
    "ROSA GALLICA FLOWER EXTRACT": {"effect": "Botanical extract with soothing properties", "score": 3},
    "SAGO": {"effect": "High-carb and low-fiber; provides energy but low nutrition.", "score": 4},
    "SALT": {"effect": "Natural mineral; safe in low concentrations.", "score": 2},
    "SANDALWOOD OIL": {"effect": "Fragrance oil; may cause irritation", "score": 6},
    "SELECTED SPICES": {"effect": "Natural spices; aid digestion and provide antioxidants.", "score": 2},
    "SERICIN": {"effect": "Silk protein that smooths and conditions skin", "score": 1},
    "SILVER OXIDE": {"effect": "Antimicrobial agent; may irritate sensitive skin", "score": 6},
    "SODIUM ASCORBYL PHOSPHATE": {"effect": "Vitamin C derivative with antioxidant benefits", "score": 2},
    "SODIUM BENZOATE": {"effect": "Preservative; safe at low concentrations", "score": 3},
    "SODIUM BICARBONATE": {"effect": "Mild abrasive; helps neutralize acids safely.", "score": 2},
    "SODIUM C14-C18 OLEFIN SULFONATE": {"effect": "Harsh surfactant; high irritation potential", "score": 7},
    "SODIUM CARBONATE": {"effect": "pH regulator; can be drying in high concentrations", "score": 2},
    "SODIUM CHLORIDE": {"effect": "Thickener; excessive amounts may cause dryness", "score": 2},
    "SODIUM CITRATE": {"effect": "Buffering agent that helps maintain product pH", "score": 2},
    "SODIUM COCOYL ISETHIONATE": {"effect": "Very mild cleanser suitable for sensitive skin.", "score": 3},
    "SODIUM GLUCONATE": {"effect": "Chelating agent that improves product stability", "score": 1},
    "SODIUM GLYCINATE": {"effect": "Mild surfactant; gentle on skin", "score": 1},
    "SODIUM HYDROXIDE": {"effect": "pH adjuster; can irritate if improperly balanced", "score": 3},
    "SODIUM ISETHIONATE": {"effect": "Gentle surfactant with low irritation potential.", "score": 3},
    "SODIUM LAURETH SULFATE": {"effect": "Can strip natural oils and cause skin or scalp irritation", "score": 7},
    "SODIUM LAUROYL LACTYLATE": {"effect": "Mild surfactant that supports skin barrier function", "score": 2},
    "SODIUM LAURYL SULFATE": {"effect": "Strong surfactant; high risk of skin and eye irritation", "score": 9},
    "SODIUM LAURYL SULPHATE": {"effect": "Foaming agent; known to irritate gums and oral tissues.", "score": 7},
    "SODIUM METABISULFITE": {"effect": "Preservative; may trigger allergic reactions.", "score": 6},
    "SODIUM MONOFLUOROPHOSPHATE": {"effect": "Fluoride source; strengthens enamel when used correctly.", "score": 4},
    "SODIUM PALM KERNELATE": {"effect": "Cleansing agent; may disrupt skin barrier", "score": 5},
    "SODIUM PALMATE": {"effect": "Soap base; can be drying to skin", "score": 5},
    "SODIUM PALMITATE": {"effect": "Soap base; may dry skin with frequent use.", "score": 4},
    "SODIUM ROSINATE": {"effect": "Resin-based surfactant; may cause skin sensitivity.", "score": 5},
    "SODIUM SACCHARIN": {"effect": "Non-nutritive sweetener; safe in toothpaste amounts.", "score": 3},
    "SODIUM SILICATE": {"effect": "Binder; may irritate tissues at high concentrations.", "score": 5},
    "SODIUM STEARATE": {"effect": "Soap surfactant; mildly drying.", "score": 4},
    "SODIUM SULFATE": {"effect": "Processing aid; low direct skin impact", "score": 2},
    "SODIUM XYLENESULFONATE": {"effect": "Surfactant that can increase skin irritation", "score": 6},
    "SORBITOL": {"effect": "Humectant that helps retain skin moisture.", "score": 2},
    "SORGHUM": {"effect": "Gluten-free whole grain; rich in antioxidants and fiber.", "score": 1},
    "SOY LECITHIN (E322)": {"effect": "Emulsifier; generally safe and well-tolerated.", "score": 3},
    "SOYA LECITHIN (EMULSIFIER)": {"effect": "Food emulsifier; generally safe and well tolerated.", "score": 3},
    "SPICES & CONDIMENTS (MIXED)": {"effect": "Natural spices; aid digestion and provide antioxidants.", "score": 2},
    "STEARIC ACID": {"effect": "Fatty acid that conditions skin and improves texture.", "score": 2},
    "STYRENE/ACRYLATES COPOLYMER": {"effect": "Synthetic polymer; potential environmental and skin concerns", "score": 6},
    "SUGAR": {"effect": "Excess consumption linked to obesity and diabetes.", "score": 7},
    "SWEETENER E955 (SUCRALOSE)": {"effect": "Artificial sweetener; may affect gut microbiome.", "score": 5},
    "TALC": {"effect": "Safe topically; inhalation risk if airborne.", "score": 5},
    "TAPIOCA STARCH": {"effect": "Easily digestible carbohydrate; safe in moderate amounts.", "score": 2},
    "TARTARIC ACID (INS 334)": {"effect": "Acidity regulator; safe in food use.", "score": 3},
    "TEA TREE OIL": {"effect": "Antimicrobial oil; can cause irritation if overused.", "score": 5},
    "TEA-DODECYLBENZENESULFONATE": {"effect": "Strong surfactant; high irritation potential", "score": 8},
    "TERPINEOL": {"effect": "Fragrance component; potential skin sensitizer", "score": 6},
    "TETRASODIUM EDTA": {"effect": "Chelating agent; can enhance absorption of other chemicals", "score": 4},
    "TETRASODIUM ETIDRONATE": {"effect": "Chelating agent; low toxicity", "score": 4},
    "THYMOL": {"effect": "Antimicrobial compound; may cause irritation", "score": 6},
    "TITANIUM DIOXIDE": {"effect": "UV filter and colorant; safe in topical products", "score": 3},
    "TOCOPHERYL ACETATE": {"effect": "Vitamin E derivative; protects from oxidative damage", "score": 2},
    "TOMATO POWDER": {"effect": "Provides antioxidants; safe in food quantities.", "score": 3},
    "TRIDECETH-10": {"effect": "Emulsifier; may increase skin penetration of other chemicals", "score": 4},
    "TRIDECETH-12": {"effect": "Emulsifier; moderate irritation risk", "score": 4},
    "TURMERIC POWDER": {"effect": "Anti-inflammatory spice with health benefits.", "score": 1},
    "VITAMIN E ACETATE": {"effect": "Antioxidant that protects skin from damage", "score": 2},
    "VP/VA COPOLYMER": {"effect": "Film-forming polymer; low toxicity", "score": 4},
    "WATER": {"effect": "Safe solvent used as a base for dissolving other ingredients", "score": 1},
    "XANTHAN GUM": {"effect": "Natural thickener; non-toxic and skin-safe", "score": 1},
    "YEAST": {"effect": "Natural leavening agent; safe and beneficial for digestion.", "score": 1},
    "ZEA MAYS (CORN) STARCH": {"effect": "Absorbs moisture and improves texture", "score": 1},
    "ZERO TRANSFAT BUTTER": {"effect": "Contains fats; safer than regular butter but still adds calories.", "score": 5},
    "ZINC OXIDE": {"effect": "Skin protectant; soothing and non-toxic.", "score": 3},
}


def predict_with_lstm(ingredient_name):
    if model is None or tokenizer is None:
        return None
    words = ingredient_name.upper().split()
    if not any(w in tokenizer.word_index for w in words):
        return None
    try:
        seq = tokenizer.texts_to_sequences([ingredient_name.upper()])
        padded = tf.keras.preprocessing.sequence.pad_sequences(
            seq, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post"
        )
        prediction = model.predict(padded, verbose=0)
        raw = float(prediction[0][0])
        return round(min(max(raw * 10, 1.0), 10.0), 2)
    except Exception:
        return None


def classify_product(final_score):
    if final_score <= 5:
        return "Safe"
    elif final_score <= 7:
        return "Moderate Risk"
    else:
        return "Harmful"


def analyze_ingredients(ingredients_raw):
    ingredients = [i.strip().upper() for i in ingredients_raw.split(",") if i.strip()]
    results = []
    unrecognized = []

    for ing in ingredients:
        clean_ing = ing.rstrip(".")
        if clean_ing in KNOWN_INGREDIENTS:
            data = KNOWN_INGREDIENTS[clean_ing]
            results.append({
                "name": clean_ing,
                "effect": data["effect"],
                "harm_score": float(data["score"]),
                "source": "database",
                "recognized": True,
            })
        else:
            predicted = predict_with_lstm(clean_ing)
            if predicted is not None:
                results.append({
                    "name": clean_ing,
                    "effect": "ML-predicted score based on ingredient structure",
                    "harm_score": predicted,
                    "source": "lstm_model",
                    "recognized": True,
                })
            else:
                unrecognized.append(clean_ing)
                results.append({
                    "name": clean_ing,
                    "effect": "Unrecognized ingredient - no harm score predicted",
                    "harm_score": None,
                    "source": "unknown",
                    "recognized": False,
                })

    scored = [r for r in results if r["harm_score"] is not None]
    scores = [r["harm_score"] for r in scored]

    if not scores:
        return {"ingredients": results, "summary": None,
                "unrecognized": unrecognized, "high_risk_ingredients": []}

    avg_score = round(sum(scores) / len(scores), 2)
    max_score = round(max(scores), 2)
    final_score = round((avg_score + max_score) / 2, 2)

    return {
        "ingredients": results,
        "summary": {
            "total_ingredients": len(ingredients),
            "analyzed_ingredients": len(scored),
            "unrecognized_count": len(unrecognized),
            "average_score": avg_score,
            "max_score": max_score,
            "final_product_score": final_score,
            "risk_classification": classify_product(final_score),
        },
        "unrecognized": unrecognized,
        "high_risk_ingredients": [r for r in scored if r["harm_score"] >= 7],
    }


# FastAPI app
app = FastAPI(title="Smart Ingredient Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    ingredients: str


@app.get("/")
def root():
    return {"message": "Smart Ingredient Analyzer API is running!"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None,
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    if not request.ingredients.strip():
        raise HTTPException(status_code=400, detail="Ingredients cannot be empty.")
    return analyze_ingredients(request.ingredients)


@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)
    ingredients = [i.strip() for i in text.replace('\n', ',').split(',') if i.strip()]
    return {"ingredients": ingredients, "raw_text": text}