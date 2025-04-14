
import { useState } from 'react';
import NeonButton from './NeonButton';
import GameOptionsModal from './GameOptionsModal';

const Navbar = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handlePlayNowClick = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSinglePlayerSelect = () => {
    // For now, just close the modal
    setIsModalOpen(false);
    // In a real application, you would redirect or load the single player game
    console.log("Starting single player game from navbar");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-dark/80 backdrop-blur-md z-50 border-b border-neon-blue/20">
      <div className="container mx-auto py-4 px-4 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-white">
            <span className="text-neon-blue neon-text-blue">Particles</span> IO
          </h1>
        </div>
        <div className="space-x-4 hidden md:flex items-center">
          <a href="#game-modes" className="text-gray-300 hover:text-neon-blue transition-colors">
            Game Modes
          </a>
          <a href="#gameplay" className="text-gray-300 hover:text-neon-blue transition-colors">
            Gameplay
          </a>
          <a href="#features" className="text-gray-300 hover:text-neon-blue transition-colors">
            Features
          </a>
          <a href="#community" className="text-gray-300 hover:text-neon-blue transition-colors">
            Community
          </a>
          <NeonButton size="sm" showIcon={true} onClick={handlePlayNowClick}>
            Play Now
          </NeonButton>
        </div>
        <div className="md:hidden">
          <NeonButton size="sm" showIcon={true} onClick={handlePlayNowClick}>
            Play
          </NeonButton>
        </div>
      </div>
      
      {/* Game Options Modal */}
      <GameOptionsModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSelectSinglePlayer={handleSinglePlayerSelect}
      />
    </nav>
  );
};

export default Navbar;
