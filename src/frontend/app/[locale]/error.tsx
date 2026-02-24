"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Locale page error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <div className="text-center space-y-4 px-4 max-w-md">
        <h2 className="text-3xl font-bold text-destructive">
          Something went wrong! / حدث خطأ ما!
        </h2>
        <p className="text-muted-foreground">
          {error.message || "An unexpected error occurred / حدث خطأ غير متوقع"}
        </p>
        {error.digest && (
          <p className="text-xs text-muted-foreground">
            Error ID: {error.digest}
          </p>
        )}
        <div className="flex gap-3 justify-center pt-4">
          <button
            onClick={reset}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Try again / حاول مرة أخرى
          </button>
          <Link
            href="/en/dashboard"
            className="px-6 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90 transition-colors"
          >
            Go Home / الصفحة الرئيسية
          </Link>
        </div>
      </div>
    </div>
  );
}
