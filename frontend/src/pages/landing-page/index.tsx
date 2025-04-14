
import React, { useState } from 'react';
import { 
  User, 
  Users, 
  Zap, 
  Target, 
  Sparkles, 
  Laptop, 
  ArrowRight,
  MessageCircle,
  Globe
} from 'lucide-react';

import NeonButton from './components/NeonButton';
import GameModeCard from './components/GameModeCard';
import FeatureCard from './components/FeatureCard';
import SectionTitle from './components/SectionTitle';
import Navbar from './components/Navbar';
import LeaderboardPreview from './components/LeaderboardPreview';
import GameOptionsModal from './components/GameOptionsModal';

const currentYear = (new Date()).getFullYear()

const LandingPage = () => {
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
    console.log("Starting single player game");
  };

  return (
    <div className="min-h-screen bg-dark text-white">
      <Navbar />
      
      {/* Game Options Modal */}
      <GameOptionsModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSelectSinglePlayer={handleSinglePlayerSelect}
      />
      
      {/* Hero Section */}
      <section className="relative pt-28 md:pt-40 md:pb-20 overflow-hidden">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-4">
            <span className="text-neon-blue neon-text-blue">Particles</span> IO
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-300 max-w-2xl mx-auto">
            Enter the Chaos. Outlast the Swarm.
          </p>
          <div className="flex justify-center">
            <NeonButton size="lg" className="mb-12" onClick={handlePlayNowClick}>
              Play Now
            </NeonButton>
          </div>
          
        </div>
      </section>

      {/* Game Modes Section */}
      <section id="game-modes" className="pb-20 pt-14 relative">
        <div className="container mx-auto px-4">
          <SectionTitle 
            title="Game Modes" 
            subtitle="Choose your path to chaos and glory"
            color="purple"
          />
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <GameModeCard
              title="Single Player"
              description="Challenge waves of particles in this intense solo experience. Master your skills and top the leaderboards."
              icon={User}
              color="blue"
            />
            <GameModeCard
              title="Multiplayer"
              description="Battle against other players in real-time. Absorb particles, grow in size, and become the last one standing."
              icon={Users}
              color="purple"
            />
          </div>
        </div>
      </section>

      {/* Gameplay Video Section */}
      <section id="gameplay" className="py-20 relative">
        <div className="container mx-auto px-4">
          <SectionTitle 
            title="Gameplay Trailer" 
            subtitle="See the particle chaos in action"
            color="green"
          />
          
          <div className="max-w-4xl mx-auto relative">
            <div className="aspect-video rounded-lg overflow-hidden border-2 border-neon-green neon-shadow-green">
              <iframe 
                className="w-full h-full"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ?si=example"
                title="Particles IO Gameplay Trailer"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 relative">
        <div className="container mx-auto px-4">
          <SectionTitle 
            title="Game Features" 
            subtitle="Discover what makes Particles IO unique"
            color="blue"
          />
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-6xl mx-auto">
            <FeatureCard
              title="Real-time Multiplayer"
              description="Battle with players from around the world in seamless real-time matches."
              icon={Globe}
              color="blue"
            />
            <FeatureCard
              title="Directional Shooting"
              description="Precise particle control with advanced directional shooting mechanics."
              icon={Target}
              color="purple"
            />
            <FeatureCard
              title="Explosive Effects"
              description="Stunning visual effects and particle explosions that react to your gameplay."
              icon={Sparkles}
              color="green"
            />
            <FeatureCard
              title="Cross-platform"
              description="Play on any device with full cross-platform compatibility and progression."
              icon={Laptop}
              color="blue"
            />
          </div>
        </div>
      </section>

      {/* Community Section */}
      <section id="community" className="py-20 relative">
        <div className="container mx-auto px-4">
          <SectionTitle 
            title="Join Our Community" 
            subtitle="Connect with players and stay updated"
            color="purple"
          />
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="flex flex-col justify-center">
              <h3 className="text-2xl font-bold mb-4 text-neon-purple">Be Part of the Swarm</h3>
              <p className="text-gray-300 mb-6">
                Join our thriving community of players. Share strategies, find teammates, and participate in exclusive events and tournaments.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <NeonButton color="purple" className="flex-1">
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Join Discord
                </NeonButton>
                <NeonButton color="blue" className="flex-1">
                  <Zap className="mr-2 h-5 w-5" />
                  Follow Updates
                </NeonButton>
              </div>
            </div>
            <LeaderboardPreview />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Ready to <span className="text-neon-blue neon-text-blue">Dive In</span>?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            The particle swarm awaits. Join thousands of players in the chaos.
          </p>
          <div className='mx-auto w-min'>
            <NeonButton size="lg" className="group" onClick={handlePlayNowClick}>
              Play Now
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </NeonButton>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-neon-blue/20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-2">
            <span className="text-neon-blue neon-text-blue">Particles</span> IO
          </h2>
          <p className="text-gray-500 text-sm mb-4">
            © {currentYear} Particles IO. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
