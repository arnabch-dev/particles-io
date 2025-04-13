import { useAuth0 } from "@auth0/auth0-react";
import { PropsWithChildren } from "react";

export default function AuthProtect({ children }: PropsWithChildren) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    loginWithRedirect();
  }

  return <>{children}</>;
}