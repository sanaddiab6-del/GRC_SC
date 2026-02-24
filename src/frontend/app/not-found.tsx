import Link from "next/link";

export default function NotFound() {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen flex-col items-center justify-center bg-background">
          <div className="text-center space-y-4 px-4">
            <h1 className="text-6xl font-bold text-foreground">404</h1>
            <h2 className="text-2xl font-semibold text-muted-foreground">
              Page Not Found
            </h2>
            <p className="text-muted-foreground max-w-md">
              The page you are looking for does not exist or has been moved.
            </p>
            <div className="flex gap-4 justify-center pt-4">
              <Link
                href="/en/dashboard"
                className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Go to Dashboard (English)
              </Link>
              <Link
                href="/ar/dashboard"
                className="px-6 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
              >
                الذهاب إلى لوحة التحكم (عربي)
              </Link>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
