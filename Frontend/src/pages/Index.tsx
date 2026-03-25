import { useState, useCallback } from 'react';
import Header from '@/components/Header';
import Hero from '@/components/Hero';
import ImageUpload from '@/components/ImageUpload';
import ExtractedIngredients from '@/components/ExtractedIngredients';
import AnalysisResults, { Ingredient } from '@/components/AnalysisResults';
import Footer from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { ArrowRight, RotateCcw, Tag, AlertCircle } from 'lucide-react';

// API URL - change this after deploying to Render
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://smart-incrident-analyzer-full-project.onrender.com';

interface ApiIngredient {
  name: string;
  effect: string;
  harm_score: number | null;
  source: 'database' | 'lstm_model' | 'unknown';
  recognized: boolean;
}

interface ApiSummary {
  total_ingredients: number;
  analyzed_ingredients: number;
  unrecognized_count: number;
  average_score: number;
  max_score: number;
  final_product_score: number;
  risk_classification: string;
}

interface ApiResponse {
  ingredients: ApiIngredient[];
  summary: ApiSummary | null;
  unrecognized: string[];
  high_risk_ingredients: ApiIngredient[];
}

// Convert harm score (1-10) to risk level for UI
function toRiskLevel(score: number | null): 'safe' | 'caution' | 'danger' {
  if (score === null) return 'caution';
  if (score <= 3) return 'safe';
  if (score <= 6) return 'caution';
  return 'danger';
}

function apiToIngredient(api: ApiIngredient): Ingredient {
  return {
    name: api.name,
    riskLevel: toRiskLevel(api.harm_score),
    // FIX: show the actual effect from the model, not the source type
    description: api.effect,
    category: api.harm_score !== null
      ? `Harm Score: ${api.harm_score}/10`
      : 'Unrecognized',
  };
}

