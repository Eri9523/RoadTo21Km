import type { RouteObject } from "react-router-dom";

export const routes: RouteObject[] = [
  {
    path: "/",
    lazy: () => import("./root"),
    children: [{ index: true, lazy: () => import("./home") }],
  },
];
