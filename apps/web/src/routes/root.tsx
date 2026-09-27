import { Outlet } from "react-router-dom";

export function Component() {
  return (
    <main className="min-h-screen">
      <Outlet />
    </main>
  );
}
