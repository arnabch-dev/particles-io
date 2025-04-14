import { cn } from '../../../lib/utils';

interface SectionTitleProps {
  title: string;
  subtitle?: string;
  color?: 'blue' | 'purple' | 'green';
  className?: string;
}

const SectionTitle = ({
  title,
  subtitle,
  color = 'blue',
  className
}: SectionTitleProps) => {
  const colorStyles = {
    blue: 'text-neon-blue neon-text-blue',
    purple: 'text-neon-purple neon-text-purple',
    green: 'text-neon-green neon-text-green',
  };

  return (
    <div className={cn('text-center mb-12', className)}>
      <h2 className={cn('text-3xl md:text-4xl font-bold mb-2', colorStyles[color])}>
        {title}
      </h2>
      {subtitle && (
        <p className="text-gray-400 max-w-2xl mx-auto">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default SectionTitle;