const Index: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractedIngredients, setExtractedIngredients] = useState<string[]>([]);
  const [analysisResults, setAnalysisResults] = useState<Ingredient[] | null>(null);
  const [apiSummary, setApiSummary] = useState<ApiSummary | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [productName, setProductName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const simulateOCR = useCallback(() => {
    return new Promise<string[]>((resolve) => {
      setTimeout(() => {
        resolve(['Water', 'Glycerin', 'Fragrance', 'Sodium Lauryl Sulfate', 'Parabens']);
      }, 1500);
    });
  }, []);

  // Real API call to FastAPI backend
  const analyzeWithAPI = async (ingredientList: string[]): Promise<ApiResponse> => {
    const ingredientString = ingredientList.join(', ');
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ingredients: ingredientString }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `API error: ${response.status}`);
    }
    return response.json();
  };

  const handleImageUpload = async (file: File) => {
    setIsProcessing(true);
    setShowResults(false);
    setAnalysisResults(null);
    setError(null);
    const extracted = await simulateOCR();
    setExtractedIngredients(extracted);
    setIsProcessing(false);
  };

  const handleTextInput = async (text: string) => {
    setIsProcessing(true);
    setShowResults(false);
    setAnalysisResults(null);
    setError(null);
    const ingredients = text.split(/[,;\n]/).map((i) => i.trim()).filter((i) => i.length > 0);
    setExtractedIngredients(ingredients);
    setIsProcessing(false);
  };

  // This calls your real LSTM model via FastAPI
  const handleAnalyze = async () => {
    setIsProcessing(true);
    setError(null);
    try {
      const apiResult = await analyzeWithAPI(extractedIngredients);
      const uiIngredients = apiResult.ingredients.map(apiToIngredient);
      setAnalysisResults(uiIngredients);
      setApiSummary(apiResult.summary);
      setShowResults(true);
    } catch (err: any) {
      setError(
        err.message.includes('Failed to fetch')
          ? 'Cannot connect to the API. Make sure your backend is running at ' + API_BASE_URL
          : err.message
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setExtractedIngredients([]);
    setAnalysisResults(null);
    setApiSummary(null);
    setShowResults(false);
    setProductName('');
    setError(null);
  };

  // FIX: Use the backend's final_product_score directly (it's already on 1-10 scale)
  // Display it as-is (rounded to nearest integer out of 10)
  const calculateOverallScore = (): number => {
    if (!apiSummary) return 5;
    // Return score out of 10 (rounded)
    return Math.round(apiSummary.final_product_score);
  };

  // FIX: Use the backend's risk_classification directly instead of re-computing from score
 const getRiskLevel = (): 'safe' | 'caution' | 'danger' => {
  if (!apiSummary) return 'caution';
  const c = apiSummary.risk_classification;
  if (c === 'Low Risk' || c === 'Safe') return 'safe';
  if (c === 'Moderate Risk') return 'caution';
  return 'danger';
};

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Hero />
        <section className="container mx-auto px-4 pb-20">
          {!showResults ? (
            <>
              <div className="w-full max-w-2xl mx-auto mb-10 animate-fade-in">
                <div className="relative bg-card rounded-2xl shadow-soft p-6 border border-border/50">
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/[0.02] to-transparent pointer-events-none" />
                  <div className="relative z-10">
                    <label htmlFor="productName" className="text-xs font-medium text-muted-foreground tracking-wide uppercase mb-3 block text-center">
                      Product Identification
                    </label>
                    <div className="relative max-w-lg mx-auto">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
                        <Tag className="w-5 h-5 text-primary/60" />
                      </div>
                      <input
                        id="productName"
                        type="text"
                        value={productName}
                        onChange={(e) => setProductName(e.target.value)}
                        placeholder="What product are you analyzing? (e.g., Face Wash, Shampoo)"
                        className="w-full bg-secondary/30 border-0 rounded-xl py-4 pl-12 pr-4 text-foreground placeholder:text-muted-foreground/70 text-center transition-all duration-300 outline-none focus:bg-secondary/50 focus:shadow-[0_0_0_3px_hsl(var(--primary)/0.15)] focus:ring-0"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground/60 text-center mt-3">
                      Optional — helps personalize your analysis results
                    </p>
                  </div>
                </div>
              </div>

              <ImageUpload onImageUpload={handleImageUpload} onTextInput={handleTextInput} isProcessing={isProcessing} />
              <ExtractedIngredients ingredients={extractedIngredients} isVisible={extractedIngredients.length > 0 && !isProcessing} />

              {error && (
                <div className="w-full max-w-2xl mx-auto mt-4 p-4 bg-danger-bg border border-danger/20 rounded-xl flex items-start gap-3 animate-fade-in">
                  <AlertCircle className="w-5 h-5 text-danger mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-danger">{error}</p>
                </div>
              )}

              {extractedIngredients.length > 0 && !isProcessing && (
                <div className="flex justify-center mt-6 animate-fade-in">
                  <Button
                    onClick={handleAnalyze}
                    size="lg"
                    className="gradient-hero text-primary-foreground px-8 py-6 text-lg font-semibold rounded-xl shadow-card hover:shadow-elevated hover:scale-[1.02] transition-all duration-300"
                  >
                    Analyze Safety
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </div>
              )}
            </>
          ) : (
            <>
              {apiSummary && (
                <div className="w-full max-w-3xl mx-auto mb-6 p-4 bg-card rounded-2xl shadow-soft border border-border/50 animate-fade-in">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold">{apiSummary.total_ingredients}</p>
                      <p className="text-xs text-muted-foreground">Total Ingredients</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{apiSummary.average_score.toFixed(1)}</p>
                      <p className="text-xs text-muted-foreground">Avg Harm Score</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{apiSummary.final_product_score.toFixed(1)}</p>
                      <p className="text-xs text-muted-foreground">Final Score /10</p>
                    </div>
                    <div>
                      <p className={`text-lg font-bold ${
                        apiSummary.risk_classification === 'Low Risk' ? 'text-safe' :
                        apiSummary.risk_classification === 'Moderate Risk' ? 'text-caution' : 'text-danger'
                      }`}>{apiSummary.risk_classification}</p>
                      <p className="text-xs text-muted-foreground">Classification</p>
                    </div>
                  </div>
                </div>
              )}
              <div className="flex justify-center mb-8">
                <Button onClick={handleReset} variant="outline" className="gap-2">
                  <RotateCcw className="w-4 h-4" />
                  Analyze Another Product
                </Button>
              </div>
              {analysisResults && (
                <AnalysisResults
                  ingredients={analysisResults}
                  overallScore={calculateOverallScore()}
                  productName={productName || undefined}
                  riskLevel={getRiskLevel()}
                />
              )}
            </>
          )}
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Index;