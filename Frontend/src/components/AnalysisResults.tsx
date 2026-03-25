import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Shield, AlertTriangle, XCircle, Tag } from 'lucide-react';
import { cn } from '@/lib/utils';

ChartJS.register(ArcElement, Tooltip, Legend);

export interface Ingredient {
  name: string;
  riskLevel: 'safe' | 'caution' | 'danger';
  description: string;
  category: string;
}

interface AnalysisResultsProps {
  ingredients: Ingredient[];
  overallScore: number;
  productName?: string;
  riskLevel?: 'safe' | 'caution' | 'danger'; // FIX: accept from parent (backend)
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  ingredients,
  overallScore,
  productName,
  riskLevel,
}) => {
  const safeCount = ingredients.filter((i) => i.riskLevel === 'safe').length;
  const cautionCount = ingredients.filter((i) => i.riskLevel === 'caution').length;
  const dangerCount = ingredients.filter((i) => i.riskLevel === 'danger').length;

  // FIX: Use riskLevel from backend if provided, otherwise fall back to score-based logic
  const getOverallRating = () => {
    if (riskLevel) {
      const labels = { safe: 'Safe', caution: 'Moderate', danger: 'Concerning' };
      return { label: labels[riskLevel], level: riskLevel };
    }
    if (overallScore <= 3) return { label: 'Safe', level: 'safe' as const };
    if (overallScore <= 6) return { label: 'Moderate', level: 'caution' as const };
    return { label: 'Concerning', level: 'danger' as const };
  };

  const rating = getOverallRating();

  const chartData = {
    labels: ['Safe', 'Caution', 'Danger'],
    datasets: [
      {
        data: [safeCount, cautionCount, dangerCount],
        backgroundColor: [
          'hsl(152, 60%, 42%)',
          'hsl(38, 92%, 50%)',
          'hsl(0, 72%, 51%)',
        ],
        borderColor: [
          'hsl(152, 60%, 35%)',
          'hsl(38, 92%, 43%)',
          'hsl(0, 72%, 44%)',
        ],
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle',
          font: {
            family: 'Plus Jakarta Sans',
            size: 13,
            weight: 500,
          },
        },
      },
      tooltip: {
        backgroundColor: 'hsl(0, 0%, 100%)',
        titleColor: 'hsl(150, 25%, 15%)',
        bodyColor: 'hsl(150, 25%, 15%)',
        borderColor: 'hsl(145, 20%, 88%)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 12,
        titleFont: {
          family: 'Plus Jakarta Sans',
          size: 14,
          weight: 600,
        },
        bodyFont: {
          family: 'Plus Jakarta Sans',
          size: 13,
        },
      },
    },
    cutout: '60%',
  };

  return (
    <div className="w-full animate-slide-up">
      {/* Overall Score Card */}
      <div
        className={cn(
          "relative overflow-hidden rounded-3xl p-8 mb-8 text-center",
          rating.level === 'safe' && "gradient-safe",
          rating.level === 'caution' && "gradient-caution",
          rating.level === 'danger' && "gradient-danger"
        )}
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.2),transparent)]" />
        <div className="relative z-10">
          {productName && (
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm text-white text-sm font-medium mb-4 animate-fade-in">
              <Tag className="w-4 h-4" />
              <span>Product:</span>
              <span className="font-semibold">{productName}</span>
            </div>
          )}
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="w-24 h-24 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
              {/* FIX: Show score as X/10 instead of 0-100 */}
              <span className="text-4xl font-bold text-white">{overallScore}<span className="text-lg">/10</span></span>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            {rating.label} Product
          </h2>
          <p className="text-white/80 text-sm max-w-md mx-auto">
            Based on analysis of {ingredients.length} ingredients
          </p>
        </div>
      </div>

      {/* Chart and Stats */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-card rounded-2xl p-6 shadow-card">
          <h3 className="text-lg font-semibold mb-4">Ingredient Distribution</h3>
          <div className="h-64">
            <Doughnut data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="bg-card rounded-2xl p-6 shadow-card">
          <h3 className="text-lg font-semibold mb-4">Quick Overview</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-safe-bg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-safe flex items-center justify-center">
                  <Shield className="w-5 h-5 text-safe-foreground" />
                </div>
                <span className="font-medium">Safe</span>
              </div>
              <span className="text-2xl font-bold text-safe">{safeCount}</span>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-caution-bg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-caution flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-caution-foreground" />
                </div>
                <span className="font-medium">Moderate Risk</span>
              </div>
              <span className="text-2xl font-bold text-caution">{cautionCount}</span>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-danger-bg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-danger flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-danger-foreground" />
                </div>
                <span className="font-medium">Harmful</span>
              </div>
              <span className="text-2xl font-bold text-danger">{dangerCount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Ingredient List */}
      <div className="bg-card rounded-2xl p-6 shadow-card">
        <h3 className="text-lg font-semibold mb-4">Ingredient Analysis</h3>
        <div className="space-y-3">
          {ingredients.map((ingredient, index) => (
            <IngredientCard key={index} ingredient={ingredient} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
};

const IngredientCard: React.FC<{ ingredient: Ingredient; index: number }> = ({
  ingredient,
  index,
}) => {
  const [expanded, setExpanded] = React.useState(false);

  const bgClass = {
    safe: 'bg-safe-bg border-safe/20',
    caution: 'bg-caution-bg border-caution/20',
    danger: 'bg-danger-bg border-danger/20',
  }[ingredient.riskLevel];

  const iconBgClass = {
    safe: 'bg-safe text-safe-foreground',
    caution: 'bg-caution text-caution-foreground',
    danger: 'bg-danger text-danger-foreground',
  }[ingredient.riskLevel];

  const labelClass = {
    safe: 'text-safe',
    caution: 'text-caution',
    danger: 'text-danger',
  }[ingredient.riskLevel];

  const Icon = {
    safe: Shield,
    caution: AlertTriangle,
    danger: XCircle,
  }[ingredient.riskLevel];

  return (
    <div
      className={cn(
        "border rounded-xl overflow-hidden transition-all duration-300 cursor-pointer hover:shadow-soft",
        bgClass
      )}
      style={{ animationDelay: `${index * 50}ms` }}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <div className={cn("w-10 h-10 rounded-full flex items-center justify-center", iconBgClass)}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <p className="font-semibold">{ingredient.name}</p>
            <p className="text-xs text-muted-foreground">{ingredient.category}</p>
          </div>
        </div>
        <div className={cn("text-sm font-semibold capitalize", labelClass)}>
          {ingredient.riskLevel === 'safe' ? 'Safe' : ingredient.riskLevel === 'caution' ? 'Caution' : 'Danger'}
        </div>
      </div>
      {expanded && (
        <div className="px-4 pb-4 animate-fade-in">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {ingredient.description}
          </p>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;