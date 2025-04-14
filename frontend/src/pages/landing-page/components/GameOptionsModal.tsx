import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import NeonButton from "./NeonButton";
import { User } from "lucide-react";
import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router";

interface GameOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSinglePlayer: () => void;
}

const GameOptionsModal = ({
  isOpen,
  onClose,
  onSelectSinglePlayer,
}: GameOptionsModalProps) => {
  const { isAuthenticated } = useAuth0();

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
            <Link to="/single">
              <NeonButton
                color="blue"
                className="w-full text-lg"
                onClick={onSelectSinglePlayer}
              >
                Single Player
              </NeonButton>
            </Link>

            <Link to="/multiplayer">
              <NeonButton color="purple" className="w-full text-lg">
                <User className="mr-2 h-5 w-5" />
                Multiplayer{isAuthenticated ? "" : "(Login Required)"}
              </NeonButton>
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default GameOptionsModal;
