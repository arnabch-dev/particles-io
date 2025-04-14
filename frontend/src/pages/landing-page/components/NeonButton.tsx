
import React from 'react';
import { cn } from '../../../lib/utils';
import { Button } from '../../../components/ui/button';
import { Play } from 'lucide-react';

interface NeonButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  color?: 'blue' | 'purple' | 'green';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

const NeonButton = ({ 
  children, 
  className, 
  color = 'blue', 
  size = 'md',
  showIcon = true,
  ...props 
}: NeonButtonProps) => {
  const colorStyles = {
    blue: 'bg-neon-blue/10 text-neon-blue border-neon-blue neon-shadow-blue hover:bg-neon-blue/20',
    purple: 'bg-neon-purple/10 text-neon-purple border-neon-purple neon-shadow-purple hover:bg-neon-purple/20',
    green: 'bg-neon-green/10 text-neon-green border-neon-green neon-shadow-green hover:bg-neon-green/20',
  };

  const sizeStyles = {
    sm: 'text-sm py-1 px-4',
    md: 'text-base py-2 px-6',
    lg: 'text-lg py-3 px-8',
  };

  return (
    <Button
      className={cn(
        'relative transition-all duration-300 border-2 flex items-center justify-center gap-2 font-bold rounded-lg',
        'animate-pulse-glow',
        colorStyles[color],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {showIcon && color === 'blue' && <Play className="h-5 w-5" />}
      {children}
    </Button>
  );
};

export default NeonButton;
