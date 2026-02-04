export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      {/* Form side */}
      <div className="flex flex-1 items-center justify-center px-8">
        <div className="w-full max-w-sm">{children}</div>
      </div>
      {/* Brand panel */}
      <div className="hidden w-1/2 bg-ink-900 lg:flex lg:flex-col lg:items-center lg:justify-center lg:px-12">
        <div className="max-w-md text-center">
          <div className="mx-auto mb-8 flex h-12 w-12 items-center justify-center rounded-lg bg-white">
            <span className="text-lg font-bold text-ink-900">EN</span>
          </div>
          <h2 className="text-2xl font-semibold text-white">
            The platform for modern newsrooms
          </h2>
          <p className="mt-4 text-sm leading-relaxed text-ink-400">
            Connect with verified freelance journalists, manage pitches and
            assignments, and streamline your editorial workflow — all in one
            place.
          </p>
          <div className="mt-10 border-t border-ink-800 pt-8">
            <blockquote className="text-sm italic text-ink-400">
              &ldquo;Elastic Newsroom transformed how we work with freelancers.
              Our editorial team is more efficient and our coverage has never
              been better.&rdquo;
            </blockquote>
            <p className="mt-3 text-xs font-medium text-ink-500">
              — Sarah Chen, Managing Editor at The Daily Record
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
