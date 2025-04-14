
import { cn } from '../../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color?: 'blue' | 'purple' | 'green';
  className?: string;
}

const FeatureCard = ({
  title,
  description,
  icon: Icon,
  color = 'blue',
  className
}: FeatureCardProps) => {
  const colorStyles = {
    blue: 'border-neon-blue [&_svg]:text-neon-blue [&_h3]:text-neon-blue',
    purple: 'border-neon-purple [&_svg]:text-neon-purple [&_h3]:text-neon-purple',
    green: 'border-neon-green [&_svg]:text-neon-green [&_h3]:text-neon-green',
  };

  return (
    <div className={cn(
      'bg-dark-lighter/50 p-5 rounded-lg border transition-all hover:scale-105',
      colorStyles[color],
      className
    )}>
      <div className="flex items-start gap-4">
        <div className="mt-1">
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-lg font-bold mb-1">{title}</h3>
          <p className="text-gray-400 text-sm">{description}</p>
        </div>
      </div>
    </div>
  );
};

export default FeatureCard;
