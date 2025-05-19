
import { cn } from '../../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface GameModeCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color?: 'blue' | 'purple' | 'green';
  className?: string;
}

const GameModeCard = ({
  title,
  description,
  icon: Icon,
  color = 'blue',
  className
}: GameModeCardProps) => {
  const colorStyles = {
    blue: 'border-neon-blue neon-shadow-blue [&_svg]:text-neon-blue [&_h3]:text-neon-blue [&_h3]:neon-text-blue',
    purple: 'border-neon-purple neon-shadow-purple [&_svg]:text-neon-purple [&_h3]:text-neon-purple [&_h3]:neon-text-purple',
    green: 'border-neon-green neon-shadow-green [&_svg]:text-neon-green [&_h3]:text-neon-green [&_h3]:neon-text-green',
  };

  return (
    <div className={cn(
      'bg-dark-lighter p-6 rounded-lg border transition-all hover:scale-105',
      'animate-pulse-glow',
      colorStyles[color],
      className
    )}>
      <div className="mb-4">
        <Icon className="w-16 h-16" />
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </div>
  );
};

export default GameModeCard;
