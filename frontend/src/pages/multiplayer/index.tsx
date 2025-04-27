import { useAuth0 } from "@auth0/auth0-react";
import MultiplayerBoard from "./components/MultiplayerBoard";
import Loader from "../../components/Loader";

export default function MultiplayerPage() {
  const { isLoading } = useAuth0();
  if (isLoading) return <Loader text="Loading User...." />;
  console.log('game page')
  return <MultiplayerBoard />;
}
