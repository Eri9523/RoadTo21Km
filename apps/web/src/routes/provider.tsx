import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { routes } from "./routes";

export function AppRouterProvider() {
  return <RouterProvider router={createBrowserRouter(routes)} />;
}
