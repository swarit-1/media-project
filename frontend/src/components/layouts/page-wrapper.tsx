interface PageWrapperProps {
  children: React.ReactNode;
}

export function PageWrapper({ children }: PageWrapperProps) {
  return (
    <main className="flex-1 overflow-y-auto">
      <div className="px-8 py-6">{children}</div>
    </main>
  );
}
