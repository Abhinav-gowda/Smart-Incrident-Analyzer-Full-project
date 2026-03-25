import { Sparkles, Shield, Zap, Eye } from 'lucide-react';

const Hero: React.FC = () => {
  return (
    <section className="relative py-20 px-4 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
      </div>
      
      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in">
          <Sparkles className="w-4 h-4" />
          AI-Powered Ingredient Analysis
        </div>
        
        {/* Main heading */}
        <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight animate-slide-up">
          Know What's In
          <span className="block bg-gradient-to-r from-primary to-emerald-500 bg-clip-text text-transparent">
            Your Products
          </span>
        </h1>
        
        {/* Subtitle */}
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-12 animate-fade-in" style={{ animationDelay: '100ms' }}>
          Upload any ingredient label and get instant, AI-powered safety analysis. 
          Make informed decisions about what you consume.
        </p>
        
        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto animate-fade-in" style={{ animationDelay: '200ms' }}>
          <FeatureCard
            icon={<Eye className="w-5 h-5" />}
            title="OCR Technology"
            description="Extract text from images instantly"
          />
          <FeatureCard
            icon={<Shield className="w-5 h-5" />}
            title="Safety Ratings"
            description="Color-coded risk assessment"
          />
          <FeatureCard
            icon={<Zap className="w-5 h-5" />}
            title="Instant Analysis"
            description="ML-powered ingredient evaluation"
          />
        </div>
      </div>
    </section>
  );
};

const FeatureCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
}> = ({ icon, title, description }) => {
  return (
    <div className="flex items-center gap-3 p-4 rounded-xl bg-card shadow-soft">
      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
        {icon}
      </div>
      <div className="text-left">
        <p className="font-semibold text-sm">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  );
};

export default Hero;
