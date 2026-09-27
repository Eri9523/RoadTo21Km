import { StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { AppRouterProvider } from "./routes/provider";
import { Loading } from "./components/Loading";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Suspense fallback={<Loading />}>
      <AppRouterProvider />
    </Suspense>
  </StrictMode>,
);
