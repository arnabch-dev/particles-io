import { withAuthenticationRequired } from "@auth0/auth0-react";
import { PropsWithChildren } from "react";

export default function AuthProtect({ children }: PropsWithChildren) {
  const Protected = withAuthenticationRequired(() => <>{children}</>);
  return <Protected />;
}
