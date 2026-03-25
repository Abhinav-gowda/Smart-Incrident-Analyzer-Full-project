import React from 'react';
import { Tag, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExtractedIngredientsProps {
  ingredients: string[];
  isVisible: boolean;
}

const ExtractedIngredients: React.FC<ExtractedIngredientsProps> = ({
  ingredients,
  isVisible,
}) => {
  if (!isVisible || ingredients.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mb-8 animate-slide-up">
      <div className="bg-card rounded-2xl p-6 shadow-card">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <Tag className="w-4 h-4 text-primary" />
          </div>
          <h3 className="text-lg font-semibold">Extracted Ingredients</h3>
          <span className="ml-auto text-sm text-muted-foreground">
            {ingredients.length} found
          </span>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {ingredients.map((ingredient, index) => (
            <span
              key={index}
              className={cn(
                "px-3 py-1.5 bg-secondary text-secondary-foreground rounded-full text-sm font-medium",
                "hover:bg-accent transition-colors cursor-default",
                "animate-scale-in"
              )}
              style={{ animationDelay: `${index * 30}ms` }}
            >
              {ingredient}
            </span>
          ))}
        </div>
        
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            <ChevronRight className="w-4 h-4" />
            Click analyze to get detailed safety information
          </p>
        </div>
      </div>
    </div>
  );
};

export default ExtractedIngredients;
