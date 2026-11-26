import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoEvolve Protocol | Decentralized ZK-Attested Autonomous Agent Dashboard",
  description:
    "Interactive Developer Dashboard & Frontend Visualizer for AutoEvolve Protocol: Real-Time Execution DAG, Side-by-Side Diffs, Circom Groth16 ZK Attestations, and Cross-Agent Memory Inheritance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#07090e] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}

