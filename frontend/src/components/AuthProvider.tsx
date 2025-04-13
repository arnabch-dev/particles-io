import { PropsWithChildren } from "react";
import { Auth0Provider, type AuthorizationParams } from "@auth0/auth0-react";
const AUTH_DOMAIN = import.meta.env.VITE_AUTH0_DOMAIN;
const AUTH_CLIENT_ID = import.meta.env.VITE_AUTH0_CLIENT_ID;

export default function AuthProvider({
  children,
  redirect_uri,
}: AuthorizationParams & PropsWithChildren) {
  return (
    <Auth0Provider
      domain={AUTH_DOMAIN}
      clientId={AUTH_CLIENT_ID}
      authorizationParams={{ redirect_uri }}
    >
      {children}
    </Auth0Provider>
  );
}
