import React, { useCallback, useState } from 'react';
import { Upload, Image, FileText, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
  onTextInput: (text: string) => void;
  isProcessing: boolean;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onImageUpload, onTextInput, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [inputMode, setInputMode] = useState<'image' | 'text'>('image');
  const [textValue, setTextValue] = useState('');

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        handleFile(file);
      }
    }
  }, []);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    onImageUpload(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const clearPreview = () => {
    setPreview(null);
  };

  const handleTextSubmit = () => {
    if (textValue.trim()) {
      onTextInput(textValue);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Input Mode Toggle */}
      <div className="flex justify-center gap-2 mb-6">
        <button
          onClick={() => setInputMode('image')}
          className={cn(
            "flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all duration-300",
            inputMode === 'image'
              ? "gradient-hero text-primary-foreground shadow-card"
              : "bg-secondary text-secondary-foreground hover:bg-accent"
          )}
        >
          <Image className="w-5 h-5" />
          Upload Image
        </button>
        <button
          onClick={() => setInputMode('text')}
          className={cn(
            "flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all duration-300",
            inputMode === 'text'
              ? "gradient-hero text-primary-foreground shadow-card"
              : "bg-secondary text-secondary-foreground hover:bg-accent"
          )}
        >
          <FileText className="w-5 h-5" />
          Enter Text
        </button>
      </div>

      {inputMode === 'image' ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={cn(
            "relative border-2 border-dashed rounded-2xl p-8 transition-all duration-300",
            dragActive
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border hover:border-primary/50 hover:bg-accent/50",
            preview && "border-solid border-primary/30"
          )}
        >
          {preview ? (
            <div className="relative animate-scale-in">
              <button
                onClick={clearPreview}
                className="absolute -top-3 -right-3 z-10 p-2 bg-card rounded-full shadow-card hover:bg-accent transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
              <img
                src={preview}
                alt="Uploaded ingredient label"
                className="w-full max-h-80 object-contain rounded-xl"
              />
              {isProcessing && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded-xl">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-sm font-medium text-muted-foreground">Analyzing ingredients...</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <label className="flex flex-col items-center justify-center cursor-pointer py-8">
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-4 animate-float">
                <Upload className="w-10 h-10 text-primary" />
              </div>
              <p className="text-lg font-semibold mb-2">
                Drop your ingredient label here
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                or click to browse from your device
              </p>
              <span className="text-xs text-muted-foreground/60">
                Supports: JPG, PNG, WEBP
              </span>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
            </label>
          )}
        </div>
      ) : (
        <div className="space-y-4 animate-fade-in">
          <textarea
            value={textValue}
            onChange={(e) => setTextValue(e.target.value)}
            placeholder="Paste or type your ingredient list here...

Example: Water, Sugar, Palm Oil, Cocoa Powder, Emulsifier (Soy Lecithin), Natural Flavoring, Salt"
            className="w-full h-48 p-4 rounded-2xl border-2 border-border bg-card text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all resize-none"
          />
          <button
            onClick={handleTextSubmit}
            disabled={!textValue.trim() || isProcessing}
            className={cn(
              "w-full py-4 rounded-xl font-semibold transition-all duration-300",
              textValue.trim() && !isProcessing
                ? "gradient-hero text-primary-foreground shadow-card hover:shadow-elevated hover:scale-[1.02]"
                : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            {isProcessing ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </span>
            ) : (
              "Analyze Ingredients"
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
