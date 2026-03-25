import { Leaf, Heart } from 'lucide-react';
const Footer: React.FC = () => {
  return <footer className="border-t border-border bg-card/50 mt-20">
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg gradient-hero flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-bold">
              Ingredient<span className="text-primary"> IQ</span>
            </span>
          </div>
          
          <p className="text-sm text-muted-foreground flex items-center gap-1">Made with
for healthier choices<Heart className="w-4 h-4 text-danger fill-danger" /> for healthier choices
          </p>
          
          <p className="text-sm text-muted-foreground">©  Smart Ingredient Analyzer</p>
        </div>
      </div>
    </footer>;
};
export default Footer;