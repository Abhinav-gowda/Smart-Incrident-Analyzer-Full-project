import { Leaf, Github } from 'lucide-react';
const Header: React.FC = () => {
  return <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl gradient-hero flex items-center justify-center shadow-soft">
            <Leaf className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold">
            Ingredient<span className="text-primary"> IQ</span>
          </span>
        </div>
        
        <nav className="hidden md:flex items-center gap-6">
          <a href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            How it works
          </a>
          <a href="#" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            About
          </a>
        </nav>
        
        <div className="flex items-center gap-3">
          
          
        </div>
      </div>
    </header>;
};
export default Header;