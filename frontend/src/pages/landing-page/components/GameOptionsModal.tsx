
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import NeonButton from './NeonButton';
import { User } from 'lucide-react';
import { toast } from '../../../components/ui/use-toast';

interface GameOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSinglePlayer: () => void;
}

const GameOptionsModal = ({
  isOpen,
  onClose,
  onSelectSinglePlayer
}: GameOptionsModalProps) => {
  const handleMultiplayerClick = () => {
    // For now, just show a toast notification about login requirement
    toast({
      title: "Login Required",
      description: "You need to login to play multiplayer mode.",
      variant: "destructive",
    });
    
    // Close the modal after showing the toast
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="bg-dark-lighter border-neon-blue neon-shadow-blue w-full">
        <DialogHeader>
          <DialogTitle className="text-2xl text-center text-neon-blue neon-text-blue">
            Choose Game Mode
          </DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-6 py-4">
          <div className="flex flex-col items-center gap-4">
            <NeonButton 
              color="blue" 
              className="w-full text-lg" 
              onClick={onSelectSinglePlayer}
            >
              Single Player
            </NeonButton>
            
            <NeonButton 
              color="purple" 
              className="w-full text-lg" 
              onClick={handleMultiplayerClick}
            >
              <User className="mr-2 h-5 w-5" />
              Multiplayer (Login Required)
            </NeonButton>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default GameOptionsModal;
